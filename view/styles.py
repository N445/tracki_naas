# view/styles.py
from ttkbootstrap import Style
from config import CONFIG

def apply_style(root):
    style = Style(theme="darkly")  # Thème sombre
    root.style = style

    # Appliquer les couleurs de configuration
    style.configure("TButton", background=CONFIG["button_color"], foreground=CONFIG["foreground_color"])
    style.configure("TEntry", background=CONFIG["entry_background_color"], foreground=CONFIG["entry_foreground_color"])
    style.configure("TLabel", background=CONFIG["background_color"], foreground=CONFIG["foreground_color"])
    style.configure("TFrame", background=CONFIG["background_color"])
    style.map("TButton", background=[('active', CONFIG["button_hover_color"])])
