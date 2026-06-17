from app.controllers.theme_manager import ThemeManager
from app.controllers.game_controller import GameController
from app.models.jogador import Jogador
from app.jogodavelha.jogo import JogoDaVelha

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import SpinnerOption
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.metrics import dp, sp
from kivy.core.text import LabelBase
from kivy.animation import Animation
from kivy.clock import Clock
from app.models.bot import Bot
from typing import Optional

LabelBase.register(
    name='FonteTitulo',
    fn_regular='assets/fonts/IrishGrover-Regular.ttf'
)

LabelBase.register(
    name='coracoes',
    fn_regular='assets/fonts/NotoEmoji-Regular.ttf'
)

class EmojiOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'coracoes'
        self.font_size = '18sp'
        self.height = 48

# Paleta de símbolos e cores por jogador
_SIMBOLOS   = ["X", "O"]
_COR_X      = {"dark":  (0.56, 0.40, 1.00, 1),  "light": (0.38, 0.20, 0.80, 1)}
_COR_O      = {"dark":  (1.00, 0.55, 0.35, 1),  "light": (0.90, 0.35, 0.10, 1)}
_COR_VAZIO  = {"dark":  (0.18, 0.18, 0.24, 1),  "light": (0.88, 0.88, 0.95, 1)}


class CelulaButton(Button):
    """Célula do tabuleiro 3×3."""
    def __init__(self, linha: int, coluna: int, **kwargs):
        super().__init__(**kwargs)
        self.linha   = linha
        self.coluna  = coluna
        self.simbolo = None          # None | "X" | "O"

        self.background_color = (0, 0, 0, 0)
        self.font_name        = "FonteTitulo"
        self.font_size        = sp(42)
        self.bold             = True
        self.size_hint        = (None, None)
        self.size             = (dp(110), dp(110))
        self.text             = ""

        ThemeManager.instance().bind(on_theme_change=self._on_theme)
        self.bind(pos=self._redraw, size=self._redraw, state=self._redraw)
        self._redraw()

    def _tm(self):
        return ThemeManager.instance()

    def _get_fill(self):
        tm      = self._tm()
        theme   = tm.theme
        if self.simbolo == "X":
            return _COR_X[theme]
        if self.simbolo == "O":
            return _COR_O[theme]
        # vazia
        r, g, b, a = _COR_VAZIO[theme]
        if self.state == "down" and self.simbolo is None:
            return (r * 1.25, g * 1.25, b * 1.25, a)
        return (r, g, b, a)

    def _redraw(self, *_):
        fill    = self._get_fill()
        self.canvas.before.clear()
        with self.canvas.before:
            # sombra
            Color(0, 0, 0, 0.18)
            RoundedRectangle(
                pos=(self.x + dp(3), self.y - dp(3)),
                size=self.size,
                radius=[dp(18)]
            )
            # fundo
            Color(*fill)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(18)]
            )

    def marcar(self, simbolo: str):
        """Exibe o símbolo na célula e desabilita interação."""
        self.simbolo  = simbolo
        self.text     = simbolo
        self.disabled = True
        self._update_text_color()
        # animação de "pop"
        self.opacity = 0
        anim = Animation(opacity=1, duration=0.18)
        anim.start(self)
        self._redraw()

    def _on_theme(self, *_):
        self._update_text_color()
        self._redraw()

    def _update_text_color(self):
        tm    = self._tm()
        theme = tm.theme
        if self.simbolo == "X":
            # texto claro sobre fundo roxo
            self.color = (1, 1, 1, 1)
        elif self.simbolo == "O":
            self.color = (1, 1, 1, 1)
        else:
            # célula vazia — sem texto
            self.color = (0, 0, 0, 0)


