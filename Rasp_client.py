import sys
import socket
import selectors
import types
import pandas as pd
import os
import subprocess
import time
from datetime import datetime



sel = selectors.DefaultSelector()

messages = ["Hello yunsang"]

def start_connections(host, port, ip_num):
        server_addr = (host,port)
        connid = ip_num
        print(f"Starting connection {connid} to {server_addr}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(sock)
        sock.setblocking(True)
        try:
            sock.connect(server_addr)
        except:
            print("exception occurred")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        print(messages[0].encode('utf-8'))
        to_list = []
        to_list.append(messages[0].encode('utf-8'))
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=len(to_list[0]),
            recv_total=0,
            messages=list(to_list),
            outb=b"",
        )
        sel.register(sock, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        start_time = datetime.now()
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.recv_total += len(recv_data)
            # print(recv_data[:7])
            print(f"Received command {recv_data} ")
            result = recv_data.decode('utf-8')
            if result[:7] == "Command":
                # result = recv_data.decode('utf-8')
                res = result.split(' ')[2]
                fd_popen = subprocess.Popen(res, stdout=subprocess.PIPE).stdout
                comm_result = fd_popen.read().strip()
                data.outb += "result ".encode('utf-8')
                data.outb += comm_result
                recv_time = datetime.now()
                data.outb += bytes(" runtime ", 'utf-8')
                data.outb += bytes(str(recv_time - start_time)+str("\n"), 'utf-8')
                print(f"timestamp: {recv_time - start_time}")
            elif result[:5] == "Hello":
                # data.outb += "Hello".encode('utf-8')
                print("Good!")
                
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            # sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)  # Should be ready to write
            time.sleep(1)
            data.outb = data.outb[sent:]


# if len(sys.argv) != 3:
#     print(f"Usage: {sys.argv[0]} <host info> <command file>")
#     sys.exit(1)


ip_data = pd.read_csv(sys.argv[1])
print(ip_data["id"][0])
port = 65432

start_connections(ip_data["ip_address"][0] , port, len(ip_data))
try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
