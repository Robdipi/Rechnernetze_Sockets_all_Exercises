import socket
import time
from enum import Enum

Server_IP = '127.0.0.1'
Server_PORT = 50000



#<ID><Rechenoperation><N><z1><z2>…<zN>




def send_command(ID, operator, nums):
    message = '<' +  ID.__str__() + '>' + '<' +  operator + '>'
    for num in nums:
        message += '<' + str(num)+ '>'
    print('Sending message', message)
    sock.send(message.encode('utf-8'))

def test_commands():
    send_command(1, "SUM", [1,2])
    send_command(2, "PRO", [3,4])
    send_command(3, "MAX", [5,6])
    send_command(4, "MIN", [7,8])
    send_command(5, "SUM", range(1,1000))


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
print('Connecting to TCP server with IP ', Server_IP, ' on Port ', Server_PORT)
sock.connect((Server_IP, Server_PORT))
test_commands()
noTimeout = True
while noTimeout:
    try:
        msg=sock.recv(1024).decode('utf-8')
        print('Message received; ', msg)
    except socket.timeout:
        print('Socket timed out at',time.asctime())
        noTimeout = False
    #sock.close()


