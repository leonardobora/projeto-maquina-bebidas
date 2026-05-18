# -*- coding: utf-8 -*-
"""
Máquina de Bebidas - Entry point + state machine + loop principal.

Trabalho da disciplina Introdução à Linguagem Python (PUCPR).
Ver spec em docs/superpowers/specs/2026-05-16-maquina-bebidas-design.md
"""
import time
from enum import Enum, auto
from typing import Optional, Dict

from rich.console import Console
from rich.prompt import Prompt, IntPrompt

from produtos import (
    Catalogo,
    Produto,
    ProdutoNaoEncontrado,
    EstoqueZerado,
    IdJaExistente,
)
from caixa import Caixa, DENOMINACOES, TrocoImpossivel
from eventos import (
    deve_travar,
    tapa_resolve,
    mensagem,
    MAX_TENTATIVAS_TAPA,
    resolver_tapa_livre,
    ResultadoTapaLivre,
    COOLDOWN_QUEBRA_SEGUNDOS,
)
from ui import (
    render_idle,
    render_visor,
    render_displays,
    render_troco_completo,
    render_admin,
)
from animacoes import animar_dispensar, animar_troco, animar_tapa, animar_creditos
import audio


SENHA_ADMIN = "1234"
TAPAS_KONAMI = 5


class Estado(Enum):
    IDLE = auto()
    PRODUTO_SELECIONADO = auto()
    AGUARDANDO_PAGAMENTO = auto()
    DISPENSANDO = auto()
    TRAVADA = auto()
    DEVOLVENDO_TROCO = auto()
    ADMIN_LOGIN = auto()
    ADMIN_MODE = auto()
    SAIR = auto()


def _formatar_preco(centavos: int) -> str:
    sinal = "-" if centavos < 0 else ""
    centavos = abs(centavos)
    return f"{sinal}R${centavos // 100},{centavos % 100:02d}"


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
            mensagem("cooldown", segundos=restante),
            tipo="erro"
        ))
        time.sleep(1)


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


# ============================================================================
# Easter egg (Konami: 5 tapas seguidos)
# ============================================================================

def mostrar_creditos(console: Console) -> None:
    """Animação de stick figure + card de créditos. Espera ENTER pra voltar."""
    console.clear()
    animar_creditos(console)
    Prompt.ask("", default="", show_default=False)


# ============================================================================
# Input helpers
# ============================================================================

def ler_entrada_idle(console: Console) -> str:
    """Lê input do user no estado idle: '1'-'5' ou 'admin' ou 'q'."""
    return Prompt.ask("\n[bold]Entrada[/bold]", default="").strip().lower()


def ler_cedula(console: Console) -> Optional[int]:
    """
    Lê valor inserido pelo user.
    Aceita: '5', '5.00', '5,00', '0.25', etc.
    Retorna valor em centavos válido, None se vazio (finalizar), -1 se inválido.
    """
    raw = Prompt.ask(
        "[bold]Inserir cédula/moeda[/bold] (ENTER pra finalizar)",
        default=""
    ).strip().replace(",", ".")
    if raw == "":
        return None
    try:
        valor_reais = float(raw)
        centavos = round(valor_reais * 100)
    except ValueError:
        return -1
    if centavos not in DENOMINACOES:
        return -1
    return centavos


# ============================================================================
# Fluxo de compra
# ============================================================================

def coletar_pagamento(
    console: Console,
    produto: Produto,
    catalogo: Catalogo,
) -> Optional[Dict[int, int]]:
    """
    Coleta cédulas até o user finalizar (ENTER vazio com valor suficiente).
    Retorna dict {denominacao: qtd} ou None se cancelou.
    """
    inserido: Dict[int, int] = {d: 0 for d in DENOMINACOES}
    total_inserido = 0

    while True:
        console.clear()
        console.print(render_idle(catalogo.listar(), selecionado=produto.id))
        falta = max(0, produto.preco_centavos - total_inserido)
        console.print(render_visor(
            f"{produto.nome} · {_formatar_preco(produto.preco_centavos)} · "
            f"Insira cédulas/moedas (ENTER finaliza)"
        ))
        if falta > 0:
            console.print(render_displays(total_inserido, "FALTA", falta))
        else:
            troco = total_inserido - produto.preco_centavos
            console.print(render_displays(total_inserido, "TROCO", troco))

        valor = ler_cedula(console)
        if valor is None:
            if total_inserido >= produto.preco_centavos:
                return inserido
            console.print(render_visor(
                f"Faltam {_formatar_preco(falta)}. Continue inserindo.",
                tipo="erro"
            ))
            time.sleep(1.5)
            continue
        if valor == -1:
            console.print(render_visor(
                "Valor inválido. Use 1, 2, 5, 10, 20, 50, 100 ou 0,01-0,50.",
                tipo="erro"
            ))
            time.sleep(1.5)
            continue

        inserido[valor] += 1
        total_inserido += valor


