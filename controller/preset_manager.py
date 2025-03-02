# preset_manager.py

import os
import json

PRESET_FOLDER = "presets"

# Vérifier si le dossier des presets existe, sinon le créer
if not os.path.exists(PRESET_FOLDER):
    os.makedirs(PRESET_FOLDER)

def save_preset(name, camera):
    """Sauvegarde les valeurs actuelles de la caméra dans un fichier JSON."""
    preset_path = os.path.join(PRESET_FOLDER, f"{name}.json")
    data = {
        "pitch": camera.pitch,
        "yaw": camera.yaw,
        "roll": camera.roll,
        "x": camera.x,
        "y": camera.y,
        "z": camera.z
    }

    with open(preset_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Preset '{name}' sauvegardé avec succès.")

def load_preset(name, camera):
    """Charge un preset et met à jour la caméra."""
    preset_path = os.path.join(PRESET_FOLDER, f"{name}.json")
    if not os.path.exists(preset_path):
        print(f"Preset '{name}' introuvable.")
        return None

    with open(preset_path, 'r') as file:
        data = json.load(file)

    camera.update(**data)
    print(f"Preset '{name}' chargé avec succès.")
    return data

def list_presets():
    """Retourne la liste des presets disponibles."""
    return [f.split(".json")[0] for f in os.listdir(PRESET_FOLDER) if f.endswith(".json")]
