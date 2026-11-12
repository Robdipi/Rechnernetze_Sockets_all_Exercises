import socket
import time
from enum import Enum

Server_IP = '127.0.0.1'
Server_PORT = 50000
MESSAGE = 'smello world'


#<ID><Rechenoperation><N><z1><z2>…<zN>
Operations = Enum('SUM','PRO','MIN','MAX')
def send_command(ID, operator, nums):
    s = '<' +  ID + '>' + '<' +  operator + '>'
    for num in nums:
        s += '<' + str(num)+ '>'
    return s

def test_commands():
    send_command(1, Operations.SUM, [1,2])





sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
print('Connecting to TCP server with IP ', Server_IP, ' on Port ', Server_PORT)
sock.connect((Server_IP, Server_PORT))
print('Sending message', MESSAGE)
sock.send(MESSAGE.encode('utf-8'))
try:
    msg=sock.recv(1024).decode('utf-8')
    print('Message received; ', msg)
except socket.timeout:
    print('Socket timed out at',time.asctime())
sock.close()


