"""
Regras do Jogo da Velha.

  1. RegraVezCorretaVelha  → só quem é da vez pode jogar
  2. RegraPosicaoValidaVelha → posição deve estar dentro do tabuleiro e livre
"""
from app.models.regra import Regra, ConjuntoDeRegras


class RegraVezCorretaVelha(Regra):
    """Garante que a jogada pertence ao jogador da vez."""

    def validar(self, jogada, tabuleiro, turno) -> tuple[bool, str]:
        if jogada.jogador is not turno.jogador_atual:
            return False, f"Não é a vez de '{jogada.jogador}'."
        return True, ""


class RegraPosicaoValidaVelha(Regra):
    """Garante que linha/coluna são válidas e a célula está vazia."""

    def validar(self, jogada, tabuleiro, turno) -> tuple[bool, str]:
        linha = jogada.dados.get("linha")
        coluna = jogada.dados.get("coluna")

        if linha is None or coluna is None:
            return False, "Informe linha e coluna."

        if not (0 <= linha < 3 and 0 <= coluna < 3):
            return (
                False,
                f"Posição ({linha + 1}, {coluna + 1}) fora do tabuleiro 3×3.",
            )

        if not tabuleiro.celula_vazia(linha, coluna):
            return False, f"Posição ({linha + 1}, {coluna + 1}) já está ocupada."

        return True, ""


def criar_regras_velha() -> ConjuntoDeRegras:
    """Fábrica: monta e retorna o ConjuntoDeRegras do Jogo da Velha."""
    return (
        ConjuntoDeRegras()
        .adicionar_regra(RegraVezCorretaVelha())
        .adicionar_regra(RegraPosicaoValidaVelha())
    )