"""
app/theme_manager.py
Singleton central de tema. Importe SEMPRE daqui — nunca redefina em outro módulo.
 
Uso:
    from app.theme_manager import ThemeManager
 
    ThemeManager.instance().toggle()
    ThemeManager.instance().set_theme("light")
    ThemeManager.instance().bind(on_theme_change=minha_funcao)
"""
 
import json
import os
 
from kivy.event import EventDispatcher
from kivy.properties import OptionProperty
 
 
CONFIG_PATH = "config.json"
 
THEMES = {
    "dark": {
        "bg":          (0.10, 0.10, 0.14, 1),
        "btn_bg":      (0.93, 0.93, 0.97, 1),
        "btn_text":    (0.38, 0.28, 0.72, 1),
        "btn_shadow":  (0.00, 0.00, 0.00, 0.22),
        "btn_pressed": 0.88,
        "title":       (1.00, 1.00, 1.00, 1),
        "menu_label":  (0.75, 0.75, 0.80, 1),
        "toggle_icon": "\u2600",   # ☀
        "toggle_hint": (0.75, 0.75, 0.80, 1),
    },
    "light": {
        "bg":          (0.95, 0.95, 0.98, 1),
        "btn_bg":      (1.00, 1.00, 1.00, 1),
        "btn_text":    (0.30, 0.20, 0.65, 1),
        "btn_shadow":  (0.60, 0.60, 0.70, 0.20),
        "btn_pressed": 0.92,
        "title":       (0.15, 0.10, 0.35, 1),
        "menu_label":  (0.40, 0.35, 0.55, 1),
        "toggle_icon": "\u263e",   # ☾
        "toggle_hint": (0.40, 0.35, 0.55, 1),
    },
}
 
 
class ThemeManager(EventDispatcher):
 
    theme     = OptionProperty("dark", options=["dark", "light"])
    _instance = None
 
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._carregar()
        return cls._instance
 
    def __init__(self, **kwargs):
        self.register_event_type("on_theme_change")
        super().__init__(**kwargs)
 
    # ── persistência ─────────────────────────────────────────────
    def _carregar(self):
        """Lê config.json e aplica o tema salvo (sem disparar evento)."""
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH) as f:
                    dados = json.load(f)
                tema = dados.get("tema", "dark")
                if tema in THEMES:
                    self.theme = tema   # direto — telas ainda não existem
            except (json.JSONDecodeError, OSError):
                pass   # arquivo corrompido → usa o padrão "dark"
 
    def _salvar(self, name: str):
        """Grava o tema atual em config.json."""
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump({"tema": name}, f)
        except OSError:
            pass
 
    # ── API pública ───────────────────────────────────────────────
    def set_theme(self, name: str):
        import traceback
        print(f"\n{'='*40}")
        print(f"set_theme chamado com: {name}")
        traceback.print_stack(limit=6)   # mostra quem chamou
        print('='*40)

        if name not in THEMES:
            raise ValueError(f"Tema desconhecido: {name!r}. Use 'dark' ou 'light'.")
        if self.theme != name:
            self.theme = name
            self.dispatch("on_theme_change", name)
            self._salvar(name)
 
    def toggle(self):
        self.set_theme("light" if self.theme == "dark" else "dark")
 
    def color(self, key: str):
        return THEMES[self.theme][key]
 
    def value(self, key: str):
        return THEMES[self.theme][key]
 
    def on_theme_change(self, *args):
        pass
