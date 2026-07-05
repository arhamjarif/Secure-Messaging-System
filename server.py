import socket

host = "127.0.0.1"
port = 6000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind((host,port))
    server.listen()
    print('Server started\nWaiting for connection...\n')
    conn, addr = server.accept()
    print(f'Client connected!\n')
    with conn:
        while True:
            print(f'Recieved:\n{conn.recv(1024).decode()}')
            conn.send(input('Enter Message:\n').encode())