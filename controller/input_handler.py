# controller/input_handler.py
import tkinter as tk
from model.camera import Camera
from model.opentrack_sender import send_data_to_opentrack
from config import app_config



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
    send_data_to_opentrack(pitch, yaw, roll, x, y, z, app_config["opentrack_port"])


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

# Synchronisation du champ de saisie avec le slider
def on_entry_change(event, camera, attribute, slider):
    try:
        value = float(event.widget.get())
        setattr(camera, attribute, value)
        slider.set(value)
        send_data(camera)
    except ValueError:
        pass

# Synchronisation du slider avec le champ de saisie
def on_slider_change(val, entry, camera, attribute):
    value = float(val)
    entry.delete(0, tk.END)
    entry.insert(0, f"{value:.2f}")
    setattr(camera, attribute, value)
    send_data(camera)



def set_absolute_value(entry, val, camera, attribute):
    """
    Met directement l'Entry à `val`,
    met camera.<attribute> = val,
    et envoie à OpenTrack.
    """
    entry.delete(0, tk.END)
    entry.insert(0, f"{val:.2f}")  # Affichage formaté dans l'Entry
    setattr(camera, attribute, val) # Mise à jour de l'objet camera
    send_data(camera)               # Envoi à OpenTrack