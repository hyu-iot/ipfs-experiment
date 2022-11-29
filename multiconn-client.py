#!/usr/bin/env python3

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

# Load the command.txt file
f = open(sys.argv[2], 'r')
lines = f.readlines()
messages = {"id": [] , "command": []}
for line in lines:
    line_v = line.strip()
    if line_v[0] == '#':
        continue
    messages["id"].append(line_v.split('\n')[0].split(" ",maxsplit=1)[0])
    messages["command"].append(line_v.split('\n')[0].split(" ",maxsplit=1)[1])
f.close()
print(messages)

sss_list =[]
def connection(ip_data, port):
    socket_list = []
    for i in range(len(ip_data)):
        connect_id = ip_data["id"][i]
        server_addr = (ip_data["ip_address"][i] , port)
        print(f"Starting connection {connect_id} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(True)
        re_val = sock.settimeout(5)
        try:
            sock.connect(server_addr)
        except:
            print("Warning!!")
            print(f"Fail to connect {server_addr}")
            continue
        socket_info = connect_id , sock
        socket_list.append(socket_info)
    return socket_list

def put_message(messages, id, sock_list):
    # for i in range(len(messages["id"])):
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    to_list = []
    # to_list.append(messages["command"][i].encode('utf-8'))        
    to_list.append(messages.encode('utf-8'))        
    length = 0
    soc_num = 100
    for j in range(len(sock_list)):
        if id == str(sock_list[j][0]):
            soc_num = j 
    if soc_num == 100:
        return 0
    connid = sock_list[soc_num][0]
    sock = sock_list[soc_num][1]
    for to in to_list:
        length += len(to)
    data = types.SimpleNamespace(
        connid=connid,
        msg_total=length,
        recv_total=0,
        messages=list(to_list),
        outb=b"",
    )
    sel.register(sock, events, data=data)
    return 1

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print(f"Received {recv_data!r} from connection {data.connid}")
            dt = datetime.now()
            save_result = str(datetime.timestamp(dt)) + " R node " + str(data.connid) + " result "  + str(recv_data)
            save_result += "\n"
            print(save_result)
            sss_list.append(save_result)
            time.sleep(0.1)
            data.recv_total += len(recv_data)
            sel.unregister(sock)
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)
            dt = datetime.now()
            save_send_message = str(datetime.timestamp(dt)) + " T node " + str(data.connid) + " command "  + str(data.outb)
            save_send_message += "\n"
            print(save_send_message)
            sss_list.append(save_send_message)  # Should be ready to write
            time.sleep(0.1)
            data.outb = data.outb[sent:]


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host file> <command file>")
    sys.exit(1)



ip_data = pd.read_csv(sys.argv[1])
port = 65432
sock_list = connection(ip_data,port)
# put_message(messages=messages, sock_list=sock_list)
f = open("log_result.txt", 'w')
try:
    # events = sel.select(timeout=1)
    for i in range(len(messages["id"])):
        put_message(messages=messages["command"][i], id= messages["id"][i], sock_list=sock_list)
        while True:
            events = sel.select(timeout=1)
            if events:
                for key, mask in events:
                    service_connection(key, mask)
        # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    print(f"여기!!!{sss_list}")
    for i in range(len(sss_list)):
        f.write(sss_list[i])
    f.close()
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()

