"""
Módulo core.jogo
----------------
Define:
  - EstadoJogo   → enum com os estados possíveis de uma partida
  - ResultadoJogo → objeto de valor com o resultado final
  - JogoTabuleiro → classe abstrata que define o contrato e o loop
                    de qualquer jogo de tabuleiro

Qualquer jogo concreto herda de JogoTabuleiro e implementa os
métodos abstratos. O loop principal (jogar) não precisa ser alterado.

Relações:
  - JogoTabuleiro *usa* GerenciadorDeTurnos    (associação)
  - JogoTabuleiro *possui* Tabuleiro           (composição)
  - JogoTabuleiro *possui* ConjuntoDeRegras    (composição)
  - JogoTabuleiro *possui* List[Jogador]       (agregação)
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Optional

from .tabuleiro import Tabuleiro
from .jogador import Jogador
from .jogada import Jogada
from .turno import GerenciadorDeTurnos
from .regra import ConjuntoDeRegras


# ──────────────────────────────────────────────
#  Estado da partida
# ──────────────────────────────────────────────

class EstadoJogo(Enum):
    NAO_INICIADO = "não iniciado"
    EM_ANDAMENTO = "em andamento"
    FINALIZADO   = "finalizado"


# ──────────────────────────────────────────────
#  Resultado (value object)
# ──────────────────────────────────────────────

class ResultadoJogo:
    """
    Encapsula o resultado de uma partida encerrada.
    Exatamente um dos dois cenários deve ser verdadeiro:
      - vencedor is not None  → há um vencedor
      - empate == True        → jogo empatado
    """

    def __init__(
        self,
        vencedor: Optional[Jogador] = None,
        empate: bool = False,
        motivo: str = "",
    ):
        self._vencedor = vencedor
        self._empate = empate
        self._motivo = motivo

    @property
    def vencedor(self) -> Optional[Jogador]:
        return self._vencedor

    @property
    def empate(self) -> bool:
        return self._empate

    @property
    def motivo(self) -> str:
        return self._motivo

    def __str__(self) -> str:
        if self._empate:
            return f"Empate! {self._motivo}"
        if self._vencedor:
            return f"🏆  Vencedor: {self._vencedor}!  {self._motivo}"
        return "Resultado indefinido."

    def __repr__(self) -> str:
        return (
            f"ResultadoJogo(vencedor={self._vencedor!r}, "
            f"empate={self._empate}, motivo='{self._motivo}')"
        )


# ──────────────────────────────────────────────
#  Classe base abstrata
# ──────────────────────────────────────────────

class JogoTabuleiro(ABC):
    """
    Classe-base abstrata para jogos de tabuleiro.

    Define:
      • o estado e ciclo de vida de uma partida
      • o loop principal de jogo (Template Method)
      • os pontos de extensão obrigatórios (métodos abstratos)

    Subclasses implementam os métodos abstratos para
    customizar comportamento específico de cada jogo.
    """

    def __init__(self, nome: str, jogadores: List[Jogador]):
        self._nome = nome
        self._jogadores: List[Jogador] = jogadores
        self._tabuleiro: Optional[Tabuleiro] = None
        self._turno: Optional[GerenciadorDeTurnos] = None
        self._regras: Optional[ConjuntoDeRegras] = None
        self._estado: EstadoJogo = EstadoJogo.NAO_INICIADO
        self._resultado: Optional[ResultadoJogo] = None

    # ── Propriedades ──────────────────────────

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def estado(self) -> EstadoJogo:
        return self._estado

    @property
    def resultado(self) -> Optional[ResultadoJogo]:
        return self._resultado

    @property
    def tabuleiro(self) -> Optional[Tabuleiro]:
        return self._tabuleiro

    @property
    def turno(self) -> Optional[GerenciadorDeTurnos]:
        return self._turno

    @property
    def jogadores(self) -> List[Jogador]:
        return list(self._jogadores)

    # ── Ciclo de vida ─────────────────────────

    def iniciar(self) -> None:
        """Configura e inicia uma nova partida."""
        self._tabuleiro = self._criar_tabuleiro()
        self._turno = GerenciadorDeTurnos(self._jogadores)
        self._regras = self._configurar_regras()
        self.inicializar_tabuleiro()
        self._estado = EstadoJogo.EM_ANDAMENTO
        self._resultado = None
        self._exibir_cabecalho()

    def reiniciar(self) -> None:
        """Reinicia a partida do zero."""
        self._estado = EstadoJogo.NAO_INICIADO
        self.iniciar()

    def realizar_jogada(self, jogada: Jogada) -> bool:
        """
        Valida e aplica uma jogada.

        Retorna True se a jogada foi aceita, False caso contrário.
        Após aplicar, verifica se o jogo terminou.
        """
        if self._estado != EstadoJogo.EM_ANDAMENTO:
            print("  ⚠  O jogo não está em andamento.")
            return False

        valida, msg = self._regras.validar_tudo(jogada, self._tabuleiro, self._turno)
        if not valida:
            print(f"  ✗  Jogada inválida: {msg}")
            jogada.valida = False
            return False

        jogada.valida = True
        self.aplicar_jogada(jogada)

        resultado = self.verificar_fim_de_jogo()
        if resultado is not None:
            self._resultado = resultado
            self._estado = EstadoJogo.FINALIZADO
            self._tabuleiro.exibir()
            print(f"\n  {resultado}\n")
            self._atualizar_estatisticas(resultado)
        else:
            self._turno.avancar()

        return True

    def jogar(self) -> None:
        """
        Loop principal — Template Method.
        Não deve ser sobrescrito; customize os métodos abstratos.
        """
        self.iniciar()
        while self._estado == EstadoJogo.EM_ANDAMENTO:
            self._tabuleiro.exibir()
            print(f"  Turno {self._turno.numero_turno}  →  vez de {self._turno.jogador_atual}")
            jogada = self.obter_jogada_do_jogador()
            self.realizar_jogada(jogada)

    # ── Utilitários internos ──────────────────

    def _exibir_cabecalho(self) -> None:
        sep = "─" * 44
        print(f"\n  {sep}")
        print(f"  {self._nome:^44}")
        jogadores_str = "  ×  ".join(str(j) for j in self._jogadores)
        print(f"  {jogadores_str:^44}")
        print(f"  {sep}\n")

    def _atualizar_estatisticas(self, resultado: ResultadoJogo) -> None:
        if resultado.vencedor:
            resultado.vencedor.registrar_vitoria()
            for j in self._jogadores:
                if j is not resultado.vencedor:
                    j.registrar_derrota()
        elif resultado.empate:
            for j in self._jogadores:
                j.registrar_empate()

    # ── Pontos de extensão (obrigatórios) ─────

    @abstractmethod
    def _criar_tabuleiro(self) -> Tabuleiro:
        """Instancia e retorna o tabuleiro específico do jogo."""
        pass

    @abstractmethod
    def _configurar_regras(self) -> ConjuntoDeRegras:
        """Monta e retorna o conjunto de regras do jogo."""
        pass

    @abstractmethod
    def inicializar_tabuleiro(self) -> None:
        """Posiciona peças iniciais (se houver) e limpa o estado."""
        pass

    @abstractmethod
    def aplicar_jogada(self, jogada: Jogada) -> None:
        """Aplica a jogada validada ao tabuleiro."""
        pass

    @abstractmethod
    def verificar_fim_de_jogo(self) -> Optional[ResultadoJogo]:
        """
        Analisa o estado atual.
        Retorna ResultadoJogo se o jogo terminou, None caso contrário.
        """
        pass

    @abstractmethod
    def obter_jogada_do_jogador(self) -> Jogada:
        """Lê e retorna a próxima jogada do jogador atual."""
        pass

    # ── Repr ──────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"nome='{self._nome}', estado={self._estado.value})"
        )