"""
Módulo core.tabuleiro
---------------------
Define a classe abstrata Tabuleiro — uma grade bidimensional genérica.

Subclasses devem implementar `exibir()` para renderizar o tabuleiro
de forma apropriada para cada jogo.
"""
from abc import ABC, abstractmethod
from typing import Any


class Tabuleiro(ABC):
    """
    Grade bidimensional de linhas × colunas.

    Cada célula pode conter qualquer valor (None = vazia).
    Fornece operações primitivas de acesso, escrita e consulta
    para que as subclasses não precisem reescrever lógica de grade.

    Composição: o JogoTabuleiro *possui* um Tabuleiro.
    """

    def __init__(self, linhas: int, colunas: int):
        self._linhas = linhas
        self._colunas = colunas
        self._grade: list[list[Any]] = []
        self._inicializar_grade()

    # --- Inicialização interna ---

    def _inicializar_grade(self) -> None:
        self._grade = [
            [None for _ in range(self._colunas)]
            for _ in range(self._linhas)
        ]

    # --- Propriedades ---

    @property
    def linhas(self) -> int:
        return self._linhas

    @property
    def colunas(self) -> int:
        return self._colunas

    @property
    def grade(self) -> list[list[Any]]:
        """Retorna referência à grade (leitura; evite mutação direta)."""
        return self._grade

    # --- Acesso às células ---

    def obter_celula(self, linha: int, coluna: int) -> Any:
        self._validar_posicao(linha, coluna)
        return self._grade[linha][coluna]

    def definir_celula(self, linha: int, coluna: int, valor: Any) -> None:
        self._validar_posicao(linha, coluna)
        self._grade[linha][coluna] = valor

    def celula_vazia(self, linha: int, coluna: int) -> bool:
        return self.obter_celula(linha, coluna) is None

    # --- Consultas ---

    def esta_cheio(self) -> bool:
        """True se não existe nenhuma célula vazia no tabuleiro."""
        return all(
            self._grade[l][c] is not None
            for l in range(self._linhas)
            for c in range(self._colunas)
        )

    def limpar(self) -> None:
        """Reinicia todas as células para None."""
        self._inicializar_grade()

    # --- Validação interna ---

    def _validar_posicao(self, linha: int, coluna: int) -> None:
        if not (0 <= linha < self._linhas and 0 <= coluna < self._colunas):
            raise IndexError(
                f"Posição ({linha}, {coluna}) fora dos limites "
                f"do tabuleiro {self._linhas}×{self._colunas}."
            )

    # --- Interface obrigatória ---

    @abstractmethod
    def exibir(self) -> None:
        """Renderiza o tabuleiro no terminal."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._linhas}×{self._colunas})"