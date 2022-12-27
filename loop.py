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

def sub_write_bytes(sub_message):
    str_length = str(len(sub_message))
    str_length_len = str(len(str_length))
    
    return str_length_len + str_length +sub_message

command = sys.argv[1:]
comm_str = ' '.join(s for s in command)
count = 0
start_time = datetime.now()
fd_open = os.popen(comm_str).read()
time_interval = datetime.now() - start_time
print(fd_open + sub_write_bytes(str(time_interval)))