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
