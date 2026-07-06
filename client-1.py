import socket, threading,json



host = "127.0.0.1"
port = 6000
def recv_check(client: socket.socket):
    while True:
        incoming_transmission = recv_all(client)
        if incoming_transmission == b'':
            break
        incoming_packet = json.loads(incoming_transmission.decode())
        if incoming_packet['type'] == 'public':
            print(f"{incoming_packet['sender']}: {incoming_packet['message']}")

        elif incoming_packet['type'] == 'private':
            print(f"[private]{incoming_packet['sender']}: {incoming_packet['message']}")

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

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
    client.connect((host,port))
    print('Connected to server.\n')

    

    while True:
        username = input('Enter username: ')
        login_packet = {'type':'login','username':username,}
        send_all(client,login_packet)
        login_validation = json.loads(recv_all(client).decode())
        if login_validation['type'] == 'login_success':
            break
        else:
            print('Username taken. Please try again')
    
    receive_thread = threading.Thread(target=recv_check,args=(client,))
    receive_thread.start()

    while True:
        message = input("Enter Message (if you wish to send a private message, Enter '/pm'):\n")
        if message == '/pm':
            userlist_packet = {'type':'userlist_request'}
            send_all(client,userlist_packet)
            userlist = json.loads(recv_all(client).decode())
            print('Available users:')
            index = 0
            for user in userlist['users']:
                print(f'{index}. {user}')
                index += 1
            pm_recipient = int(input('Select user no: '))
            private_message = input('Enter Message:\n')
            private_packet = {'type':'private', 'recipient':userlist['users'][pm_recipient], 'message':private_message}
            send_all(client,private_packet)
        else:
            public_packet = {'type':'public','message':message}
            send_all(client,public_packet)
        