def tentar_dispensar(console: Console, produto: Produto, catalogo: Catalogo) -> bool:
    """
    Tenta dispensar a bebida (pode travar).
    Retorna True se dispensou, False se a máquina desistiu (3 tapas sem sucesso).
    """
    animar_dispensar(console, produto.nome.upper())

    if not deve_travar():
        return True

    # TRAVOU
    tentativas = 0
    while tentativas < MAX_TENTATIVAS_TAPA:
        console.clear()
        console.print(render_idle(catalogo.listar(), selecionado=produto.id))
        console.print(render_visor(
            mensagem("trava", bebida=produto.nome) + " Aperte [T] pra dar um tapa.",
            tipo="erro"
        ))
        tecla = Prompt.ask(
            "[bold red][T]apa ou [Q] desistir[/bold red]",
            choices=["t", "q"],
            default="t",
            show_choices=False,
        ).lower()

        if tecla == "q":
            return False

        animar_tapa(console)
        if tapa_resolve():
            console.print(render_visor(mensagem("tapa_sucesso"), tipo="ok"))
            time.sleep(1.5)
            return True

        tentativas += 1
        console.print(render_visor(mensagem("tapa_falha"), tipo="erro"))
        time.sleep(1.2)

    # 3 tapas sem sucesso
    console.print(render_visor(mensagem("desistencia"), tipo="erro"))
    time.sleep(2)
    return False


def finalizar_venda(
    console: Console,
    produto: Produto,
    pagamento: Dict[int, int],
    caixa: Caixa,
    catalogo: Catalogo,
) -> bool:
    """
    Fluxo completo com travamento:
    1. Aplica pagamento no caixa.
    2. Tenta calcular troco. Falha → rollback pagamento → cancela.
    3. Tenta dispensar (pode travar). Falha → rollback → cancela.
    4. Sucesso → decrementa estoque → aplica troco.

    Retorna True se a venda foi finalizada com sucesso.
    """
    # 1. Pagamento entra no caixa
    caixa.aplicar_pagamento(pagamento)
    total_pago = sum(d * q for d, q in pagamento.items())
    troco_valor = total_pago - produto.preco_centavos

    # 2. Calcular troco
    try:
        troco = caixa.calcular_troco(troco_valor)
    except TrocoImpossivel:
        caixa.aplicar_troco(pagamento)  # rollback
        console.print(render_visor(
            "Sem cédulas suficientes pro troco. Compra cancelada.",
            tipo="erro"
        ))
        console.print(render_visor(
            f"Devolvendo: {_formatar_preco(total_pago)}",
            tipo="info"
        ))
        time.sleep(2.5)
        return False

    # 3. Tentar dispensar (com travamento)
    dispensou = tentar_dispensar(console, produto, catalogo)
    if not dispensou:
        caixa.aplicar_troco(pagamento)  # rollback total
        console.print(render_visor(
            f"Reembolso: {_formatar_preco(total_pago)}",
            tipo="info"
        ))
        time.sleep(2)
        return False

    # 4. Sucesso: decrementa estoque + aplica troco
    produto.decrementar()
    caixa.aplicar_troco(troco)

    console.print(render_visor(f"Aproveite sua {produto.nome}!", tipo="ok"))
    if troco_valor > 0:
        animar_troco(console, troco)
    time.sleep(2)
    return True


# ============================================================================
# Modo Admin
# ============================================================================

def handle_admin(
    console: Console,
    catalogo: Catalogo,
    caixa: Caixa,
    vendas: int,
    tapas_premiados: int = 0,
) -> None:
    # Login
    tentativas = 3
    autenticado = False
    while tentativas > 0:
        senha = Prompt.ask("[bold cyan]Senha admin[/bold cyan]", password=True)
        if senha == SENHA_ADMIN:
            autenticado = True
            break
        tentativas -= 1
        console.print(render_visor(
            f"Senha incorreta. {tentativas} tentativas restantes.",
            tipo="erro"
        ))
        time.sleep(1.2)

    if not autenticado:
        console.print(render_visor("Acesso negado.", tipo="erro"))
        time.sleep(2)
        return

    # Loop admin
    while True:
        console.clear()
        console.print(render_admin(catalogo.listar(), caixa.total_em_centavos(), vendas, tapas_premiados))
        comando = Prompt.ask(
            "[bold cyan]Comando[/bold cyan]",
            choices=["a", "e", "r", "v"],
            default="v",
        ).lower()

        if comando == "v":
            return
        elif comando == "a":
            _admin_adicionar(console, catalogo)
        elif comando == "e":
            _admin_editar(console, catalogo)
        elif comando == "r":
            _admin_remover(console, catalogo)


