"""
Módulo core.turno
-----------------
Define GerenciadorDeTurnos — controla a alternância entre jogadores
e mantém o número do turno atual.

Associação: o JogoTabuleiro usa um GerenciadorDeTurnos.
"""
from __future__ import annotations
from typing import List
from .jogador import Jogador


class GerenciadorDeTurnos:
    """
    Gerencia a ordem de vez dos jogadores em round-robin.

    Atributos privados:
        _jogadores:     lista ordenada de jogadores
        _indice_atual:  índice do jogador que deve jogar agora
        _numero_turno:  contador de turnos (1-indexed)
    """

    def __init__(self, jogadores: List[Jogador]):
        if not jogadores:
            raise ValueError("É necessário pelo menos um jogador.")
        self._jogadores = list(jogadores)
        self._indice_atual: int = 0
        self._numero_turno: int = 1

    # --- Propriedades ---

    @property
    def jogador_atual(self) -> Jogador:
        return self._jogadores[self._indice_atual]

    @property
    def numero_turno(self) -> int:
        return self._numero_turno

    @property
    def jogadores(self) -> List[Jogador]:
        return list(self._jogadores)

    # --- Controle ---

    def avancar(self) -> None:
        """Passa a vez para o próximo jogador e incrementa o turno."""
        self._indice_atual = (self._indice_atual + 1) % len(self._jogadores)
        self._numero_turno += 1

    def reiniciar(self) -> None:
        """Volta ao primeiro jogador, turno 1."""
        self._indice_atual = 0
        self._numero_turno = 1

    def __repr__(self) -> str:
        return (
            f"GerenciadorDeTurnos("
            f"turno={self._numero_turno}, "
            f"atual='{self.jogador_atual}')"
        )