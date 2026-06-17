from kivy.clock import Clock
from app.models.jogada import Jogada
from app.models.jogo import EstadoJogo
from app.models.bot import Bot


class GameController:

    def __init__(self, jogo, view):

        self.jogo = jogo
        self.view = view

    def realizar_jogada(
        self,
        linha,
        coluna
    ):

        turno = self.jogo.turno
        jogador = turno.jogador_atual

        if isinstance(jogador, Bot):
            return

        jogada = Jogada(
            jogador,
            linha=linha,
            coluna=coluna
        )

        if not self.jogo.realizar_jogada(jogada):
            return

        simbolo = self.jogo.simbolo_do_jogador(jogador)

        self.view.marcar_celula(
            linha,
            coluna,
            simbolo
        )

        self._pos_jogada()
    def _pos_jogada(self):

        if self.jogo.estado == EstadoJogo.FINALIZADO:

            Clock.schedule_once(
                lambda dt:
                self._finalizar(),
                0.5
            )

            return

        self.view.atualizar_status()

        jogador = self.jogo.turno.jogador_atual

        if isinstance(jogador, Bot):
            Clock.schedule_once(
                self.jogada_bot,
                0.6
            )

    def jogada_bot(self, *_):

        turno = self.jogo.turno
        bot = turno.jogador_atual

        if not isinstance(bot, Bot):
            return

        pecas = self.jogo._pecas_por_jogador
        simb_bot = pecas[bot.id].simbolo
        simb_adversario = "X" if simb_bot == "O" else "O"

        tabuleiro = [[None]*3 for _ in range(3)]

        for l in range(3):
            for c in range(3):
                tabuleiro[l][c] = (
                    self.view._celulas[l][c].simbolo
                )

        linha, coluna = bot.escolher_jogada(
            tabuleiro,
            simb_bot,
            simb_adversario
        )

        jogada = Jogada(
            bot,
            linha=linha,
            coluna=coluna
        )

        self.jogo.realizar_jogada(jogada)

        self.view.marcar_celula(
            linha,
            coluna,
            simb_bot
        )

        self._pos_jogada()
    
    def _finalizar(self):

        resultado = self.jogo.resultado

        jogador1 = self.view._jogador1
        jogador2 = self.view._jogador2

        if resultado.vencedor == jogador1:
            jogador2.perder_vida()

        elif resultado.vencedor == jogador2:
            jogador1.perder_vida()

        self.view.atualizar_vidas()

        if jogador1.vida == 0 or jogador2.vida == 0:
            self.view.finalizar_jogo(resultado)
        else:
            self.jogo.reiniciar()
            self.view._limpar_tabuleiro()
            self.view.atualizar_status()

    def reiniciar(self):

        self.jogo.reiniciar()

        self.view._limpar_tabuleiro()
        self.view.atualizar_status()