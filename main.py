import tkinter as tk
from gui import create_gui

def main():
    root = tk.Tk()
    root.title("OpenTrack Data Sender")

    camera, pitch_entry, yaw_entry, roll_entry, x_entry, y_entry, z_entry = create_gui(root)

    # Lancer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == "__main__":
    main()