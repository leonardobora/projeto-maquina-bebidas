# -*- coding: utf-8 -*-
import math
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


# Spinning donut clássico — porte do donut.c (Andy Sloane, 2006).
# https://www.a1k0n.net/2011/07/20/donut-math.html
_DONUT_W = 48
_DONUT_H = 18
_DONUT_CHARS = ".,-~:;=!*#$@"


def _render_donut(A: float, B: float) -> str:
    """Renderiza um frame do toroide rotacionado por A (eixo X) e B (eixo Z).
    Fórmula clássica de https://www.a1k0n.net/2011/07/20/donut-math.html"""
    z = [0.0] * (_DONUT_W * _DONUT_H)
    b = [" "] * (_DONUT_W * _DONUT_H)
    sin_A, cos_A = math.sin(A), math.cos(A)
    sin_B, cos_B = math.sin(B), math.cos(B)
    k1 = 18  # distância projetada do eixo X (controla "tamanho")

    j = 0.0  # phi: ângulo em torno do eixo Y
    while j < 6.28:
        sin_phi, cos_phi = math.sin(j), math.cos(j)
        i = 0.0  # theta: posição no círculo da seção
        while i < 6.28:
            sin_theta, cos_theta = math.sin(i), math.cos(i)
            h = cos_theta + 2  # R2 + R1*cos(theta), com R2=2 e R1=1
            D = 1 / (sin_theta * sin_A * cos_phi + cos_phi * h * sin_A + 5)  # placeholder; recalcula abaixo
            # Coordenadas 3D antes da projeção:
            circ_x = h * cos_phi
            circ_y = h * sin_phi
            circ_z = sin_theta
            # Aplicar rotação A no eixo X e B no eixo Z:
            x = circ_x * cos_B + (circ_y * cos_A - circ_z * sin_A) * sin_B
            y = -circ_x * sin_B + (circ_y * cos_A - circ_z * sin_A) * cos_B
            zp = circ_y * sin_A + circ_z * cos_A + 5  # distância do "observador"
            ooz = 1 / zp
            xp = int(_DONUT_W / 2 + k1 * ooz * x)
            yp = int(_DONUT_H / 2 - (k1 / 2) * ooz * y)
            # Luminância: produto escalar entre normal da superfície e luz (em (0, 1, -1))
            lum = (cos_phi * cos_theta * sin_B
                   - cos_A * cos_theta * sin_phi
                   - sin_A * sin_theta
                   + cos_B * (cos_A * sin_theta - cos_theta * sin_A * sin_phi))
            if 0 <= yp < _DONUT_H and 0 <= xp < _DONUT_W and ooz > z[xp + _DONUT_W * yp]:
                z[xp + _DONUT_W * yp] = ooz
                idx = int(lum * 8)
                b[xp + _DONUT_W * yp] = _DONUT_CHARS[idx if idx > 0 else 0]
            i += 0.04
        j += 0.10

    return "\n".join("".join(b[i * _DONUT_W:(i + 1) * _DONUT_W]) for i in range(_DONUT_H))


def _painel_creditos(A: float, B: float) -> Panel:
    donut = _render_donut(A, B)
    conteudo = Text()
    conteudo.append(donut, style="bold yellow")
    conteudo.append("\n\n")
    conteudo.append("Desenvolvido por\n", style="dim white")
    conteudo.append("LEONARDO BORA\n", style="bold magenta")
    conteudo.append("\n")
    # Hyperlink clicável via Rich OSC 8 (funciona em Windows Terminal, iTerm, Kitty)
    conteudo.append(
        "linkedin.com/in/leonardobora\n",
        style="link https://linkedin.com/in/leonardobora cyan underline",
    )
    conteudo.append("\n")
    conteudo.append("Introdução à Linguagem Python · Turma U\n", style="dim white")
    conteudo.append("Pós-graduação IA & Ciência de Dados · PUCPR\n", style="dim white")
    conteudo.append("2026\n", style="dim white")
    conteudo.append("\n")
    conteudo.append("[pressione ENTER pra voltar]", style="dim italic")
    return Panel(
        Align.center(conteudo),
        border_style="bold magenta",
        title="✨ EASTER EGG ✨",
        title_align="center",
        padding=(1, 4),
    )


def animar_creditos(console: Console, duracao_s: float = 6.0) -> None:
    """Donut 3D girando + card de créditos. Anima por `duracao_s` segundos,
    depois congela no último frame até o caller chamar input()."""
    A, B = 1.0, 1.0
    with Live(_painel_creditos(A, B), console=console, refresh_per_second=20) as live:
        inicio = time.time()
        while time.time() - inicio < duracao_s:
            A += 0.07
            B += 0.03
            live.update(_painel_creditos(A, B))
            time.sleep(0.04)
