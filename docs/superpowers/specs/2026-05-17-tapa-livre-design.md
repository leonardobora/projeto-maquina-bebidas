# Design — Tapa Livre + Sons Reais (extensão da Máquina de Bebidas)

**Status:** approved · pronto pra plano de implementação
**Data:** 2026-05-17
**Spec base:** [`2026-05-16-maquina-bebidas-design.md`](./2026-05-16-maquina-bebidas-design.md)

---

## 1. Objetivo

Expandir a feature autoral do tapa: hoje ele só existe **reativamente** quando a máquina trava durante a dispensa. Esta extensão adiciona um **tapa livre** acionável pelo user a qualquer momento no IDLE, com três desfechos probabilísticos (nada / bebida grátis / quebra com cooldown) e uma trilha sonora real usando `pygame.mixer`.

## 2. Decisões fechadas (do brainstorm)

| Decisão | Valor |
|---|---|
| Disponibilidade do tapa livre | Só no estado IDLE |
| Probabilidade — nada acontece | 70% |
| Probabilidade — bebida grátis aleatória | 20% |
| Probabilidade — quebra com cooldown | 10% |
| Duração do cooldown | 10 segundos (blocking real-time com countdown) |
| Bebida grátis conta como venda? | **Não** (categoria separada, ver §6) |
| Lib de áudio | `pygame.mixer` |
| Sons mínimos | 4 (tapa, dispensar, bebida_gratis, quebra) |
| Origem dos sons | URLs curados de freesound.org (CC0) — eu entrego, user baixa |

## 3. Arquitetura — onde cada coisa mora

| Mudança | Arquivo | Detalhe |
|---|---|---|
| Probabilidades, sorteador, mensagens | `eventos.py` | Constantes `PROB_TAPA_LIVRE_BEBIDA`, `PROB_TAPA_LIVRE_QUEBRA`, `COOLDOWN_QUEBRA_SEGUNDOS`. Função `resolver_tapa_livre() -> ResultadoTapaLivre` (Enum). Novas pools `tapa_livre_nada`, `tapa_livre_bebida`, `tapa_livre_quebra`, `cooldown`. |
| Tecla `t` no IDLE + roteamento | `maquina.py` | `ler_entrada_idle` aceita `'t'`. Nova função `handle_tapa_livre(console, catalogo)` despacha o resultado. Visor IDLE menciona `[T] tapa`. |
| Cooldown bloqueante com countdown | `maquina.py` | Função `executar_cooldown(console, segundos, catalogo)` — loop `time.sleep(1)` decrementando e redesenhando o visor a cada segundo. |
| Sorteio de bebida grátis | `produtos.py` | Método novo `Catalogo.sortear_com_estoque() -> Produto \| None`. |
| Camada de áudio | `audio.py` (novo módulo) | `init_audio()`, `tocar(nome)`, `tocar_async(nome)`. Mute opcional via env var `MAQUINA_MUTE=1` (útil pra testes). |
| Hooks de som | `animacoes.py`, `maquina.py` | Chamar `audio.tocar("tapa")` no início de `animar_tapa`, `audio.tocar("dispensar")` em `animar_dispensar`, etc. |
| Painel admin com `tapas_premiados` | `ui.py`, `maquina.py` | `render_admin` recebe terceiro parâmetro `tapas_premiados`. `main` passa o contador adiante. |
| Assets | `assets/sounds/` (novo dir) | Arquivos `.wav` ou `.ogg`. `README.md` na pasta com créditos e URLs do freesound. |
| Dependência nova | `requirements.txt` | `pygame>=2.5` |

## 4. Fluxo do tapa livre

```
IDLE (user digita 't')
  ↓
audio.tocar("tapa") + animar_tapa()
  ↓
resolver_tapa_livre() → ResultadoTapaLivre
  │
  ├─ NADA (70%)
  │    └─ visor: mensagem("tapa_livre_nada") · sleep 1.5s · volta IDLE
  │
  ├─ BEBIDA_GRATIS (20%)
  │    └─ produto = catalogo.sortear_com_estoque()
  │       ├─ None (tudo esgotado) → cai pra mensagem específica "bugou_vazio" · volta IDLE
  │       └─ Produto → audio.tocar("bebida_gratis")
  │                     animar_dispensar(produto.nome)
  │                     produto.decrementar()
  │                     tapas_premiados += 1
  │                     volta IDLE
  │
  └─ QUEBRA (10%)
       └─ audio.tocar("quebra")
          visor: mensagem("tapa_livre_quebra") · sleep 1s
          executar_cooldown(COOLDOWN_QUEBRA_SEGUNDOS, catalogo)
          volta IDLE
```

## 5. Contrato do módulo `audio.py`

```python
# audio.py
"""Wrapper fino sobre pygame.mixer. Tolerante a falha — se inicialização
quebrar (sem placa de som, headless, etc.), todas as chamadas viram no-op."""

_sons: dict[str, pygame.mixer.Sound] = {}
_habilitado: bool = False

def init_audio() -> None:
    """Inicializa pygame.mixer e carrega sons de assets/sounds/.
    Falha silenciosa: define _habilitado=False se algo der errado."""

def tocar(nome: str) -> None:
    """Toca som não-bloqueante. No-op se desabilitado ou nome inválido."""

def parar_tudo() -> None:
    """Para todos os sons em execução (usado em transições abruptas)."""
```

