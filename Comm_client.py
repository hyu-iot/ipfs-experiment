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
import csv
from ast import literal_eval

hello_rc = 0
hello_cc = 1
hello_ms = 2
command_rc = 3
command_cc = 4
command_ms = 5
result_default = 15
result_rc_mf = 16
result_rc_af = 17
result_ms = 7
client_info_cc = 10
client_info_ms = 11
add_message = 20
bytes_num = 1024




sel = selectors.DefaultSelector()

bytes_num = bytes_num

# messages = [b"Message 1 from client.", b"Message 2 from client."]

# f = open(sys.argv[2], 'r')
id = "command client"
# lines = f.readlines()
# for line in lines:
#     messages.append((line.split('\n')[0]).encode('utf-8'))
#     f.close()


f = open(sys.argv[2], 'r')
lines = f.readlines()
send_command = {"index": [] , "block" :[], "command": []}
for line in lines:
    line_v = line.strip()
    if line_v[0] == '#':
        continue
    send_command["index"].append(line_v.split('\n')[0].split(" ",maxsplit=2)[0])
    send_command["block"].append(line_v.split('\n')[0].split(" ",maxsplit=2)[1])
    send_command["command"].append(line_v.split('\n')[0].split(" ",maxsplit=2)[2])
f.close()
print(send_command)

def str2sec(x):
    h, m, s = x.strip().split(':') 
    return float(h)*3600 + float(m)*60 + float(s) #int() 

def make_csv(dic):
    with open('result_1.csv', 'w', newline='') as csvfile:
        fieldnames = ['client_id','command', 'result']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(len(dic['command'])):
            client_id_0 = dic["client_id"][i]
            command = dic['command'][i]
            result_0 = dic['result'][i]
            # print(client_id, command, result_0)
            writer.writerow({'client_id': client_id_0, 'command': command, 'result': result_0})
    kr_ = pd.read_csv("result_1.csv", converters={"result": literal_eval})
    kr_["Duration of Time"] = ''
    kr_["Timestamp"] = 0
    kr_["Duration of Time(sec)"] = ''
    for i,j in enumerate(kr_["command"]):
        if j[:8] == "ipfs add":
            kr_["Duration of Time"][i] = kr_["result"][i][1]
            kr_["Timestamp"][i] = kr_["result"][i][2]
            kr_["Duration of Time(sec)"][i] = str2sec(kr_["result"][i][1])
            kr_["result"][i] = kr_["result"][i][0]
        elif j == "Timeout expired":
            kr_["Duration of Time"][i] = None
            kr_["Timestamp"][i] = None
            kr_["Duration of Time(sec)"][i] = None
            kr_["result"][i] = None
        else:
            kr_["Duration of Time"][i] = kr_["result"][i][0]
            kr_["Timestamp"][i] = kr_["result"][i][1]
            kr_["Duration of Time(sec)"][i] = str2sec(kr_["result"][i][0])
            kr_["result"][i] = None
    kr_.columns.values[2] = "Hash value"
    kr_.to_csv('result_1.csv',index=False)
   

def split_result(res, total_len):
    res_list = []
    num3 = 0
    while True:
        if total_len == num3:
            break
        num = int(res[0])
        payload_len = int(res[1:1+num])
        result = res[1+num:1+num+payload_len]
        res_list.append(result)
        print(result)
        num3 += num +1 +payload_len
        res = res[1+num+payload_len:]
    return res_list


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
        
def sub_write_bytes(sub_message):
    str_length = str(len(sub_message)-17)
    str_length_len = str(len(str_length))
    
    return str_length_len + str_length + sub_message


def payload_buf_length(buffer):
    num = 0;
    for i in range(4):
        num |= buffer[i] << 8*(3-i) 

    return num

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