class RoundedButton(Button):
    """Botão padrão do projeto."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.font_size        = sp(16)
        self.size_hint        = (None, None)
        self.size             = (dp(180), dp(48))
        self._apply_theme()
        ThemeManager.instance().bind(on_theme_change=self._on_theme)
        self.bind(pos=self._redraw, size=self._redraw, state=self._redraw)

    def _tm(self):
        return ThemeManager.instance()

    def _apply_theme(self):
        self.color = self._tm().color("btn_text")
        self._redraw()

    def _on_theme(self, *_):
        self._apply_theme()

    def _redraw(self, *_):
        tm = self._tm()
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*tm.color("btn_shadow"))
            RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size,
                radius=[dp(14)]
            )
            r, g, b, a = tm.color("btn_bg")
            if self.state == "down":
                f = tm.value("btn_pressed")
                r, g, b = r * f, g * f, b * f
            Color(r, g, b, a)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])


class GameScreen(Screen):
    """
    Tela principal de jogo.

    Espera receber (via `iniciar_partida`) dois objetos Jogador,
    monta o JogoDaVelha e gerencia cliques nas células.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._jogo: Optional[JogoDaVelha] = None
        self._celulas: list[list[CelulaButton]] = []
        self.controller = None  # inicializado aqui para evitar AttributeError antes de iniciar_partida()
        self._build_ui()
        ThemeManager.instance().bind(on_theme_change=self._on_theme)

    def on_enter(self, *args):
        """Chamado pelo ScreenManager ao navegar para esta tela.
        Pega o jogo salvo pelo ConfigGame em manager.jogo e inicializa a partida.
        """
        jogo = getattr(self.manager, "jogo", None)
        if jogo is not None:
            self.iniciar_partida(jogo)

    # ── Construção da UI ──────────────────────────────────────────

    def _tm(self):
        return ThemeManager.instance()

    def marcar_celula(self, linha, coluna, simbolo):

        self._celulas[linha][coluna].marcar(
            simbolo
        )

    def _build_ui(self):
        tm          = self._tm()
        self._root  = FloatLayout()

        with self._root.canvas.before:
            self._bg_color_instr = Color(*tm.color("bg"))
            self._bg_rect        = Rectangle(pos=self._root.pos, size=self._root.size)
        self._root.bind(pos=self._update_bg, size=self._update_bg)

        # ── Coluna central ────────────────────────────────────────
        center = BoxLayout(
            orientation="vertical",
            spacing=dp(18),
            size_hint=(None, None),
            width=dp(420),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
        )
        center.bind(minimum_height=center.setter("height"))

        vida_row = BoxLayout(
    orientation="horizontal",
    size_hint_y=None,
    height=dp(30),
    )
        self._vida_j1 = Label(
            text='',
            markup = True,
            font_size=sp(18),
            halign='center',
            valign='middle',
        )
        self._vida_j2 = Label(
            text='',
            markup = True,
            font_size=sp(18),
            halign='center',
            valign='middle',
        )
        self._vida_j1.bind(size=self._vida_j1.setter('text_size'))
        self._vida_j2.bind(size=self._vida_j2.setter('text_size'))
        vida_row.add_widget(self._vida_j1)
        vida_row.add_widget(self._vida_j2)
        center.add_widget(vida_row)

        # Título
        self._title = Label(
            text="Jogo da Velha",
            font_name="FonteTitulo",
            font_size=sp(42),
            color=tm.color("title"),
            bold=True,
            size_hint_y=None,
            height=dp(70),
            halign="center",
            valign="middle",
        )
        self._title.bind(size=self._title.setter("text_size"))
        center.add_widget(self._title)

        # Label de status (turno / resultado)
        self._status_label = Label(
            text="",
            font_size=sp(18),
            color=tm.color("menu_label"),
            size_hint_y=None,
            height=dp(34),
            halign="center",
            valign="middle",
        )
        self._status_label.bind(size=self._status_label.setter("text_size"))
        center.add_widget(self._status_label)

        # Grade do tabuleiro
        self._grid = GridLayout(
            cols=3,
            spacing=dp(10),
            size_hint=(None, None),
            size=(dp(350), dp(350)),
            pos_hint={"center_x": 0.5},
        )
        self._celulas = []
        for linha in range(3):
            linha_cells = []
            for coluna in range(3):
                cell = CelulaButton(linha=linha, coluna=coluna)
                cell.bind(on_release=self._on_celula_press)
                self._grid.add_widget(cell)
                linha_cells.append(cell)
            self._celulas.append(linha_cells)
        center.add_widget(self._grid)

        # Botões inferiores
        botoes_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint=(None, None),
            size=(dp(380), dp(52)),
            pos_hint={"center_x": 0.5},
        )
        self._btn_reiniciar = RoundedButton(text="Reiniciar")
        self._btn_reiniciar.bind(on_release=self._on_reiniciar)
        self._btn_menu = RoundedButton(text="Menu")
        self._btn_menu.bind(on_release=self._on_menu)
        botoes_row.add_widget(self._btn_reiniciar)
        botoes_row.add_widget(self._btn_menu)
        center.add_widget(botoes_row)

        self._root.add_widget(center)
        self.add_widget(self._root)

    # ── Inicialização de partida ──────────────────────────────────

    def iniciar_partida(self, jogo):
        self._jogo = jogo
        self.controller = GameController(
            jogo=self._jogo,
            view=self
        )

        self._jogador1 = jogo.jogadores[0]
        self._jogador2 = jogo.jogadores[1]

        self._limpar_tabuleiro()
        self.atualizar_status()
        self.atualizar_vidas()

    
    def atualizar_vidas(self):
        """Atualiza os labels de vida de ambos os jogadores."""
        if not hasattr(self, '_jogador1'):
            return
        coracoes1 = "♥" * self._jogador1.vida
        coracoes2 = "♥" * self._jogador2.vida
        self._vida_j1.text = f"{self._jogador1.nome}: [font=coracoes]{coracoes1}[/font]"
        self._vida_j2.text = f"{self._jogador2.nome}: [font=coracoes]{coracoes2}[/font]"

    def _limpar_tabuleiro(self):
        for linha in self._celulas:
            for cell in linha:
                cell.simbolo  = None
                cell.text     = ""
                cell.disabled = False
                cell.opacity  = 1
                cell._redraw()

    def atualizar_status(self):
        """Atualiza o label de turno com o jogador da vez."""
        if self._jogo is None or self._jogo.turno is None:
            self._status_label.text = ""
            return
        from app.models.jogo import EstadoJogo
        if self._jogo.estado == EstadoJogo.FINALIZADO:
            resultado = self._jogo.resultado
            if resultado.empate:
                self._status_label.text = "Empate!"
            else:
                self._status_label.text = f"Vencedor: {resultado.vencedor.nome}!"
        else:
            jogador = self._jogo.turno.jogador_atual
            simbolo = self._jogo.simbolo_do_jogador(jogador)
            self._status_label.text = f"Vez de {jogador.nome} ({simbolo})"

    # ── Eventos de UI ─────────────────────────────────────────────

    def _on_celula_press(self, cell):

        if self.controller is None:
            return

        self.controller.realizar_jogada(
            cell.linha,
            cell.coluna
        )


    def _on_reiniciar(self, *_):

        if self.controller is None:
            return

        self.controller.reiniciar()

    def _on_menu(self, *_):
        if self.manager and "main_menu" in self.manager.screen_names:
            self.manager.current = "main_menu"

    # ── Tema ──────────────────────────────────────────────────────

    def _on_theme(self, *_):
        tm = self._tm()
        self._bg_color_instr.rgba = tm.color("bg")
        self._title.color         = tm.color("title")
        self._status_label.color  = tm.color("menu_label")

    def _update_bg(self, instance, *_):
        self._bg_rect.pos  = instance.pos
        self._bg_rect.size = instance.size
    
    def finalizar_jogo(self, resultado):

        if self.manager is None:
            return

        tela = self.manager.get_screen("result")

        tela.exibir_resultado(
            resultado,
            [self._jogador1, self._jogador2]
        )

        self.manager.current = "result"