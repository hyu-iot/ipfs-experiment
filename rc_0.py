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

hello_rc = 0
hello_cc = 1
hello_ms = 2
command_rc = 3
command_cc = 4
command_ms = 5
result_rc = 6
result_ms = 7
client_info_cc = 10
client_info_ms = 11
add_message = 20
bytes_num = 1024




sel = selectors.DefaultSelector()

id = "yeongbin"
execute_file = "loop.py" 

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

def payload_concat(msg_type, msg):
    messages_len = len(msg) + 4 + 1
    messages = bytearray(messages_len)
    messages[0] = int(hex(msg_type),16)
    if len(msg) + 5 > bytes_num:
        messages[1] = int(hex(1),16)
    else:
        messages[1] = int(hex(0),16)
    messages[2:6] = write_bytes(len(msg))
    messages[6:] = bytes.fromhex(msg.encode('utf-8').hex())

    return messages


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
        messages_buf = payload_concat(hello_rc, id)
        print(messages_buf)
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
        recv_data = sock.recv(bytes_num)  # Should be ready to read
        if recv_data:
            print(recv_data)
            data.recv_total += len(recv_data)

            total_len = len(recv_data)
            print(recv_data)
            while True:
                num1 = payload_buf_length(recv_data[2:6])
                print(f"total {total_len}, num {num1+6}")
                total_len -= (num1 + 6)

                if recv_data[0] == command_ms:
                    print(f"Receive the message: {recv_data[6:6+num1].decode('utf-8')}")
                    
                    comm_data = recv_data[6:6+num1].decode('utf-8').split(" ")
                    # comm_data.insert(0,'time')
                    # comm_data.insert(1,'python3')
                    # comm_data.insert(2,execute_file)
                    comm_data.insert(0,'python3')
                    comm_data.insert(1,execute_file)
                    comm_data.insert(2,'time')
                    
                    print(comm_data)                
                    cpu_usage, memory_usage = _check_usage_of_cpu_and_memory()
                    fd_popen = subprocess.Popen(comm_data, stdout=subprocess.PIPE)
                    cpu_usage, memory_usage = _check_usage_of_cpu_and_memory()

                    try:
                        outs, err = fd_popen.communicate(timeout=15)
                    except TimeoutError:
                        fd_popen.kill()
                    finally:
                        pass
                    if outs:
                        comm_recv_str = outs.decode('utf-8')
                    else:
                        comm_recv_str = err.decode('utf-8')

                    cpu_usage, memory_usage = _check_usage_of_cpu_and_memory()
                    io = psutil.net_io_counters()
                    bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv
                    print(f"Upload usage: {get_size(io.bytes_sent)}   "
                            f", Download usage: {get_size(io.bytes_recv)}   ")
                    print(len(comm_recv_str))
                    print(type(len(comm_recv_str)))
                    messages_buf = payload_concat(result_rc, comm_recv_str)
                    data.outb += messages_buf
                    recv_time = datetime.now()
                    print(f"timestamp: {recv_time - start_time}")

                elif recv_data[0] == hello_ms:
                    print(f"Receive the message: {recv_data[6:6+num1].decode('utf-8')}")
                if total_len <= 0:
                    break
                recv_data = recv_data[6+num1:]
                    
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            # sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb) 
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
