"""
conftest.py — configuração global do pytest.

Adiciona a pasta src/ ao sys.path para que os imports
absolutos (ex: from core.tabuleiro import Tabuleiro)
funcionem corretamente ao rodar pytest da raiz do projeto.
"""
import sys
import os

# Caminho absoluto para a pasta src/ (irmã deste arquivo)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))