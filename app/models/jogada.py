"""
Módulo core.jogada
------------------
Define Jogada — um objeto de valor (value object) imutável que encapsula
os dados de uma única jogada: quem jogou e os parâmetros da jogada.

Cada jogo decide quais chaves incluir em `dados` (ex: linha/coluna, coluna, etc.).
"""
from __future__ import annotations
from typing import Any


class Jogada:
    """
    Encapsula uma intenção de jogada de um Jogador.

    Parâmetros nomeados em **dados permitem que cada jogo defina
    sua própria estrutura sem alterar esta classe.

    Exemplos:
        Jogada(jogador, linha=1, coluna=2)  # Jogo da Velha
        Jogada(jogador, coluna=3)           # Lig-4
    """

    def __init__(self, jogador, **dados: Any):
        self._jogador = jogador
        self._dados: dict[str, Any] = dados
        self._valida: bool | None = None  # definida após validação

    # --- Propriedades ---

    @property
    def jogador(self):
        return self._jogador

    @property
    def dados(self) -> dict[str, Any]:
        return self._dados

    @property
    def valida(self) -> bool | None:
        return self._valida

    @valida.setter
    def valida(self, valor: bool) -> None:
        self._valida = valor

    def __repr__(self) -> str:
        return f"Jogada(jogador={self._jogador!r}, dados={self._dados}, valida={self._valida})"