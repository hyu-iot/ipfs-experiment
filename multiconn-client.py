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
messages = []
lines = f.readlines()
for line in lines:
    messages.append((line.split('\n')[0]).encode('utf-8'))
    f.close()

def start_connections(host, port, ip_num):
    # server_addr = (host, port)
    for i in range(0, ip_num):
        # server_addr = (host[i],port)
        server_addr = ('127.0.0.1',6543)
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        start_time = time.time()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(sock)
        sock.setblocking(True)
        # sock.connect_ex(server_addr)
        re_val = sock.settimeout(5)
        # print(re_val)
        try:
            sock.connect(server_addr)
        except:
            print("exception occurred")
        # print(re_val)
        # sock.settimeout(None)
        print(sock)
        # print(f"sock int : {a}")
        # if a == 0:
        #     # send_message(s, command_list)
        #     break
        # else:
        #     if(time.time() - start_time > 5):
        #         sock.close()
        #         break
        #     else:
        #         time.sleep(0.1)
        #         sock.close()
        #         continue
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        print(messages)
        to_list = []
        to_list.append(messages[i])
        print(list(messages[i]))
        print(to_list)
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


# if len(sys.argv) != 4:
#     print(f"Usage: {sys.argv[0]} <host> <port> <num_connections>")
#     sys.exit(1)


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
