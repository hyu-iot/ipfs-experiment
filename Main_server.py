import sys
import socket
import selectors
import types
import subprocess
import time
from datetime import datetime



sel = selectors.DefaultSelector()

# f = open(sys.argv[1], 'r')
# lines = f.readlines()
# messages = {"id": [] , "command": []}
# for line in lines:
#     line_v = line.strip()
#     if line_v[0] == '#':
#         continue
#     messages["id"].append(line_v.split('\n')[0].split(" ",maxsplit=1)[0])
#     messages["command"].append(line_v.split('\n')[0].split(" ",maxsplit=1)[1])
# f.close()
# print(messages)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

client_list = {"sock":[] , "id":[], "data" : [] }
command_client = {"sock":[] , "id":[], "data" : []}
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            result = recv_data.decode('utf-8')
            if result[:len("Hello")] == "Hello":
                data.outb += "yeongbin, Thank you for your connection".encode('utf-8')
                client_list["sock"].append(sock)
                client_list["id"].append("yeongbin")
                client_list["data"].append(data)
                print(f"Received {recv_data} from client yeongbin")
                print(client_list)
            elif result[:7] == "Command":
                print("ffff")
            elif result[:11] == "Comm_client":
                data.outb += "Thank you for your connection".encode('utf-8')
                command_client["sock"].append(sock)
                command_client["id"].append("yeongbin")
                command_client["data"].append(data)
                print(f"Received {recv_data} from client yeongbin")
                print(command_client)
            elif result[:11] == "client_info":
                data.outb += client_list["id"][0].encode('utf-8')
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            # sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


# if len(sys.argv) != 3:
#     print(f"Usage: {sys.argv[0]} <host> <port>")
#     sys.exit(1)
port = 65432
host, port = 'localhost', port
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
