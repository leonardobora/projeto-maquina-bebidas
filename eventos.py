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
