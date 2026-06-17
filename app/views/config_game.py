from app.controllers.theme_manager import ThemeManager
from app.controllers.config_controller import ConfigController
from app.models.bot import Bot
from app.models.jogador import Jogador
 
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.core.text import LabelBase
from app.views.game import _COR_X, _COR_O

LabelBase.register(
    name='FonteTitulo',
    fn_regular='assets/fonts/IrishGrover-Regular.ttf'
)
LabelBase.register(
    name='Coracoes',
    fn_regular='assets/fonts/NotoEmoji-Regular.ttf'
)


class EmojiOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Coracoes'
        self.font_size = '18sp'
        self.height = 48


class RoundedButton(Button):
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


class ToggleBotButton(ToggleButton):
    """Botão toggle para ativar/desativar o bot."""

    def __init__(self, **kwargs):
        kwargs.setdefault('group', str(id(self)))
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.font_size        = sp(16)
        self.size_hint        = (None, None)
        self.size             = (dp(180), dp(48))
        self._sync_text()
        ThemeManager.instance().bind(on_theme_change=self._on_theme)
        self.bind(pos=self._redraw, size=self._redraw, state=self._on_state)

    def _tm(self):
        return ThemeManager.instance()

    def _sync_text(self):
        if self.state == "down":
            self.text = "Bot: Ligado"
        else:
            self.text = "Bot: Desligado"

    def _on_state(self, *_):
        self._sync_text()
        self._redraw()

    def _on_theme(self, *_):
        self._redraw()

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
            else:
                Color(r * 0.8, g * 0.8, b * 0.85, a)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])

        self.color = (1, 1, 1, 1)  


