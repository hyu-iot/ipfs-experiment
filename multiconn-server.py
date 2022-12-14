#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import subprocess
import time
from datetime import datetime

sel = selectors.DefaultSelector()


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        start_time = datetime.now()
        recv_data = sock.recv(1024)  # Should be ready to read
        print(recv_data)
        if recv_data:
            print(f"Received command {recv_data} ")
            result = recv_data.decode('utf-8')
            res = result.split(' ')
            print(res)
            fd_popen = subprocess.Popen(res, stdout=subprocess.PIPE).stdout
            comm_result = fd_popen.read().strip()
            print(comm_result)
            print(type(comm_result))
            data.outb += comm_result
            recv_time = datetime.now()
            print(type(recv_time))
            data.outb += bytes(" runtime ", 'utf-8')
            data.outb += bytes(str(recv_time - start_time), 'utf-8')
            print(f"timestamp: {recv_time - start_time}")
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            # sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            time.sleep(1)
            data.outb = data.outb[sent:]


# if len(sys.argv) != 2:
#     print(f"Usage: {sys.argv[0]} <host>")
#     sys.exit(1)

port = 65432
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
    sel.close()
