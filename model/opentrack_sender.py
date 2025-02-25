# model/opentrack_sender.py
import socket
import logging
import struct

# Configuration
OPENTRACK_IP = '127.0.0.1'  # Adresse IP d'OpenTrack (généralement localhost)
OPENTRACK_PORT = 4242       # Port par défaut d'OpenTrack (vérifiez et modifiez si nécessaire)

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Créer un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_data_to_opentrack(pitch, yaw, roll, x, y, z):
    # Créer un message de données au format FreeTrack
    message = f"{pitch} {yaw} {roll} {x} {y} {z}"

    data = struct.pack('dddddd', x, y, z, yaw, pitch, roll)

    # Envoyer le message à OpenTrack
    sock.sendto(data, (OPENTRACK_IP, OPENTRACK_PORT))
    logging.debug(f"Sent data to OpenTrack: {message}")
