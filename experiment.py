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

command = sys.argv[1:]
comm_str = ' '.join(s for s in command)
count = 0
fd_open = os.popen(comm_str).read()
# print(fd_open)

messages = bytearray(18)
messages[0] = int(hex(5),16)

print(messages)

messages = messages[5:]

print(messages)

print(len("time ipfs cat QmTZntCxWgZDooSEdSCnePpZy5nom2cbMr6edZgLgX7AnN > read_file1"))