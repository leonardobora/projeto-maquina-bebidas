# Tapa Livre + Sons Reais — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar tapa livre no IDLE (3 desfechos probabilísticos) + trilha sonora real com pygame.mixer.

**Architecture:** Extensão pura — sem reescrever o que já existe. Novo módulo `audio.py` tolerante a falha (env var `MAQUINA_MUTE=1` desabilita; mixer init que falha vira no-op). Nova função `resolver_tapa_livre()` em `eventos.py` retornando enum `ResultadoTapaLivre`. Hook de input no IDLE (tecla `t`) dispara fluxo isolado em `handle_tapa_livre()`. Cooldown blocking via `time.sleep(1)` em loop com redraw do visor.

**Tech Stack:** Python 3, `pygame>=2.5` (mixer), `rich` (já em uso), `unittest` (já em uso).

**Spec base:** [`docs/superpowers/specs/2026-05-17-tapa-livre-design.md`](../specs/2026-05-17-tapa-livre-design.md)

---

## Task 1: Dependências + estrutura de assets

**Files:**
- Modify: `requirements.txt`
- Create: `assets/sounds/README.md`
- Create: `assets/sounds/.gitkeep`

- [ ] **Step 1: Adicionar pygame ao requirements**

Substituir conteúdo de `requirements.txt`:

```
rich>=13.0
pygame>=2.5
```

- [ ] **Step 2: Criar pasta de sons + README de créditos**

Criar `assets/sounds/README.md`:

```markdown
# Sons da Máquina de Bebidas

Sons usados no projeto — todos com licença Creative Commons 0 (CC0) do freesound.org.

| Arquivo | Descrição | Origem |
|---|---|---|
| `tapa.wav` | Impacto seco na lateral metálica | TBD (preencher após Task 11) |
| `dispensar.wav` | Motor + lata caindo | TBD (preencher após Task 11) |
| `bebida_gratis.wav` | Ding-ding curto de jackpot | TBD (preencher após Task 11) |
| `quebra.wav` | Zap elétrico / curto-circuito | TBD (preencher após Task 11) |

Se algum arquivo estiver ausente, o programa segue funcionando sem som (ver `audio.py`).

Pra rodar mudo: `MAQUINA_MUTE=1 python maquina.py`
```

Criar `assets/sounds/.gitkeep` (arquivo vazio).

- [ ] **Step 3: Verificar instalação**

Run: `pip install -r requirements.txt`
Expected: pygame instala sem erros.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt assets/sounds/README.md assets/sounds/.gitkeep
git commit -m "chore: adicionar pygame + estrutura de assets/sounds"
```

---

## Task 2: Catalogo.sortear_com_estoque() (TDD)

**Files:**
- Modify: `produtos.py`
- Modify: `tests/test_produtos.py`

- [ ] **Step 1: Adicionar import de random no topo do test_produtos.py se ainda não existe**

Verificar com Grep se `import random` já existe em `tests/test_produtos.py`. Se não, adicionar logo após `import unittest`.

- [ ] **Step 2: Escrever testes que falham**

Adicionar ao final de `tests/test_produtos.py`:

```python
class TestSortearComEstoque(unittest.TestCase):
    def test_sortear_retorna_produto_com_estoque(self):
        cat = Catalogo()
        rng = random.Random(42)
        for _ in range(50):
            p = cat.sortear_com_estoque(rng=rng)
            self.assertIsNotNone(p)
            self.assertTrue(p.tem_estoque())

    def test_sortear_nunca_retorna_produto_esgotado(self):
        cat = Catalogo()
        # zera tudo menos café (ID 4)
        for produto in cat.listar():
            if produto.id != 4:
                produto.estoque = 0
        rng = random.Random(7)
        for _ in range(20):
            p = cat.sortear_com_estoque(rng=rng)
            self.assertEqual(p.id, 4)

    def test_sortear_retorna_none_quando_tudo_esgotado(self):
        cat = Catalogo()
        for produto in cat.listar():
            produto.estoque = 0
        self.assertIsNone(cat.sortear_com_estoque())

    def test_sortear_aceita_rng_none(self):
        cat = Catalogo()
        resultado = cat.sortear_com_estoque()
        self.assertIsNotNone(resultado)
