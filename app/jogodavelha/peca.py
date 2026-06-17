"""Peça do Jogo da Velha (X ou O)."""
from app.models.peca import Peca


class PecaVelha(Peca):
    """Especialização de Peca para o Jogo da Velha. Sem comportamento extra."""

    def __init__(self, simbolo: str, dono=None):
        super().__init__(simbolo, dono)