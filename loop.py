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
print(fd_open)