```

- [ ] **Step 3: Rodar e confirmar falha**

Run: `python -m unittest tests.test_produtos.TestSortearComEstoque -v`
Expected: 4 erros do tipo `AttributeError: 'Catalogo' object has no attribute 'sortear_com_estoque'`

- [ ] **Step 4: Implementar `sortear_com_estoque`**

Adicionar import no topo de `produtos.py` (logo após `from typing import List`):

```python
import random as _random
from typing import List, Optional
```

Adicionar método ao final da classe `Catalogo` (depois de `remover`):

```python
    def sortear_com_estoque(self, rng: Optional[_random.Random] = None) -> Optional[Produto]:
        """Sorteia uniformemente entre produtos com estoque > 0.
        Retorna None se todos estão esgotados."""
        rng = rng or _random
        disponiveis = [p for p in self._produtos if p.tem_estoque()]
        if not disponiveis:
            return None
        return rng.choice(disponiveis)
```

- [ ] **Step 5: Rodar e confirmar PASS**

Run: `python -m unittest tests.test_produtos.TestSortearComEstoque -v`
Expected: 4 testes PASS.

- [ ] **Step 6: Rodar suite inteira pra garantir não-regressão**

Run: `python -m unittest discover tests -v`
Expected: todos os testes PASS.

- [ ] **Step 7: Commit**

```bash
git add produtos.py tests/test_produtos.py
git commit -m "feat(produtos): Catalogo.sortear_com_estoque pra bebida grátis"
```

---

## Task 3: ResultadoTapaLivre + resolver_tapa_livre (TDD)

**Files:**
- Modify: `eventos.py`
- Modify: `tests/test_eventos.py`

- [ ] **Step 1: Escrever testes que falham**

Adicionar ao final de `tests/test_eventos.py` (antes do `if __name__`):

```python
from eventos import (
    ResultadoTapaLivre,
    resolver_tapa_livre,
    PROB_TAPA_LIVRE_BEBIDA,
    PROB_TAPA_LIVRE_QUEBRA,
    COOLDOWN_QUEBRA_SEGUNDOS,
)


class TestProbabilidadesTapaLivre(unittest.TestCase):
    def test_constantes_tem_valores_esperados(self):
        self.assertEqual(PROB_TAPA_LIVRE_BEBIDA, 0.20)
        self.assertEqual(PROB_TAPA_LIVRE_QUEBRA, 0.10)
        self.assertEqual(COOLDOWN_QUEBRA_SEGUNDOS, 10)

    def test_enum_tem_tres_resultados(self):
        valores = {r for r in ResultadoTapaLivre}
        self.assertEqual(len(valores), 3)
        self.assertIn(ResultadoTapaLivre.NADA, valores)
        self.assertIn(ResultadoTapaLivre.BEBIDA_GRATIS, valores)
        self.assertIn(ResultadoTapaLivre.QUEBRA, valores)


class TestResolverTapaLivre(unittest.TestCase):
    def test_distribuicao_aproximada(self):
        rng = random.Random(2026)
        amostras = 10000
        contagem = {r: 0 for r in ResultadoTapaLivre}
        for _ in range(amostras):
            contagem[resolver_tapa_livre(rng=rng)] += 1
        self.assertAlmostEqual(contagem[ResultadoTapaLivre.QUEBRA] / amostras, 0.10, delta=0.02)
        self.assertAlmostEqual(contagem[ResultadoTapaLivre.BEBIDA_GRATIS] / amostras, 0.20, delta=0.02)
        self.assertAlmostEqual(contagem[ResultadoTapaLivre.NADA] / amostras, 0.70, delta=0.02)

    def test_aceita_rng_none(self):
        resultado = resolver_tapa_livre()
        self.assertIn(resultado, list(ResultadoTapaLivre))