**Por que tolerante a falha:** o projeto roda em ambientes acadêmicos (corretores em VMs sem áudio). A ausência de som não pode quebrar o programa. Env var `MAQUINA_MUTE=1` força `_habilitado = False` direto, ignorando init.

## 6. Estatísticas no admin

Adicionar contador `tapas_premiados` ao loop main (paralelo a `vendas`). Passar pra `handle_admin` → `render_admin`. Painel admin passa a mostrar:

```
Vendas: 12 · Tapas premiados: 3 · Caixa: R$45,50
```

Pequena mudança em `ui.render_admin` pra incluir o terceiro número.

## 7. Mensagens novas (pools em `eventos.py`)

```python
"tapa_livre_nada": [
    "Só ecoou. Bonitão.",
    "A máquina nem se mexeu.",
    "Tomou o tapa calada.",
    "Você bateu, ela ignorou.",
],
"tapa_livre_bebida": [
    "🎰 BUGOU! Uma {bebida} caiu de graça!",
    "🎰 Acidente feliz. Pega a {bebida}.",
    "🎰 Jackpot da gambiarra: {bebida} grátis!",
],
"tapa_livre_bebida_vazio": [
    "Bugou mas tava tudo vazio. Sorte da casa.",
    "Cuspiu vento. Estoque zerado.",
],
"tapa_livre_quebra": [
    "💥 QUEBROU. Você passou do ponto.",
    "💥 Curto-circuito. Foi mal, amigão.",
    "💥 Fumacinha saindo da lateral. Era isso?",
],
"cooldown": [
    "⚙ Manutenção · {segundos}s",
],
```

## 8. Sons a curar (freesound.org)

Vou entregar 4 URLs curadas (licença CC0 / Creative Commons 0). Nomes esperados em `assets/sounds/`:

| Arquivo | Descrição | Quando toca |
|---|---|---|
| `tapa.wav` | Impacto seco/thump na lateral metálica | `animar_tapa` |
| `dispensar.wav` | Motor de espiral + lata caindo | `animar_dispensar` |
| `bebida_gratis.wav` | Ding-ding de jackpot/slot machine curto | Resultado BEBIDA_GRATIS |
| `quebra.wav` | Zap elétrico / curto-circuito | Resultado QUEBRA |

Critérios de curadoria: < 2 segundos cada (exceto `dispensar` que pode ir até 3s), volume normalizado, sem voz humana, sem música melódica.

**Fallback:** se algum arquivo não existir em runtime, `tocar(nome)` é no-op. Programa funciona sem som.

## 9. Edge cases

| Caso | Comportamento |
|---|---|
| Sorteia BEBIDA_GRATIS mas catálogo todo esgotado | Cai pra mensagem `tapa_livre_bebida_vazio`, sem decrementar nada |
| `pygame.mixer.init()` falha | `_habilitado = False`, todas chamadas `tocar()` viram no-op |
| Arquivo `.wav` ausente em `assets/sounds/` | Log silencioso (print stderr opcional), no-op |
| Env var `MAQUINA_MUTE=1` setado | Pula init, `_habilitado = False` direto |
| User pressiona Ctrl+C durante cooldown | Comportamento padrão do `sleep` (KeyboardInterrupt sobe) — aceitável |

## 10. Testes a escrever (em `tests/`)

| Arquivo | Teste |
|---|---|
| `tests/test_eventos.py` (existente) | `resolver_tapa_livre()` com RNG seedado: distribuição em N=10000 fica dentro de ±2% das probabilidades configuradas |
| `tests/test_eventos.py` | Cada nova pool de mensagem não está vazia e formata corretamente |
| `tests/test_produtos.py` (existente ou novo) | `Catalogo.sortear_com_estoque()` nunca retorna produto com `estoque == 0` |
| `tests/test_produtos.py` | `Catalogo.sortear_com_estoque()` retorna `None` quando todos esgotados |
| `tests/test_audio.py` (novo) | `init_audio()` com `MAQUINA_MUTE=1` não chama `pygame.mixer.init`. `tocar()` é no-op quando desabilitado (sem exceções) |

Áudio em si **não é testado** acusticamente. Só o contrato (no-op seguro, env var respeitada).

## 11. Mudanças visíveis ao usuário (resumo)

1. Menu IDLE agora mostra `[T] tapa` como opção.
2. Pressionar `t` no IDLE dispara animação + som + um dos 3 desfechos.
3. Quando quebra, terminal fica bloqueado por 10s com countdown.
4. Painel admin mostra `Tapas premiados: N` ao lado de `Vendas`.
5. Sons reais tocam em momentos-chave (tapa, dispensar, jackpot, quebra).

## 12. Não-objetivos (YAGNI)

- Tapa em outros estados que não IDLE.
- Cooldown reduzido por ação do user (ex: "tapa 5x rápido pra acelerar").
- Histórico persistente de eventos entre execuções.
- Volume configurável em runtime (use env var ou edite a constante).
- Mixagem de múltiplos sons simultâneos (`pygame.mixer` aguenta, mas não vou usar ativamente).
- Música de fundo / idle hum.
