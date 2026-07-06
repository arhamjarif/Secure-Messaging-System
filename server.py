import socket,threading,json


host = "127.0.0.1"
port = 6000
def recv_exact(conn:socket.socket, required_bytes:int):
    received_bytes = conn.recv(required_bytes)
    if received_bytes == b'':
        return b''
    received_bytes_counter = len(received_bytes)
    while received_bytes_counter != required_bytes:
        chunk = conn.recv(required_bytes-received_bytes_counter)
        if chunk == b'':
            return b''
        received_bytes += chunk 
        received_bytes_counter = len(received_bytes)
    return received_bytes


def recv_all(conn:socket.socket):
    header = recv_exact(conn,4)
    if header == b'':
        return header
    length = int(header.decode())
    received_bytes = recv_exact(conn,length)
    return received_bytes



def send_all(conn:socket.socket,packet:dict):
    outgoing_transmission = json.dumps(packet).encode()
    length = str(len(outgoing_transmission)).rjust(4,'0').encode()
    conn.sendall(length + outgoing_transmission)


def cleanup(conn:socket.socket,connections_to_usernames:dict,usernames_to_connections:dict):
    if conn not in connections_to_usernames:
        return
    username = connections_to_usernames[conn][0]
    del usernames_to_connections[username]
    del connections_to_usernames[conn]
    print(f'{username} disconnected')
    system_packet = {'type': 'public','sender':'SYSTEM','message': f'{username} has disconnected'}
    for connection in connections_to_usernames:
        send_all(connection,system_packet)

def handle_client(conn: socket.socket, connections_to_usernames:dict, usernames_to_connections: dict):
    with conn:
        while True:
            try:
                incoming_transmission = recv_all(conn)

                if incoming_transmission == b'':
                    cleanup(conn,connections_to_usernames,usernames_to_connections)
                    break

                incoming_packet = json.loads(incoming_transmission.decode())
                
               
                if incoming_packet['type'] == 'login':
                    if incoming_packet['username'] in usernames_to_connections:
                        login_fail = {'type':'login_failed'}
                        send_all(conn,login_fail)
                    else:
                        login_success = {'type':'login_success'}
                        connections_to_usernames[conn] = (incoming_packet['username'], incoming_packet['public_key'])
                        usernames_to_connections[incoming_packet['username']] = (conn, incoming_packet['public_key'])
                        send_all(conn,login_success)

                elif incoming_packet['type'] == 'userlist_request':
                    userlist = {'type':'userlist', 'users': list(usernames_to_connections.keys())}
                    send_all(conn,userlist)

                elif incoming_packet['type'] == 'public_key_request':
                    requested_public_key = {'type':'public_key_response', 'public_key':usernames_to_connections[incoming_packet['user']][1]}
                    send_all(conn, requested_public_key)

                elif incoming_packet['type'] == 'public':
                    outgoing_packet = {'type': 'public', 'sender':connections_to_usernames[conn][0],'message':incoming_packet['message']}
                    
                    for connection in connections_to_usernames:
                        if conn != connection:
                            send_all(connection,outgoing_packet)

                elif incoming_packet['type'] == 'private':
                    if incoming_packet['recipient'] in usernames_to_connections:
                        outgoing_packet = {'type':'private', 'sender':connections_to_usernames[conn][0], 'message':incoming_packet['message']}
                        send_all(usernames_to_connections[incoming_packet['recipient']][0],outgoing_packet)
                    else:
                        system_packet = {'type': 'public', 'sender': 'SYSTEM', 'message': f'{incoming_packet['recipient']} does not exist'}
                        send_all(conn,system_packet)
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
