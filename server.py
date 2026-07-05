import socket

host = "127.0.0.1"
port = 6000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((host,port))
    server.listen()
    print('Server started\nWaiting for connection...\n')
    conn, add = server.accept()
    print(f'CLient connected!\n')
    with conn:
        print('Recieved:')
        data = conn.recv(1024).decode()
        print(data)