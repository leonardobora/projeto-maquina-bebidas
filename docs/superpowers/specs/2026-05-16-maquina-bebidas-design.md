# Design — Máquina de Bebidas (Projeto da Disciplina · Python)

**Status:** approved (visual brainstorm) · pronto pra plano de implementação
**Data:** 2026-05-16
**Disciplina:** Introdução à Linguagem Python (Turma U) · PUCPR Pós Lato Sensu IA & CD
**Canvas:** [Projeto da Disciplina · assignment 325433](https://pucpr.instructure.com/courses/67212/assignments/325433) · vale 10 pontos
**Prazo:** 24/05/2026 23:59 BRT (8 dias)
**Enunciado:** [`Projeto-Maquina-de-Bebidas.pdf`](../../../../projeto-final-enunciados/Projeto-Maquina-de-Bebidas.pdf)

> ⚠️ O PDF do enunciado está marcado como "Atividade opcional". A confirmar com o professor se afeta a obrigatoriedade.

---

## 1. Objetivo

Implementar uma máquina de bebidas via terminal em Python, com **interface visual rica em ASCII art usando Rich**, atendendo aos 7 requisitos do enunciado (incluindo os dois desafios opcionais), mais uma feature autoral de "máquina travando" que precisa ser destravada com tapas na lateral.

## 2. Requisitos cobertos

### Do enunciado (PDF)

| # | Requisito | Cobertura |
|---|---|---|
| 1 | Loop interativo aceitando cédulas/moedas em reais | ✅ |
| 2 | Catálogo inicial de 5 produtos com IDs, preços, estoque | ✅ |
| 3 | Validação de código + estoque antes da compra | ✅ |
| 4 | Validação de valor pago ≥ preço, re-prompt se insuficiente | ✅ |
| 5 | Cálculo de troco com algoritmo guloso (menor volume) | ✅ |
| 6 | Decremento de estoque após dispensar | ✅ |
| 7a | Modo admin com CRUD de produtos | ✅ |
| 7b | Estoque finito de cédulas, cancela se não há troco | ✅ |

### Adicionais (autorais)

- Feature de máquina travando aleatoriamente (25%) com destravamento via tapa.
- 5 telas com mockups distintos + 4 animações pontuais.
- Paleta de cores temática das marcas (Coca vermelha, Pepsi azul, etc).
- Mensagens aleatórias de variedade textual.

## 3. Decisões de design

| Decisão | Escolha | Por quê |
|---|---|---|
| Stack visual | **Rich** (lib Python) | Sweet spot entre capricho e simplicidade; suporta truecolor + live updates |
| Estética | Máquina física clássica (slots como prateleira) | Cor de marca brilha mais em slots individuais |
| Intensidade de cor | Sutil (foreground only) | Elegante, legível em qualquer terminal |
| Animação | Pontuais com `rich.live` | Capricho sem virar TUI completo |
| Valores monetários | `int` em centavos | Evita imprecisão de float |
| Input | `rich.prompt.Prompt.ask()` + `msvcrt.getch()` pra atalhos | Validação built-in + single-key feel |
| Persistência | Memória apenas, reset por run | Suficiente pro escopo acadêmico |
| Encoding | `# -*- coding: utf-8 -*-` em todos `.py` | Garante acentuação no Windows |
| RNG | `random.random()` com seed opcional via env var | Reprodutível em testes |
| Senha admin | `1234` hardcoded | Escopo acadêmico não precisa de mais |
| Testes | `unittest` stdlib | Zero deps de teste |

### Paleta (truecolor)

```python
CORES = {
    "coca":    "#E61E1E",   # vermelho Coca-Cola
    "pepsi":   "#004B93",   # azul Pepsi
    "monster": "#82C341",   # verde Monster
    "cafe":    "#6F4E37",   # marrom expresso
    "redbull": "#CC0000",   # vermelho RB (nome alterna com #003B82)
    "visor":   "#FFCC00",   # amarelo LCD
    "erro":    "#FF3333",
    "ok":      "#33FF66",
    "neutro":  "#888888",   # esgotado
}
```

## 4. Arquitetura

### Estrutura de arquivos

```
projeto-maquina-bebidas/
├── README.md
├── DECLARACAO-IA.md           # CONSUN 274/2024 antes da submissão
├── requirements.txt           # só rich
├── maquina.py                 # entry point + state machine + loop
├── produtos.py                # dataclass Produto + catálogo + CRUD
├── caixa.py                   # Cédula + algoritmo guloso de troco
├── eventos.py                 # RNG: travamento, tapa, pool de mensagens
├── ui.py                      # builders de Panel/Layout do Rich
├── animacoes.py               # tapa (shake), dispensar (spinner), troco (1-a-1)
├── docs/superpowers/specs/    # este arquivo
└── tests/
    ├── test_caixa.py          # algoritmo guloso + caso do PDF + edges
    └── test_produtos.py       # CRUD + decremento de estoque
```

### State machine

```
IDLE
  digita 1-5  → PRODUTO_SELECIONADO
  digita admin → ADMIN_LOGIN
  digita Q     → SAIR

PRODUTO_SELECIONADO
  estoque OK    → AGUARDANDO_PAGAMENTO
  sem estoque   → ERRO ("esgotada", 2s) → IDLE
  código inválido → ERRO ("inválido", 2s) → IDLE

AGUARDANDO_PAGAMENTO
  valor < preço → continua coletando
  valor ≥ preço → DISPENSANDO

DISPENSANDO
  random < 0.25  → TRAVADA
  random ≥ 0.25  → CALCULANDO_TROCO

TRAVADA
  user [T] + random < 0.50 → CALCULANDO_TROCO
  user [T] + random ≥ 0.50 → TRAVADA (contador++)
  contador = 3            → ERRO ("desistiu") + reembolso → IDLE

CALCULANDO_TROCO
  troco viável → DEVOLVENDO_TROCO
  sem cédulas  → ERRO ("sem troco") + reembolso → IDLE
                 (estoque da bebida NÃO decrementa)

DEVOLVENDO_TROCO
  animação → decrementa estoque bebida → atualiza caixa → IDLE

ADMIN_LOGIN
  senha OK    → ADMIN_MODE
  senha falha → IDLE (3 tentativas)

ADMIN_MODE
  A/E/R → wizards de CRUD
  V    → IDLE
```

## 5. Telas (mockups)

### 5.1 Idle (estado base)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                  PUCPR BEVERAGE CO.                    ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ ╭──────────────────────────────────────────────────╮   ┃
┃ │  ▸ ESCOLHA UMA BEBIDA (1-5) · "admin" · Q sair   │   ┃
┃ ╰──────────────────────────────────────────────────╯   ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                        ┃
┃  ╔══[1]══╗   ╔══[2]══╗   ╔══[3]══╗                     ┃
┃  ║       ║   ║       ║   ║       ║                     ┃
┃  ║ COCA  ║   ║ PEPSI ║   ║MONSTER║                     ┃
┃  ║       ║   ║       ║   ║       ║                     ┃
┃  ║R$3,75 ║   ║R$3,67 ║   ║R$9,96 ║                     ┃
┃  ║  x2   ║   ║  x5   ║   ║  x1   ║                     ┃
┃  ╚═══════╝   ╚═══════╝   ╚═══════╝                     ┃
┃                                                        ┃
┃  ╔══[4]══╗   ╔══[5]══╗                                 ┃
┃  ║       ║   ║       ║                                 ┃
┃  ║ CAFÉ  ║   ║REDBULL║                                 ┃
┃  ║       ║   ║       ║                                 ┃
┃  ║R$1,25 ║   ║R$13,99║                                 ┃
┃  ║ x100  ║   ║  x2   ║                                 ┃
┃  ╚═══════╝   ╚═══════╝                                 ┃
┃                                                        ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  ┌─ INSERIR ────┐    ┌─ TROCO ──────────────────┐      ┃
┃  │  R$ 0,00     │    │  --                      │      ┃
┃  └──────────────┘    └──────────────────────────┘      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

Cores: nome e borda do slot na cor da marca. Slot esgotado fica cinza + nome riscado.

### 5.2 Produto selecionado

Slot escolhido ganha indicador `▶`, visor atualiza, rodapé mostra "FALTA":

```
╭──────────────────────────────────────────────────╮
│  ▸ PEPSI selecionada · R$ 3,67                   │
│    Insira cédulas/moedas (ENTER pra finalizar)   │
╰──────────────────────────────────────────────────╯
...
╔══[2]══╗ → ╔▶═[2]═▶╗
...
┌─ INSERIR ────┐    ┌─ FALTA ──────────────────┐
│  R$ 0,00     │    │  R$ 3,67                 │
└──────────────┘    └──────────────────────────┘
```

### 5.3 Inserindo dinheiro (animado)

Contador "INSERIR" sobe com `▲` piscando (300ms), "FALTA" decrementa em tempo real. Quando paga: vira "TROCO".

### 5.4 Dispensando (animado)

Spinner Rich (`⠋⠙⠹⠸⠼⠴`) no visor por ~1,5s. Slot da bebida mostra ela "caindo" (`↓`).

### 5.5 Devolvendo troco (animado)

Cada item aparece 1-a-1 com delay de 200ms:

```
╭──────────────────────────────────────────────────╮
│  ▸ Aproveite sua PEPSI! Aqui está seu troco:     │
╰──────────────────────────────────────────────────╯
┌─ TROCO RECEBIDO ─────────────────────────────────┐
│  1 × R$ 2,00   ✓                                 │
│  1 × R$ 0,25   ✓                                 │
│  1 × R$ 0,05   ✓                                 │
│  3 × R$ 0,01   ✓                                 │
│  ─────────────                                   │
│  Total: R$ 2,33                                  │
└──────────────────────────────────────────────────┘
```

Depois 3s → volta pra idle com estoque decrementado.

### 5.6 Erro

Visor vermelho por 2s, mensagens:
- "⚠ Código inválido. Use 1-5."
- "⚠ MONSTER esgotada. Escolha outra."
- "⚠ Faltam R$ 1,67. Continue inserindo."
- "⚠ Sem cédulas pro troco. Compra cancelada."

### 5.7 Modo admin

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                   🔧 MODO ADMIN 🔧                      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ ╭──────────────────────────────────────────────────╮   ┃
┃ │  [A]dicionar  [E]ditar  [R]emover  [V]oltar      │   ┃
┃ ╰──────────────────────────────────────────────────╯   ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃   ID │ PRODUTO    │ PREÇO    │ ESTOQUE │ COR           ┃
┃   ───┼────────────┼──────────┼─────────┼─────          ┃
┃    1 │ Coca-cola  │ R$  3,75 │    2    │ ████ vermelho ┃
┃    2 │ Pepsi      │ R$  3,67 │    5    │ ████ azul     ┃
┃    3 │ Monster    │ R$  9,96 │    1    │ ████ verde    ┃
┃    4 │ Café       │ R$  1,25 │  100    │ ████ marrom   ┃
┃    5 │ Redbull    │ R$ 13,99 │    2    │ ████ rb       ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  Caixa: R$ 425,30  │  Total dispensado hoje: 18        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## 6. Feature de travamento (autoral)

### Mecânica

| Evento | Probabilidade |
|---|---|
| Trava ao dispensar | 25% |
| Sucesso por tapa | 50% por tentativa |
| Tentativas até desistir | 3 |

Se desistir: reembolso integral + estoque da bebida **não** decrementa.

### Animação do tapa

`rich.live` com 4 frames consecutivos (~80ms cada), 2 loops:

| Frame | Conteúdo |
|---|---|
| A | Posição normal |
| B | Shift +2 chars direita, "*** TAPA! ***" no visor |
| C | Shift -2 chars esquerda |
| D | Normal + resultado |

### Pool de mensagens

**Trava:**
- "EITA! A {bebida} travou na espiral..."
- "Aff, presa de novo. Clássico."
- "A {bebida} ficou pendurada no espiral..."

**Tapa sucesso:**
- "✓ Caiu! Aproveite."
- "✓ Bingo! Foi com força."
- "✓ Resolveu na marra."

**Tapa falha:**
- "✗ Continua presa. Tenta de novo?"
- "✗ Quase! Mais um tapa."
- "✗ Tá emperrada mesmo. Insiste aí."

**Desistência:**
- "💸 A máquina desistiu de você. Toma seu dinheiro."
- "💸 Não rolou. Reembolso na área."

## 7. Estoque de cédulas (desafio 7b)

### Estado inicial

```python
caixa_inicial = {
    10000: 5,    # R$ 100
    5000:  8,    # R$ 50
    2000:  15,   # R$ 20
    1000:  20,   # R$ 10
    500:   30,   # R$ 5
    200:   50,   # R$ 2
    100:   40,   # R$ 1
    50:    50,   # 50¢
    25:    50,   # 25¢
    10:    100,  # 10¢
    5:     100,  # 5¢
    1:     200,  # 1¢
}
```

### Algoritmo

1. Guloso clássico (maior denominação primeiro) respeitando estoque disponível.
2. Se sobrar valor após esgotar denominações → falha → cancela compra.
3. Sucesso → incrementa caixa com o pagamento recebido, decrementa com o troco devolvido.
4. Falha → reembolsa as mesmas cédulas que o user inseriu (devolução exata).

### Edge case crítico

Ordem dos efeitos colaterais:
1. Pagamento recebido entra no caixa **só após** confirmação de que o troco é possível.
2. Estoque da bebida decrementa **só após** dispensar bem-sucedido + troco entregue.
3. Se trava + desiste: reembolso integral, caixa volta ao estado pré-pagamento, estoque intacto.

## 8. Plano de testes (unittest stdlib)

### `test_caixa.py`

- `test_troco_caso_pdf`: produto R$ 3,67, pago R$ 10,00 → 1×R$5 + 1×R$1 + 1×20¢ + 1×10¢ + 3×1¢.
- `test_troco_zero`: pago == preço → troco vazio.
- `test_troco_sem_cedulas_falha`: caixa sem moedas de 1¢, troco precisa de 1¢ → exception/None.
- `test_caixa_atualiza_pagamento`: incrementa denominações recebidas.
- `test_caixa_atualiza_troco`: decrementa denominações entregues.
- `test_caixa_reembolso_integral`: devolve exatamente as cédulas inseridas.

### `test_produtos.py`

- `test_catalogo_inicial`: 5 produtos com IDs 1-5, valores e estoques do PDF.
- `test_decrementa_estoque`: dispensar Coca x2 vezes → estoque vai pra 0.
- `test_admin_adicionar`: cria produto com ID novo + atributos.
- `test_admin_editar`: muda preço/estoque/cor.
- `test_admin_remover`: remove ID, próxima query retorna None.
- `test_admin_id_duplicado_falha`: tentativa de criar ID existente → erro.

### Manuais

- Animações (visualmente revisar shake, spinner, troco caindo).
- Acentuação correta em todos visores (sem `\uXXXX` escape).
- Modo admin completo (login → CRUD → voltar).

## 9. Não-objetivos (YAGNI)

- Persistência em arquivo/DB entre runs.
- Múltiplos usuários ou histórico de vendas além da contagem da sessão.
- Internacionalização (só pt-BR).
- Cross-platform robusto (foco Windows + Windows Terminal).
- Suporte a outras moedas além de BRL.
- Sistema de senha sofisticado (hash, lockout, etc).
- Modo "hard" gamificado (descartado explicitamente).

## 10. Próximos passos

1. Spec aprovado pelo Leo (este arquivo).
2. Invocar `superpowers:writing-plans` pra gerar plano de implementação.
3. Implementar seguindo TDD (test_caixa primeiro, depois UI).
4. Geração de PDF via Pandoc + Chrome headless (ver [`pos/WORKFLOW.md`](../../../../../../WORKFLOW.md)).
5. Submissão Canvas com `DECLARACAO-IA.md` acompanhando.

## 11. Política PUCPR de IA

Conforme Resolução CONSUN 274/2024, qualquer uso de IA na elaboração deste trabalho será declarado em `DECLARACAO-IA.md` antes da submissão. Blocos gerados com auxílio do Claude Code serão atribuídos explicitamente.
