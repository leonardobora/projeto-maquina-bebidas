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


if __name__ == "__main__":
    unittest.main()
