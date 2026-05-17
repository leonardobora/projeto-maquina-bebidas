# -*- coding: utf-8 -*-
from dataclasses import dataclass
import random as _random
from typing import List, Optional


class ProdutoNaoEncontrado(Exception):
    pass


class EstoqueZerado(Exception):
    pass


class IdJaExistente(Exception):
    pass


@dataclass
class Produto:
    id: int
    nome: str
    preco_centavos: int
    estoque: int
    cor_hex: str

    def tem_estoque(self) -> bool:
        return self.estoque > 0

    def decrementar(self) -> None:
        if not self.tem_estoque():
            raise EstoqueZerado(f"{self.nome} esgotada")
        self.estoque -= 1


def _catalogo_inicial() -> List[Produto]:
    return [
        Produto(1, "Coca-cola", 375, 2, "#E61E1E"),
        Produto(2, "Pepsi", 367, 5, "#004B93"),
        Produto(3, "Monster", 996, 1, "#82C341"),
        Produto(4, "Café", 125, 100, "#6F4E37"),
        Produto(5, "Redbull", 1399, 2, "#CC0000"),
    ]


class Catalogo:
    def __init__(self):
        self._produtos: List[Produto] = _catalogo_inicial()

    def listar(self) -> List[Produto]:
        return list(self._produtos)

    def buscar(self, id_: int) -> Produto:
        for p in self._produtos:
            if p.id == id_:
                return p
        raise ProdutoNaoEncontrado(f"ID {id_} não existe")

    def adicionar(self, produto: Produto) -> None:
        try:
            self.buscar(produto.id)
        except ProdutoNaoEncontrado:
            self._produtos.append(produto)
            return
        raise IdJaExistente(f"ID {produto.id} já existe")

    def editar(self, id_: int, **campos) -> None:
        p = self.buscar(id_)
        for campo, valor in campos.items():
            if not hasattr(p, campo):
                raise ValueError(f"Campo desconhecido: {campo}")
            setattr(p, campo, valor)

    def remover(self, id_: int) -> None:
        p = self.buscar(id_)
        self._produtos.remove(p)

    def sortear_com_estoque(self, rng: Optional[_random.Random] = None) -> Optional[Produto]:
        """Sorteia uniformemente entre produtos com estoque > 0.
        Retorna None se todos estão esgotados."""
        rng = rng or _random
        disponiveis = [p for p in self._produtos if p.tem_estoque()]
        if not disponiveis:
            return None
        return rng.choice(disponiveis)