class TestMensagensTapaLivre(unittest.TestCase):
    def test_pool_tapa_livre_nada_nao_vazio(self):
        msg = mensagem("tapa_livre_nada", rng=random.Random(0))
        self.assertTrue(len(msg) > 0)

    def test_pool_tapa_livre_bebida_substitui_nome(self):
        rng = random.Random(0)
        encontrou = False
        for _ in range(50):
            msg = mensagem("tapa_livre_bebida", bebida="MONSTER", rng=rng)
            if "MONSTER" in msg:
                encontrou = True
                break
        self.assertTrue(encontrou)

    def test_pool_tapa_livre_bebida_vazio_nao_vazio(self):
        msg = mensagem("tapa_livre_bebida_vazio", rng=random.Random(0))
        self.assertTrue(len(msg) > 0)

    def test_pool_tapa_livre_quebra_nao_vazio(self):
        msg = mensagem("tapa_livre_quebra", rng=random.Random(0))
        self.assertTrue(len(msg) > 0)
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `python -m unittest tests.test_eventos -v`
Expected: erros de `ImportError` (não existem ainda).

- [ ] **Step 3: Implementar em eventos.py**

Substituir conteúdo de `eventos.py`:

```python
# -*- coding: utf-8 -*-
import random
from enum import Enum, auto
from typing import Optional

PROBABILIDADE_TRAVAR = 0.25
PROBABILIDADE_TAPA_SUCESSO = 0.50
MAX_TENTATIVAS_TAPA = 3

PROB_TAPA_LIVRE_BEBIDA = 0.20
PROB_TAPA_LIVRE_QUEBRA = 0.10
COOLDOWN_QUEBRA_SEGUNDOS = 10


class ResultadoTapaLivre(Enum):
    NADA = auto()
    BEBIDA_GRATIS = auto()
    QUEBRA = auto()


_MENSAGENS = {
    "trava": [
        "EITA! A {bebida} travou na espiral...",
        "Aff, presa de novo. Clássico.",
        "A {bebida} ficou pendurada no espiral...",
    ],
    "tapa_sucesso": [
        "✓ Caiu! Aproveite.",
        "✓ Bingo! Foi com força.",
        "✓ Resolveu na marra.",
    ],
    "tapa_falha": [
        "✗ Continua presa. Tenta de novo?",
        "✗ Quase! Mais um tapa.",
        "✗ Tá emperrada mesmo. Insiste aí.",
    ],
    "desistencia": [
        "💸 A máquina desistiu de você. Toma seu dinheiro.",
        "💸 Não rolou. Reembolso na área.",
    ],
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
}


def deve_travar(rng: Optional[random.Random] = None) -> bool:
    rng = rng or random
    return rng.random() < PROBABILIDADE_TRAVAR


def tapa_resolve(rng: Optional[random.Random] = None) -> bool:
    rng = rng or random
    return rng.random() < PROBABILIDADE_TAPA_SUCESSO


def resolver_tapa_livre(rng: Optional[random.Random] = None) -> ResultadoTapaLivre:
    """Sorteia o desfecho do tapa livre.
    Probabilidades: QUEBRA={PROB_QUEBRA}, BEBIDA_GRATIS={PROB_BEBIDA}, NADA=resto.
    """
    rng = rng or random
    r = rng.random()
    if r < PROB_TAPA_LIVRE_QUEBRA:
        return ResultadoTapaLivre.QUEBRA
    if r < PROB_TAPA_LIVRE_QUEBRA + PROB_TAPA_LIVRE_BEBIDA:
        return ResultadoTapaLivre.BEBIDA_GRATIS
    return ResultadoTapaLivre.NADA


def mensagem(categoria: str, bebida: str = "", rng: Optional[random.Random] = None) -> str:
    rng = rng or random
    opcoes = _MENSAGENS[categoria]
    template = rng.choice(opcoes)
    return template.format(bebida=bebida)
```

