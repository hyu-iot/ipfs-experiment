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

# command = sys.argv[1:]
# comm_str = ' '.join(s for s in command)
# count = 0
# fd_open = os.popen(comm_str).read()
# # print(fd_open)

# messages = bytearray(18)
# messages[0] = int(hex(5),16)

# print(messages)

# messages = messages[5:]

# print(messages)

# print(len("time ipfs cat QmTZntCxWgZDooSEdSCnePpZy5nom2cbMr6edZgLgX7AnN > read_file1"))
import csv

result = {'command': ['head -c 10240000 < /dev/urandom > test_file1', 'time ipfs add test_file1', 'time ipfs cat QmRJp6VcQNJYw9P6EpJMSQ4aM3CDEPboXD7fYWDfuhUJtH > read_file1', 'head -c 102400000 < /dev/urandom > test_file5', 'time ipfs add test_file5', 'time ipfs cat QmRJp6VcQNJYw9P6EpJMSQ4aM3CDEPboXD7fYWDfuhUJtH > read_file5', 'head -c 1024000000 < /dev/urandom > test_file6', 'time ipfs add test_file6', 'time ipfs cat QmRJp6VcQNJYw9P6EpJMSQ4aM3CDEPboXD7fYWDfuhUJtH > read_file6'], 'result': [['0:00:00.034477'], ['QmRJp6VcQNJYw9P6EpJMSQ4aM3CDEPboXD7fYWDfuhUJtH', '0:00:01.663138'], ['0:00:00.147699'], ['0:00:00.237123'], ['QmdKDzAnc8of2n5TYnb4Qy774BWKaAdh7yGCVia1kM7R6p', '0:00:14.220975'], ['0:00:00.133051'], ['0:00:02.426554'], ['QmTZ7QdjgNZCaqFHTawjnhLcJw9xea7WZcHhpy7Bjcezp5', '0:02:19.466247'], ['0:00:00.135504']]}
print(len(result['command']))
with open('result.csv', 'w', newline='') as csvfile:
    fieldnames = ['command', 'result']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i in range(len(result['command'])):
        command = result['command'][i]
        result_0 = result['result'][i]
        print(command, result_0)
        writer.writerow({'command': command, 'result': result_0})