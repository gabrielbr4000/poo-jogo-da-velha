from typing import List, Optional
 
from app.controllers.theme_manager import ThemeManager
from app.models.jogo import ResultadoJogo
from app.models.jogador import Jogador
from app.models.bot import Bot
from app.controllers.result_controller import ResultController
from app.jogodavelha.jogo import JogoDaVelha
 
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.core.text import LabelBase
from kivy.animation import Animation

LabelBase.register(
    name='FonteTitulo',
    fn_regular='assets/fonts/IrishGrover-Regular.ttf'
)


LabelBase.register(
    name='NotoEmoji',
    fn_regular='assets/fonts/NotoEmoji-Regular.ttf'
)

# Cores de destaque por contexto
_COR_VITORIA = {"dark": (0.56, 0.40, 1.00, 1), "light": (0.38, 0.20, 0.80, 1)}
_COR_EMPATE  = {"dark": (0.80, 0.80, 0.90, 1), "light": (0.40, 0.40, 0.55, 1)}
_COR_PLACAR  = {"dark": (0.22, 0.22, 0.30, 1), "light": (0.80, 0.80, 0.92, 1)}


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


class CartaoPlacar(BoxLayout):
    """
    Card que exibe nome, vitórias, derrotas e empates de um jogador.
    """

    def __init__(self, jogador: Jogador, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(6),
            size_hint=(None, None),
            size=(dp(160), dp(120)),
            **kwargs
        )
        self._jogador = jogador
        self._build()
        ThemeManager.instance().bind(on_theme_change=self._on_theme)
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _tm(self):
        return ThemeManager.instance()

    def _build(self):
        tm = self._tm()

        self._nome_lbl = Label(
            text=self._jogador.nome,
            font_size=sp(16),
            bold=True,
            color=tm.color("title"),
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle",
        )
        self._nome_lbl.bind(size=self._nome_lbl.setter("text_size"))
        self.add_widget(self._nome_lbl)

        stats = self._jogador.estatisticas()
        self._stats_lbl = Label(
            text=(
                f"[font=NotoEmoji]\U0001F3C6[/font]  {stats['vitorias']} vitória(s)\n"
                f"[font=NotoEmoji]\U0000274C[/font]  {stats['derrotas']} derrota(s)\n"
                f"[font=NotoEmoji]\U00002B50[/font]  {stats['empates']} empate(s)"
            ),
            markup=True,
            font_size=sp(13),
            color=tm.color("menu_label"),
            size_hint_y=None,
            height=dp(68),
            halign="center",
            valign="middle",
        )
        self._stats_lbl.bind(size=self._stats_lbl.setter("text_size"))
        self.add_widget(self._stats_lbl)

    def atualizar(self):
        stats = self._jogador.estatisticas()
        self._stats_lbl.text = (
            f"[font=NotoEmoji]\U0001F3C6[/font]  {stats['vitorias']} vitória(s)\n"
            f"[font=NotoEmoji]\U0000274C[/font]  {stats['derrotas']} derrota(s)\n"
            f"[font=NotoEmoji]\U00002B50[/font]  {stats['empates']} empate(s)"
        )

    def _redraw(self, *_):
        tm = self._tm()
        bg = _COR_PLACAR[tm.theme]
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 0.15)
            RoundedRectangle(
                pos=(self.x + dp(3), self.y - dp(3)),
                size=self.size,
                radius=[dp(16)]
            )
            Color(*bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])

    def _on_theme(self, *_):
        tm = self._tm()
        self._nome_lbl.color  = tm.color("title")
        self._stats_lbl.color = tm.color("menu_label")
        self._redraw()


