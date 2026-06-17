"""
Bot para o Jogo da Velha com 3 níveis de dificuldade.

- Fácil:  jogada aleatória
- Médio:  bloqueia vitória do adversário, senão tenta vencer, senão aleatório
- Difícil: minimax — imbatível
"""

import random
from app.models.jogador import Jogador
from app.models.jogada import Jogada


class Bot(Jogador):
    """Jogador controlado pela máquina."""

    FACIL   = "Fácil"
    MEDIO   = "Médio"
    DIFICIL = "Difícil"

    def __init__(self, dificuldade: str = MEDIO, vida: int = 3):
        # Repassa vida para Jogador via super().__init__, eliminando a necessidade
        # de atribuições externas a atributos privados (_vida, _vida_inicial).
        super().__init__(nome="Bot", id_jogador=2, vida=vida)
        self._dificuldade = dificuldade

    @property
    def dificuldade(self) -> str:
        return self._dificuldade

    def escolher_jogada(self, tabuleiro: list[list[str | None]], simbolo_bot: str, simbolo_adversario: str) -> tuple[int, int]:
        """
        Retorna (linha, coluna) da próxima jogada.
        tabuleiro: lista 3x3 com None, "X" ou "O"
        """
        if self._dificuldade == self.FACIL:
            return self._jogada_aleatoria(tabuleiro)
        elif self._dificuldade == self.MEDIO:
            return self._jogada_media(tabuleiro, simbolo_bot, simbolo_adversario)
        else:
            return self._jogada_minimax(tabuleiro, simbolo_bot, simbolo_adversario)

    # ── Fácil ─────────────────────────────────────────────────────

    def _jogada_aleatoria(self, tabuleiro):
        vazias = self._celulas_vazias(tabuleiro)
        return random.choice(vazias)

    # ── Médio ─────────────────────────────────────────────────────

    def _jogada_media(self, tabuleiro, simbolo_bot, simbolo_adversario):
        # 1. tenta vencer
        vitoria = self._achar_jogada_vencedora(tabuleiro, simbolo_bot)
        if vitoria:
            return vitoria
        # 2. bloqueia adversário
        bloqueio = self._achar_jogada_vencedora(tabuleiro, simbolo_adversario)
        if bloqueio:
            return bloqueio
        # 3. centro
        if tabuleiro[1][1] is None:
            return (1, 1)
        # 4. aleatório
        return self._jogada_aleatoria(tabuleiro)

    def _achar_jogada_vencedora(self, tabuleiro, simbolo):
        """Retorna a célula que completa uma vitória para o símbolo, ou None."""
        for linha, coluna in self._celulas_vazias(tabuleiro):
            copia = self._copiar(tabuleiro)
            copia[linha][coluna] = simbolo
            if self._verificar_vitoria(copia, simbolo):
                return (linha, coluna)
        return None

    # ── Difícil (minimax) ─────────────────────────────────────────

    def _jogada_minimax(self, tabuleiro, simbolo_bot, simbolo_adversario):
        melhor_score = float('-inf')
        melhor_jogada = None

        for linha, coluna in self._celulas_vazias(tabuleiro):
            copia = self._copiar(tabuleiro)
            copia[linha][coluna] = simbolo_bot
            score = self._minimax(copia, False, simbolo_bot, simbolo_adversario)
            if score > melhor_score:
                melhor_score = score
                melhor_jogada = (linha, coluna)

        return melhor_jogada

    def _minimax(self, tabuleiro, maximizando, simbolo_bot, simbolo_adversario):
        if self._verificar_vitoria(tabuleiro, simbolo_bot):
            return 10
        if self._verificar_vitoria(tabuleiro, simbolo_adversario):
            return -10
        if not self._celulas_vazias(tabuleiro):
            return 0

        if maximizando:
            melhor = float('-inf')
            for linha, coluna in self._celulas_vazias(tabuleiro):
                copia = self._copiar(tabuleiro)
                copia[linha][coluna] = simbolo_bot
                melhor = max(melhor, self._minimax(copia, False, simbolo_bot, simbolo_adversario))
            return melhor
        else:
            melhor = float('inf')
            for linha, coluna in self._celulas_vazias(tabuleiro):
                copia = self._copiar(tabuleiro)
                copia[linha][coluna] = simbolo_adversario
                melhor = min(melhor, self._minimax(copia, True, simbolo_bot, simbolo_adversario))
            return melhor

    # ── Utilitários ───────────────────────────────────────────────

    def _celulas_vazias(self, tabuleiro) -> list[tuple[int, int]]:
        return [
            (l, c)
            for l in range(3)
            for c in range(3)
            if tabuleiro[l][c] is None
        ]

    def _copiar(self, tabuleiro) -> list[list]:
        return [linha[:] for linha in tabuleiro]

    def _verificar_vitoria(self, tabuleiro, simbolo) -> bool:
        t = tabuleiro
        # linhas e colunas
        for i in range(3):
            if all(t[i][j] == simbolo for j in range(3)):
                return True
            if all(t[j][i] == simbolo for j in range(3)):
                return True
        # diagonais
        if all(t[i][i] == simbolo for i in range(3)):
            return True
        if all(t[i][2 - i] == simbolo for i in range(3)):
            return True
        return False