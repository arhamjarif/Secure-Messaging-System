import socket, threading,json,queue
from cryptography.hazmat.primitives.asymmetric import rsa
from network import recv_all,send_all
from crypto import generate_rsa_keys,load_public_key,encrypt_private_message,decrypt_private_message



host = "127.0.0.1"
port = 6000
def recv_check(client: socket.socket, private_key:rsa.RSAPrivateKey):
    while True:
        try:
            incoming_transmission = recv_all(client)
            if incoming_transmission == b'':
                print('Server disconnected')
                break

            incoming_packet = json.loads(incoming_transmission.decode())
            
            if incoming_packet['type'] == 'public':
                print(f"{incoming_packet['sender']}: {incoming_packet['message']}")

            elif incoming_packet['type'] == 'private':
                message = decrypt_private_message(incoming_packet['nonce'],incoming_packet['AES_key'],incoming_packet['message'],private_key)
                print(f"[private]{incoming_packet['sender']}: {message}")

            else:
                response_queue.put(incoming_packet)
        except OSError:
            break

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
    client.connect((host,port))
    print('Connected to server.\n')

    private_key, serialized_public_key = generate_rsa_keys()

    while True:
        username = input('Enter username: ')
        login_packet = {'type':'login','username':username, 'public_key': serialized_public_key}
        
        send_all(client,login_packet)
            
        login_validation = json.loads(recv_all(client).decode())            
            
        if login_validation['type'] == 'login_success':
            break
        else:
            print('Username taken. Please try again')
    
    response_queue = queue.Queue()
    receive_thread = threading.Thread(target=recv_check,args=(client,private_key))
    receive_thread.start()

    while True:
        message = input("Enter Message (for available commands, Enter '/h'):\n")
        if message == '/pm':
            userlist_packet = {'type':'userlist_request'}
            send_all(client,userlist_packet)
            userlist = response_queue.get()
            print('Available users:')
            index = 1
            for user in userlist['users']:
                print(f'{index}. {user}')
                index += 1
            while True:
                try:
                    pm_recipient = int(input("Select user no: "))
                except(ValueError):
                    print('Please enter a number.')
                    continue
                if pm_recipient in range(1,index):
                    recipient = userlist["users"][pm_recipient - 1]
                    break
                print("Please choose one of the listed users.")
            public_key_request = {'type':'public_key_request','user':recipient}
            send_all(client,public_key_request)
            requested_public_key_dict = response_queue.get() 
            requested_public_key = load_public_key(requested_public_key_dict)

            private_message = input('Enter Message:\n')
            encrypted_private_message,encrypted_aes_key,nonce_b64 = encrypt_private_message(private_message,requested_public_key)
            private_packet = {'type':'private', 'recipient':recipient, 'message':encrypted_private_message, 'AES_key':encrypted_aes_key, 'nonce': nonce_b64}
            send_all(client,private_packet)
        elif message == '/h':
            print('Private Message = /pm\nQuit program = /q')
        elif message == '/q':
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            receive_thread.join()
            print('Goodbye!')
            break

        else:
            public_packet = {'type':'public','message':message}
            send_all(client,public_packet)
        
