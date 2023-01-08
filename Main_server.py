import sys
import socket
import selectors
import types
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
result_default = 15
result_rc_mf = 16
result_rc_af = 17
result_ms = 7
client_info_cc = 10
client_info_ms = 11
add_message = 20
bytes_num = 1024


sel = selectors.DefaultSelector()

def sub_write_bytes(sub_message):
    str_length = str(len(sub_message))
    str_length_len = str(len(str_length))
    
    return str_length_len + str_length +sub_message

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
    if len(msg) + 5 > bytes_num:
        messages[1] = int(hex(1),16)
    else:
        messages[1] = int(hex(0),16)
    messages[2:6] = write_bytes(len(msg))
    messages[6:] = bytes.fromhex(msg.encode('utf-8').hex())

    return messages


def accept_wrapper(sock):
    conn, addr = sock.accept()  
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

client_list = {"sock":[] , "id":[], "data" : [] }
command_client = {"sock":[] , "id":[], "data" : []}
payload_max_num = 0
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    global payload_max_num
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(bytes_num)  # Should be ready to read
        if recv_data:
            total_len = len(recv_data)
            print(recv_data)
            exceeded_num = 0
            while True:
                if total_len <= 0:
                    break
                num1 = payload_buf_length(recv_data[2:6])
                print(f"total {total_len}, num {num1+6}")
                
                total_len -= (num1 + 6)
                if payload_max_num == 1:
                    sock = command_client["sock"][0] 
                    data = command_client["data"][0]
                    messages_buf = payload_concat(add_message,recv_data[:exceeded_num].decode('utf-8'))
                    data.outb += messages_buf
                    sent = sock.send(data.outb) 
                    data.outb = data.outb[sent:]
                    print(f"Receive the message: {recv_data.decode('utf-8')}")
                    payload_max_num = 0
                else:   
                    if recv_data[1] == 1:
                        payload_max_num = 1
                        exceeded_num = num1 - total_len

                    if recv_data[0] == hello_rc:
                        name = recv_data[6:6 + num1].decode('utf-8')
                        print(name)
                        messages_buf = payload_concat(hello_ms, "secure connection")
                        data.outb += messages_buf
                        reply_block = 0
                        for j,k in enumerate(client_list["id"]):
                            if k == name:
                                print(f"Received 'Hello message' from client {name}")
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
                    elif recv_data[0] == command_cc:
                        print(f"Receive the message: {recv_data[6:6+num1].decode('utf-8')}")
                        name_length = int(recv_data[6:8].decode('utf-8'))
                        name = recv_data[8:8+name_length].decode('utf-8')
                        print(name)
                        command_len_type = int(recv_data[8+name_length:9+name_length].decode('utf-8'))
                        command_length = recv_data[9+name_length:9+name_length+command_len_type].decode('utf-8')
                        command = recv_data[9+name_length+command_len_type:6+num1].decode('utf-8')
                        print(command)
                        for i,j in enumerate(client_list["id"]):
                            if name == j:
                                sock = client_list["sock"][i] 
                                data = client_list["data"][i]
                                messages_buf = payload_concat(command_ms,command)
                                data.outb += messages_buf
                                sent = sock.send(data.outb)  # Should be ready to write
                                data.outb = data.outb[sent:]
                    elif recv_data[0] == result_default or recv_data[0] == result_rc_mf or recv_data[0] == result_rc_af:
                        print(f"Receive the message: {recv_data[6:6+num1].decode('utf-8')}")
                        client_id = ""
                        for i,j in enumerate(client_list["sock"]):
                            if sock == j:
                                client_id = client_list["id"][i]  
                                print(client_id)
                        sock = command_client["sock"][0]
                        data = command_client["data"][0]
                        messages_buf = payload_concat(result_ms, sub_write_bytes(client_id) + recv_data[6:6+num1].decode('utf-8'))
                        data.outb = messages_buf
                        print(f"Echoing {data.outb!r} to {data.addr}")
                        sent = sock.send(data.outb)  # Should be ready to write
                        data.outb = data.outb[sent:]

                    elif recv_data[0] == hello_cc:
                        name = recv_data[6:6 + num1].decode('utf-8')
                        print(name)
                        messages_buf = payload_concat(hello_ms, "secure connection")
                        data.outb += messages_buf
                        if not command_client["sock"]:    
                            command_client["sock"].append(sock)
                            command_client["id"].append(name)
                            command_client["data"].append(data)
                        else:    
                            command_client["sock"][0] = sock
                            command_client["id"][0] = name
                            command_client["data"][0] = data
                        print(f"Received hello message from client computer")
                    elif recv_data[0] == client_info_cc:
                        print(f"Receive the message: {recv_data[6:6+num1].decode('utf-8')}")
                        messages_buf = payload_concat(client_info_ms,' '.join(map(str, client_list["id"])))
                        data.outb += messages_buf
                    else:
                        print(f"Closing connection to {data.addr} !!")
                        sel.unregister(sock)
                recv_data = recv_data[6+num1:]
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
