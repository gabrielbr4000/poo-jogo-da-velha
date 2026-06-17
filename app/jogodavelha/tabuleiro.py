"""Tabuleiro 3×3 do Jogo da Velha."""
from app.models.tabuleiro import Tabuleiro


class TabuleiroVelha(Tabuleiro):
    """
    Grade 3×3 com exibição em estilo clássico:

       1   2   3
    1  X | O |
       ---+---+---
    2    | X |
       ---+---+---
    3  O |   | X
    """

    def __init__(self):
        super().__init__(3, 3)

    def exibir(self) -> None:
        print()
        print("     1   2   3")
        for i, linha in enumerate(self._grade):
            celulas = [str(c) if c is not None else " " for c in linha]
            print(f"  {i + 1}  {'  |  '.join(celulas)}")
            if i < self._linhas - 1:
                print("     ---+---+---")
        print()