import socket

host = "127.0.0.1"
port = 6000

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
    client.connect((host,port))
    print('Connected to server.\n')
    client.send(input('Messege:\n').encode())