- [ ] **Step 4: Rodar e confirmar PASS**

Run: `python -m unittest tests.test_eventos -v`
Expected: todos os testes PASS (incluindo os antigos).

- [ ] **Step 5: Commit**

```bash
git add eventos.py tests/test_eventos.py
git commit -m "feat(eventos): ResultadoTapaLivre + resolver_tapa_livre + pools de mensagens"
```

---

## Task 4: Módulo audio.py com fallback (TDD)

**Files:**
- Create: `audio.py`
- Create: `tests/test_audio.py`

- [ ] **Step 1: Escrever testes que falham**

Criar `tests/test_audio.py`:

```python
# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch

import audio


class TestAudioMute(unittest.TestCase):
    def setUp(self):
        # Garante estado limpo entre testes
        audio._habilitado = False
        audio._sons = {}

    def test_init_com_mute_nao_chama_mixer(self):
        with patch.dict(os.environ, {"MAQUINA_MUTE": "1"}):
            with patch("audio.pygame.mixer.init") as mixer_init:
                audio.init_audio()
                mixer_init.assert_not_called()
        self.assertFalse(audio._habilitado)

    def test_tocar_quando_desabilitado_eh_noop(self):
        audio._habilitado = False
        # Não deve lançar exceção mesmo com nome inválido
        audio.tocar("nome_que_nao_existe")
        audio.tocar("tapa")

    def test_tocar_com_nome_desconhecido_eh_noop(self):
        audio._habilitado = True
        audio._sons = {}  # nenhum som carregado
        audio.tocar("inexistente")  # não lança

    def test_parar_tudo_quando_desabilitado_eh_noop(self):
        audio._habilitado = False
        audio.parar_tudo()  # não lança


class TestAudioInitFalha(unittest.TestCase):
    def setUp(self):
        audio._habilitado = False
        audio._sons = {}

    def test_init_falha_no_mixer_deixa_desabilitado(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("audio.pygame.mixer.init", side_effect=Exception("sem áudio")):
                audio.init_audio()
        self.assertFalse(audio._habilitado)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `python -m unittest tests.test_audio -v`
Expected: `ModuleNotFoundError: No module named 'audio'`

- [ ] **Step 3: Implementar audio.py**

Criar `audio.py`:

```python
# -*- coding: utf-8 -*-
"""Wrapper fino sobre pygame.mixer. Tolerante a falha:
- env var MAQUINA_MUTE=1 desabilita áudio sem tentar inicializar
- exceção em init_audio() ou load deixa o módulo em modo no-op
- chamadas a tocar() / parar_tudo() em modo no-op não lançam exceção
"""
import os
from pathlib import Path
from typing import Dict

import pygame


_SONS_DIR = Path(__file__).parent / "assets" / "sounds"

_ARQUIVOS = {
    "tapa": "tapa.wav",
    "dispensar": "dispensar.wav",
    "bebida_gratis": "bebida_gratis.wav",
    "quebra": "quebra.wav",
}

_sons: Dict[str, "pygame.mixer.Sound"] = {}
_habilitado: bool = False


def init_audio() -> None:
    """Inicializa pygame.mixer e carrega sons de assets/sounds/.
    Falha silenciosa: define _habilitado=False se algo der errado."""
    global _habilitado, _sons

    if os.environ.get("MAQUINA_MUTE") == "1":
        _habilitado = False
        return

    try:
        pygame.mixer.init()
    except Exception:
        _habilitado = False
        return

    _sons = {}
    for nome, arquivo in _ARQUIVOS.items():
        caminho = _SONS_DIR / arquivo
        if not caminho.exists():
            continue
        try:
            _sons[nome] = pygame.mixer.Sound(str(caminho))
        except Exception:
            continue

    _habilitado = True


