# controller/xbox_controller.py
import inputs
import threading
from controller.input_handler import update_value

# Fonction pour gérer la manette Xbox
def start_xbox_control(camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry):
    def handle_xbox_input():
        events = inputs.get_gamepad()
        for event in events:
            if event.ev_type == "Key":
                if event.code == "BTN_SOUTH" and event.state == 1:  # Bouton A
                    update_value(z_entry, +0.1, camera, "z")  # Réduire la sensibilité
                elif event.code == "BTN_NORTH" and event.state == 1:  # Bouton B
                    update_value(z_entry, -0.1, camera, "z")  # Réduire la sensibilité
                elif event.code == "BTN_TL" and event.state == 1:  # Gâchette gauche
                    update_value(z_entry, -0.1, camera, "z")  # Corriger la fonctionnalité de descente
                elif event.code == "BTN_TR" and event.state == 1:  # Gâchette droite
                    update_value(z_entry, +0.1, camera, "z")  # Corriger la fonctionnalité de montée
            elif event.ev_type == "Absolute":
                if event.code == "ABS_X":
                    update_value(x_entry, event.state / 32767 * 0.5, camera, "x")  # Réduire la sensibilité
                elif event.code == "ABS_Y":
                    update_value(y_entry, event.state / 32767 * 0.5, camera, "y")  # Réduire la sensibilité
                elif event.code == "ABS_RX":
                    update_value(pitch_entry, event.state / 32767 * 0.5, camera, "pitch")  # Réduire la sensibilité
                elif event.code == "ABS_RY":
                    update_value(yaw_entry, event.state / 32767 * 0.5, camera, "yaw")  # Réduire la sensibilité
                elif event.code == "ABS_HAT0X":
                    update_value(roll_entry, event.state * 10, camera, "roll")  # Garder la sensibilité inchangée
                elif event.code == "ABS_HAT0Y":
                    update_value(roll_entry, event.state * 10, camera, "roll")  # Garder la sensibilité inchangée

    while xbox_enabled.get():
        handle_xbox_input()
        root.after(10)

def stop_xbox_control():
    pass
