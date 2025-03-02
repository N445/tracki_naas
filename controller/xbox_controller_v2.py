# xbox_controller_v2.py

import pygame
import threading
import time
import logging

from controller.input_handler import send_data, set_absolute_value

# ---------------------------------------------------------------------------------------
# Classe XboxControllerV2
# ---------------------------------------------------------------------------------------
class XboxControllerV2:
    """
    Gère la manette Xbox en mode orienté objet.
    - Initialise la manette (pygame).
    - Lit en continu les inputs dans un thread.
    - Met à jour la Camera + l'UI (Entry/Slider).
    - Peut être démarrée et arrêtée facilement via start() / stop().
    """

    def __init__(
        self,
        root,
        camera,
        pitch_entry,
        yaw_entry,
        roll_entry,
        x_entry,
        y_entry,
        z_entry,
        xbox_enabled_var,
        device_index=0,
        deadzone=0.3,
        base_smooth=0.005,
        slow_smooth=0.0005
    ):
        self.root = root
        self.camera = camera

        # Références vers les widgets de l'UI
        self.pitch_entry = pitch_entry
        self.yaw_entry   = yaw_entry
        self.roll_entry  = roll_entry
        self.x_entry     = x_entry
        self.y_entry     = y_entry
        self.z_entry     = z_entry

        # Variable pour activer/désactiver la manette
        self.xbox_enabled_var = xbox_enabled_var

        self.device_index = device_index

        # Paramètres de configuration
        self.DEADZONE = deadzone
        self.BASE_SMOOTH = base_smooth
        self.SLOW_SMOOTH = slow_smooth

        # Bornes pour les valeurs
        self.MIN_ANGLE = -180.0
        self.MAX_ANGLE =  180.0
        self.MIN_POS   = -100.0
        self.MAX_POS   =  100.0

        # Variables internes pour stocker les valeurs
        self._horizontal = 0.0   # pour X
        self._vertical   = 0.0   # pour Y
        self._profondeur   = 0.0   # pour Z
        self._pitch      = 0.0
        self._yaw        = 0.0
        self._roll       = 0.0

        self._thread = None
        self._joystick = None
        self._running = False

    def start(self):
        """Initialise la manette et démarre le thread de lecture."""
        pygame.joystick.quit()
        pygame.joystick.init()

        count = pygame.joystick.get_count()
        if count == 0:
            print("Aucun périphérique de jeu détecté (XboxControllerV2).")
            return

        # Détection d'une manette "xbox" ou "xinput"
        chosen_index = None
        for i in range(count):
            j = pygame.joystick.Joystick(i)
            j.init()
            if "xbox" in j.get_name().lower() or "xinput" in j.get_name().lower():
                chosen_index = i
                print(f"[XboxControllerV2] Détection auto: index {i} -> {j.get_name()}")
                break

        if chosen_index is None:
            chosen_index = self.device_index if self.device_index < count else 0

        self._joystick = pygame.joystick.Joystick(chosen_index)
        self._joystick.init()
        print(f"[XboxControllerV2] Utilisation du joystick index {chosen_index} -> {self._joystick.get_name()}")

        self.reset_internal_values()

        self._running = True
        self._thread = threading.Thread(target=self._xbox_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Arrête la lecture en continu."""
        self._running = False
        logging.debug("[XboxControllerV2] Demande d'arrêt du thread.")

    def _xbox_loop(self):
        """Boucle de lecture des inputs de la manette."""
        while self.xbox_enabled_var.get() and self._running:
            self._handle_xbox_input()
            time.sleep(0.01)  # 10 ms
        logging.debug("[XboxControllerV2] Fin de la boucle de contrôle.")

    def _handle_xbox_input(self):
        """Gère la lecture des axes et boutons de la manette et met à jour l'UI et la caméra."""
        if not pygame.get_init():
            print("[XboxControllerV2] Erreur : Pygame non initialisé !")
            return

        # Mise à jour de la file d'événements sans retourner de liste (évite les erreurs en thread)
        pygame.event.pump()

        # Bouton B (index 1) pour reset
        if self._joystick.get_button(1):
            self.reset_internal_values()
            self._update_all_entries()
            send_data(self.camera)

        # Bouton X (index 2) pour mouvement lent
        current_smooth = self.SLOW_SMOOTH if self._joystick.get_button(2) else self.BASE_SMOOTH

        # ---------------- STICK GAUCHE (X, Y) ----------------
        axis_lx = self._joystick.get_axis(0)
        axis_ly = self._joystick.get_axis(1)
        if abs(axis_lx) < self.DEADZONE:
            axis_lx = 0.0
        if abs(axis_ly) < self.DEADZONE:
            axis_ly = 0.0

        self._horizontal += axis_lx * 180.0 * current_smooth
        self._profondeur   += -axis_ly * 180.0 * current_smooth
        self._horizontal = self._clamp(self._horizontal, self.MIN_POS, self.MAX_POS)
        self._profondeur   = self._clamp(self._profondeur, self.MIN_POS, self.MAX_POS)

        # ---------------- GÂCHETTES pour ALTITUDE (Z) ----------------
        axis_lt = self._joystick.get_axis(2)
        axis_rt = self._joystick.get_axis(5)
        if abs(axis_lt) < self.DEADZONE:
            axis_lt = -1.0
        if abs(axis_rt) < self.DEADZONE:
            axis_rt = -1.0
        alt_input = (axis_rt - axis_lt) * 90.0
        self._vertical += alt_input * current_smooth
        self._vertical = self._clamp(self._vertical, self.MIN_POS, self.MAX_POS)

        # ---------------- STICK DROIT (Yaw, Pitch) ----------------
        axis_rx = self._joystick.get_axis(3)
        axis_ry = self._joystick.get_axis(4)
        # Correction : si l'axe du stick droit vertical renvoie une valeur proche de -1 au repos, la remettre à 0
        if abs(axis_ry + 1.0) < 0.05:
            axis_ry = 0.0
        if abs(axis_rx) < self.DEADZONE:
            axis_rx = 0.0
        if abs(axis_ry) < self.DEADZONE:
            axis_ry = 0.0

        self._yaw   += axis_rx * 180.0 * current_smooth
        self._pitch += -axis_ry * 180.0 * current_smooth
        self._yaw   = self._clamp(self._yaw,   self.MIN_ANGLE, self.MAX_ANGLE)
        self._pitch = self._clamp(self._pitch, self.MIN_ANGLE, self.MAX_ANGLE)

        # ---------------- LB/RB pour ROLL ----------------
        if self._joystick.get_button(4):
            self._roll -= 180.0 * current_smooth
        elif self._joystick.get_button(5):
            self._roll += 180.0 * current_smooth
        self._roll = self._clamp(self._roll, self.MIN_ANGLE, self.MAX_ANGLE)

        # Mise à jour de l'UI et de l'objet Camera
        self._update_all_entries()
        send_data(self.camera)

        logging.debug(
            f"[XboxControllerV2] X={self._horizontal:.2f}, Y={self._vertical:.2f}, Z={self._profondeur:.2f}, "
            f"Pitch={self._pitch:.2f}, Yaw={self._yaw:.2f}, Roll={self._roll:.2f}"
        )

    def _update_all_entries(self):
        """Met à jour les Entry et l'objet Camera avec les valeurs courantes."""
        set_absolute_value(self.pitch_entry, self._pitch,       self.camera, "pitch")
        set_absolute_value(self.yaw_entry,   self._yaw,         self.camera, "yaw")
        set_absolute_value(self.roll_entry,  self._roll,        self.camera, "roll")
        set_absolute_value(self.x_entry,     self._horizontal,  self.camera, "x")
        set_absolute_value(self.y_entry,     self._vertical,    self.camera, "y")
        set_absolute_value(self.z_entry,     self._profondeur,    self.camera, "z")

    def reset_internal_values(self):
        """Réinitialise toutes les valeurs internes à zéro."""
        self._horizontal = 0.0
        self._vertical   = 0.0
        self._profondeur   = 0.0
        self._pitch      = 0.0
        self._yaw        = 0.0
        self._roll       = 0.0

    def _clamp(self, val, min_val, max_val):
        return max(min(val, max_val), min_val)