clients_list = []
total_result_list = {"client_id" : [], "command":[], "result": []}
command = ""
choice_num = 0
block_num = 0
recv_num = 0
send_num = 0
blocking = 0
reply_num = 0
hash_val = ''
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    global clients_list
    global command
    global choice_num
    global block_num
    global recv_num, send_num, blocking, reply_num
    global hash_val
    if mask & selectors.EVENT_READ:
        start_time = datetime.now()
        recv_data = sock.recv(bytes_num)  # Should be ready to read
        if recv_data:
            data.recv_total += len(recv_data)
            total_len = len(recv_data)
            while True:

                num1 = payload_buf_length(recv_data[2:6])
                print(f"total {total_len}, num {num1+6}")
                total_len -= (num1 + 6)

                if recv_data[0] == add_message:
                    print(f"Addition to messages {recv_data[6:6+num1].decode('utf-8')}")
                # print(recv_data[:7])
                # print(f"Received command {recv_data} ")
                if recv_data[0] == hello_ms:
                    messages_buf = paylsload_concat(client_info_cc,"please client's info")
                    data.outb += messages_buf
                elif recv_data[0] == client_info_ms:
                    print(f"Receive the message: {recv_data[6:6+num1]}")
                    clients_list = recv_data[6:6+num1].decode('utf-8').split(" ")
                    print(clients_list)
                    clients_num = len(clients_list)
                    print(f"client number : {clients_num}")
                    command = send_command["command"][0]
                    choice_num = int(send_command["index"][0])
                    command_str = sub_write_bytes(command)
                    messages_buf = payload_concat(command_cc,str(len(clients_list[choice_num])) + clients_list[choice_num] + command_str)
                    data.outb += messages_buf
                    sent = sock.send(data.outb) 
                    data.outb = data.outb[sent:]
                    del send_command["command"][0] , send_command["index"][0], send_command["block"][0]
                    send_num += 1
                    print(f"Send the messages: {messages_buf[6:].decode('utf-8')}")

                if recv_data[0] == result_ms:
                    recv_num += 1
                    print(f"Receive the message: {recv_data[6:6+num1].decode('utf-8')}, len : {len(recv_data[6:6+num1].decode('utf-8'))}")
                    
                    recv_result = (recv_data[6:6+num1].decode('utf-8')).strip("\n")
                    print(recv_result)
                    sp_result = split_result(recv_result, num1)
                    print(sp_result)
                    total_result_list["client_id"].append(sp_result[0])
                    total_result_list["command"].append(sp_result[1])
                    total_result_list["result"].append(sp_result[2:])
                    print(total_result_list)
                    if ((blocking == 1) & (recv_num == send_num)) | (blocking == 0):
                        while len(send_command["command"]):
                            command = send_command["command"][0]
                            blocking = int(send_command["block"][0]) 
                            print(command)  
                            if ('add' in command):
                                reply_num = 0                    
                            if ('$1' in command):
                                if (block_num == 0 | reply_num == 0):
                                    hash_val = sp_result[2]
                                    print(hash_val)
                                    print("Input hash value")
                                    command = command.replace('$1', hash_val)
                                else:
                                    print(hash_val)
                                    print("Input hash value")
                                    command = command.replace('$1', hash_val)
                                reply_num += 1
                            clients_num = len(clients_list)
                            choice_num = int(send_command["index"][0])
                            command_str = sub_write_bytes(command)
                            messages_buf = payload_concat(command_cc,str(len(clients_list[choice_num])) + clients_list[choice_num] + command_str)
                            data.outb += messages_buf
                            sent = sock.send(data.outb) 
                            data.outb = data.outb[sent:]
                            send_num += 1
                            print(f"Send the messages: {messages_buf[6:].decode('utf-8')}")                            
                            if (send_command["block"][0] == "1") & (len(send_command["command"]) != 1):    
                                del send_command["command"][0] , send_command["index"][0], send_command["block"][0]
                                break
                            del send_command["command"][0] , send_command["index"][0], send_command["block"][0]                        
                            block_num += 1
                    block_num = 0
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


# if len(sys.argv) != 3:
#     print(f"Usage: {sys.argv[0]} <host info> <command file>")
#     sys.exit(1)


ip_data = pd.read_csv(sys.argv[1])
print(ip_data["id"][0])
port = 7001

start_connections(ip_data["ip_address"][1] , port, len(ip_data))

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            time.sleep(50)
            start_connections(ip_data["ip_address"][1] , port, len(ip_data))
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    make_csv(total_result_list)
    print("File creation")
    sel.close()
