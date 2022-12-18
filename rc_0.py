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


sel = selectors.DefaultSelector()

messages = ["Hello yunsang"]
execute_file = "loop.py" 

def _check_usage_of_cpu_and_memory():
    
    pid = os.getpid()
    py  = psutil.Process(pid)
    
    cpu_usage   = os.popen("ps aux | grep " + str(pid) + " | grep -v grep | awk '{print $3}'").read()
    cpu_usage   = cpu_usage.replace("\n","")
    
    memory_usage  = round(py.memory_info()[0] /2.**30, 2)
    
    print("cpu usage\t\t:", cpu_usage, "%")
    print("memory usage\t\t:", memory_usage, "%")
    
    return cpu_usage, memory_usage

def get_size(bytes):
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024


def start_connections(host, port, ip_num):
        server_addr = (host,port)
        connid = ip_num
        
        print(f"Starting connection {connid} to {server_addr}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.setblocking(True)
        sock.settimeout(10)
        try:
            sock.connect(server_addr)
        except:
            print("Connection Failed.\nLet's restart to connect to server")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
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
        recv_data = sock.recv(4096)  # Should be ready to read
        if recv_data:
            data.recv_total += len(recv_data)
            
            print(f"Received command  {recv_data} ")
            recv_str = recv_data.decode('utf-8')
            if recv_str[:7] == "Command":
                comm_data = recv_str.split(" ")[2:]
                comm_data.insert(0,'python3')
                comm_data.insert(1,execute_file)
                print(comm_data)
                fd_popen = subprocess.Popen(comm_data, stdout=subprocess.PIPE).stdout
                cpu_usage, memory_usage = _check_usage_of_cpu_and_memory()
                # fd_popen = subprocess.Popen(res, stdout=subprocess.PIPE).stdout
                io = psutil.net_io_counters()
                bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv
                print(f"Upload usage: {get_size(io.bytes_sent)}   "
                        f", Download usage: {get_size(io.bytes_recv)}   ")
                cpu_usage, memory_usage = _check_usage_of_cpu_and_memory()
                comm_recv_str = fd_popen.read().strip()
                cpu_usage, memory_usage = _check_usage_of_cpu_and_memory()
                data.outb += "result ".encode('utf-8')
                data.outb += comm_recv_str
                recv_time = datetime.now()
                data.outb += bytes(" runtime ", 'utf-8')
                data.outb += bytes(str(recv_time - start_time) + str("\n"), 'utf-8')
                print(f"timestamp: {recv_time - start_time}")
            elif recv_str[:5] == "Hello":
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
                
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <host info>")
    sys.exit(1)


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
            time.sleep(10)
            start_connections(ip_data["ip_address"][0] , port, len(ip_data))

except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
    
finally:
    sel.close()
