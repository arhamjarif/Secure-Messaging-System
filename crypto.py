from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os,base64

def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public_key = private_key.public_key()
    serialized_public_key = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return private_key,serialized_public_key

def load_public_key(requested_public_key_dict:dict):
    requested_public_key = serialization.load_pem_public_key(requested_public_key_dict['public_key'].encode())
    return requested_public_key

def encrypt_private_message(private_message:str, requested_public_key):
    aes_key = AESGCM.generate_key(bit_length=256)
    aes = AESGCM(aes_key)
    nonce = os.urandom(12)
    #message encryption
    encrypted_private_message_bytes = aes.encrypt(nonce,private_message.encode(),None)
    encrypted_private_message = base64.urlsafe_b64encode(encrypted_private_message_bytes).decode()

    #AES key encryption
    encrypted_aes_key_bytes = requested_public_key.encrypt(aes_key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(),label=None))
    encrypted_aes_key = base64.urlsafe_b64encode(encrypted_aes_key_bytes).decode()

    #nonce encoding
    nonce_b64 = base64.urlsafe_b64encode(nonce).decode()
    return encrypted_private_message,encrypted_aes_key,nonce_b64

def decrypt_private_message(nonce_str:str, encrypted_aes_key_str:str,encrypted_private_message:str,private_key):
    nonce = base64.urlsafe_b64decode(nonce_str.encode())
    encrypted_aes_key = base64.urlsafe_b64decode(encrypted_aes_key_str.encode())
    aes_key = private_key.decrypt(encrypted_aes_key, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))

    encrypted_private_message_bytes = base64.urlsafe_b64decode(encrypted_private_message.encode())
    aes = AESGCM(aes_key)
    message = aes.decrypt(nonce,encrypted_private_message_bytes,None).decode()

    return message