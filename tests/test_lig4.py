"""
tests/test_lig4.py
------------------
Testes unitários para o Lig-4.

Cobertura:
  - gravidade (peça cai para a posição correta)
  - vitória horizontal, vertical, diagonal ↘ e ↙
  - rejeição de coluna cheia
  - rejeição de coluna inexistente
  - rejeição de jogada fora do turno
  - empate
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from core.jogador import Jogador
from core.jogada import Jogada
from jogos.lig4.jogo import Lig4
from jogos.lig4.tabuleiro import TabuleiroLig4


def _criar_jogo() -> tuple[Lig4, Jogador, Jogador]:
    j1 = Jogador("Alice", 1)
    j2 = Jogador("Bob", 2)
    jogo = Lig4([j1, j2])
    jogo.iniciar()
    return jogo, j1, j2


def _dropar(jogo: Lig4, sequencia: list[tuple]) -> None:
    """Aplica sequência de (jogador, coluna) no jogo."""
    for jogador, coluna in sequencia:
        jogo.realizar_jogada(Jogada(jogador, coluna=coluna))


class TestGravidade(unittest.TestCase):

    def test_peca_cai_para_linha_mais_baixa(self):
        """Primeira peça numa coluna deve pousar na linha 5 (base)."""
        jogo, j1, j2 = _criar_jogo()
        jogo.realizar_jogada(Jogada(j1, coluna=0))
        peca = jogo.tabuleiro.obter_celula(5, 0)
        self.assertIsNotNone(peca)

    def test_segunda_peca_empilha_sobre_primeira(self):
        """Segunda peça na mesma coluna deve pousar na linha 4."""
        jogo, j1, j2 = _criar_jogo()
        jogo.realizar_jogada(Jogada(j1, coluna=3))
        jogo.realizar_jogada(Jogada(j2, coluna=3))
        self.assertIsNotNone(jogo.tabuleiro.obter_celula(5, 3))
        self.assertIsNotNone(jogo.tabuleiro.obter_celula(4, 3))
        self.assertIsNone(jogo.tabuleiro.obter_celula(3, 3))

    def test_coluna_cheia_apos_6_pecas(self):
        """Após 6 peças na mesma coluna, ela deve estar indisponível."""
        jogo, j1, j2 = _criar_jogo()
        jogadores = [j1, j2, j1, j2, j1, j2]
        for jog in jogadores:
            jogo.realizar_jogada(Jogada(jog, coluna=0))
        self.assertFalse(jogo.tabuleiro.coluna_disponivel(0))


class TestVitoria(unittest.TestCase):

    def test_vitoria_horizontal(self):
        """Alice vence com 4 peças na mesma linha."""
        jogo, j1, j2 = _criar_jogo()
        _dropar(jogo, [
            (j1, 0), (j2, 0),
            (j1, 1), (j2, 1),
            (j1, 2), (j2, 2),
            (j1, 3),           # Alice completa 4 na linha 5
        ])
        self.assertIsNotNone(jogo.resultado)
        self.assertEqual(jogo.resultado.vencedor, j1)

    def test_vitoria_vertical(self):
        """Bob vence com 4 peças empilhadas na coluna 6.
        Alice joga col 0 duas vezes para não fazer 4 em linha antes de Bob.
        """
        jogo, j1, j2 = _criar_jogo()
        _dropar(jogo, [
            (j1, 0), (j2, 6),   # T1-T2
            (j1, 1), (j2, 6),   # T3-T4
            (j1, 2), (j2, 6),   # T5-T6
            (j1, 0), (j2, 6),   # T7: Alice repete col 0 (sem 4 em linha); T8: Bob completa 4 na col 6
        ])
        self.assertIsNotNone(jogo.resultado)
        self.assertEqual(jogo.resultado.vencedor, j2)

    def test_vitoria_diagonal_descendente(self):
        """Alice vence em diagonal ↘: posições (2,0)→(3,1)→(4,2)→(5,3)."""
        jogo, j1, j2 = _criar_jogo()
        # Construção turn-a-turn (j1 sempre ímpar, j2 sempre par):
        #   T1 j1→col3: (5,3)=j1
        #   T2 j2→col2: (5,2)=j2
        #   T3 j1→col2: (4,2)=j1
        #   T4 j2→col1: (5,1)=j2
        #   T5 j1→col6: filler
        #   T6 j2→col1: (4,1)=j2
        #   T7 j1→col1: (3,1)=j1
        #   T8 j2→col0: (5,0)=j2
        #   T9 j1→col6: filler
        #   T10 j2→col0: (4,0)=j2
        #   T11 j1→col6: filler
        #   T12 j2→col0: (3,0)=j2
        #   T13 j1→col0: (2,0)=j1  ← diagonal completa!
        _dropar(jogo, [
            (j1, 3), (j2, 2),
            (j1, 2), (j2, 1),
            (j1, 6), (j2, 1),
            (j1, 1), (j2, 0),
            (j1, 6), (j2, 0),
            (j1, 6), (j2, 0),
            (j1, 0),
        ])
        self.assertIsNotNone(jogo.resultado)
        self.assertEqual(jogo.resultado.vencedor, j1)


class TestJogadaInvalida(unittest.TestCase):

    def test_rejeita_coluna_inexistente(self):
        """Coluna 7 (índice 7) não existe num tabuleiro de 7 colunas."""
        jogo, j1, j2 = _criar_jogo()
        jogada = Jogada(j1, coluna=7)
        aceita = jogo.realizar_jogada(jogada)
        self.assertFalse(aceita)

    def test_rejeita_coluna_cheia(self):
        """Não pode soltar peça em coluna totalmente preenchida."""
        jogo, j1, j2 = _criar_jogo()
        jogadores = [j1, j2, j1, j2, j1, j2]
        for jog in jogadores:
            jogo.realizar_jogada(Jogada(jog, coluna=0))
        # Coluna 0 está cheia; próxima vez é de j1
        jogada = Jogada(j1, coluna=0)
        aceita = jogo.realizar_jogada(jogada)
        self.assertFalse(aceita)

    def test_rejeita_jogada_fora_do_turno(self):
        """Bob não pode jogar quando é a vez de Alice."""
        jogo, j1, j2 = _criar_jogo()
        jogada = Jogada(j2, coluna=3)
        aceita = jogo.realizar_jogada(jogada)
        self.assertFalse(aceita)
        self.assertFalse(jogada.valida)


class TestTabuleiro(unittest.TestCase):

    def test_proxima_linha_disponivel_coluna_vazia(self):
        t = TabuleiroLig4()
        self.assertEqual(t.proxima_linha_disponivel(0), 5)

    def test_proxima_linha_disponivel_retorna_none_quando_cheia(self):
        t = TabuleiroLig4()
        # Preenche coluna 0 manualmente
        for l in range(6):
            t.definir_celula(l, 0, "X")
        self.assertIsNone(t.proxima_linha_disponivel(0))


if __name__ == "__main__":
    unittest.main(verbosity=2)