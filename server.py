import socket,threading

host = "127.0.0.1"
port = 6000
def handle_client(conn: socket.socket):
    with conn:
        while True:
            print(f'Recieved:\n{conn.recv(1024).decode()}')
            conn.send(input('Enter Message:\n').encode())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind((host,port))
    server.listen()
    print('Server started\nWaiting for connection...\n')
    while True:
        conn, addr = server.accept()
        print(f'{addr} has successfully connected...\n')
        worker_thread = threading.Thread(target=handle_client,args=(conn,))
        worker_thread.start()
