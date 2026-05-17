# -*- coding: utf-8 -*-
from typing import List, Optional, Dict
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.table import Table

from produtos import Produto


CORES = {
    "coca":    "#E61E1E",
    "pepsi":   "#004B93",
    "monster": "#82C341",
    "cafe":    "#6F4E37",
    "redbull": "#CC0000",
    "redbull_alt": "#003B82",
    "visor":   "#FFCC00",
    "erro":    "#FF3333",
    "ok":      "#33FF66",
    "neutro":  "#888888",
    "borda":   "#FFFFFF",
}


def _cor_do_produto(p: Produto) -> str:
    if not p.tem_estoque():
        return CORES["neutro"]
    return p.cor_hex


def _formatar_preco(centavos: int) -> str:
    sinal = "-" if centavos < 0 else ""
    centavos = abs(centavos)
    reais = centavos // 100
    cents = centavos % 100
    return f"{sinal}R${reais},{cents:02d}"


def render_slot(produto: Produto, selecionado: bool = False) -> Panel:
    cor = _cor_do_produto(produto)
    estoque_txt = f"x{produto.estoque}" if produto.tem_estoque() else "ESGOTADO"

    conteudo = Text()
    conteudo.append(f"\n{produto.nome.upper()[:7]:^7}\n", style=f"bold {cor}")
    conteudo.append(f"\n{_formatar_preco(produto.preco_centavos):^7}\n", style="white")
    conteudo.append(f"{estoque_txt:^7}\n", style=cor if produto.tem_estoque() else "dim")

    titulo = f"▶[{produto.id}]◀" if selecionado else f"[{produto.id}]"
    return Panel(
        Align.center(conteudo),
        title=titulo,
        border_style=cor,
        width=13,
        height=8,
    )


def render_idle(produtos: List[Produto], selecionado: Optional[int] = None) -> Panel:
    slots = [render_slot(p, selecionado=(p.id == selecionado)) for p in produtos]
    return Panel(
        Columns(slots, padding=(0, 1)),
        title="PUCPR BEVERAGE CO.",
        title_align="center",
        border_style="bold white",
        padding=(1, 2),
    )


def render_visor(mensagem: str, tipo: str = "normal") -> Panel:
    """tipo: 'normal' | 'erro' | 'ok' | 'info'"""
    cores_tipo = {
        "normal": CORES["visor"],
        "erro":   CORES["erro"],
        "ok":     CORES["ok"],
        "info":   "white",
    }
    cor = cores_tipo.get(tipo, "white")
    txt = Text(f"▸ {mensagem}", style=cor)
    return Panel(
        txt,
        border_style=cor,
        padding=(0, 1),
    )


def render_displays(inserir_centavos: int, info_label: str, info_centavos: int) -> Columns:
    """info_label: 'FALTA' | 'TROCO'"""
    inserir_panel = Panel(
        Align.center(Text(_formatar_preco(inserir_centavos), style="bold white")),
        title="INSERIR",
        border_style="white",
        width=20,
        height=3,
    )
    info_panel = Panel(
        Align.center(Text(_formatar_preco(info_centavos), style="bold yellow")),
        title=info_label,
        border_style="yellow",
        width=30,
        height=3,
    )
    return Columns([inserir_panel, info_panel], padding=(0, 2))


def render_troco_completo(troco: Dict[int, int]) -> Panel:
    linhas = Text()
    total = 0
    for denom in sorted(troco.keys(), reverse=True):
        qtd = troco[denom]
        if qtd == 0:
            continue
        subtotal = denom * qtd
        total += subtotal
        linhas.append(f"  {qtd} × {_formatar_preco(denom)}   ✓\n", style="white")
    linhas.append(f"  ─────────────\n", style="dim")
    linhas.append(f"  Total: {_formatar_preco(total)}", style="bold yellow")
    return Panel(linhas, title="TROCO RECEBIDO", border_style="yellow")


def render_admin(
    produtos: List[Produto],
    caixa_total_centavos: int,
    vendas_sessao: int,
    tapas_premiados: int = 0,
) -> Panel:
    tabela = Table(show_header=True, header_style="bold cyan")
    tabela.add_column("ID", justify="center", width=4)
    tabela.add_column("PRODUTO", width=14)
    tabela.add_column("PREÇO", justify="right", width=10)
    tabela.add_column("ESTOQUE", justify="center", width=8)
    tabela.add_column("COR", width=18)

    for p in produtos:
        tabela.add_row(
            str(p.id),
            p.nome,
            _formatar_preco(p.preco_centavos),
            str(p.estoque),
            Text(f"████ {p.cor_hex}", style=p.cor_hex),
        )

    cabecalho = Panel(
        Align.center(Text("[A]dicionar  [E]ditar  [R]emover  [V]oltar", style="bold white")),
        border_style="cyan",
    )
    rodape = Panel(
        Align.center(Text(
            f"Caixa: {_formatar_preco(caixa_total_centavos)}  │  "
            f"Vendas: {vendas_sessao}  │  Tapas premiados: {tapas_premiados}",
            style="dim white"
        )),
        border_style="cyan",
    )

    layout = Layout()
    layout.split_column(
        Layout(cabecalho, size=3),
        Layout(tabela),
        Layout(rodape, size=3),
    )

    return Panel(
        layout,
        title="🔧 MODO ADMIN 🔧",
        title_align="center",
        border_style="bold cyan",
        height=18,
    )
