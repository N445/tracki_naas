import tkinter as tk
from tkinter import ttk
import threading
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
    ttk.Label(left_frame, text="Pitch/Yaw/Roll", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=2, pady=5)

    # Pitch
    pitch_entry, pitch_slider = create_input_row(left_frame, "Pitch:", camera, "pitch", 1, -180, 180)
    # Yaw
    yaw_entry, yaw_slider = create_input_row(left_frame, "Yaw:", camera, "yaw", 3, -180, 180)
    # Roll
    roll_entry, roll_slider = create_input_row(left_frame, "Roll:", camera, "roll", 5, -180, 180)

    # Section X/Y/Z
    ttk.Label(right_frame, text="X/Y/Z", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=2, pady=5)

    # X
    x_entry, x_slider = create_input_row(right_frame, "X:", camera, "x", 1, -100, 100)
    # Y
    y_entry, y_slider = create_input_row(right_frame, "Y:", camera, "y", 3, -100, 100)
    # Z
    z_entry, z_slider = create_input_row(right_frame, "Z:", camera, "z", 5, -100, 100)

    # Boutons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=2, column=0, columnspan=2, pady=10)

    reset_button = ttk.Button(button_frame, text="Reset", command=lambda: reset_values(camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry, pitch_slider, yaw_slider, roll_slider, x_slider, y_slider, z_slider))
    reset_button.grid(row=0, column=0, padx=5)

    close_button = ttk.Button(button_frame, text="Fermer", command=root.destroy)
    close_button.grid(row=0, column=1, padx=5)

    always_on_top = tk.BooleanVar(value=False)
    def toggle_always_on_top():
        always_on_top.set(not always_on_top.get())
        root.attributes("-topmost", always_on_top.get())
    ttk.Button(button_frame, text="Always on Top", command=toggle_always_on_top).grid(row=0, column=2, padx=5)

#    xbox_enabled = tk.BooleanVar(value=False)
#    def toggle_xbox():
#        xbox_enabled.set(not xbox_enabled.get())
#        if xbox_enabled.get():
#            from controller.xbox_controller import start_xbox_control
#            threading.Thread(target=start_xbox_control, args=(root, camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry, xbox_enabled)).start()
#        else:
#            from controller.xbox_controller import stop_xbox_control
#            stop_xbox_control()
#    ttk.Button(button_frame, text="Toggle Xbox Controller", command=toggle_xbox).grid(row=0, column=3, padx=5)

    return camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry

def create_input_row(frame, label_text, camera, attribute, row, min_val, max_val):
    ttk.Label(frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
    
    entry = ttk.Entry(frame, width=10, justify="center")
    entry.insert(0, "0")
    entry.grid(row=row, column=1, padx=5, pady=5)
    
    slider = ttk.Scale(frame, from_=min_val, to=max_val, orient="horizontal", length=300,
                       command=lambda val: on_slider_change(val, entry, camera, attribute))
    slider.set(0)
    slider.grid(row=row + 1, column=0, columnspan=2, padx=4, pady=5, sticky="ew")
    
    entry.bind("<FocusOut>", lambda event: on_entry_change(event, camera, attribute, slider))
    entry.bind("<Return>", lambda event: on_entry_change(event, camera, attribute, slider))
    
    return entry, slider

def on_slider_change(val, entry, camera, attribute):
    value = float(val)
    entry.delete(0, tk.END)
    entry.insert(0, f"{value:.2f}")
    setattr(camera, attribute, value)
    send_data(camera)
