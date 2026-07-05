import socket,threading,json

host = "127.0.0.1"
port = 6000
def handle_client(conn: socket.socket, connections:dict):
    with conn:
        while True:
            incoming_transmission = conn.recv(1024)
            incoming_packet = json.loads(incoming_transmission.decode())
            if incoming_packet['type'] == 'login':
                connections[conn] = incoming_packet['username']
            elif incoming_packet['type'] == 'public':
                outgoing_packet = {'type': 'public', 'sender':connections[conn],'message':incoming_packet['message']}
                outgoing_transmission = json.dumps(outgoing_packet).encode()
                for connection in connections:
                    if conn != connection:
                        connection.send(outgoing_transmission)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind((host,port))
    server.listen()
    print('Server started\nWaiting for connection...\n')
    connections = {}
    while True:
        conn, addr = server.accept()
        print(f'{addr} has successfully connected...\n')
        worker_thread = threading.Thread(target=handle_client,args=(conn, connections))
        worker_thread.start()
