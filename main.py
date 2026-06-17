import json
import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from app.controllers.theme_manager import ThemeManager
from app.models.jogador import Jogador

from app.views.main_menu import MainMenuScreen
from app.views.config import SettingsScreen
from app.views.config_game import ConfigGame
from app.views.game import GameScreen
from app.views.result import ResultScreen


def carregar_tema():
    if os.path.exists("config.json"):
        try:
            with open("config.json") as f:
                dados = json.load(f)
                ThemeManager.instance().set_theme(dados.get("tema", "dark"))
        except (json.JSONDecodeError, OSError):
            pass


class JogoDaVelhaApp(App):
    def build(self):
        carregar_tema()

        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="main_menu"))
        sm.add_widget(SettingsScreen(name="settings"))

        config_game = ConfigGame(name="config_game")
        sm.add_widget(config_game)

        game_screen = GameScreen(name="game")
        sm.add_widget(game_screen)

        result_screen = ResultScreen(name="result")
        sm.add_widget(result_screen)

        # O botão "Iniciar jogo" do menu principal já navega para "game"
        return sm


if __name__ == "__main__":
    JogoDaVelhaApp().run()