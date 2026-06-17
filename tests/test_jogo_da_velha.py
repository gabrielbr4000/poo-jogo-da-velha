"""
tests/test_jogo_da_velha.py
---------------------------
Testes unitários para o Jogo da Velha.

Cobertura:
  - detecção de vitória (linha, coluna, diagonal)
  - detecção de empate
  - rejeição de jogada fora do turno
  - rejeição de posição já ocupada
  - rejeição de posição fora do tabuleiro
  - reinício correto da partida
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from core.jogador import Jogador
from core.jogada import Jogada
from jogos.jogodavelha.jogo import JogoDaVelha


def _criar_jogo() -> tuple[JogoDaVelha, Jogador, Jogador]:
    """Cria um jogo e dois jogadores prontos para uso."""
    j1 = Jogador("Alice", 1)
    j2 = Jogador("Bob", 2)
    jogo = JogoDaVelha([j1, j2])
    jogo.iniciar()
    return jogo, j1, j2


def _jogar(jogo: JogoDaVelha, sequencia: list[tuple]) -> None:
    """
    Aplica uma sequência de jogadas sem passar pelo input do usuário.
    Cada elemento é (jogador, linha, coluna) — valores 0-indexados.
    """
    for jogador, linha, coluna in sequencia:
        jogada = Jogada(jogador, linha=linha, coluna=coluna)
        jogo.realizar_jogada(jogada)


class TestVitoria(unittest.TestCase):

    def test_vitoria_por_linha(self):
        """X ganha preenchendo a linha 0 inteira."""
        jogo, j1, j2 = _criar_jogo()
        _jogar(jogo, [
            (j1, 0, 0), (j2, 1, 0),
            (j1, 0, 1), (j2, 1, 1),
            (j1, 0, 2),            # X completa linha 0
        ])
        self.assertIsNotNone(jogo.resultado)
        self.assertEqual(jogo.resultado.vencedor, j1)

    def test_vitoria_por_coluna(self):
        """O ganha preenchendo a coluna 2 inteira."""
        jogo, j1, j2 = _criar_jogo()
        _jogar(jogo, [
            (j1, 0, 0), (j2, 0, 2),
            (j1, 1, 0), (j2, 1, 2),
            (j1, 2, 1), (j2, 2, 2),  # O completa coluna 2
        ])
        self.assertIsNotNone(jogo.resultado)
        self.assertEqual(jogo.resultado.vencedor, j2)

    def test_vitoria_por_diagonal_principal(self):
        """X ganha pela diagonal principal (↘)."""
        jogo, j1, j2 = _criar_jogo()
        _jogar(jogo, [
            (j1, 0, 0), (j2, 0, 1),
            (j1, 1, 1), (j2, 0, 2),
            (j1, 2, 2),             # X em (0,0),(1,1),(2,2)
        ])
        self.assertIsNotNone(jogo.resultado)
        self.assertEqual(jogo.resultado.vencedor, j1)

    def test_vitoria_por_diagonal_secundaria(self):
        """O ganha pela diagonal secundária (↙)."""
        jogo, j1, j2 = _criar_jogo()
        _jogar(jogo, [
            (j1, 0, 0), (j2, 0, 2),
            (j1, 1, 0), (j2, 1, 1),
            (j1, 2, 1), (j2, 2, 0),  # O em (0,2),(1,1),(2,0)
        ])
        self.assertIsNotNone(jogo.resultado)
        self.assertEqual(jogo.resultado.vencedor, j2)


class TestEmpate(unittest.TestCase):

    def test_empate_tabuleiro_cheio(self):
        """
        Tabuleiro cheio sem vencedor deve resultar em empate.
        Sequência que não gera vitória:
          X O X
          X X O
          O X O
        """
        jogo, j1, j2 = _criar_jogo()
        _jogar(jogo, [
            (j1, 0, 0), (j2, 0, 1),
            (j1, 0, 2), (j2, 1, 2),
            (j1, 1, 0), (j2, 2, 0),
            (j1, 1, 1), (j2, 2, 2),
            (j1, 2, 1),             # último para X — empate
        ])
        self.assertIsNotNone(jogo.resultado)
        self.assertTrue(jogo.resultado.empate)
        self.assertIsNone(jogo.resultado.vencedor)


class TestJogadaInvalida(unittest.TestCase):

    def test_rejeita_jogada_fora_do_turno(self):
        """Bob não pode jogar quando é a vez de Alice."""
        jogo, j1, j2 = _criar_jogo()
        jogada = Jogada(j2, linha=0, coluna=0)   # vez de j1 (Alice)
        aceita = jogo.realizar_jogada(jogada)
        self.assertFalse(aceita)
        self.assertFalse(jogada.valida)

    def test_rejeita_posicao_ja_ocupada(self):
        """Não pode colocar peça em célula já ocupada."""
        jogo, j1, j2 = _criar_jogo()
        jogo.realizar_jogada(Jogada(j1, linha=0, coluna=0))  # Alice joga (0,0)
        jogada = Jogada(j2, linha=0, coluna=0)               # Bob tenta o mesmo
        aceita = jogo.realizar_jogada(jogada)
        self.assertFalse(aceita)
        self.assertFalse(jogada.valida)

    def test_rejeita_posicao_fora_do_tabuleiro(self):
        """Linha ou coluna fora do intervalo 0–2 devem ser rejeitadas."""
        jogo, j1, j2 = _criar_jogo()
        jogada = Jogada(j1, linha=5, coluna=0)
        aceita = jogo.realizar_jogada(jogada)
        self.assertFalse(aceita)
        self.assertFalse(jogada.valida)

    def test_rejeita_jogada_apos_fim_do_jogo(self):
        """Nenhuma jogada deve ser aceita após o jogo terminar."""
        jogo, j1, j2 = _criar_jogo()
        # X vence na linha 0
        _jogar(jogo, [
            (j1, 0, 0), (j2, 1, 0),
            (j1, 0, 1), (j2, 1, 1),
            (j1, 0, 2),
        ])
        jogada_extra = Jogada(j2, linha=2, coluna=2)
        aceita = jogo.realizar_jogada(jogada_extra)
        self.assertFalse(aceita)


class TestEstatisticas(unittest.TestCase):

    def test_estatisticas_atualizadas_apos_vitoria(self):
        """Após vitória de Alice, suas stats devem refletir 1 vitória."""
        jogo, j1, j2 = _criar_jogo()
        _jogar(jogo, [
            (j1, 0, 0), (j2, 1, 0),
            (j1, 0, 1), (j2, 1, 1),
            (j1, 0, 2),
        ])
        self.assertEqual(j1.vitorias, 1)
        self.assertEqual(j2.derrotas, 1)

    def test_estatisticas_atualizadas_apos_empate(self):
        """Após empate, ambos os jogadores devem ter 1 empate."""
        jogo, j1, j2 = _criar_jogo()
        _jogar(jogo, [
            (j1, 0, 0), (j2, 0, 1),
            (j1, 0, 2), (j2, 1, 2),
            (j1, 1, 0), (j2, 2, 0),
            (j1, 1, 1), (j2, 2, 2),
            (j1, 2, 1),
        ])
        self.assertEqual(j1.empates, 1)
        self.assertEqual(j2.empates, 1)


class TestReinicio(unittest.TestCase):

    def test_reinicio_limpa_tabuleiro(self):
        """Após reiniciar, o tabuleiro deve estar vazio."""
        jogo, j1, j2 = _criar_jogo()
        jogo.realizar_jogada(Jogada(j1, linha=0, coluna=0))
        jogo.reiniciar()
        grade = jogo.tabuleiro.grade
        todas_vazias = all(grade[l][c] is None for l in range(3) for c in range(3))
        self.assertTrue(todas_vazias)

    def test_reinicio_restaura_turno(self):
        """Após reiniciar, deve ser a vez do primeiro jogador novamente."""
        jogo, j1, j2 = _criar_jogo()
        jogo.realizar_jogada(Jogada(j1, linha=0, coluna=0))  # avança turno
        jogo.reiniciar()
        self.assertEqual(jogo.turno.jogador_atual, j1)
        self.assertEqual(jogo.turno.numero_turno, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)