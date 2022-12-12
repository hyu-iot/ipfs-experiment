import socket
import os
import subprocess
import sys
import pandas as pd
import time
from threading import Timer


def send_message (s, command_list):
    for command in command_list:    
            # s.sendall(b"ls")
        com = command.encode('utf-8')
        print(com)
        print(type(com))
        s.sendall(com)
        time.sleep(0.1)
        data = s.recv(1024)
        u_data = data.decode('utf-8')
        list_data = u_data.split('\n')
        sub_list.append(list_data)
    total_list.append(sub_list)
    s.close()


ip_data = pd.read_csv(sys.argv[1])
print(ip_data["id"][0])
print(len(ip_data))

# HOST = ip_data["ip_address"][0]  # Standard loopback interface address (localhost)
# print(HOST)
PORT = 7001  # The port used by the server

f = open(sys.argv[2], 'r')
command_list = []
lines = f.readlines()
for line in lines:
    command_list.append(line.split('\n')[0])
f.close()
total_list = []
timeout = 5
for i in range(len(ip_data)):
    sub_list = []
    start_time = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        while True:
            a = s.connect_ex((ip_data["ip_address"][i], PORT))
            if a == 0:
                send_message(s, command_list)
                break
            else:
                if(time.time() - start_time > timeout):
                    s.close()
                    break
                else:
                    time.sleep(0.1)
                    s.close()
                    continue

    # a = connection_timeout(5,command_list)
    print(a)
    if a != 0:
        print("Times up, next connection")
        continue
    print(f"어떻게 나올까? {a}")
        # time.sleep(5) # 5 sec delay when cannot connect to the server
    # for command in command_list:    
    #         # s.sendall(b"ls")
    #     com = command.encode('utf-8')
    #     print(com)
    #     print(type(com))
    #     s.sendall(com)
    #     time.sleep(0.1)
    #     data = s.recv(1024)
    #     u_data = data.decode('utf-8')
        
    #     list_data = u_data.split('\n')
    #     sub_list.append(list_data)
    # total_list.append(sub_list)
    # s.close()
print("Received")

print(total_list)

