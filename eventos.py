# -*- coding: utf-8 -*-
import random
from typing import Optional

PROBABILIDADE_TRAVAR = 0.25
PROBABILIDADE_TAPA_SUCESSO = 0.50
MAX_TENTATIVAS_TAPA = 3

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
}


def deve_travar(rng: Optional[random.Random] = None) -> bool:
    rng = rng or random
    return rng.random() < PROBABILIDADE_TRAVAR


def tapa_resolve(rng: Optional[random.Random] = None) -> bool:
    rng = rng or random
    return rng.random() < PROBABILIDADE_TAPA_SUCESSO


def mensagem(categoria: str, bebida: str = "", rng: Optional[random.Random] = None) -> str:
    rng = rng or random
    opcoes = _MENSAGENS[categoria]
    template = rng.choice(opcoes)
    return template.format(bebida=bebida)
