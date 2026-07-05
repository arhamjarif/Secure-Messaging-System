import socket,threading

host = "127.0.0.1"
port = 6000
def handle_client(conn: socket.socket, connections:list):
    with conn:
        while True:
            message = conn.recv(1024)
            print(f'Received:\n{message.decode()}')
            for connection in connections:
                if conn != connection:
                    connection.send(message)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind((host,port))
    server.listen()
    print('Server started\nWaiting for connection...\n')
    connections = []
    while True:
        conn, addr = server.accept()
        print(f'{addr} has successfully connected...\n')
        connections.append(conn)
        worker_thread = threading.Thread(target=handle_client,args=(conn, connections))
        worker_thread.start()
