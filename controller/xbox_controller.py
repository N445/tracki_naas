import pygame
import threading
import time
import logging

from controller.input_handler import send_data, set_absolute_value

# -------------------- Variables globales --------------------
horizontal = 0.0   # Contrôle X
vertical   = 0.0   # Contrôle Y
altitude   = 0.0   # Contrôle Z
pitch      = 0.0
yaw        = 0.0
roll       = 0.0

# -------------------- Paramètres --------------------
DEADZONE     = 0.15    # Pour éviter les petites variations quand les sticks sont au repos
BASE_SMOOTH  = 0.01    # Vitesse "normale" de déplacement
SLOW_SMOOTH  = 0.002   # Vitesse "lente" (bouton X)
MIN_VAL      = -180.0
MAX_VAL      =  180.0


def start_xbox_control(
    root,
    camera,
    pitch_entry, yaw_entry, roll_entry,
    x_entry, y_entry, z_entry,
    xbox_enabled,
    device_index
):
    """
    Lance la détection et l'écoute d'une manette Xbox/XInput.
    root         : fenêtre Tk
    camera       : instance de Camera
    *_entry      : champs d'input Tkinter pour pitch, yaw, roll, x, y, z
    xbox_enabled : BooleanVar indiquant si la manette est activée
    device_index : index du joystick à utiliser
    """
    # (Re)initialiser pygame pour scanner les manettes
    pygame.joystick.quit()
    pygame.joystick.init()

    count = pygame.joystick.get_count()
    if count == 0:
        print("Aucun périphérique de jeu détecté.")
        return

    chosen_index = None
    for i in range(count):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        if "xbox" in joy.get_name().lower() or "xinput" in joy.get_name().lower():
            chosen_index = i
            print(f"Détection auto: joystick index {i} -> {joy.get_name()}")
            break

    # Si on ne trouve pas "xbox/xinput", on prend device_index ou 0
    if chosen_index is None:
        chosen_index = device_index if device_index < count else 0

    if chosen_index >= count:
        print(f"Index de joystick invalide : {chosen_index}, aucun périphérique trouvé.")
        return

    # Initialiser la manette sélectionnée
    try:
        selected_joystick = pygame.joystick.Joystick(chosen_index)
        selected_joystick.init()
        print(f"Utilisation du joystick index {chosen_index} -> {selected_joystick.get_name()}")
    except pygame.error as e:
        print(f"Erreur lors de l'initialisation du joystick : {e}")
        return

    # Lancer un thread qui lit la manette en continu
    def xbox_loop():
        while xbox_enabled.get():
            try:
                handle_xbox_input(
                    camera,
                    pitch_entry, yaw_entry, roll_entry,
                    x_entry, y_entry, z_entry,
                    selected_joystick
                )
            except Exception as e:
                print(f"Erreur dans xbox_loop : {e}")
            time.sleep(0.01)  # 10 ms de pause

        logging.debug("Fin de la boucle de contrôle Xbox (xbox_enabled = False)")

    threading.Thread(target=xbox_loop, daemon=True).start()


def stop_xbox_control():
    """
    Met fin à la boucle quand xbox_enabled passe à False.
    (Aucun 'kill' explicite, le thread lit la variable.)
    """
    logging.debug("Xbox control stopped.")


def handle_xbox_input(camera, pitch_entry, yaw_entry, roll_entry,
                      x_entry, y_entry, z_entry, joystick):

    global horizontal, vertical, altitude, pitch, yaw, roll

    # 1) Mise à jour des événements
    pygame.event.pump()

    # 2) Debug: afficher la valeur de chaque axis, SANS imposer de sleep de 0.2
    axes_count = joystick.get_numaxes()
    for i in range(axes_count):
        val = joystick.get_axis(i)
        if abs(val) > 0.02:  # deadzone plus petite pour l'affichage
            print(f"[DEBUG] Axis {i}: {val:.2f}")

    # 3) Debug: afficher les boutons pressés
    buttons_count = joystick.get_numbuttons()
    for i in range(buttons_count):
        if joystick.get_button(i):
            print(f"[DEBUG] Bouton {i} pressé")

    # 4) Bouton B => reset
    if joystick.get_button(1):
        horizontal = vertical = altitude = pitch = yaw = roll = 0.0
        update_all_entries(camera, pitch_entry, yaw_entry, roll_entry,
                           x_entry, y_entry, z_entry)
        send_data(camera)
        return

    # 5) Smoothing (bouton X => lent)
    current_smoothing = SLOW_SMOOTH if joystick.get_button(2) else BASE_SMOOTH

    # 6) STICK GAUCHE => X, Y (axes 0,1)
    axis_lx = joystick.get_axis(0)
    axis_ly = joystick.get_axis(1)

    if abs(axis_lx) > DEADZONE:
        horizontal += axis_lx * 180.0 * current_smoothing
    if abs(axis_ly) > DEADZONE:
        vertical   += -axis_ly * 180.0 * current_smoothing

    # 7) LT/RT => altitude (axes 4,5)
    axis_lt = joystick.get_axis(4)
    axis_rt = joystick.get_axis(5)
    if (abs(axis_lt) > DEADZONE) or (abs(axis_rt) > DEADZONE):
        alt_input = (axis_rt - axis_lt) * 90.0
        altitude += alt_input * current_smoothing

    # 8) STICK DROIT => yaw, pitch (ex: axes 2,3)
    axis_rx = joystick.get_axis(2)
    axis_ry = joystick.get_axis(3)

    if abs(axis_rx) > DEADZONE:
        yaw += axis_rx * 180.0 * current_smoothing
    if abs(axis_ry) > DEADZONE:
        pitch += -axis_ry * 180.0 * current_smoothing

    # 9) LB/RB => roll (boutons 4,5)
    if joystick.get_button(4):
        roll -= 180.0 * current_smoothing
    if joystick.get_button(5):
        roll += 180.0 * current_smoothing

    # 10) clamp
    horizontal = clamp(horizontal, MIN_VAL, MAX_VAL)
    vertical   = clamp(vertical,   MIN_VAL, MAX_VAL)
    altitude   = clamp(altitude,   MIN_VAL, MAX_VAL)
    pitch      = clamp(pitch,      MIN_VAL, MAX_VAL)
    yaw        = clamp(yaw,        MIN_VAL, MAX_VAL)
    roll       = clamp(roll,       MIN_VAL, MAX_VAL)

    # 11) update UI + send data
    update_all_entries(camera, pitch_entry, yaw_entry, roll_entry,
                       x_entry, y_entry, z_entry)
    send_data(camera)

    # Debug console
    logging.debug(
        f"[xbox_input] X={horizontal:.1f}, Y={vertical:.1f}, Z={altitude:.1f}, "
        f"Pitch={pitch:.1f}, Yaw={yaw:.1f}, Roll={roll:.1f}"
    )


def update_all_entries(
    camera,
    pitch_entry, yaw_entry, roll_entry,
    x_entry, y_entry, z_entry
):
    """
    Met à jour l'UI (Entry) + l'objet Camera, puis envoie les données.
    """
    global horizontal, vertical, altitude, pitch, yaw, roll

    set_absolute_value(pitch_entry, pitch, camera, "pitch")
    set_absolute_value(yaw_entry, yaw, camera, "yaw")
    set_absolute_value(roll_entry, roll, camera, "roll")
    set_absolute_value(x_entry, horizontal, camera, "x")
    set_absolute_value(y_entry, vertical, camera, "y")
    set_absolute_value(z_entry, altitude, camera, "z")


def clamp(val, mini, maxi):
    return max(min(val, maxi), mini)
