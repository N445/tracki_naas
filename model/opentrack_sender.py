# opentrack_sender.py

import socket
import logging
import struct

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

OPENTRACK_IP = '127.0.0.1'
# On enlève OPENTRACK_PORT d’ici pour le passer en paramètre

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_data_to_opentrack(pitch, yaw, roll, x, y, z, port=4242):
    message = f"{pitch} {yaw} {roll} {x} {y} {z}"
    data = struct.pack('dddddd', x, y, z, yaw, pitch, roll)
    sock.sendto(data, (OPENTRACK_IP, port))
    #logging.debug(f"Sent data to OpenTrack (port={port}): {message}")
