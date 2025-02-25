import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from opentrack_sender import send_data_to_opentrack
from camera import Camera
from config import CONFIG
import inputs
import threading

# Fonction pour mettre à jour une valeur et l'objet Camera
def update_value(entry, increment, camera, attribute):
    try:
        current_value = float(entry.get())
    except ValueError:
        current_value = 0
    new_value = current_value + increment
    entry.delete(0, tk.END)
    entry.insert(0, str(new_value))
    setattr(camera, attribute, new_value)
    send_data(camera)

# Fonction pour envoyer les données à OpenTrack
def send_data(camera):
    pitch, yaw, roll, x, y, z = camera.get_data()
    send_data_to_opentrack(pitch, yaw, roll, x, y, z)

# Fonction pour réinitialiser les valeurs
def reset_values(camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry):
    camera.update(pitch=0, yaw=0, roll=0, x=0, y=0, z=0)
    pitch_entry.delete(0, tk.END)
    pitch_entry.insert(0, "0")
    yaw_entry.delete(0, tk.END)
    yaw_entry.insert(0, "0")
    roll_entry.delete(0, tk.END)
    roll_entry.insert(0, "0")
    x_entry.delete(0, tk.END)
    x_entry.insert(0, "0")
    y_entry.delete(0, tk.END)
    y_entry.insert(0, "0")
    z_entry.delete(0, tk.END)
    z_entry.insert(0, "0")
    send_data(camera)

