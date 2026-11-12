import socket
import time

My_IP = '127.0.0.1'
My_PORT = 50000
server_activity_period=30

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((My_IP, My_PORT))
sock.settimeout(1.0)
print('Listening on Port ',My_PORT, ' for incoming TCP connections')

t_end=time.time()+server_activity_period # Ende der Aktivitätsperiode

sock.listen(1)
print('Listening ...')

conn = None
while time.time()<t_end:
    try:
        conn, addr = sock.accept()
        print('Incoming connection accepted: ', addr)
        conn.settimeout(1.0)
        break
    except socket.timeout:
        pass


def calculateResult(message):
    parts = [x for x in message.split('<') if x]
    parts = [x.replace('>', '') for x in parts]

    ID = int(parts[0])
    operator = parts[1]
    nums = [int(x) for x in parts[2:]]
    print(ID, operator, nums)
    match operator:
        case 'SUM':
            return str(sum(nums))
        case 'MIN':
            return str(min(nums))
        case 'PRO':
            n = 1
            for i in range(len(nums)):
                n *= nums[i]
            return str(n)
        case 'MAX':
            return str(max(nums))

    return "NotValidOperation"


if conn:
    while time.time()<t_end:
        try:
            data = conn.recv(1024)
            if not data: # receiving empty messages means that the socket other side closed the socket
                print('Connection closed from other side')
                print('Closing ...')
                conn.close()
                conn = None
                break
            conn.send(calculateResult(data.decode('utf-8')).encode('utf-8'))
        except socket.timeout:
            pass

sock.close()
if conn:
    conn.close()
