# -*- coding: utf-8 -*-
import unittest
from caixa import (
    DENOMINACOES,
    calcular_troco_guloso,
    Caixa,
    TrocoImpossivel,
)


class TestDenominacoes(unittest.TestCase):
    def test_denominacoes_em_ordem_decrescente(self):
        self.assertEqual(DENOMINACOES, sorted(DENOMINACOES, reverse=True))

    def test_denominacoes_brl_completas(self):
        esperadas = [10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 1]
        self.assertEqual(DENOMINACOES, esperadas)


class TestCalcularTrocoGuloso(unittest.TestCase):
    def test_troco_caso_pdf_6_33_valor_total_bate(self):
        resultado = calcular_troco_guloso(633)
        total = sum(k * v for k, v in resultado.items())
        self.assertEqual(total, 633)
        # Menor volume: 1×R$5 + 1×R$1 + 1×25¢ + 1×5¢ + 3×1¢ = 7 unidades
        self.assertEqual(sum(resultado.values()), 7)

    def test_troco_zero_retorna_dict_vazio_de_zeros(self):
        resultado = calcular_troco_guloso(0)
        self.assertEqual(sum(resultado.values()), 0)

    def test_troco_so_de_uma_denominacao(self):
        resultado = calcular_troco_guloso(1000)
        self.assertEqual(resultado[1000], 1)
        for k, v in resultado.items():
            if k != 1000:
                self.assertEqual(v, 0)

    def test_troco_combina_denominacoes(self):
        valor = 777
        resultado = calcular_troco_guloso(valor)
        total = sum(k * v for k, v in resultado.items())
        self.assertEqual(total, valor)


class TestCaixaEstoqueFinito(unittest.TestCase):
    def test_caixa_inicial_tem_estoque_padrao(self):
        c = Caixa()
        self.assertGreater(c.estoque_de(10000), 0)
        self.assertGreater(c.estoque_de(1), 0)

    def test_calcular_troco_respeita_estoque(self):
        c = Caixa(estoque_inicial={5000: 1})
        with self.assertRaises(TrocoImpossivel):
            c.calcular_troco(10000)

    def test_calcular_troco_combina_quando_falta_uma_denominacao(self):
        c = Caixa(estoque_inicial={2000: 2, 1000: 1, 100: 10})
        troco = c.calcular_troco(5000)
        total = sum(k * v for k, v in troco.items())
        self.assertEqual(total, 5000)

    def test_aplicar_pagamento_incrementa_estoque(self):
        c = Caixa(estoque_inicial={500: 1})
        c.aplicar_pagamento({500: 2, 100: 3})
        self.assertEqual(c.estoque_de(500), 3)
        self.assertEqual(c.estoque_de(100), 3)

    def test_aplicar_troco_decrementa_estoque(self):
        c = Caixa(estoque_inicial={500: 5, 100: 5})
        c.aplicar_troco({500: 1, 100: 2})
        self.assertEqual(c.estoque_de(500), 4)
        self.assertEqual(c.estoque_de(100), 3)

    def test_total_em_caixa_retorna_soma_em_centavos(self):
        c = Caixa(estoque_inicial={1000: 2, 100: 5})
        self.assertEqual(c.total_em_centavos(), 2500)

    def test_reembolso_devolve_exatamente_o_que_foi_inserido(self):
        c = Caixa(estoque_inicial={500: 2, 100: 3})
        pagamento = {500: 1, 100: 2}
        c.aplicar_pagamento(pagamento)
        devolucao = c.reembolsar(pagamento)
        self.assertEqual(devolucao, pagamento)
        self.assertEqual(c.estoque_de(500), 2)
        self.assertEqual(c.estoque_de(100), 3)


if __name__ == "__main__":
    unittest.main()
