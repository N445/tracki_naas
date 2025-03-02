# tracki-naas.py
import tkinter as tk
from model.camera import Camera
from view.gui import create_gui
import os

def main():
    root = tk.Tk()
    root.title("Tracki Naas : OpenTrack Data Sender")

    # Définir l'icône de la fenêtre
    #icon_path = os.path.join(os.path.dirname(__file__), "images/tracki-naas.ico")
    #root.iconbitmap(icon_path)

    camera = Camera()
    create_gui(root, camera)

    # Lancer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == "__main__":
    main()
