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

execute_file = "loop.py" 
command = "ls"
command_0 = "-l"
fd_popen = subprocess.Popen(['python3', execute_file, command, command_0], stdout=subprocess.PIPE).stdout
comm_result = fd_popen.read().strip()
print(comm_result)
print(comm_result.decode('utf-8'))
print(type(comm_result.decode('utf-8')))