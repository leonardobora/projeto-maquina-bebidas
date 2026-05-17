# -*- coding: utf-8 -*-
import unittest
import random
from produtos import Produto, Catalogo, ProdutoNaoEncontrado, EstoqueZerado, IdJaExistente


class TestProduto(unittest.TestCase):
    def test_produto_cria_com_atributos_corretos(self):
        p = Produto(id=1, nome="Coca", preco_centavos=375, estoque=2, cor_hex="#E61E1E")
        self.assertEqual(p.id, 1)
        self.assertEqual(p.nome, "Coca")
        self.assertEqual(p.preco_centavos, 375)
        self.assertEqual(p.estoque, 2)
        self.assertEqual(p.cor_hex, "#E61E1E")

    def test_tem_estoque_true_quando_maior_que_zero(self):
        p = Produto(1, "Coca", 375, 2, "#E61E1E")
        self.assertTrue(p.tem_estoque())

    def test_tem_estoque_false_quando_zero(self):
        p = Produto(1, "Coca", 375, 0, "#E61E1E")
        self.assertFalse(p.tem_estoque())

    def test_decrementar_estoque_reduz_em_1(self):
        p = Produto(1, "Coca", 375, 2, "#E61E1E")
        p.decrementar()
        self.assertEqual(p.estoque, 1)

    def test_decrementar_estoque_zerado_lanca_excecao(self):
        p = Produto(1, "Coca", 375, 0, "#E61E1E")
        with self.assertRaises(EstoqueZerado):
            p.decrementar()


class TestCatalogo(unittest.TestCase):
    def test_catalogo_inicial_tem_5_produtos(self):
        c = Catalogo()
        self.assertEqual(len(c.listar()), 5)

    def test_catalogo_inicial_contem_coca_375_centavos(self):
        c = Catalogo()
        coca = c.buscar(1)
        self.assertEqual(coca.nome, "Coca-cola")
        self.assertEqual(coca.preco_centavos, 375)
        self.assertEqual(coca.estoque, 2)

    def test_catalogo_inicial_contem_5_produtos_do_pdf(self):
        c = Catalogo()
        esperados = [
            (1, "Coca-cola", 375, 2),
            (2, "Pepsi", 367, 5),
            (3, "Monster", 996, 1),
            (4, "Café", 125, 100),
            (5, "Redbull", 1399, 2),
        ]
        for id_, nome, preco, estoque in esperados:
            p = c.buscar(id_)
            self.assertEqual(p.nome, nome)
            self.assertEqual(p.preco_centavos, preco)
            self.assertEqual(p.estoque, estoque)

    def test_buscar_id_inexistente_lanca_excecao(self):
        c = Catalogo()
        with self.assertRaises(ProdutoNaoEncontrado):
            c.buscar(99)


class TestCatalogoCRUD(unittest.TestCase):
    def test_adicionar_produto_novo(self):
        c = Catalogo()
        novo = Produto(99, "Suco", 500, 10, "#FF8800")
        c.adicionar(novo)
        self.assertEqual(c.buscar(99).nome, "Suco")

    def test_adicionar_id_duplicado_falha(self):
        c = Catalogo()
        with self.assertRaises(IdJaExistente):
            c.adicionar(Produto(1, "Outro", 100, 1, "#000000"))

    def test_editar_produto(self):
        c = Catalogo()
        c.editar(1, nome="Coca Zero", preco_centavos=400, estoque=10)
        coca = c.buscar(1)
        self.assertEqual(coca.nome, "Coca Zero")
        self.assertEqual(coca.preco_centavos, 400)
        self.assertEqual(coca.estoque, 10)

    def test_editar_apenas_um_campo(self):
        c = Catalogo()
        c.editar(1, estoque=99)
        coca = c.buscar(1)
        self.assertEqual(coca.nome, "Coca-cola")
        self.assertEqual(coca.estoque, 99)

    def test_editar_id_inexistente_falha(self):
        c = Catalogo()
        with self.assertRaises(ProdutoNaoEncontrado):
            c.editar(99, estoque=10)

    def test_remover_produto(self):
        c = Catalogo()
        c.remover(1)
        self.assertEqual(len(c.listar()), 4)
        with self.assertRaises(ProdutoNaoEncontrado):
            c.buscar(1)

    def test_remover_id_inexistente_falha(self):
        c = Catalogo()
        with self.assertRaises(ProdutoNaoEncontrado):
            c.remover(99)


class TestSortearComEstoque(unittest.TestCase):
    def test_sortear_retorna_produto_com_estoque(self):
        cat = Catalogo()
        rng = random.Random(42)
        for _ in range(50):
            p = cat.sortear_com_estoque(rng=rng)
            self.assertIsNotNone(p)
            self.assertTrue(p.tem_estoque())

    def test_sortear_nunca_retorna_produto_esgotado(self):
        cat = Catalogo()
        # zera tudo menos café (ID 4)
        for produto in cat.listar():
            if produto.id != 4:
                produto.estoque = 0
        rng = random.Random(7)
        for _ in range(20):
            p = cat.sortear_com_estoque(rng=rng)
            self.assertEqual(p.id, 4)

    def test_sortear_retorna_none_quando_tudo_esgotado(self):
        cat = Catalogo()
        for produto in cat.listar():
            produto.estoque = 0
        self.assertIsNone(cat.sortear_com_estoque())

    def test_sortear_aceita_rng_none(self):
        cat = Catalogo()
        resultado = cat.sortear_com_estoque()
        self.assertIsNotNone(resultado)


if __name__ == "__main__":
    unittest.main()
