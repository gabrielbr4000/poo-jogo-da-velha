"""
Módulo core.regra
-----------------
Define o contrato de validação de jogadas via:

  - Regra          → classe abstrata para uma regra isolada
  - ConjuntoDeRegras → agrega múltiplas regras (padrão Chain-of-Responsibility)

Cada jogo configura seu próprio conjunto de regras na inicialização.
"""
from abc import ABC, abstractmethod


class Regra(ABC):
    """
    Contrato para uma regra de validação de jogada.

    Retorna uma tupla (valida: bool, mensagem: str).
    Quando inválida, a mensagem descreve o motivo.
    """

    @abstractmethod
    def validar(self, jogada, tabuleiro, turno) -> tuple[bool, str]:
        pass


class ConjuntoDeRegras:
    """
    Agrega várias regras e as executa em sequência.
    A primeira regra que falhar interrompe a validação.

    Suporta interface fluente para encadeamento:
        ConjuntoDeRegras()
            .adicionar_regra(RegraA())
            .adicionar_regra(RegraB())
    """

    def __init__(self):
        self._regras: list[Regra] = []

    def adicionar_regra(self, regra: Regra) -> "ConjuntoDeRegras":
        if not isinstance(regra, Regra):
            raise TypeError(f"Esperado uma instância de Regra, recebeu {type(regra)}.")
        self._regras.append(regra)
        return self  # interface fluente

    def validar_tudo(self, jogada, tabuleiro, turno) -> tuple[bool, str]:
        """Executa todas as regras em ordem. Retorna na primeira falha."""
        for regra in self._regras:
            valida, msg = regra.validar(jogada, tabuleiro, turno)
            if not valida:
                return False, msg
        return True, "Jogada válida."

    def __repr__(self) -> str:
        nomes = [r.__class__.__name__ for r in self._regras]
        return f"ConjuntoDeRegras({nomes})"