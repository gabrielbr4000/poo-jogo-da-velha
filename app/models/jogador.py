class Jogador:
    def __init__(self, nome: str, id_jogador: int, vida: int = 3):
        self._nome = nome
        self._id = id_jogador
        self._vida = vida
        self._vitorias = 0
        self._derrotas = 0
        self._empates = 0
        self._vida_inicial = vida

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def id(self) -> int:
        return self._id

    @property
    def vida(self) -> int:
        return self._vida

    @property
    def vitorias(self) -> int:
        return self._vitorias

    @property
    def derrotas(self) -> int:
        return self._derrotas

    @property
    def empates(self) -> int:
        return self._empates

    def perder_vida(self) -> None:
        if self._vida > 0:
            self._vida -= 1

    def registrar_vitoria(self) -> None:
        self._vitorias += 1

    def registrar_derrota(self) -> None:
        self._derrotas += 1

    def registrar_empate(self) -> None:
        self._empates += 1

    def estatisticas(self) -> dict:
        return {
            "vitorias": self._vitorias,
            "derrotas": self._derrotas,
            "empates":  self._empates,
        }

    def __str__(self) -> str:
        return self._nome

    def __repr__(self) -> str:
        return f"Jogador(nome='{self._nome}', id={self._id})"
    # simbolo_do_jogador removido daqui — pertencia a JogoDaVelha, não a Jogador.
    # O método correto está em app/jogodavelha/jogo.py.