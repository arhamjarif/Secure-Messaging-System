import socket,threading,json

host = "127.0.0.1"
port = 6000
def cleanup(conn:socket,connections_to_usernames:dict,usernames_to_connections:dict):
    if conn not in connections_to_usernames:
        return
    username = connections_to_usernames[conn]
    del usernames_to_connections[username]
    del connections_to_usernames[conn]
    print(f'{username} disconnected')
    system_message = {'type': 'public','sender':'SYSTEM','message': f'{username} has disconnected'}
    system_packet = json.dumps(system_message).encode()
    for connection in connections_to_usernames:
        connection.send(system_packet)

def handle_client(conn: socket.socket, connections_to_usernames:dict, usernames_to_connections: dict):
    with conn:
        while True:
            try:
                incoming_transmission = conn.recv(1024)

                if incoming_transmission == b'':
                    cleanup(conn,connections_to_usernames,usernames_to_connections)
                    break

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

                elif incoming_packet['type'] == 'userlist_request':
                    userlist = list(usernames_to_connections.keys())
                    conn.send(json.dumps(userlist).encode())

                elif incoming_packet['type'] == 'public':
                    outgoing_packet = {'type': 'public', 'sender':connections_to_usernames[conn],'message':incoming_packet['message']}
                    outgoing_transmission = json.dumps(outgoing_packet).encode()
                    for connection in connections_to_usernames:
                        if conn != connection:
                            connection.send(outgoing_transmission)

                elif incoming_packet['type'] == 'private':
                    if incoming_packet['recipient'] in usernames_to_connections:
                        outgoing_packet = {'type':'private', 'sender':connections_to_usernames[conn], 'message':incoming_packet['message']}
                        outgoing_transmission = json.dumps(outgoing_packet).encode()
                        usernames_to_connections[incoming_packet['recipient']].send(outgoing_transmission)
                    else:
                        system_message = {'type': 'public', 'sender': 'SYSTEM', 'message': f'{incoming_packet['recipient']} does not exist'}
                        system_packet = json.dumps(system_message).encode()
                        conn.send(system_packet)
            except ConnectionResetError:
                cleanup(conn, connections_to_usernames,usernames_to_connections)
                break

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