class ResultScreen(Screen):
    """
    Tela exibida ao final de cada partida.

    Chame `exibir_resultado(resultado, jogadores)` antes de navegar
    para esta tela.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._jogadores: List[Jogador] = []
        self._cartas: List[CartaoPlacar] = []
        self._build_ui()
        ThemeManager.instance().bind(on_theme_change=self._on_theme)

    # ── Construção da UI ──────────────────────────────────────────

    def _tm(self):
        return ThemeManager.instance()

    def _build_ui(self):
        tm         = self._tm()
        self._root = FloatLayout()

        with self._root.canvas.before:
            self._bg_color_instr = Color(*tm.color("bg"))
            self._bg_rect        = Rectangle(pos=self._root.pos, size=self._root.size)
        self._root.bind(pos=self._update_bg, size=self._update_bg)

        center = BoxLayout(
            orientation="vertical",
            spacing=dp(22),
            size_hint=(None, None),
            width=dp(420),
            pos_hint={"center_x": 0.5, "center_y": 0.54},
        )
        center.bind(minimum_height=center.setter("height"))

        self._emoji_lbl = Label(
            text="",
            font_name="NotoEmoji",
            font_size=sp(56),
            color=tm.color("title"),
            size_hint_y=None,
            height=dp(74),
            halign="center",
        )
        center.add_widget(self._emoji_lbl)  


        # Título dinâmico (vencedor / empate)
        self._result_lbl = Label(
            text="",
            font_name="FonteTitulo",
            font_size=sp(36),
            color=tm.color("title"),
            bold=True,
            size_hint_y=None,
            height=dp(60),
            halign="center",
            valign="middle",
        )
        self._result_lbl.bind(size=self._result_lbl.setter("text_size"))
        center.add_widget(self._result_lbl)

        # Motivo 
        self._motivo_lbl = Label(
            text="",
            font_size=sp(15),
            color=tm.color("menu_label"),
            size_hint_y=None,
            height=dp(26),
            halign="center",
            valign="middle",
        )
        self._motivo_lbl.bind(size=self._motivo_lbl.setter("text_size"))
        center.add_widget(self._motivo_lbl)

        # ── Placares dos dois jogadores ────────────────────────────
        self._placar_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(24),
            size_hint=(None, None),
            size=(dp(360), dp(130)),
            pos_hint={"center_x": 0.5},
        )
        center.add_widget(self._placar_row)

        # ── Botões ─────────────────────────────────────────────────
        botoes_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint=(None, None),
            size=(dp(380), dp(52)),
            pos_hint={"center_x": 0.5},
        )
        self._btn_novo = RoundedButton(text="Jogar novamente")
        self._btn_novo.size = (dp(200), dp(48))
        self._btn_novo.bind(on_release=self._on_novo_jogo)
        self._btn_menu = RoundedButton(text="Menu")
        self._btn_menu.bind(on_release=self._on_menu)
        botoes_row.add_widget(self._btn_novo)
        botoes_row.add_widget(self._btn_menu)
        center.add_widget(botoes_row)

        self._root.add_widget(center)
        self.add_widget(self._root)

    # ── API pública ───────────────────────────────────────────────

    def exibir_resultado(
        self,
        resultado: ResultadoJogo,
        jogadores: List[Jogador],
    ):
        """
        Atualiza todos os widgets com o resultado da partida.
        Deve ser chamado ANTES de navegar para esta tela.
        """
        self._jogadores = jogadores
        tm              = self._tm()

        if resultado.empate:
            self._emoji_lbl.text   = "\U0001F91D"
            self._result_lbl.text  = "Empate!"                    
            self._result_lbl.color = _COR_EMPATE[tm.theme]        
        elif resultado.vencedor:
            self._emoji_lbl.text   = "\U0001F3C6"
            self._result_lbl.text  = f"{resultado.vencedor.nome} venceu!" 
            self._result_lbl.color = _COR_VITORIA[tm.theme]      
        else:
            self._emoji_lbl.text   = "\U00002753"
            self._result_lbl.text  = "Resultado indefinido"
            self._result_lbl.color = tm.color("title")

        self._motivo_lbl.text = resultado.motivo

        # Reconstruir cartões de placar
        self._placar_row.clear_widgets()
        self._cartas.clear()
        for jog in jogadores:
            carta = CartaoPlacar(jogador=jog)
            self._placar_row.add_widget(carta)
            self._cartas.append(carta)

        # Animação de entrada
        self._emoji_lbl.opacity  = 0
        self._result_lbl.opacity = 0
        anim = Animation(opacity=1, duration=0.35)
        anim.start(self._emoji_lbl)
        anim2 = Animation(opacity=0, duration=0.01) + Animation(opacity=1, duration=0.35, t="out_cubic")
        anim2.start(self._result_lbl)

    # ── Eventos de botões ─────────────────────────────────────────

    def _on_novo_jogo(self, *_):
        """Navega de volta para a tela de jogo e reinicia a partida."""
        if self.manager and "game" in self.manager.screen_names:
            tela = self.manager.get_screen("game")
            if len(self._jogadores) == 2:
                self._jogadores[0]._vida = self._jogadores[0]._vida_inicial  # reset vida
                self._jogadores[1]._vida = self._jogadores[1]._vida_inicial  # reset vida
                novo_jogo = JogoDaVelha(self._jogadores)
                novo_jogo.iniciar()
                self.manager.jogo = novo_jogo
                tela.iniciar_partida(novo_jogo)
            self.manager.current = "game"

    def _on_menu(self, *_):
        if self.manager and "main_menu" in self.manager.screen_names:
            self.manager.current = "main_menu"

    # ── Tema ──────────────────────────────────────────────────────

    def _on_theme(self, *_):
        tm = self._tm()
        self._bg_color_instr.rgba = tm.color("bg")
        self._motivo_lbl.color    = tm.color("menu_label")

    def _update_bg(self, instance, *_):
        self._bg_rect.pos  = instance.pos
        self._bg_rect.size = instance.size