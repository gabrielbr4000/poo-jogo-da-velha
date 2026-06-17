"""
Jogo da Velha — implementação concreta de JogoTabuleiro.

Herda toda a estrutura do núcleo e implementa apenas
o que é específico deste jogo:
  - tabuleiro 3×3
  - peças X e O
  - verificação de três em linha
"""
from __future__ import annotations
from typing import List, Optional

from app.models.jogo import JogoTabuleiro, ResultadoJogo
from app.models.tabuleiro import Tabuleiro
from app.models.jogador import Jogador
from app.models.jogada import Jogada
from app.models.regra import ConjuntoDeRegras

from .tabuleiro import TabuleiroVelha
from .peca import PecaVelha
from .regras import criar_regras_velha

# Símbolos padrão atribuídos na ordem de entrada dos jogadores
_SIMBOLOS = ["X", "O"]


class JogoDaVelha(JogoTabuleiro):
    """
    Implementação do Jogo da Velha para 2 jogadores.

    Polimorfismo em ação: sobrescreve todos os métodos abstratos
    de JogoTabuleiro sem alterar o loop principal herdado.
    """

    def __init__(self, jogadores: List[Jogador]):
        if len(jogadores) != 2:
            raise ValueError("O Jogo da Velha requer exatamente 2 jogadores.")
        super().__init__("Jogo da Velha", jogadores)
        self._pecas_por_jogador: dict[int, PecaVelha] = {}

    # ── Implementações obrigatórias ───────────

    def _criar_tabuleiro(self) -> Tabuleiro:
        return TabuleiroVelha()

    def _configurar_regras(self) -> ConjuntoDeRegras:
        return criar_regras_velha()

    def inicializar_tabuleiro(self) -> None:
        self._tabuleiro.limpar()
        self._pecas_por_jogador = {
            jogador.id: PecaVelha(_SIMBOLOS[i], jogador)
            for i, jogador in enumerate(self._jogadores)
        }

    def aplicar_jogada(self, jogada: Jogada) -> None:
        linha = jogada.dados["linha"]
        coluna = jogada.dados["coluna"]
        peca = self._pecas_por_jogador[jogada.jogador.id]
        self._tabuleiro.definir_celula(linha, coluna, peca)

    def verificar_fim_de_jogo(self) -> Optional[ResultadoJogo]:
        grade = self._tabuleiro.grade

        # Sequências a verificar: 3 linhas + 3 colunas + 2 diagonais
        sequencias = []
        for linha in grade:
            sequencias.append(lista := list(linha))
        for c in range(3):
            sequencias.append([grade[l][c] for l in range(3)])
        sequencias.append([grade[i][i] for i in range(3)])
        sequencias.append([grade[i][2 - i] for i in range(3)])

        for seq in sequencias:
            if (
                seq[0] is not None
                and all(p is not None and p.simbolo == seq[0].simbolo for p in seq)
            ):
                return ResultadoJogo(vencedor=seq[0].dono, motivo="Três em linha!")

        if self._tabuleiro.esta_cheio():
            return ResultadoJogo(empate=True, motivo="Tabuleiro cheio, sem vencedor.")

        return None

    def obter_jogada_do_jogador(self) -> Jogada:
        jogador = self._turno.jogador_atual
        simbolo = self._pecas_por_jogador[jogador.id].simbolo
        prompt = f"  {jogador} ({simbolo}) › linha coluna (ex: 2 3): "
        while True:
            try:
                partes = input(prompt).strip().split()
                if len(partes) != 2:
                    print("  Digite dois números separados por espaço.")
                    continue
                linha, coluna = int(partes[0]) - 1, int(partes[1]) - 1
                return Jogada(jogador, linha=linha, coluna=coluna)
            except ValueError:
                print("  Entrada inválida. Use números inteiros.")

    def simbolo_do_jogador(self, jogador: Jogador) -> str:
        """Retorna o símbolo ('X' ou 'O') associado ao jogador nesta partida.

        Método público que expõe de forma controlada a relação jogador→peça,
        evitando que controllers acessem _pecas_por_jogador diretamente.
        Deve ser chamado após iniciar() para que o mapeamento exista.
        """
        return self._pecas_por_jogador[jogador.id].simbolo