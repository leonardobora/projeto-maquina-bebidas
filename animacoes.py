# -*- coding: utf-8 -*-
import time
from typing import Dict
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
from rich.align import Align

import audio


def animar_dispensar(console: Console, nome_bebida: str, duracao_s: float = 1.5) -> None:
    """Spinner Rich + texto 'Preparando sua {bebida}...' por duracao_s segundos."""
    audio.tocar("dispensar")
    spinner = Spinner(
        "dots",
        text=Text(f" Preparando sua {nome_bebida}...", style="yellow"),
    )
    painel = Panel(spinner, border_style="yellow", title="DISPENSANDO")
    with Live(painel, console=console, refresh_per_second=12) as live:
        inicio = time.time()
        while time.time() - inicio < duracao_s:
            time.sleep(0.05)


def animar_troco(console: Console, troco: Dict[int, int], delay_s: float = 0.25) -> None:
    """Mostra cédulas do troco aparecendo uma por uma com delay via rich.live."""
    def _fmt(cv: int) -> str:
        return f"R${cv // 100},{cv % 100:02d}"

    def _build_panel(linhas: list) -> Panel:
        texto = Text("\n".join(linhas), style="white")
        return Panel(texto, title="TROCO RECEBIDO", border_style="yellow")

    denoms_com_qtd = [
        (d, q) for d, q in sorted(troco.items(), reverse=True) if q > 0
    ]
    linhas: list = []
    total = 0

    with Live(_build_panel(linhas), console=console, refresh_per_second=8) as live:
        for denom, qtd in denoms_com_qtd:
            linhas.append(f"  {qtd} × {_fmt(denom)}   ✓")
            total += denom * qtd
            live.update(_build_panel(linhas))
            time.sleep(delay_s)
        linhas.append("  ─────────────")
        linhas.append(f"  Total: {_fmt(total)}")
        live.update(_build_panel(linhas))
        time.sleep(0.5)


def _painel_tapa(texto_central: str, shift_chars: int) -> Panel:
    indent = " " * abs(shift_chars) if shift_chars > 0 else ""
    conteudo = Text()
    conteudo.append("\n")
    conteudo.append(f"{indent}{texto_central:^30}", style="bold yellow on red")
    conteudo.append("\n")
    return Panel(
        Align.center(conteudo),
        border_style="red",
        title="⚠ MÁQUINA TRAVADA ⚠",
        height=5,
    )


def animar_tapa(console: Console) -> None:
    """4 frames com texto explodindo + deslocamento horizontal, 2 loops. ~0.6s."""
    audio.tocar("tapa")
    frames = [
        ("              ", 0),
        ("  *** TAPA! ***", 2),
        ("*** TAPA! ***   ", -2),
        ("              ", 0),
    ]

    with Live(_painel_tapa("", 0), console=console, refresh_per_second=15) as live:
        for _ in range(2):
            for texto, shift in frames:
                live.update(_painel_tapa(texto, shift))
                time.sleep(0.08)


# Lata genérica em ASCII + vapor frio que muda de posição em cada frame.
# Cada frame tem 9 linhas: 2 de vapor + 7 da lata estática.
_LATA_BASE = [
    "  _________  ",
    " /  ___    \\ ",
    "|  /   \\    |",
    "| | BFIA |  |",
    "|  \\___/    |",
    "|           |",
    "|___________|",
]
_FRAMES_VAPOR = [
    ["   °  °  °   ", "    °   °    "],
    ["  °   °      ", "     °  °  ° "],
    ["    °     °  ", "  °  °   °   "],
    ["   °   °  °  ", "      °  °   "],
]


def _frame_lata(idx: int) -> list:
    return _FRAMES_VAPOR[idx] + _LATA_BASE


def _painel_creditos(frame_idx: int) -> Panel:
    linhas = _frame_lata(frame_idx)
    conteudo = Text()
    conteudo.append("\n")
    # Vapor em ciano claro, lata em amarelo
    for i, linha in enumerate(linhas):
        if i < 2:
            conteudo.append(linha, style="bold cyan")
        else:
            conteudo.append(linha, style="bold yellow")
        conteudo.append("\n")
    conteudo.append("\n")
    conteudo.append("Desenvolvido por\n", style="dim white")
    conteudo.append("LEONARDO BORA\n", style="bold magenta")
    conteudo.append("\n")
    conteudo.append("linkedin.com/in/leonardobora\n", style="cyan underline")
    conteudo.append("\n")
    conteudo.append("[pressione ENTER pra voltar]", style="dim italic")
    return Panel(
        Align.center(conteudo),
        border_style="bold magenta",
        title="✨ EASTER EGG ✨",
        title_align="center",
        padding=(1, 4),
    )


def animar_creditos(console: Console, loops: int = 4, delay_s: float = 0.22) -> None:
    """Lata estática com vapor subindo + card de créditos. Loop infinito até user dar ENTER."""
    with Live(_painel_creditos(0), console=console, refresh_per_second=15) as live:
        for _ in range(loops):
            for i in range(len(_FRAMES_VAPOR)):
                live.update(_painel_creditos(i))
                time.sleep(delay_s)
        # Para no frame 0 pra leitura
        live.update(_painel_creditos(0))
