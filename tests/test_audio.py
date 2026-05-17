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
