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
fd_popen = subprocess.Popen(command, stdout=subprocess.PIPE)
try:
    outs, err = fd_popen.communicate(timeout=15)
except TimeoutError:
    fd_popen.kill()
finally:
    pass

if outs:
    print(outs)
else:
    print(err)