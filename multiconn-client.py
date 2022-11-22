#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import pandas as pd
import os
import subprocess
import time


sel = selectors.DefaultSelector()
# messages = [b"Message 1 from client.", b"Message 2 from client."]

f = open(sys.argv[2], 'r')
lines = f.readlines()
messages = {"id": [] , "command": []}
for line in lines:
    line_v = line.strip()
    if line_v[0] == '#':
        continue
    messages["id"].append(line_v.split('\n')[0].split(" ")[0])
    messages["command"].append(line_v.split('\n')[0].split(" ")[1])
f.close()


f = open("command.txt", 'r')
a = []
dic = {"id": [] , "command": []}
lines = f.readlines()
for line in lines:
    line_v = line.strip()
    if line_v[0] == '#':
        continue
    dic["id"].append(line.split('\n')[0].split(" ")[0])
    dic["command"].append(line.split('\n')[0].split(" ")[1])
f.close()
socket_list = []
def start_connections(host, port, ip_num):
    for i in range(0, ip_num):
        server_addr = (host[i],port)
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(True)
        re_val = sock.settimeout(5)
        try:
            sock.connect(server_addr)
        except:
            print("exception occurred")
            continue
        socket_info = connid , server_addr
        socket_list.append(socket_info)
        print(f"socket list : {socket_list}")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        print(f"message : {messages}")
        to_list = []
        for j in range(len(messages["id"])):
            if messages["id"][j] == str(connid):
                to_list.append(messages["command"][j].encode('utf-8'))        
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
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print(f"Received {recv_data!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host file> <command file>")
    sys.exit(1)



ip_data = pd.read_csv(sys.argv[1])
print(ip_data["id"][0])
port = 65432

start_connections(ip_data["ip_address"] , port, len(ip_data))

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