def _admin_adicionar(console: Console, catalogo: Catalogo) -> None:
    try:
        id_ = IntPrompt.ask("ID novo")
        nome = Prompt.ask("Nome")
        preco_reais = float(Prompt.ask("Preço (ex: 4.50)"))
        estoque = IntPrompt.ask("Estoque inicial")
        cor = Prompt.ask("Cor hex (ex: #FF8800)", default="#888888")
        novo = Produto(id_, nome, round(preco_reais * 100), estoque, cor)
        catalogo.adicionar(novo)
        console.print(render_visor(f"{nome} adicionado.", tipo="ok"))
    except IdJaExistente:
        console.print(render_visor("ID já existe.", tipo="erro"))
    except Exception as e:
        console.print(render_visor(f"Erro: {e}", tipo="erro"))
    time.sleep(1.5)


def _admin_editar(console: Console, catalogo: Catalogo) -> None:
    try:
        id_ = IntPrompt.ask("ID a editar")
        produto = catalogo.buscar(id_)
        console.print(f"Atual: {produto}")
        campo = Prompt.ask(
            "Campo",
            choices=["nome", "preco_centavos", "estoque", "cor_hex"],
        )
        if campo == "preco_centavos":
            novo_valor = round(float(Prompt.ask("Novo preço (ex: 4.50)")) * 100)
        elif campo == "estoque":
            novo_valor = IntPrompt.ask("Novo estoque")
        else:
            novo_valor = Prompt.ask(f"Novo {campo}")
        catalogo.editar(id_, **{campo: novo_valor})
        console.print(render_visor("Editado.", tipo="ok"))
    except ProdutoNaoEncontrado:
        console.print(render_visor("ID não existe.", tipo="erro"))
    except Exception as e:
        console.print(render_visor(f"Erro: {e}", tipo="erro"))
    time.sleep(1.5)


def _admin_remover(console: Console, catalogo: Catalogo) -> None:
    try:
        id_ = IntPrompt.ask("ID a remover")
        produto = catalogo.buscar(id_)
        confirma = Prompt.ask(
            f"Remover {produto.nome}? [s/N]",
            default="n",
        ).lower()
        if confirma == "s":
            catalogo.remover(id_)
            console.print(render_visor("Removido.", tipo="ok"))
        else:
            console.print(render_visor("Cancelado.", tipo="info"))
    except ProdutoNaoEncontrado:
        console.print(render_visor("ID não existe.", tipo="erro"))
    time.sleep(1.5)


# ============================================================================
# Main loop
# ============================================================================

def main() -> None:
    audio.init_audio()
    console = Console()
    catalogo = Catalogo()
    caixa = Caixa()
    vendas = 0
    tapas_premiados = 0
    tapas_consecutivos = 0

    while True:
        console.clear()
        console.print(render_idle(catalogo.listar()))
        console.print(render_visor("ESCOLHA UMA BEBIDA (1-5) · [T]apa · 'admin' · 'q' sair"))

        entrada = ler_entrada_idle(console)
        if entrada == "q":
            console.print(render_visor("Até a próxima!", tipo="ok"))
            return

        if entrada == "admin":
            tapas_consecutivos = 0
            handle_admin(console, catalogo, caixa, vendas, tapas_premiados)
            continue

        if entrada == "t":
            ganhou = handle_tapa_livre(console, catalogo)
            if ganhou:
                tapas_premiados += 1
            tapas_consecutivos += 1
            if tapas_consecutivos >= TAPAS_KONAMI:
                mostrar_creditos(console)
                tapas_consecutivos = 0
            continue

        # Qualquer outra entrada quebra a sequência konami
        tapas_consecutivos = 0

        try:
            id_ = int(entrada)
        except ValueError:
            console.print(render_visor("Código inválido. Use 1-5.", tipo="erro"))
            time.sleep(2)
            continue

        try:
            produto = catalogo.buscar(id_)
        except ProdutoNaoEncontrado:
            console.print(render_visor(f"Código {id_} não existe.", tipo="erro"))
            time.sleep(2)
            continue

        if not produto.tem_estoque():
            console.print(render_visor(f"{produto.nome} esgotada.", tipo="erro"))
            time.sleep(2)
            continue

        pagamento = coletar_pagamento(console, produto, catalogo)
        if pagamento is None:
            continue

        sucesso = finalizar_venda(console, produto, pagamento, caixa, catalogo)
        if sucesso:
            vendas += 1


if __name__ == "__main__":
    main()
