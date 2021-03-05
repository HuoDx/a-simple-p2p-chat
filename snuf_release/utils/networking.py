import socket
from snuf_release.utils import serialization

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_dict(server_ip, server_port, message: dict):
    global client_socket
    client_socket.sendto(serialization.serialize(message), (server_ip, server_port))
