import pygame
import threading
import time
import logging

from controller.input_handler import update_value, send_data, set_absolute_value

# Variables globales représentant la position/orientation
horizontal = 0.0  # X
vertical   = 0.0  # Y
altitude   = 0.0  # Z
pitch      = 0.0
yaw        = 0.0
roll       = 0.0

# Paramètres
DEADZONE     = 0.3    # 30% de zone morte
BASE_SMOOTH  = 0.005  # Vitesse d'évolution standard
SLOW_SMOOTH  = 0.0005  # Vitesse quand on maintient X
MIN_VAL      = -180.0
MAX_VAL      =  180.0

def start_xbox_control(
    root,
    camera,
    pitch_entry,
    yaw_entry,
    roll_entry,
    x_entry,
    y_entry,
    z_entry,
    xbox_enabled,
    device_index
):
    """
    Lance un thread qui lit en continu l'état du joystick sélectionné
    (ou, si possible, celui qui contient "xbox"/"xinput" dans son nom).
    """

    pygame.joystick.quit()
    pygame.joystick.init()

    count = pygame.joystick.get_count()
    if count == 0:
        print("Aucun périphérique de jeu détecté.")
        return

    # On essaye de détecter un joystick "xbox" en priorité
    chosen_index = None
    for i in range(count):
        j = pygame.joystick.Joystick(i)
        j.init()
        name_lower = j.get_name().lower()
        if "xbox" in name_lower or "xinput" in name_lower:
            chosen_index = i
            print(f"Détection auto: joystick index {i} -> {j.get_name()}")
            break

    # Sinon, on prend device_index ou 0
    if chosen_index is None:
        if device_index < count:
            chosen_index = device_index
        else:
            chosen_index = 0

    selected_joystick = pygame.joystick.Joystick(chosen_index)
    selected_joystick.init()
    print(f"Utilisation du joystick index {chosen_index} -> {selected_joystick.get_name()}")

    # Boucle d'écoute dans un thread
    def xbox_loop():
        while xbox_enabled.get():
            handle_xbox_input(
                camera,
                pitch_entry,
                yaw_entry,
                roll_entry,
                x_entry,
                y_entry,
                z_entry,
                selected_joystick
            )
            time.sleep(0.01)  # 10 ms

        logging.debug("Fin de la boucle de contrôle Xbox (xbox_enabled = False)")

    threading.Thread(target=xbox_loop, daemon=True).start()

def stop_xbox_control():
    """Stoppe la boucle quand xbox_enabled = False."""
    logging.debug("Xbox control stopped.")

