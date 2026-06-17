import json
import os

from app.controllers.theme_manager import ThemeManager

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.event import EventDispatcher
from kivy.properties import OptionProperty
from kivy.core.text import LabelBase

LabelBase.register(
    name='FonteTitulo',
    fn_regular='assets/fonts/IrishGrover-Regular.ttf'
)



class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color   = (0, 0, 0, 0)
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



class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()
        ThemeManager.instance().bind(on_theme_change=self._on_theme)
    
    def _tm(self):
        return ThemeManager.instance()
    
    def _build_ui(self):
        tm         = self._tm()
        self._root = FloatLayout()

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
            text="Jogo Da Velha",
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

        center_col.add_widget(Label(size_hint_y=None, height=dp(10)))

        for text, callback in [
            ("Iniciar jogo",    self.on_start),
            ("Configurações",   self.on_settings),
            ("Sair",            self.on_quit)
        ]:
            btn = RoundedButton(text=text)
            btn.pos_hint = {"center_x": 0.5}
            btn.bind(on_release=callback)
            center_col.add_widget(btn)
            # self._action_buttons.append(btn)
        
        self._root.add_widget(center_col)
        self.add_widget(self._root)
    
    def _on_theme(self, *_):
        tm = self._tm()
        self._bg_color_instr.rgba   = tm.color("bg")
        self._title.color           = tm.color("title")
    
    def _update_bg(self, instance, *_):
        self._bg_rect.pos   = instance.pos
        self._bg_rect.size  = instance.size
    
    def on_start(self, *_):
        if self.manager and "config_game" in self.manager.screen_names:
            self.manager.current = "config_game"
    
    def on_settings(self, *_):
        if self.manager and "settings" in self.manager.screen_names:
            self.manager.current = "settings"
    
    def on_quit(self, *_):
        from kivy.app import App
        App.get_running_app().stop()
