# tracki-naas.py
import tkinter as tk
from model.camera import Camera
from view.gui import create_gui

def main():
    root = tk.Tk()
    root.title("Tracki Naas : OpenTrack Data Sender")

    camera = Camera()
    create_gui(root, camera)

    # Lancer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == "__main__":
    main()
