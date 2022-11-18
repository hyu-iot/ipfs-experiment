import socket
import os
import subprocess
import sys
import pandas as pd

result = pd.read_csv(sys.argv[1])
print(result["id"][0])
print(len(result))

HOST = result["ip_address"][0]  # Standard loopback interface address (localhost)
print(HOST)
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"ls")
    data = s.recv(1024)
    result = data.decode('utf-8')


print("Received")

list = result.split('\n')

print(list)

