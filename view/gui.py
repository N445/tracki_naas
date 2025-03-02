# gui.py
import tkinter as tk
from tkinter import ttk
import threading
import pygame

from view.styles import apply_style
from controller.input_handler import update_value, send_data, reset_values, on_entry_change
from controller.xbox_controller import start_xbox_control, stop_xbox_control
from config import app_config

def create_gui(root, camera):
    # Initialiser Pygame pour pouvoir lister les joysticks
    pygame.init()

    # Appliquer le style
    apply_style(root)

    # ---------------- Barre de menu en haut ----------------
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    options_menu = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Options", menu=options_menu)
    # Ajout d’une entrée "Settings" qui ouvre la fenêtre de configuration
    options_menu.add_command(
        label="Settings",
        command=lambda: open_settings_window(root, app_config)
    )

    # ---------------- Conteneur principal ----------------
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # Frames gauche/droite
    left_frame = ttk.Frame(main_frame, borderwidth=2, relief="solid")
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    right_frame = ttk.Frame(main_frame, borderwidth=2, relief="solid")
    right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # ---------- Section Pitch/Yaw/Roll ----------
    ttk.Label(left_frame, text="Pitch/Yaw/Roll", font=("Helvetica", 14)).grid(
        row=0, column=0, columnspan=2, pady=5
    )

    pitch_entry, pitch_slider = create_input_row(left_frame, "Pitch:", camera, "pitch", 1, -180, 180)
    yaw_entry,   yaw_slider   = create_input_row(left_frame, "Yaw:",   camera, "yaw",   3, -180, 180)
    roll_entry,  roll_slider  = create_input_row(left_frame, "Roll:",  camera, "roll",  5, -180, 180)

    # ---------- Section X/Y/Z ----------
    ttk.Label(right_frame, text="X/Y/Z", font=("Helvetica", 14)).grid(
        row=0, column=0, columnspan=2, pady=5
    )

    x_entry, x_slider = create_input_row(right_frame, "X:", camera, "x", 1, -100, 100)
    y_entry, y_slider = create_input_row(right_frame, "Y:", camera, "y", 3, -100, 100)
    z_entry, z_slider = create_input_row(right_frame, "Z:", camera, "z", 5, -100, 100)

    # ---------- Boutons / Checkbuttons en bas ----------
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=2, column=0, columnspan=2, pady=10)

    reset_button = ttk.Button(
        button_frame,
        text="Reset",
        command=lambda: reset_values(
            camera,
            pitch_entry, yaw_entry, roll_entry,
            x_entry, y_entry, z_entry,
            pitch_slider, yaw_slider, roll_slider,
            x_slider, y_slider, z_slider
        )
    )
    reset_button.grid(row=0, column=0, padx=5)

    close_button = ttk.Button(button_frame, text="Fermer", command=root.destroy)
    close_button.grid(row=0, column=1, padx=5)

    # Case "Always on top"
    always_on_top = tk.BooleanVar(value=False)
    def toggle_always_on_top():
        root.attributes("-topmost", always_on_top.get())

    always_on_top_check = ttk.Checkbutton(
        button_frame,
        text="Always on Top",
        variable=always_on_top,
        command=toggle_always_on_top
    )
    always_on_top_check.grid(row=0, column=2, padx=5)

    # Case "Xbox Controller"
    xbox_enabled = tk.BooleanVar(value=False)
    xbox_thread = None

    def toggle_xbox():
        nonlocal xbox_thread
        if xbox_enabled.get():
            # Démarrer le contrôle Xbox
            xbox_thread = threading.Thread(
                target=start_xbox_control,
                args=(root, camera, pitch_entry, yaw_entry, roll_entry,
                      x_entry, y_entry, z_entry,
                      xbox_enabled,
                      app_config["device_index"]),  # On passe l’index du device choisi
                daemon=True
            )
            xbox_thread.start()
        else:
            # Stopper le contrôle
            stop_xbox_control()
            xbox_thread = None

    xbox_check = ttk.Checkbutton(
        button_frame,
        text="Xbox Controller",
        variable=xbox_enabled,
        command=toggle_xbox
    )
    xbox_check.grid(row=0, column=3, padx=5)

    return camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry


def create_input_row(frame, label_text, camera, attribute, row, min_val, max_val):
    ttk.Label(frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")

    entry = ttk.Entry(frame, width=10, justify="center")
    entry.insert(0, "0")
    entry.grid(row=row, column=1, padx=5, pady=5)

    slider = ttk.Scale(
        frame,
        from_=min_val,
        to=max_val,
        orient="horizontal",
        length=300,
        command=lambda val: on_slider_change(val, entry, camera, attribute)
    )
    slider.set(0)
    slider.grid(row=row + 1, column=0, columnspan=2, padx=4, pady=5, sticky="ew")

    entry.bind("<FocusOut>", lambda event: on_entry_change(event, camera, attribute, slider))
    entry.bind("<Return>",   lambda event: on_entry_change(event, camera, attribute, slider))

    return entry, slider

def on_slider_change(val, entry, camera, attribute):
    value = float(val)
    entry.delete(0, tk.END)
    entry.insert(0, f"{value:.2f}")
    setattr(camera, attribute, value)
    send_data(camera)


# --------------------- Fenêtre de configuration ----------------------

def open_settings_window(root, app_config):
    """
    Ouvre une fenêtre Toplevel avec :
    - Un Entry pour le port d’OpenTrack
    - Un Combobox pour choisir le périphérique de jeu
    - Un bouton "Appliquer"
    """
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("350x200")

    # Variables Tkinter liées à la config
    port_var = tk.StringVar(value=str(app_config["opentrack_port"]))
    device_var = tk.StringVar()

    # Lister les joysticks
    joystick_names = []
    pygame.joystick.quit()  # On relance pour être sûr de rescanner
    pygame.joystick.init()
    count = pygame.joystick.get_count()
    for i in range(count):
        j = pygame.joystick.Joystick(i)
        j.init()
        joystick_names.append(f"{i}: {j.get_name()}")

    # Label + Entry pour le port
    ttk.Label(settings_window, text="OpenTrack Port:").pack(pady=5)
    port_entry = ttk.Entry(settings_window, textvariable=port_var, width=10)
    port_entry.pack()

    # Label + Combobox pour les périphériques
    ttk.Label(settings_window, text="Choisir le périphérique:").pack(pady=5)
    device_combo = ttk.Combobox(settings_window, textvariable=device_var, values=joystick_names, state="readonly")
    device_combo.pack()

    # Pour sélectionner par défaut l’index connu
    if 0 <= app_config["device_index"] < len(joystick_names):
        device_combo.current(app_config["device_index"])
    else:
        device_combo.current(0)  # par défaut 0 si hors range

    def apply_changes():
        # Récupérer le port
        try:
            port = int(port_var.get())
        except ValueError:
            port = 4242  # fallback si invalide

        app_config["opentrack_port"] = port

        # Récupérer l’index du périphérique choisi
        sel = device_combo.get()  # ex: "0: Xbox Wireless Controller"
        if sel:
            # On parse le début pour avoir l'index
            idx_str = sel.split(":")[0]
            try:
                idx = int(idx_str)
            except ValueError:
                idx = 0
            app_config["device_index"] = idx

        # Fermer la fenêtre
        settings_window.destroy()

    # Bouton Appliquer
    ttk.Button(settings_window, text="Appliquer", command=apply_changes).pack(pady=10)
