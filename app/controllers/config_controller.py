from app.models.jogador import Jogador
from app.models.bot import Bot
from app.jogodavelha.jogo import JogoDaVelha


class ConfigController:

    def criar_jogo(
        self,
        nome1,
        vida1,
        usar_bot,
        dificuldade,
        nome2=None,
        vida2=None
    ):
        jogador1 = Jogador(nome1, 1, vida1)

        if usar_bot:
            # Bot recebe a vida pelo construtor de Jogador via super().__init__,
            # sem precisar acessar atributos privados diretamente.
            jogador2 = Bot(dificuldade=dificuldade, vida=vida1)
        else:
            jogador2 = Jogador(nome2, 2, vida2)

        # JogoDaVelha espera List[Jogador] — passa como lista, não como args posicionais.
        jogo = JogoDaVelha([jogador1, jogador2])
        jogo.iniciar()  # popula _pecas_por_jogador e prepara o tabuleiro
        return jogo