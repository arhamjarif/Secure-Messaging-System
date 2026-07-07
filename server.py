import socket,threading,json
from network import recv_all,send_all

host = "127.0.0.1"
port = 6000




def cleanup(conn:socket.socket,connections_to_usernames:dict,usernames_to_connections:dict):
    if conn not in connections_to_usernames:
        return
    username = connections_to_usernames[conn]['username']
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
                        connections_to_usernames[conn] = {'username':incoming_packet['username'], 'public_key':incoming_packet['public_key']}
                        usernames_to_connections[incoming_packet['username']] = {'conn':conn, 'public_key':incoming_packet['public_key']}
                        send_all(conn,login_success)
                        system_packet = {'type': 'public','sender':'SYSTEM','message': f'{incoming_packet['username']} has connected'}
                        print(f'Connection username set to: {incoming_packet['username']}\n')
                        for connection in connections_to_usernames:
                            send_all(connection,system_packet)

                elif incoming_packet['type'] == 'userlist_request':
                    userlist = {'type':'userlist', 'users': list(usernames_to_connections.keys())}
                    send_all(conn,userlist)

                elif incoming_packet['type'] == 'public_key_request':
                    requested_public_key = {'type':'public_key_response', 'public_key':usernames_to_connections[incoming_packet['user']]['public_key']}
                    send_all(conn, requested_public_key)

                elif incoming_packet['type'] == 'public':
                    outgoing_packet = {'type': 'public', 'sender':connections_to_usernames[conn]['username'],'message':incoming_packet['message']}
                    
                    for connection in connections_to_usernames:
                        if conn != connection:
                            send_all(connection,outgoing_packet)

                elif incoming_packet['type'] == 'private':
                    if incoming_packet['recipient'] in usernames_to_connections:
                        outgoing_packet = {'type':'private', 'sender':connections_to_usernames[conn]['username'], 'message':incoming_packet['message'], 'AES_key':incoming_packet['AES_key'], 'nonce':incoming_packet['nonce']}
                        send_all(usernames_to_connections[incoming_packet['recipient']]['conn'],outgoing_packet)
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
        print(f'{addr} has successfully connected...')
        worker_thread = threading.Thread(target=handle_client,args=(conn, connections_to_usernames, usernames_to_connections))
        worker_thread.start()
