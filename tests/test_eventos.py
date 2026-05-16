# -*- coding: utf-8 -*-
import unittest
import random
from eventos import (
    deve_travar,
    tapa_resolve,
    mensagem,
    PROBABILIDADE_TRAVAR,
    PROBABILIDADE_TAPA_SUCESSO,
    MAX_TENTATIVAS_TAPA,
)


class TestProbabilidades(unittest.TestCase):
    def test_probabilidades_no_intervalo_esperado(self):
        self.assertEqual(PROBABILIDADE_TRAVAR, 0.25)
        self.assertEqual(PROBABILIDADE_TAPA_SUCESSO, 0.50)
        self.assertEqual(MAX_TENTATIVAS_TAPA, 3)


class TestDeveTravar(unittest.TestCase):
    def test_deve_travar_proporcao_aproxima_25_porcento(self):
        rng = random.Random(42)
        amostras = 10000
        travas = sum(1 for _ in range(amostras) if deve_travar(rng=rng))
        proporcao = travas / amostras
        self.assertAlmostEqual(proporcao, 0.25, delta=0.02)

    def test_deve_travar_aceita_rng_none_e_usa_random_global(self):
        resultado = deve_travar()
        self.assertIsInstance(resultado, bool)


class TestTapaResolve(unittest.TestCase):
    def test_tapa_resolve_proporcao_aproxima_50_porcento(self):
        rng = random.Random(123)
        amostras = 10000
        sucessos = sum(1 for _ in range(amostras) if tapa_resolve(rng=rng))
        proporcao = sucessos / amostras
        self.assertAlmostEqual(proporcao, 0.50, delta=0.02)


class TestMensagens(unittest.TestCase):
    def test_mensagem_trava_retorna_string_nao_vazia(self):
        rng = random.Random(0)
        msg = mensagem("trava", bebida="PEPSI", rng=rng)
        self.assertTrue(len(msg) > 0)

    def test_mensagem_trava_substitui_bebida_quando_template_usa(self):
        rng = random.Random(0)
        encontrou_pepsi = False
        for _ in range(50):
            msg = mensagem("trava", bebida="PEPSI", rng=rng)
            if "PEPSI" in msg:
                encontrou_pepsi = True
                break
        self.assertTrue(encontrou_pepsi)

    def test_mensagem_tapa_sucesso_nao_vazia(self):
        rng = random.Random(0)
        msg = mensagem("tapa_sucesso", rng=rng)
        self.assertTrue(len(msg) > 0)

    def test_mensagem_categoria_invalida_lanca(self):
        with self.assertRaises(KeyError):
            mensagem("inexistente")


if __name__ == "__main__":
    unittest.main()
