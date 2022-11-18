import socket
import os
import subprocess


# HOST = "192.168.0.100"  # Standard loopback interface address (localhost)
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Command {data} ")
            result = data.decode('utf-8')
            fd_popen = subprocess.Popen(result, stdout=subprocess.PIPE).stdout
            data = fd_popen.read().strip()
            fd_popen.close()
            conn.sendall(data)
