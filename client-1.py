import socket, threading

host = "127.0.0.1"
port = 6000
def recv_check(client: socket.socket):
    while True:
        message = client.recv(1024)
        print(f'Received: {message.decode()}')
with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
    client.connect((host,port))
    print('Connected to server.\n')
    receive_thread = threading.Thread(target=recv_check,args=(client,))
    receive_thread.start()
    while True:
        client.send(input('Enter Message:\n').encode())
        