def tocar(nome: str) -> None:
    """Toca som não-bloqueante. No-op se desabilitado ou nome ausente."""
    if not _habilitado:
        return
    som = _sons.get(nome)
    if som is None:
        return
    try:
        som.play()
    except Exception:
        pass


def parar_tudo() -> None:
    """Para todos os sons. No-op se desabilitado."""
    if not _habilitado:
        return
    try:
        pygame.mixer.stop()
    except Exception:
        pass
```

- [ ] **Step 4: Rodar e confirmar PASS**

Run: `python -m unittest tests.test_audio -v`
Expected: 5 testes PASS.

- [ ] **Step 5: Rodar suite completa**

Run: `python -m unittest discover tests -v`
Expected: todos PASS.

- [ ] **Step 6: Commit**

```bash
git add audio.py tests/test_audio.py
git commit -m "feat(audio): wrapper pygame.mixer com fallback tolerante (mute via env)"
```

---

## Task 5: Hook de áudio nas animações existentes

**Files:**
- Modify: `animacoes.py`

- [ ] **Step 1: Adicionar import de audio no topo**

Editar `animacoes.py`, adicionar logo após os imports do Rich:

```python
import audio
```

- [ ] **Step 2: Tocar som no início de `animar_dispensar`**

Localizar a função `animar_dispensar` (linha ~12) e adicionar `audio.tocar("dispensar")` como primeira linha do corpo da função (antes da criação do spinner):

```python
def animar_dispensar(console: Console, nome_bebida: str, duracao_s: float = 1.5) -> None:
    """Spinner Rich + texto 'Preparando sua {bebida}...' por duracao_s segundos."""
    audio.tocar("dispensar")
    spinner = Spinner(
```

- [ ] **Step 3: Tocar som no início de `animar_tapa`**

Localizar `animar_tapa` (linha ~66) e adicionar `audio.tocar("tapa")` como primeira linha do corpo:

```python
def animar_tapa(console: Console) -> None:
    """4 frames com texto explodindo + deslocamento horizontal, 2 loops. ~0.6s."""
    audio.tocar("tapa")
    frames = [
```

- [ ] **Step 4: Verificar que testes continuam passando**

Run: `python -m unittest discover tests -v`
Expected: todos PASS (audio.tocar em modo no-op não interfere).

- [ ] **Step 5: Commit**

```bash
git add animacoes.py
git commit -m "feat(animacoes): hooks de som em animar_dispensar e animar_tapa"
```

---

## Task 6: handle_tapa_livre + executar_cooldown em maquina.py

**Files:**
- Modify: `maquina.py`

- [ ] **Step 1: Atualizar imports no topo de maquina.py**

Localizar o bloco de imports e ajustar:

Substituir:

```python
from eventos import deve_travar, tapa_resolve, mensagem, MAX_TENTATIVAS_TAPA
```

por:

```python
from eventos import (
    deve_travar,
    tapa_resolve,
    mensagem,
    MAX_TENTATIVAS_TAPA,
    resolver_tapa_livre,
    ResultadoTapaLivre,
    COOLDOWN_QUEBRA_SEGUNDOS,
)
```

E também adicionar import de `audio`. Localizar a linha `from animacoes import animar_dispensar, animar_troco, animar_tapa` e adicionar logo depois:

```python
import audio
```

- [ ] **Step 2: Adicionar executar_cooldown logo após `_formatar_preco`**

Inserir após a função `_formatar_preco` (antes do comentário `# Input helpers`):

```python
# ============================================================================
# Cooldown da máquina quebrada
# ============================================================================

def executar_cooldown(console: Console, segundos: int, catalogo: Catalogo) -> None:
    """Bloqueia o terminal por `segundos`, redesenhando o IDLE + visor com countdown.
    User não consegue interagir durante o cooldown (sleep blocking)."""
    for restante in range(segundos, 0, -1):
        console.clear()
        console.print(render_idle(catalogo.listar()))
        console.print(render_visor(
            mensagem("cooldown").format(segundos=restante),
            tipo="erro"
        ))
        time.sleep(1)
```

- [ ] **Step 3: Adicionar handle_tapa_livre logo após executar_cooldown**

Continuar inserindo, antes de `# Input helpers`:

```python
# ============================================================================
# Tapa livre (acionável no IDLE)
# ============================================================================

def handle_tapa_livre(console: Console, catalogo: Catalogo) -> bool:
    """Executa o fluxo do tapa livre. Retorna True se ganhou bebida grátis.
    Pode bloquear por COOLDOWN_QUEBRA_SEGUNDOS se quebrar a máquina."""
    animar_tapa(console)
    resultado = resolver_tapa_livre()

    if resultado == ResultadoTapaLivre.NADA:
        console.print(render_visor(mensagem("tapa_livre_nada"), tipo="info"))
        time.sleep(1.5)
        return False

    if resultado == ResultadoTapaLivre.BEBIDA_GRATIS:
        produto = catalogo.sortear_com_estoque()
        if produto is None:
            console.print(render_visor(
                mensagem("tapa_livre_bebida_vazio"),
                tipo="info"
            ))
            time.sleep(1.5)
            return False
        console.print(render_visor(
            mensagem("tapa_livre_bebida", bebida=produto.nome.upper()),
            tipo="ok"
        ))
        time.sleep(1.2)
        audio.tocar("bebida_gratis")
        animar_dispensar(console, produto.nome.upper())
        produto.decrementar()
        console.print(render_visor(f"Aproveite sua {produto.nome} grátis!", tipo="ok"))
        time.sleep(1.5)
        return True

    # QUEBRA
    audio.tocar("quebra")
    console.print(render_visor(mensagem("tapa_livre_quebra"), tipo="erro"))
    time.sleep(1.0)
    executar_cooldown(console, COOLDOWN_QUEBRA_SEGUNDOS, catalogo)
    return False
```

- [ ] **Step 4: Verificar sintaxe**

Run: `python -c "import maquina"`
Expected: sem erros.

- [ ] **Step 5: Commit**

```bash
git add maquina.py
git commit -m "feat(maquina): handle_tapa_livre + executar_cooldown"
```

---

## Task 7: Wire-up no main loop (tecla 't' + contador tapas_premiados + init áudio)

**Files:**
- Modify: `maquina.py`

- [ ] **Step 1: Inicializar áudio no início de main**

Localizar a função `main` (linha ~355). Adicionar `audio.init_audio()` como primeira linha do corpo, antes de `console = Console()`:

```python
def main() -> None:
    audio.init_audio()
    console = Console()
    catalogo = Catalogo()
    caixa = Caixa()
    vendas = 0
```

- [ ] **Step 2: Adicionar contador tapas_premiados**

Logo após `vendas = 0` no `main`:

```python
    vendas = 0
    tapas_premiados = 0
```

- [ ] **Step 3: Atualizar mensagem do visor IDLE**

Localizar a linha:

```python
        console.print(render_visor("ESCOLHA UMA BEBIDA (1-5) · 'admin' · 'q' sair"))
```

e substituir por:

```python
        console.print(render_visor("ESCOLHA UMA BEBIDA (1-5) · [T]apa · 'admin' · 'q' sair"))
```

- [ ] **Step 4: Adicionar branch pra tecla 't' no loop + propagar tapas_premiados pro admin**

Localizar o bloco existente:

```python
        if entrada == "admin":
            handle_admin(console, catalogo, caixa, vendas)
            continue
```

e substituir por:

```python
        if entrada == "admin":
            handle_admin(console, catalogo, caixa, vendas, tapas_premiados)
            continue

        if entrada == "t":
            ganhou = handle_tapa_livre(console, catalogo)
            if ganhou:
                tapas_premiados += 1
            continue
```

A chamada de `handle_admin` agora passa `tapas_premiados` — assinatura será atualizada na Task 8.

- [ ] **Step 5: Verificar sintaxe**

Run: `python -c "import maquina"`
Expected: sem erros (handle_admin pode aceitar arg extra após Task 8 — por enquanto vai dar erro de assinatura se executar, mas import passa).

- [ ] **Step 6: Commit (não rodar suite ainda — handle_admin tem assinatura desalinhada até Task 8)**

```bash
git add maquina.py
git commit -m "feat(maquina): tecla [T]apa no IDLE + contador tapas_premiados + init áudio"
```

---

## Task 8: Render_admin com tapas_premiados + handle_admin atualizado

**Files:**
- Modify: `ui.py`
- Modify: `maquina.py`

- [ ] **Step 1: Atualizar assinatura de render_admin em ui.py**

Localizar `render_admin` (linha ~124) e atualizar a assinatura + rodapé:

Substituir:

```python
def render_admin(
    produtos: List[Produto],
    caixa_total_centavos: int,
    vendas_sessao: int,
) -> Panel:
```

por:

```python
def render_admin(
    produtos: List[Produto],
    caixa_total_centavos: int,
    vendas_sessao: int,
    tapas_premiados: int = 0,
) -> Panel:
```

E substituir o `rodape` (procurar por `f"Caixa: {_formatar_preco(caixa_total_centavos)}  │  Vendas hoje: {vendas_sessao}"`) por:

```python
    rodape = Panel(
        Align.center(Text(
            f"Caixa: {_formatar_preco(caixa_total_centavos)}  │  "
            f"Vendas: {vendas_sessao}  │  Tapas premiados: {tapas_premiados}",
            style="dim white"
        )),
        border_style="cyan",
    )
```

- [ ] **Step 2: Atualizar handle_admin em maquina.py pra aceitar e propagar tapas_premiados**

Localizar `def handle_admin` (linha ~246). Atualizar assinatura:

```python
def handle_admin(
    console: Console,
    catalogo: Catalogo,
    caixa: Caixa,
    vendas: int,
    tapas_premiados: int = 0,
) -> None:
```

E na chamada de `render_admin` dentro de `handle_admin`, atualizar:

```python
        console.print(render_admin(catalogo.listar(), caixa.total_em_centavos(), vendas, tapas_premiados))
```

- [ ] **Step 3: Verificar sintaxe**

Run: `python -c "import maquina"`
Expected: sem erros.

- [ ] **Step 4: Rodar suite completa**

Run: `python -m unittest discover tests -v`
Expected: todos PASS.

- [ ] **Step 5: Commit**

```bash
git add ui.py maquina.py
git commit -m "feat(ui): render_admin mostra tapas_premiados no rodapé"
```

---

## Task 9: Smoke test manual (modo mudo) + ajustes finos

**Files:** nenhum modificado se tudo correr bem.

- [ ] **Step 1: Rodar a máquina em modo mudo**

Run (PowerShell): `$env:MAQUINA_MUTE='1'; python maquina.py`

Expected: máquina abre normalmente. Visor IDLE mostra `[T]apa`.

- [ ] **Step 2: Testar tapa livre com vários inputs**

Pressionar `t` repetidamente (uns 15-20 tapas) e verificar:

- [ ] Aparece animação de tapa
- [ ] Às vezes "nada acontece" com mensagem de zoeira
- [ ] Eventualmente cai uma bebida grátis (estoque do produto decrementa visível no slot)
- [ ] Eventualmente quebra: countdown de 10s aparece, terminal fica blocked
- [ ] Após cooldown, volta pro IDLE normal

- [ ] **Step 3: Testar admin mostra tapas_premiados**

Digite `admin` → senha `1234` → verificar rodapé: `Vendas: X  │  Tapas premiados: Y`.

- [ ] **Step 4: Esgotar todos os produtos via admin (editar estoque pra 0) e testar bebida grátis vazia**

Editar admin → set estoque=0 pra todos. Sair admin. Dar tapas até cair em "bebida grátis" — deve mostrar mensagem `tapa_livre_bebida_vazio` sem decrementar nada.

- [ ] **Step 5: Sair com `q`**

Pressionar `q` no IDLE → mensagem "Até a próxima!".

- [ ] **Step 6: Se algum bug encontrado, corrigir e commitar separado**

Se tudo OK, sem commit nessa task.

---

## Task 10: Curadoria dos sons (URLs do freesound.org)

**Files:**
- Modify: `assets/sounds/README.md`

> **NOTA:** As 4 URLs abaixo são placeholders que devem ser substituídas por buscas reais no freesound.org. Quem executar essa task: faça uma `WebSearch` por cada categoria, pegue URLs reais de sons CC0, baixe o `.wav`, salve em `assets/sounds/` com o nome esperado, e preencha o README.

- [ ] **Step 1: Buscar 4 sons no freesound.org via WebSearch**

Usar WebSearch com queries:

1. `site:freesound.org metal slap thump short wav CC0`
2. `site:freesound.org vending machine dispense can drop wav`
3. `site:freesound.org slot machine jackpot ding short wav`
4. `site:freesound.org electric zap short circuit wav`

Pra cada um: escolher um som curto (<2s), com licença CC0 (Creative Commons 0).

- [ ] **Step 2: Baixar os 4 sons**

Cada freesound.org tem botão "Download" — precisa de login (conta gratuita). Salvar como:

- `assets/sounds/tapa.wav`
- `assets/sounds/dispensar.wav`
- `assets/sounds/bebida_gratis.wav`
- `assets/sounds/quebra.wav`

- [ ] **Step 3: Atualizar `assets/sounds/README.md`**

Substituir os "TBD" pelas URLs reais e nomes dos autores. Exemplo de linha preenchida:

```markdown
| `tapa.wav` | Impacto seco na lateral metálica | https://freesound.org/people/Fulano/sounds/12345/ (CC0) |
```

- [ ] **Step 4: Adicionar sons ao git (são pequenos, OK commitar)**

```bash
git add assets/sounds/*.wav assets/sounds/README.md
git commit -m "chore(assets): adicionar 4 sons CC0 do freesound.org"
```

- [ ] **Step 5: Smoke test com áudio ligado**

Run (PowerShell): `python maquina.py`

- [ ] Tapa toca som de impacto
- [ ] Comprar bebida toca som de dispensar
- [ ] Tapa livre que dá jackpot toca ding
- [ ] Tapa livre que quebra toca zap

Se algum som tá alto/baixo demais ou irritante, pode normalizar volume com Audacity (export como WAV) e recommitar.

---

## Task 11: Atualizar README do projeto

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Verificar conteúdo atual**

Run: `head -50 README.md` (ou usar Read).

- [ ] **Step 2: Adicionar seção sobre o tapa livre**

Adicionar um parágrafo na seção de features mencionando:

```markdown
## Tapa Livre (novo!)

Pressione `T` no IDLE pra dar um tapa na máquina a qualquer momento:
- 70% das vezes: nada acontece (a máquina te ignora)
- 20% das vezes: uma bebida aleatória com estoque cai de graça
- 10% das vezes: a máquina quebra e fica em manutenção por 10s

Pra rodar sem som: `MAQUINA_MUTE=1 python maquina.py` (ou `$env:MAQUINA_MUTE='1'` no PowerShell).
```

- [ ] **Step 3: Commit final**

```bash
git add README.md
git commit -m "docs: documentar tapa livre + modo mudo no README"
```

---

## Verificação final

- [ ] **Suite de testes 100% verde:**

Run: `python -m unittest discover tests -v`
Expected: todos PASS, sem erros nem warnings.

- [ ] **Lint visual no diff:**

Run: `git log --oneline main..HEAD`
Expected: ~10 commits coerentes, mensagens em português, escopo claro.

- [ ] **Smoke test final com som ligado:**

Rodar `python maquina.py`, dar 20+ tapas, comprar uma bebida normal, abrir admin. Tudo funcionando = pronto.
