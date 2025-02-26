import pygame
import threading
from controller.input_handler import update_value, send_data
import logging

# Initialisation de pygame et du joystick
pygame.init()

# Vérifier qu'un joystick est connecté
if pygame.joystick.get_count() == 0:
    print("Aucun contrôleur détecté.")
    pygame.quit()
    exit()

# Récupérer le premier joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Contrôleur détecté : {joystick.get_name()}")

# Variables de mouvement avec plage de -180 à 180
horizontal = 0  # Déplacement gauche/droite
vertical = 0    # Déplacement avant/arrière
altitude = 0    # Montée/descente (gâchettes)
pitch = 0       # Contrôle du pitch
yaw = 0         # Contrôle du yaw
roll = 0        # Contrôle du roll (RB et LB)

# Zone morte pour éviter les micro-mouvements
DEADZONE = 0.15
SMOOTHING = 0.0001  # Coefficient de lissage réduit pour ralentir l'évolution des valeurs

# Limites pour éviter de dépasser -180 ou 180
MIN_VAL = -180
MAX_VAL = 180

# Variables pour savoir si un bouton est pressé
rb_pressed = False
lb_pressed = False
x_pressed = False

def start_xbox_control(root, camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry, xbox_enabled):
    def handle_xbox_input():
        global horizontal, vertical, altitude, pitch, yaw, roll, rb_pressed, lb_pressed, x_pressed, SMOOTHING

        #logging.debug(joystick.get_button(2))
        #logging.debug(joystick.get_button(1))

        for event in pygame.event.get():  # Écoute des événements pygame
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Vérifier l'état des boutons X et B
        if joystick.get_button(2):  # Bouton X
            SMOOTHING = 0.00001
            x_pressed = True
        else:
            SMOOTHING = 0.0001
            x_pressed = False

        if joystick.get_button(1):  # Bouton B
            horizontal = vertical = altitude = pitch = yaw = roll = 0
            update_value(pitch_entry, pitch, camera, "pitch")
            update_value(yaw_entry, yaw, camera, "yaw")
            update_value(roll_entry, roll, camera, "roll")
            update_value(x_entry, horizontal, camera, "x")
            update_value(y_entry, vertical, camera, "y")
            update_value(z_entry, altitude, camera, "z")
            send_data(camera)

        # 🎮 Déplacements avec le joystick gauche
        new_horizontal = joystick.get_axis(0) * 180 if abs(joystick.get_axis(0)) > DEADZONE else 0
        new_vertical = -joystick.get_axis(1) * 180 if abs(joystick.get_axis(1)) > DEADZONE else 0

        # Ajustement progressif basé sur le mouvement (gauche/droite ou avant/arrière)
        if new_horizontal != 0:
            horizontal += new_horizontal * SMOOTHING
            horizontal = max(MIN_VAL, min(horizontal, MAX_VAL))  # Limite à -180, 180
        else:
            horizontal = 0  # Réinitialiser si aucun mouvement

        if new_vertical != 0:
            vertical += new_vertical * SMOOTHING
            vertical = max(MIN_VAL, min(vertical, MAX_VAL))  # Limite à -180, 180
        else:
            vertical = 0  # Réinitialiser si aucun mouvement

        # 🔄 Pitch & Yaw avec le joystick droit
        new_pitch = -joystick.get_axis(3) * 180 if abs(joystick.get_axis(3)) > DEADZONE else 0
        new_yaw = joystick.get_axis(2) * 180 if abs(joystick.get_axis(2)) > DEADZONE else 0

        # Ajustement progressif du pitch et du yaw
        if new_pitch != 0:
            pitch += new_pitch * SMOOTHING
            pitch = max(MIN_VAL, min(pitch, MAX_VAL))  # Limite à -180, 180
        else:
            pitch = 0  # Réinitialiser si aucun mouvement

        if new_yaw != 0:
            yaw += new_yaw * SMOOTHING
            yaw = max(MIN_VAL, min(yaw, MAX_VAL))  # Limite à -180, 180
        else:
            yaw = 0  # Réinitialiser si aucun mouvement

        # ↕️ Altitude avec gâchettes (de -180 à +180)
        trigger_left = joystick.get_axis(4)  # LT
        trigger_right = joystick.get_axis(5)  # RT
        new_altitude = (trigger_right - trigger_left) * 180  # Plage de -180 à +180

        # Ajustement progressif de l'altitude
        if new_altitude != 0:
            altitude += new_altitude * SMOOTHING
            altitude = max(MIN_VAL, min(altitude, MAX_VAL))  # Limite à -180, 180
        else:
            altitude = 0  # Réinitialiser si aucun mouvement

        # ↻ Roll avec les boutons RB et LB (contrôle progressif)
        rb = joystick.get_button(5)  # RB
        lb = joystick.get_button(4)  # LB

        if rb:  # Si RB est pressé, augmenter progressivement le roll vers 180
            roll += SMOOTHING * 180  # Progression vers 180
            rb_pressed = True
        elif lb:  # Si LB est pressé, diminuer progressivement le roll vers -180
            roll -= SMOOTHING * 180  # Progression vers -180
            lb_pressed = True
        else:
            if not rb_pressed and not lb_pressed:
                roll = 0  # Réinitialiser si aucun bouton n'est pressé
            rb_pressed = False
            lb_pressed = False

        # Limite du roll à -180 et 180
        roll = max(MIN_VAL, min(roll, MAX_VAL))

        # Mettre à jour les entrées et les sliders dans Tkinter
        update_value(pitch_entry, pitch, camera, "pitch")
        update_value(yaw_entry, yaw, camera, "yaw")
        update_value(roll_entry, roll, camera, "roll")
        update_value(x_entry, horizontal, camera, "x")
        update_value(y_entry, vertical, camera, "y")
        update_value(z_entry, altitude, camera, "z")

        # Vérifier si les valeurs ont changé avant d'envoyer les données
        if (horizontal != 0 or vertical != 0 or altitude != 0 or
            pitch != 0 or yaw != 0 or roll != 0):
            send_data(camera)

        # Affichage des valeurs (simule une sortie moteur)
        print(f"Déplacement: H={horizontal:.2f}, V={vertical:.2f} | Altitude={altitude:.2f} | "
              f"Pitch={pitch:.2f}, Yaw={yaw:.2f}, Roll={roll:.2f}")

    while xbox_enabled.get():
        handle_xbox_input()
        root.after(10)

def stop_xbox_control():
    pygame.quit()
