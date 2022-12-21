import sys
import socket
import selectors
import types
import pandas as pd
import os
import subprocess
import time
from datetime import datetime
import psutil
import random



hello_rc = 0
hello_cc = 1
hello_ms = 2
command_rc = 3
client_info_cc = 10
client_info_ms = 11
sel = selectors.DefaultSelector()
# messages = [b"Message 1 from client.", b"Message 2 from client."]

# f = open(sys.argv[2], 'r')
id = "command client"
# lines = f.readlines()
# for line in lines:
#     messages.append((line.split('\n')[0]).encode('utf-8'))
#     f.close()


f = open(sys.argv[2], 'r')
lines = f.readlines()
send_command = {"id": [] , "command": []}
for line in lines:
    line_v = line.strip()
    if line_v[0] == '#':
        continue
    send_command["id"].append(line_v.split('\n')[0].split(" ",maxsplit=1)[0])
    send_command["command"].append(line_v.split('\n')[0].split(" ",maxsplit=1)[1])
f.close()
print(send_command)

def write_bytes(str_len):
    str_buf = bytearray(4)
    num = str_len
    order = 0
    while True:
        if num == 0:
            break
        str_buf[3-order] = int(hex(num % 256),16)
        num = num >> 8
        order += 1
    return str_buf
        
def payload_buf_length(buffer):
    num = 0;
    for i in range(4):
        num |= buffer[i] << 8*(3-i) 

    return num

def payload_concat(msg_type, msg):
    messages_len = len(msg) + 4 + 1
    messages = bytearray(messages_len)
    messages[0] = int(hex(msg_type),16)
    messages[1:5] = write_bytes(len(msg))
    messages[5:] = bytes.fromhex(msg.encode('utf-8').hex())

    return messages

def start_connections(host, port, ip_num):
        server_addr = (host,port)
        connid = ip_num
        print(f"Starting connection {connid} to {server_addr}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(True)
        sock.settimeout(5)
        try:
            sock.connect(server_addr)
        except:
            print("Connection Failed.\nLet's restart to connect to server")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        messages_buf = payload_concat(hello_cc, id)
        to_list = []
        to_list.append(messages_buf)
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
        recv_data = sock.recv(4096)  # Should be ready to read
        if recv_data:
            data.recv_total += len(recv_data)
            # print(recv_data[:7])
            # print(f"Received command {recv_data} ")
            if recv_data[0] == hello_ms:
                data.outb += "client_info".encode('utf-8')
            elif recv_data[0] == client_info_ms:
                print(recv_data.split(" ")[1:-1])
                clients_list = recv_data.split(" ")[1:-1]
                print(clients_list)
                clients_num = len(clients_list)
                print(f"client number : {clients_num}")
                for command in send_command["command"]:
                    choice_num = random.randrange(0, clients_num)
                    print(f"choice num = {choice_num}")
                    print("Command ".encode('utf-8') + clients_list[choice_num].encode('utf-8') + (" " + command).encode('utf-8'))
                    data.outb += "Command ".encode('utf-8') + clients_list[choice_num].encode('utf-8') + (" " + command).encode('utf-8')
                    sent = sock.send(data.outb) 
                    data.outb = data.outb[sent:]
            if recv_data[:6] == "result":
                print(f"Final result")
                print(recv_data.encode("utf-8"))

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
port = 7001

start_connections(ip_data["ip_address"][0] , port, len(ip_data))

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            time.sleep(50)
            start_connections(ip_data["ip_address"][0] , port, len(ip_data))
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
