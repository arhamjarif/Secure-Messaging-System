import socket,threading,json

host = "127.0.0.1"
port = 6000
def handle_client(conn: socket.socket, connections_to_usernames:dict, usernames_to_connections: dict):
    with conn:
        while True:
            incoming_transmission = conn.recv(1024)
            incoming_packet = json.loads(incoming_transmission.decode())
            
            if incoming_packet['type'] == 'login':
                if incoming_packet['username'] in usernames_to_connections:
                    login_fail = {'type':'login_failed'}
                    conn.send(json.dumps(login_fail).encode())
                else:
                    login_success = {'type':'login_success'}
                    connections_to_usernames[conn] = incoming_packet['username']
                    usernames_to_connections[incoming_packet['username']] = conn
                    conn.send(json.dumps(login_success).encode())

            elif incoming_packet['type'] == 'public':
                outgoing_packet = {'type': 'public', 'sender':connections_to_usernames[conn],'message':incoming_packet['message']}
                outgoing_transmission = json.dumps(outgoing_packet).encode()
                for connection in connections_to_usernames:
                    if conn != connection:
                        connection.send(outgoing_transmission)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind((host,port))
    server.listen()
    print('Server started\nWaiting for connection...\n')
    connections_to_usernames = {}
    usernames_to_connections = {}
    
    while True:
        conn, addr = server.accept()
        print(f'{addr} has successfully connected...\n')
        worker_thread = threading.Thread(target=handle_client,args=(conn, connections_to_usernames, usernames_to_connections))
        worker_thread.start()
