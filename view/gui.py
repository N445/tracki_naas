﻿# view/gui.py
import tkinter as tk
from tkinter import ttk
from view.styles import apply_style
from controller.input_handler import update_value, send_data, reset_values, on_entry_change

def create_gui(root, camera):
    # Appliquer le style
    apply_style(root)

    # Créer un conteneur principal
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # Créer deux sections : pitch/yaw/roll à gauche et X/Y/Z à droite
    left_frame = ttk.Frame(main_frame, borderwidth=2, relief="solid")
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    right_frame = ttk.Frame(main_frame, borderwidth=2, relief="solid")
    right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Section pitch/yaw/roll
    ttk.Label(left_frame, text="Pitch/Yaw/Roll", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=5, pady=5)

    # Pitch
    pitch_entry = create_input_row(left_frame, "Pitch:", camera, "pitch", 1)
    # Yaw
    yaw_entry = create_input_row(left_frame, "Yaw:", camera, "yaw", 2)
    # Roll
    roll_entry = create_input_row(left_frame, "Roll:", camera, "roll", 3)

    # Section X/Y/Z
    ttk.Label(right_frame, text="X/Y/Z", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=5, pady=5)

    # X
    x_entry = create_input_row(right_frame, "X:", camera, "x", 1)
    # Y
    y_entry = create_input_row(right_frame, "Y:", camera, "y", 2)
    # Z
    z_entry = create_input_row(right_frame, "Z:", camera, "z", 3)

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
            from controller.xbox_controller import start_xbox_control
            threading.Thread(target=start_xbox_control, args=(camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry)).start()
        else:
            from controller.xbox_controller import stop_xbox_control
            stop_xbox_control()

    ttk.Button(main_frame, text="Toggle Xbox Controller", command=toggle_xbox).grid(row=3, column=0, columnspan=2, pady=10)

    # Bouton Fermer
    def close_application():
        root.destroy()

    ttk.Button(main_frame, text="Fermer", command=close_application).grid(row=4, column=0, columnspan=2, pady=10)

    return camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry

def create_input_row(frame, label_text, camera, attribute, row):
    ttk.Label(frame, text=label_text).grid(row=row, column=2, padx=5, pady=5)
    entry = ttk.Entry(frame, width=10, justify="center")
    entry.insert(0, "0")
    entry.grid(row=row, column=3, padx=5, pady=5)
    ttk.Button(frame, text="-10", command=lambda: update_value(entry, -10, camera, attribute)).grid(row=row, column=1, padx=2, pady=5)
    ttk.Button(frame, text="-5", command=lambda: update_value(entry, -5, camera, attribute)).grid(row=row, column=0, padx=2, pady=5)
    ttk.Button(frame, text="+5", command=lambda: update_value(entry, +5, camera, attribute)).grid(row=row, column=4, padx=2, pady=5)
    ttk.Button(frame, text="+10", command=lambda: update_value(entry, +10, camera, attribute)).grid(row=row, column=5, padx=2, pady=5)
    entry.bind("<KeyRelease>", lambda event: on_entry_change(event, camera, attribute))
    return entry