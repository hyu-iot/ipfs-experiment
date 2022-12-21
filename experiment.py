hello_rc = 0
hello_cc = 1


id = "yunsang"
execute_file = "loop.py" 


def find_bytes(buf_len):
    str_len = bytearray(4)
    
    str_len[0] = int(hex(150),16)

    return str_len   

print(find_bytes(16)[0])         
print(find_bytes(16))         
print(type(find_bytes(16)[0]))

def write_bytes(str_len):
    str_buf = bytearray(4)
    num = str_len
    order = 0
    while True:
        if num == 0:
            break
        str_buf[3-order] = int(hex(num % 256),16)
        num = num >> 8
        order += 1
    return str_buf
        
def payload_buf_length(buffer):
    num = 0;
    for i in range(4):
        num |= buffer[i] << 8*(3-i) 

    return num


array = write_bytes(123123)
print(array)


payload_buf_length(array)
print(payload_buf_length(array))
messages_len = len(id) + 4 + 1
print(messages_len)
messages = bytearray(messages_len)
messages[0] = int(hex(hello_rc),16)
print(messages)
messages[1:5] = write_bytes(len(id))
print(messages)
print(id.encode('ascii'))
print(id.encode('utf-8').hex())
print(type(id.encode('utf-8').hex()))
messages[5:] = bytes.fromhex(id.encode('utf-8').hex())
print(len(messages[5:]))

if messages[0] == hello_rc:
    print("hello")
    num1 = payload_buf_length(messages[1:5])
    print(num1)