import sys
import socket
import selectors
import types
import subprocess
import time
from datetime import datetime
import psutil



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
            recv_data_str = recv_data.decode('utf-8')
            if recv_data_str[:len("Hello")] == "Hello":
                name = recv_data_str.split(" ")[1]
                data.outb += "Hello, ".encode('utf-8')
                data.outb += name.encode('utf-8')
                reply_block = 0
                for j,k in enumerate(client_list["id"]):
                    if k == name:
                        print(f"Received {recv_data} from client {name}")
                        del client_list["data"][j], client_list["sock"][j]
                        client_list["data"].append(data)
                        client_list["sock"].append(sock)
                        reply_block = 1
                        break
                if reply_block == 1:
                    pass
                else:                
                    client_list["sock"].append(sock)
                    client_list["id"].append(name)
                    client_list["data"].append(data)
                print(client_list)
            elif recv_data_str[:7] == "Command":
                print(recv_data_str.split(" ")[1])
                for i,j in enumerate(client_list["id"]):
                    if recv_data_str.split(" ")[1] == j:
                        print("여기")
                        print(recv_data_str.encode('utf-8'))
                        sock = client_list["sock"][i] 
                        data = client_list["data"][i] 
                        data.outb += recv_data_str.encode('utf-8')
                        sent = sock.send(data.outb)  # Should be ready to write
                        data.outb = data.outb[sent:]
            elif recv_data_str[:6] == "result":
                sock = command_client["sock"][0] 
                data = command_client["data"][0]
                data.outb = recv_data_str.encode('utf-8')
                print(f"Echoing {data.outb!r} to {data.addr}")
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]
                time.sleep(3)
            elif recv_data_str[:11] == "Comm_client":
                data.outb += "Thank you for your connection".encode('utf-8')
                if not command_client["sock"]:    
                    command_client["sock"].append(sock)
                    command_client["id"].append("computer")
                    command_client["data"].append(data)
                else:    
                    command_client["sock"][0] = sock
                    command_client["id"][0] = "computer"
                    command_client["data"][0] = data
                print(f"Received {recv_data} from client computer")
                print(command_client)
            elif recv_data_str[:11] == "client_info":
                data.outb += "client_info ".encode('utf-8')
                for i in range(len(client_list["id"])):
                    data.outb += client_list["id"][i].encode('utf-8')
                    data.outb += " ".encode('utf-8')
            else:
                print(f"Closing connection to {data.addr} !!")
                sel.unregister(sock)
        else:
            print(f"Closing connection to {data.addr}")
            for i,j in enumerate(client_list["sock"]):
                if j == sock:
                    del client_list["data"][i], client_list["id"][i], client_list["sock"][i]
            print(client_list["id"])
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
port = 7001
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
    lsock.close()
    sel.close()
    print("Finished")