# Fonction pour créer l'interface
def create_gui(root):
    # Appliquer un style avec ttkbootstrap
    style = Style(theme="darkly")  # Thème sombre
    root.style = style

    # Appliquer les couleurs de configuration
    style.configure("TButton", background=CONFIG["button_color"], foreground=CONFIG["foreground_color"])
    style.configure("TEntry", background=CONFIG["entry_background_color"], foreground=CONFIG["entry_foreground_color"])
    style.configure("TLabel", background=CONFIG["background_color"], foreground=CONFIG["foreground_color"])
    style.configure("TFrame", background=CONFIG["background_color"])
    style.configure("TButton", background=CONFIG["button_color"], foreground=CONFIG["foreground_color"])
    style.map("TButton", background=[('active', CONFIG["button_hover_color"])])

    # Créer un conteneur principal
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # Créer deux sections : pitch/yaw/roll à gauche et X/Y/Z à droite
    left_frame = ttk.Frame(main_frame, borderwidth=2, relief="solid")
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    right_frame = ttk.Frame(main_frame, borderwidth=2, relief="solid")
    right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Créer une instance de Camera
    camera = Camera()

    # Section pitch/yaw/roll
    ttk.Label(left_frame, text="Pitch/Yaw/Roll", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=5, pady=5)

    # Pitch
    ttk.Label(left_frame, text="Pitch:").grid(row=1, column=2, padx=5, pady=5)
    pitch_entry = ttk.Entry(left_frame, width=10, justify="center")
    pitch_entry.insert(0, "0")
    pitch_entry.grid(row=1, column=3, padx=5, pady=5)
    ttk.Button(left_frame, text="-10", command=lambda: update_value(pitch_entry, -10, camera, "pitch")).grid(row=1, column=0, padx=2, pady=5)
    ttk.Button(left_frame, text="-5", command=lambda: update_value(pitch_entry, -5, camera, "pitch")).grid(row=1, column=1, padx=2, pady=5)
    ttk.Button(left_frame, text="+5", command=lambda: update_value(pitch_entry, +5, camera, "pitch")).grid(row=1, column=4, padx=2, pady=5)
    ttk.Button(left_frame, text="+10", command=lambda: update_value(pitch_entry, +10, camera, "pitch")).grid(row=1, column=5, padx=2, pady=5)

    # Yaw
    ttk.Label(left_frame, text="Yaw:").grid(row=2, column=2, padx=5, pady=5)
    yaw_entry = ttk.Entry(left_frame, width=10, justify="center")
    yaw_entry.insert(0, "0")
    yaw_entry.grid(row=2, column=3, padx=5, pady=5)
    ttk.Button(left_frame, text="-10", command=lambda: update_value(yaw_entry, -10, camera, "yaw")).grid(row=2, column=0, padx=2, pady=5)
    ttk.Button(left_frame, text="-5", command=lambda: update_value(yaw_entry, -5, camera, "yaw")).grid(row=2, column=1, padx=2, pady=5)
    ttk.Button(left_frame, text="+5", command=lambda: update_value(yaw_entry, +5, camera, "yaw")).grid(row=2, column=4, padx=2, pady=5)
    ttk.Button(left_frame, text="+10", command=lambda: update_value(yaw_entry, +10, camera, "yaw")).grid(row=2, column=5, padx=2, pady=5)

    # Roll
    ttk.Label(left_frame, text="Roll:").grid(row=3, column=2, padx=5, pady=5)
    roll_entry = ttk.Entry(left_frame, width=10, justify="center")
    roll_entry.insert(0, "0")
    roll_entry.grid(row=3, column=3, padx=5, pady=5)
    ttk.Button(left_frame, text="-10", command=lambda: update_value(roll_entry, -10, camera, "roll")).grid(row=3, column=0, padx=2, pady=5)
    ttk.Button(left_frame, text="-5", command=lambda: update_value(roll_entry, -5, camera, "roll")).grid(row=3, column=1, padx=2, pady=5)
    ttk.Button(left_frame, text="+5", command=lambda: update_value(roll_entry, +5, camera, "roll")).grid(row=3, column=4, padx=2, pady=5)
    ttk.Button(left_frame, text="+10", command=lambda: update_value(roll_entry, +10, camera, "roll")).grid(row=3, column=5, padx=2, pady=5)

    # Section X/Y/Z
    ttk.Label(right_frame, text="X/Y/Z", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=5, pady=5)

    # X
    ttk.Label(right_frame, text="X:").grid(row=1, column=2, padx=5, pady=5)
    x_entry = ttk.Entry(right_frame, width=10, justify="center")
    x_entry.insert(0, "0")
    x_entry.grid(row=1, column=3, padx=5, pady=5)
    ttk.Button(right_frame, text="-10", command=lambda: update_value(x_entry, -10, camera, "x")).grid(row=1, column=0, padx=2, pady=5)
    ttk.Button(right_frame, text="-5", command=lambda: update_value(x_entry, -5, camera, "x")).grid(row=1, column=1, padx=2, pady=5)
    ttk.Button(right_frame, text="+5", command=lambda: update_value(x_entry, +5, camera, "x")).grid(row=1, column=4, padx=2, pady=5)
    ttk.Button(right_frame, text="+10", command=lambda: update_value(x_entry, +10, camera, "x")).grid(row=1, column=5, padx=2, pady=5)

    # Y
    ttk.Label(right_frame, text="Y:").grid(row=2, column=2, padx=5, pady=5)
    y_entry = ttk.Entry(right_frame, width=10, justify="center")
    y_entry.insert(0, "0")
    y_entry.grid(row=2, column=3, padx=5, pady=5)
    ttk.Button(right_frame, text="-10", command=lambda: update_value(y_entry, -10, camera, "y")).grid(row=2, column=0, padx=2, pady=5)
    ttk.Button(right_frame, text="-5", command=lambda: update_value(y_entry, -5, camera, "y")).grid(row=2, column=1, padx=2, pady=5)
    ttk.Button(right_frame, text="+5", command=lambda: update_value(y_entry, +5, camera, "y")).grid(row=2, column=4, padx=2, pady=5)
    ttk.Button(right_frame, text="+10", command=lambda: update_value(y_entry, +10, camera, "y")).grid(row=2, column=5, padx=2, pady=5)

    # Z
    ttk.Label(right_frame, text="Z:").grid(row=3, column=2, padx=5, pady=5)
    z_entry = ttk.Entry(right_frame, width=10, justify="center")
    z_entry.insert(0, "0")
    z_entry.grid(row=3, column=3, padx=5, pady=5)
    ttk.Button(right_frame, text="-10", command=lambda: update_value(z_entry, -10, camera, "z")).grid(row=3, column=0, padx=2, pady=5)
    ttk.Button(right_frame, text="-5", command=lambda: update_value(z_entry, -5, camera, "z")).grid(row=3, column=1, padx=2, pady=5)
    ttk.Button(right_frame, text="+5", command=lambda: update_value(z_entry, +5, camera, "z")).grid(row=3, column=4, padx=2, pady=5)
    ttk.Button(right_frame, text="+10", command=lambda: update_value(z_entry, +10, camera, "z")).grid(row=3, column=5, padx=2, pady=5)

    # Bouton Reset
    reset_button = ttk.Button(main_frame, text="Reset", command=lambda: reset_values(camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry))
    reset_button.grid(row=1, column=0, columnspan=2, pady=10)

    # Bouton Always on Top
    always_on_top = tk.BooleanVar(value=False)
    def toggle_always_on_top():
        always_on_top.set(not always_on_top.get())
        root.attributes("-topmost", always_on_top.get())

    ttk.Button(main_frame, text="Always on Top", command=toggle_always_on_top).grid(row=2, column=0, columnspan=2, pady=10)

    # Bouton pour activer/désactiver la manette Xbox
    xbox_enabled = tk.BooleanVar(value=False)
    def toggle_xbox():
        xbox_enabled.set(not xbox_enabled.get())
        if xbox_enabled.get():
            threading.Thread(target=start_xbox_control, args=(camera,)).start()
        else:
            stop_xbox_control()

    ttk.Button(main_frame, text="Toggle Xbox Controller", command=toggle_xbox).grid(row=3, column=0, columnspan=2, pady=10)

    # Fonction pour gérer la manette Xbox
    def start_xbox_control(camera):
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


    # Envoyer les données à chaque changement manuel
    def on_entry_change(event, camera, attribute):
        try:
            value = float(event.widget.get())
            setattr(camera, attribute, value)
            send_data(camera)
        except ValueError:
            pass

    pitch_entry.bind("<KeyRelease>", lambda event: on_entry_change(event, camera, "pitch"))
    yaw_entry.bind("<KeyRelease>", lambda event: on_entry_change(event, camera, "yaw"))
    roll_entry.bind("<KeyRelease>", lambda event: on_entry_change(event, camera, "roll"))
    x_entry.bind("<KeyRelease>", lambda event: on_entry_change(event, camera, "x"))
    y_entry.bind("<KeyRelease>", lambda event: on_entry_change(event, camera, "y"))
    z_entry.bind("<KeyRelease>", lambda event: on_entry_change(event, camera, "z"))

    return camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry
