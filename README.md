# Secure Messaging System

A terminal-based client-server messaging application built in Python that demonstrates custom TCP networking, multithreading, and modern end-to-end encryption using a hybrid RSA + AES-GCM encryption scheme.

## Features

* Multi-client chat server using TCP sockets
* Public and private messaging
* End-to-end encrypted private messages
* Hybrid RSA + AES-GCM end-to-end encryption
* Public key exchange
* Threaded server supporting multiple concurrent clients
* Thread-safe client message handling using queues
* Graceful client shutdown and disconnect handling
* Length-prefixed custom application protocol

## Technologies Used

* Python
* Socket Programming
* Multithreading
* RSA Public-Key Cryptography
* AES-GCM Authenticated Encryption
* OAEP Padding
* JSON
* Base64 Encoding

## Requirements

- Python 3.12 or newer
- cryptography

Install the project dependencies:

```bash
pip install -r requirements.txt
```

## How It Works

Each client generates its own RSA key pair when connecting to the server.

When sending a private message:

1. A random AES-256 key is generated.
2. The message is encrypted using AES-GCM.
3. The AES key is encrypted using the recipient's RSA public key.
4. The encrypted message, encrypted AES key, and nonce are transmitted through the server.
5. The recipient decrypts the AES key using their RSA private key before decrypting the message.

The server never has access to the plaintext contents of private messages.

## Project Structure

```text
Secure-Messaging-System/
│
├── client.py        # Client application
├── server.py        # Multi-client server
├── network.py       # Networking utilities
├── crypto.py        # Cryptographic helper functions
└── README.md
```

## Concepts Demonstrated

### Networking

* TCP client-server architecture
* Custom application-layer protocol
* Length-prefixed message framing
* Reliable stream handling with exact-byte reads
* Multi-client server design
* Graceful connection cleanup

### Concurrency

* Threaded server architecture
* Background receive thread on the client
* Thread-safe communication using `queue.Queue`

### Cryptography

* RSA key generation
* Public key serialization and exchange
* Hybrid encryption
* AES-GCM authenticated encryption
* OAEP padding
* Binary serialization with Base64

## What I Learned

This project helped reinforce practical concepts in networking and applied cryptography, including:

* Designing a custom network protocol
* Handling TCP streams correctly
* Building multithreaded client-server applications
* Implementing hybrid encryption using RSA and AES
* Public key serialization and exchange
* Thread-safe communication between concurrent threads
* Structuring larger Python projects into reusable modules

## Future Improvements

* Digital signatures for message authentication
* User authentication with passwords
* Persistent chat history
* File transfer support
* Graphical user interface
* Secure key verification to prevent man-in-the-middle attacks