def handle_xbox_input(
    camera,
    pitch_entry,
    yaw_entry,
    roll_entry,
    x_entry,
    y_entry,
    z_entry,
    joystick
):
    """
    Lit les axes/boutons de la manette avec le mappage indiqué :

    - axis(0) = stick gauche horizontal => X (gauche/droite)
    - axis(1) = stick gauche vertical   => Y (avant/arrière)
    - axis(2) = LT => altitude négative si +1
    - axis(3) = stick droit horizontal => yaw (gauche/droite)
    - axis(4) = stick droit vertical   => pitch (haut/bas)
    - axis(5) = RT => altitude positive si +1
    - button(1) = B => reset
    - button(2) = X => mouvement + lent (on réduit le smoothing)
    - button(4) = LB => roll négatif
    - button(5) = RB => roll positif
    """
    global horizontal, vertical, altitude, pitch, yaw, roll

    # Récupérer les events pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Bouton B = 1 => reset
    if joystick.get_button(1):
        horizontal = vertical = altitude = pitch = yaw = roll = 0.0
        update_all_entries(
            camera,
            pitch_entry, yaw_entry, roll_entry,
            x_entry, y_entry, z_entry
        )
        send_data(camera)

    # Bouton X = 2 => on réduit encore le smoothing
    if joystick.get_button(2):
        current_smoothing = SLOW_SMOOTH
    else:
        current_smoothing = BASE_SMOOTH

    # ---------------- STICK GAUCHE => X, Y ----------------
    axis_lx = joystick.get_axis(0)  # -1..+1 => gauche/droite
    axis_ly = joystick.get_axis(1)  # -1..+1 => haut/bas

    if abs(axis_lx) < DEADZONE:
        axis_lx = 0.0
    if abs(axis_ly) < DEADZONE:
        axis_ly = 0.0

    # On accumule sur horizontal, vertical
    # Note: -axis_ly pour inverser le sens si tu veux "haut" => Y++
    horizontal += axis_lx * 180.0 * current_smoothing
    vertical   += -axis_ly * 180.0 * current_smoothing
    horizontal  = max(MIN_VAL, min(horizontal, MAX_VAL))
    vertical    = max(MIN_VAL, min(vertical,   MAX_VAL))

    # ---------------- GÂCHETTES => ALTITUDE ----------------
    # LT = axis(2), +1 => pressé => altitude diminue
    # RT = axis(5), +1 => pressé => altitude augmente
    axis_lt = joystick.get_axis(2)
    axis_rt = joystick.get_axis(5)

    if abs(axis_lt) < DEADZONE:
        axis_lt = -1.0  # par défaut si relâché => -1
    if abs(axis_rt) < DEADZONE:
        axis_rt = -1.0  # par défaut si relâché => -1

    # Si LT=+1 => alt_input = -2   (puisque RT=-1 => -1 - (+1) = -2)
    # Si RT=+1 => alt_input = +2
    # On peut ajuster le /2 pour calmer un peu
    alt_input = ((axis_rt) - (axis_lt)) * 90.0  # *90 => max ~±180 d'amplitude
    altitude += alt_input * current_smoothing
    altitude = max(MIN_VAL, min(altitude, MAX_VAL))

    # ---------------- STICK DROIT => yaw, pitch ----------------
    axis_rx = joystick.get_axis(3)  # -1..+1
    axis_ry = joystick.get_axis(4)  # -1..+1

    if abs(axis_rx) < DEADZONE:
        axis_rx = 0.0
    if abs(axis_ry) < DEADZONE:
        axis_ry = 0.0

    yaw   += axis_rx * 180.0 * current_smoothing
    pitch += -axis_ry * 180.0 * current_smoothing
    yaw   = max(MIN_VAL, min(yaw,   MAX_VAL))
    pitch = max(MIN_VAL, min(pitch, MAX_VAL))

    # ---------------- LB/RB => ROLL ----------------
    lb = joystick.get_button(4)
    rb = joystick.get_button(5)

    if lb:
        roll -= 180.0 * current_smoothing
    elif rb:
        roll += 180.0 * current_smoothing

    roll = max(MIN_VAL, min(roll, MAX_VAL))

    # ---------------- MISE À JOUR ----------------
    update_all_entries(
        camera,
        pitch_entry, yaw_entry, roll_entry,
        x_entry, y_entry, z_entry
    )
    send_data(camera)

    logging.debug(
        f"handle_xbox_input => "
        f"H={horizontal:.2f}, V={vertical:.2f}, Alt={altitude:.2f}, "
        f"Pitch={pitch:.2f}, Yaw={yaw:.2f}, Roll={roll:.2f}"
    )

def update_all_entries(
    camera,
    pitch_entry,
    yaw_entry,
    roll_entry,
    x_entry,
    y_entry,
    z_entry
):
    """
    Met à jour l'UI (les champs Entry) et l'objet Camera
    avec les valeurs globales.
    """
    global horizontal, vertical, altitude, pitch, yaw, roll

    # On utilise update_value(...) pour :
    # - modifier l'Entry
    # - setter la valeur dans l'objet camera
    # - et déclencher l'envoi (send_data) si c'est dans update_value

    set_absolute_value(pitch_entry, pitch, camera, "pitch")
    set_absolute_value(yaw_entry,   yaw,   camera, "yaw")
    set_absolute_value(roll_entry,  roll,  camera, "roll")
    set_absolute_value(x_entry,     horizontal, camera, "x")
    set_absolute_value(y_entry,     vertical,   camera, "y")
    set_absolute_value(z_entry,     altitude,   camera, "z")
