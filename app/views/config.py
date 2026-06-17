import os

from app.controllers.theme_manager import ThemeManager

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.event import EventDispatcher
from kivy.properties import OptionProperty
from kivy.core.text import LabelBase

# Remove import os, _BASE e os.path.join — deixa simples:
LabelBase.register(name='FonteTitulo', fn_regular='assets/fonts/IrishGrover-Regular.ttf')
LabelBase.register(name='FonteCorpo',  fn_regular='assets/fonts/NotoSans-Regular.ttf')
LabelBase.register(name='FonteEmoji',  fn_regular='assets/fonts/NotoEmoji-Regular.ttf')

class ToggleRoundedButton(ToggleButton):
    def __init__(self, text_light="Claro", text_dark="Escuro", 
                 emoji_light="\U0001F31C", emoji_dark="\U0001F31E", mode="tema", **kwargs):      
        object.__setattr__(self, '_text_light', text_light)
        object.__setattr__(self, '_text_dark',  text_dark)
        object.__setattr__(self, '_mode', mode)
        object.__setattr__(self, '_emoji_light', emoji_light)
        object.__setattr__(self, '_emoji_dark', emoji_dark)
        super().__init__(**kwargs)
        self.background_color   = (0, 0, 0, 0)
        self.markup = True
        self.font_name          = 'FonteCorpo'
        self.font_size          = sp(16)
        self.size_hint          = (None, None)
        self.size               = (dp(180), dp(48))
        self._sync_state()
        ThemeManager.instance().bind(on_theme_change=self._on_theme)
        self.bind(pos=self._redraw, size=self._redraw, state=self._on_state_change)

    def _tm(self):
        return ThemeManager.instance()

    def _redraw(self, *_):
        tm = ThemeManager.instance()
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
                Color(*tm.color("btn_text"))
            else:
                Color(r*.8, g*.8, b*.85, a)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(22)])
    
    def _sync_state(self):
        if self._mode == "tema":
            if ThemeManager.instance().theme == "light":
                self.state = "down"
                self.text  = f"[font=FonteEmoji]{self._emoji_light}[/font]  {self._text_light}"
            else:
                self.state = "normal"
                self.text  = f"[font=FonteEmoji]{self._emoji_dark}[/font]  {self._text_dark}"
    
    def _apply_theme(self):
        tm         = ThemeManager.instance() 
        self.text  = tm.value("toggle_icon")
        self.color = tm.color("toggle_hint")

    def _on_theme(self, *_):
        self._sync_state()
        self._redraw()

    def _on_state_change(self, instance, value):
        if self._mode == "toggle":
            if value == "down":
                self.text = f"[font=FonteEmoji]{self._emoji_light}[/font]  {self._text_light}"
            else:
                self.text = f"[font=FonteEmoji]{self._emoji_dark}[/font]  {self._text_dark}"

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color   = (0, 0, 0, 0)
        self.font_name          = 'FonteCorpo'
        self.font_size          = sp(16)
        self.size_hint          = (None, None)
        self.size               = (dp(180), dp(48))
        self._apply_theme()
        ThemeManager.instance().bind(on_theme_change=self._on_theme)
        self.bind(pos=self._redraw, size=self._redraw, state=self._redraw)
    
    def _tm(self):
        return ThemeManager.instance()

    def _apply_theme(self):
        tm = self._tm()
        self.color = tm.color("btn_text")
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
            RoundedRectangle(
                pos=self.pos, 
                size=self.size, 
                radius=[dp(14)]
            )

            
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()
        ThemeManager.instance().bind(on_theme_change=self._on_theme)
    
    def _tm(self):
        return ThemeManager.instance()

    def _build_ui(self):
        tm          = self._tm()
        self._root  = FloatLayout()

        with self._root.canvas.before:
            self._bg_color_instr = Color(*tm.color("bg"))
            self._bg_rect        = Rectangle(pos=self._root.pos, size=self._root.size)
        self._root.bind(pos=self._update_bg, size=self._update_bg)
        
        center_col = BoxLayout(
            orientation="vertical",
            spacing=dp(20),
            size_hint=(None, None),
            width=dp(420),
            pos_hint={"center_x": 0.5, "center_y": 0.55}
        )
        center_col.bind(minimum_height=center_col.setter("height"))

        self._title = Label(
            text="Configurações",
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

        for text, callback, text1, text2, group, e_light, e_dark, mode in [
        ("Som", self.on_som, "Ligado", "Desligado", "som", "\U0001F50A", "\U0001F507", "toggle"),
        ("Mudar Tema", self.on_mudar_tema, "Claro", "Escuro", "tema", "\U0001F31E", "\U0001F31C", "tema"),
        ]:
            toggle_btn = ToggleRoundedButton(
                text_light=text1,
                text_dark=text2,
                emoji_light=e_light,
                emoji_dark=e_dark,
                mode=mode,
                group=group,
                text=text
            )
            toggle_btn.pos_hint = {"center_x": 0.5}
            toggle_btn.bind(on_release=callback)
            center_col.add_widget(toggle_btn)
        
        text, callback = "Voltar", self.on_main_menu
        btn = RoundedButton(text=text)
        btn.pos_hint = {"center_x": 0.5}
        btn.bind(on_release=callback)
        center_col.add_widget(btn)

        self._root.add_widget(center_col)
        self.add_widget(self._root)

    def _on_theme(self, *_):
        tm = self._tm()
        self._bg_color_instr.rgba   = tm.color("bg")
        self._title.color           = tm.color("title")
    
    def _update_bg(self, instance, *_):
        self._bg_rect.pos   = instance.pos
        self._bg_rect.size  = instance.size
    
    def on_som(self, *_):
        pass
    
    def on_mudar_tema(self, *_):
        tm = ThemeManager.instance()
        print(f"[ANTES] tema: {tm.theme}")
        tm.toggle()
        print(f"[DEPOIS] tema: {tm.theme}")

    def _salvar_preferencia(self):
        tema_atual = ThemeManager.instance().theme
        with open("config.json", "w") as f:
            import json
            json.dump({"tema": tema_atual}, f)

    def on_main_menu(self, *_):
        if self.manager and "main_menu" in self.manager.screen_names:
            self.manager.current = "main_menu"