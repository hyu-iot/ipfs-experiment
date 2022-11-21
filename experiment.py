import socket
import os
import subprocess
import sys

f = open(sys.argv[1], 'r')
command_list = []
lines = f.readlines()
for line in lines:
    command_list.append((line.split('\n')[0]).encode('utf-8'))
f.close()
print(command_list)