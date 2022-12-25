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
while True:
    print("1")

command = sys.argv[1:]
comm_str = ' '.join(s for s in command)
count = 0
start_time = datetime.now()
fd_open = os.popen(comm_str).read()
time_interval = datetime.now() - start_time
print(str(len(fd_open)) + fd_open + str(len(str(time_interval))) + str(time_interval))