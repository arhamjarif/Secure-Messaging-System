import socket, threading,json

host = "127.0.0.1"
port = 6000
def recv_check(client: socket.socket):
    while True:
        incoming_transmission = client.recv(1024)
        incoming_packet = json.loads(incoming_transmission.decode())
        if incoming_packet['type'] == 'public':
            print(f"{incoming_packet['sender']}: {incoming_packet['message']}")
with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
    client.connect((host,port))
    print('Connected to server.\n')

    while True:
        username = input('Enter username: ')
        login_packet = {'type':'login','username':username}
        client.send(json.dumps(login_packet).encode())
        login_validation = json.loads(client.recv(1024).decode())
        if login_validation['type'] == 'login_success':
            break
        else:
            print('Username taken. Please try again')
    
    receive_thread = threading.Thread(target=recv_check,args=(client,))
    receive_thread.start()

    while True:
        public_message = input('Enter Message:\n')
        public_packet = {'type':'public','message':public_message}
        client.send(json.dumps(public_packet).encode())
        
