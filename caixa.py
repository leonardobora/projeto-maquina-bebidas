# -*- coding: utf-8 -*-
from typing import Dict, Optional


DENOMINACOES = [10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 1]
# R$100, R$50, R$20, R$10, R$5, R$2, R$1, 50¢, 25¢, 10¢, 5¢, 1¢


CAIXA_INICIAL_PADRAO = {
    10000: 5,    # R$ 100
    5000:  8,    # R$ 50
    2000:  15,   # R$ 20
    1000:  20,   # R$ 10
    500:   30,   # R$ 5
    200:   50,   # R$ 2
    100:   40,   # R$ 1
    50:    50,   # 50¢
    25:    50,   # 25¢
    10:    100,  # 10¢
    5:     100,  # 5¢
    1:     200,  # 1¢
}


class TrocoImpossivel(Exception):
    pass


def calcular_troco_guloso(valor_centavos: int) -> Dict[int, int]:
    """
    Calcula troco com menor número de cédulas/moedas (algoritmo guloso clássico).
    Funciona porque BRL é um sistema canônico.
    Não considera estoque — assume disponibilidade infinita.
    """
    resultado = {d: 0 for d in DENOMINACOES}
    restante = valor_centavos
    for d in DENOMINACOES:
        if restante >= d:
            qtd, restante = divmod(restante, d)
            resultado[d] = qtd
    return resultado


class Caixa:
    def __init__(self, estoque_inicial: Optional[Dict[int, int]] = None):
        if estoque_inicial is None:
            estoque_inicial = CAIXA_INICIAL_PADRAO
        self._estoque: Dict[int, int] = {d: 0 for d in DENOMINACOES}
        for denom, qtd in estoque_inicial.items():
            if denom not in self._estoque:
                raise ValueError(f"Denominação inválida: {denom}")
            self._estoque[denom] = qtd

    def estoque_de(self, denom: int) -> int:
        return self._estoque.get(denom, 0)

    def total_em_centavos(self) -> int:
        return sum(d * q for d, q in self._estoque.items())

    def calcular_troco(self, valor_centavos: int) -> Dict[int, int]:
        """
        Guloso respeitando estoque disponível.
        Lança TrocoImpossivel se não há como montar com o estoque atual.
        """
        resultado = {d: 0 for d in DENOMINACOES}
        restante = valor_centavos
        for d in DENOMINACOES:
            if restante < d:
                continue
            disponivel = self._estoque[d]
            qtd_ideal = restante // d
            qtd_usada = min(qtd_ideal, disponivel)
            resultado[d] = qtd_usada
            restante -= qtd_usada * d
        if restante > 0:
            raise TrocoImpossivel(
                f"Faltam {restante} centavos — sem denominações suficientes"
            )
        return resultado

    def aplicar_pagamento(self, cedulas: Dict[int, int]) -> None:
        for denom, qtd in cedulas.items():
            self._estoque[denom] += qtd

    def aplicar_troco(self, cedulas: Dict[int, int]) -> None:
        for denom, qtd in cedulas.items():
            if self._estoque[denom] < qtd:
                raise TrocoImpossivel(
                    f"Sem {qtd}x {denom}¢ no caixa (tem {self._estoque[denom]})"
                )
            self._estoque[denom] -= qtd

    def reembolsar(self, cedulas_inseridas: Dict[int, int]) -> Dict[int, int]:
        """
        Devolve exatamente as cédulas que foram inseridas (não usa algoritmo guloso).
        Decrementa do caixa.
        """
        self.aplicar_troco(cedulas_inseridas)
        return dict(cedulas_inseridas)