class ConfigGame(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.controller = ConfigController()

        self._build_ui()
        ThemeManager.instance().bind(
            on_theme_change=self._on_theme
        )

    def _tm(self):
        return ThemeManager.instance()

    def _build_ui(self):
        tm    = self._tm()
        theme = tm.theme
        self._root = FloatLayout()

        with self._root.canvas.before:
            self._bg_color_instr = Color(*tm.color("bg"))
            self._bg_rect        = Rectangle(pos=self._root.pos, size=self._root.size)
        self._root.bind(pos=self._update_bg, size=self._update_bg)

        center_col = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            size_hint=(None, None),
            width=dp(320),
            pos_hint={"center_x": 0.5, "center_y": 0.55}
        )
        center_col.bind(minimum_height=center_col.setter("height"))

        # Título
        self._title = Label(
            text="Iniciar Partida",
            font_name="FonteTitulo",
            font_size=sp(48),
            color=tm.color("title"),
            bold=True,
            size_hint_y=None,
            height=dp(80),
            halign="center",
            valign="middle"
        )
        self._title.bind(size=self._title.setter("text_size"))
        center_col.add_widget(self._title)

        # ── Jogador 1 ─────────────────────────────────────────────
        lbl1 = Label(
            text="[X] Jogador 1",
            font_size=sp(16),
            color=_COR_X[theme],
            size_hint_y=None,
            height=dp(20),
            halign="left",
            valign="middle"
        )
        lbl1.bind(size=lbl1.setter("text_size"))
        center_col.add_widget(lbl1)

        self.jogador1 = TextInput(
            text="Jogador1",
            hint_text="Nome do Jogador 1",
            multiline=False,
            size_hint_y=None,
            height=dp(36)
        )
        center_col.add_widget(self.jogador1)

        lbl_vida1 = Label(
            text="Vidas do Jogador 1",
            font_size=sp(13),
            color=tm.color("menu_label"),
            size_hint_y=None,
            height=dp(18),
            halign="left",
            valign="middle"
        )
        lbl_vida1.bind(size=lbl_vida1.setter("text_size"))
        center_col.add_widget(lbl_vida1)

        self.jogador1_vida = Spinner(
            text='♥♥♥',
            values=['♥♥♥', '♥♥♥♥', '♥♥♥♥♥'],
            font_name="Coracoes",
            option_cls=EmojiOption,
            size_hint=(1, None),
            height=dp(36)
        )
        center_col.add_widget(self.jogador1_vida)

        # ── Bot toggle ────────────────────────────────────────────
        center_col.add_widget(Label(size_hint_y=None, height=dp(6)))

        self._bot_toggle = ToggleBotButton()
        self._bot_toggle.pos_hint = {"center_x": 0.5}
        self._bot_toggle.bind(on_release=self._on_bot_toggle)
        center_col.add_widget(self._bot_toggle)

        # Spinner de dificuldade (oculto por padrão)
        self._dificuldade_spinner = Spinner(
            text=Bot.MEDIO,
            values=[Bot.FACIL, Bot.MEDIO, Bot.DIFICIL],
            size_hint=(1, None),
            height=dp(36),
            opacity=0,
            disabled=True,
        )
        center_col.add_widget(self._dificuldade_spinner)

        # ── Jogador 2 (oculto quando bot ativo) ───────────────────
        self._j2_widgets = []  

        lbl2 = Label(
            text="[O] Jogador 2",
            font_size=sp(16),
            color=_COR_O[theme],
            size_hint_y=None,
            height=dp(20),
            halign="left",
            valign="middle"
        )
        lbl2.bind(size=lbl2.setter("text_size"))
        center_col.add_widget(lbl2)
        self._j2_widgets.append(lbl2)

        self.jogador2 = TextInput(
            text="Jogador2",
            hint_text="Nome do Jogador 2",
            multiline=False,
            size_hint_y=None,
            height=dp(36)
        )
        center_col.add_widget(self.jogador2)
        self._j2_widgets.append(self.jogador2)

        lbl_vida2 = Label(
            text="Vidas do Jogador 2",
            font_size=sp(13),
            color=tm.color("menu_label"),
            size_hint_y=None,
            height=dp(18),
            halign="left",
            valign="middle"
        )
        lbl_vida2.bind(size=lbl_vida2.setter("text_size"))
        center_col.add_widget(lbl_vida2)
        self._j2_widgets.append(lbl_vida2)

        self.jogador2_vida = Spinner(
            text='♥♥♥',
            values=['♥♥♥', '♥♥♥♥', '♥♥♥♥♥'],
            font_name="Coracoes",
            option_cls=EmojiOption,
            size_hint=(1, None),
            height=dp(36)
        )
        center_col.add_widget(self.jogador2_vida)
        self._j2_widgets.append(self.jogador2_vida)

        center_col.add_widget(Label(size_hint_y=None, height=dp(6)))

        # ── Botões ────────────────────────────────────────────────
        for text, callback in [
            ("Iniciar", self.on_start),
            ("Voltar",  self.on_menu)
        ]:
            btn = RoundedButton(text=text)
            btn.pos_hint = {"center_x": 0.5}
            btn.bind(on_release=callback)
            center_col.add_widget(btn)

        self._root.add_widget(center_col)
        self.add_widget(self._root)

    # ── Bot toggle ────────────────────────────────────────────────

    def _on_bot_toggle(self, *_):
        bot_ativo = self._bot_toggle.state == "down"

        # mostra/oculta spinner de dificuldade
        self._dificuldade_spinner.opacity  = 1 if bot_ativo else 0
        self._dificuldade_spinner.disabled = not bot_ativo

        # mostra/oculta widgets do jogador 2
        for w in self._j2_widgets:
            w.opacity  = 0 if bot_ativo else 1
            w.disabled = bot_ativo

    # ── Tema ──────────────────────────────────────────────────────

    def _on_theme(self, *_):
        tm = self._tm()
        self._bg_color_instr.rgba = tm.color("bg")
        self._title.color         = tm.color("title")

    def _update_bg(self, instance, *_):
        self._bg_rect.pos  = instance.pos
        self._bg_rect.size = instance.size

    # ── Iniciar ───────────────────────────────────────────────────

    def on_start(self, *_):

        if not (self.manager and "game" in self.manager.screen_names):
            return

        jogo = self.controller.criar_jogo(
            nome1=self.jogador1.text,
            vida1=len(self.jogador1_vida.text),

            usar_bot=self._bot_toggle.state == "down",

            dificuldade=self._dificuldade_spinner.text,

            nome2=self.jogador2.text,
            vida2=len(self.jogador2_vida.text)
        )

        self.manager.jogo = jogo
        self.manager.current = "game"

    def on_menu(self, *_):
        if self.manager and "main_menu" in self.manager.screen_names:
            self.manager.current = "main_menu"