"""
Módulo core.peca
----------------
Define a classe abstrata Peca, raiz da hierarquia de peças.
Qualquer jogo que precise de peças deve herdar desta classe.
"""
from abc import ABC, abstractmethod


class Peca(ABC):
    """
    Representa uma peça genérica de jogo de tabuleiro.

    Atributos (privados):
        _simbolo: representação visual da peça (ex: 'X', 'O', '♟')
        _dono:    referência ao Jogador dono desta peça (pode ser None)
    """

    def __init__(self, simbolo: str, dono=None):
        self._simbolo = simbolo
        self._dono = dono

    @property
    def simbolo(self) -> str:
        return self._simbolo

    @property
    def dono(self):
        return self._dono

    def __str__(self) -> str:
        return self._simbolo

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(simbolo='{self._simbolo}', dono={self._dono})"