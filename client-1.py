import socket, threading,json,base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes




host = "127.0.0.1"
port = 6000
def recv_check(client: socket.socket, private_key:rsa.RSAPrivateKey):
    while True:
        incoming_transmission = recv_all(client)
        if incoming_transmission == b'':
            print('Server disconnected')
            break
        incoming_packet = json.loads(incoming_transmission.decode())
        if incoming_packet['type'] == 'public':
            print(f"{incoming_packet['sender']}: {incoming_packet['message']}")

        elif incoming_packet['type'] == 'private':
            encrypted_private_message_bytes = base64.urlsafe_b64decode(incoming_packet['message'].encode())
            message = private_key.decrypt(encrypted_private_message_bytes, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None)).decode()
            print(f"[private]{incoming_packet['sender']}: {message}")

        else:
            shared.append(incoming_packet)

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

    private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public_key = private_key.public_key()
    serialized_public_key = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()

    while True:
        username = input('Enter username: ')
        login_packet = {'type':'login','username':username, 'public_key': serialized_public_key}
        send_all(client,login_packet)
        login_validation = json.loads(recv_all(client).decode())
        if login_validation['type'] == 'login_success':
            break
        else:
            print('Username taken. Please try again')
    
    shared = []
    receive_thread = threading.Thread(target=recv_check,args=(client,private_key))
    receive_thread.start()

    while True:
        message = input("Enter Message (if you wish to send a private message, Enter '/pm'):\n")
        if message == '/pm':
            userlist_packet = {'type':'userlist_request'}
            send_all(client,userlist_packet)
            userlist = None
            while True:
                for i in range(0,len(shared)):
                    if shared[i]['type'] == 'userlist':
                        userlist = shared[i]
                        shared.pop(i)
                        break
                if userlist != None:
                    break
            print('Available users:')
            index = 1
            for user in userlist['users']:
                print(f'{index}. {user}')
                index += 1
            pm_recipient = int(input('Select user no: '))

            public_key_request = {'type':'public_key_request','user':userlist['users'][pm_recipient-1]}
            send_all(client,public_key_request)
            requested_public_key_dict = None 
            while True:
                for i in range(0,len(shared)):
                    if shared[i]['type'] == 'public_key_response':
                        requested_public_key_dict = shared[i]
                        shared.pop(i)
                        break
                if requested_public_key_dict != None:
                    break
            requested_public_key = serialization.load_pem_public_key(requested_public_key_dict['public_key'].encode())
            

            private_message = input('Enter Message:\n').encode()

            encrypted_private_message_bytes = requested_public_key.encrypt(private_message,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(),label=None))
            encrypted_private_message = base64.urlsafe_b64encode(encrypted_private_message_bytes).decode()
            private_packet = {'type':'private', 'recipient':userlist['users'][pm_recipient-1], 'message':encrypted_private_message}
            send_all(client,private_packet)

        else:
            public_packet = {'type':'public','message':message}
            send_all(client,public_packet)
        
