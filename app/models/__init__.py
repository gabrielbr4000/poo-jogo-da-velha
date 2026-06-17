"""
Pacote core — base genérica para jogos de tabuleiro.
"""
from .jogo import JogoTabuleiro, EstadoJogo, ResultadoJogo
from .tabuleiro import Tabuleiro
from .jogador import Jogador
from .peca import Peca
from .jogada import Jogada
from .regra import Regra, ConjuntoDeRegras
from .turno import GerenciadorDeTurnos

__all__ = [
    "JogoTabuleiro",
    "EstadoJogo",
    "ResultadoJogo",
    "Tabuleiro",
    "Jogador",
    "Peca",
    "Jogada",
    "Regra",
    "ConjuntoDeRegras",
    "GerenciadorDeTurnos",
]