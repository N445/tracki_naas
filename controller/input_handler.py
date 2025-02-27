﻿# controller/input_handler.py
import tkinter as tk
from model.camera import Camera
from model.opentrack_sender import send_data_to_opentrack



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
def reset_values(camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry, pitch_slider, yaw_slider, roll_slider, x_slider, y_slider, z_slider):
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

    pitch_slider.set(0)
    yaw_slider.set(0)
    roll_slider.set(0)
    x_slider.set(0)
    y_slider.set(0)
    z_slider.set(0)

    send_data(camera)

# Variable de contrôle pour éviter les mises à jour récursives
updating = False

# Fonction pour mettre à jour les valeurs de l'objet Camera lorsque les valeurs des champs d'entrée sont modifiées manuellement
def on_entry_change(event, camera, attribute, slider, sensitivity=1):  # Ajout d'une valeur par défaut
    try:
        value = float(event.widget.get())
        setattr(camera, attribute, value)
        slider.set(value / sensitivity)
        send_data(camera)
    except ValueError:
        pass

# Fonction pour mettre à jour les valeurs de l'objet Camera lorsque les valeurs des sliders sont modifiées
def on_slider_change(val, entry, camera, attribute, sensitivity):
    value = float(val) * sensitivity
    entry.delete(0, tk.END)
    entry.insert(0, f"{value:.2f}")
    setattr(camera, attribute, value)
    send_data(camera)
