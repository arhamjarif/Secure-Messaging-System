import socket,json


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