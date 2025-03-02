# config.py
CONFIG = {
    "background_color": "#1e1e1e",  # Couleur de fond sombre
    "foreground_color": "#ffffff",  # Couleur du texte
    "button_color": "#ffa500",     # Couleur des boutons (orange)
    "button_hover_color": "#ff8c00", # Couleur des boutons au survol
    "entry_background_color": "#333333", # Couleur de fond des champs d'entrée
    "entry_foreground_color": "#ffffff", # Couleur du texte des champs d'entrée
}


# Petit dictionnaire global pour stocker la config
app_config = {
    "opentrack_port": 4242,        # Port par défaut
    "device_index": 0             # On prendra par défaut le 1er joystick
}