import socket
import threading
import os
import sys
import rsa

HEADER = 64
PORT = 9999
FORMAT = "utf-8"
DISCONNECTED_MSG = "disconnect"

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def load_or_create_keys():
    if not (os.path.exists("public.pem") and os.path.exists("private.pem")):
        # Check if private key already exists
        if os.path.exists("private.pem"):
            print("Private key exists but public key is missing!")
            sys.exit(1)
            
        try:
            print("Generating new key pair...")
            public_key, private_key = rsa.newkeys(1024)
            with open("public.pem", "wb") as f:
                f.write(public_key.save_pkcs1("PEM"))
            with open("private.pem", "wb") as f:
                f.write(private_key.save_pkcs1("PEM"))
            print("Keys generated successfully")
        except Exception as e:
            print(f"Key generation failed: {e}")
            sys.exit(1)
    else:
        try:
            with open("public.pem", "rb") as f:
                public_key = rsa.PublicKey.load_pkcs1(f.read())
            with open("private.pem", "rb") as f:
                private_key = rsa.PrivateKey.load_pkcs1(f.read())
            print("Keys loaded successfully")
        except Exception as e:
            print(f"Error loading keys: {e}")
            sys.exit(1)
    return public_key, private_key

public_key, private_key = load_or_create_keys()

def send_data(socket_obj, data):
    try:
        message = data.encode(FORMAT)
        msg_length = len(message)
        socket_obj.sendall(msg_length.to_bytes(4, 'big'))
        socket_obj.sendall(message)
        return True
    except Exception as e:
        print(f"Error sending data: {e}")
        return False

def receive():
    try:
        while True:
            length_header = client.recv(HEADER)
            if not length_header:
                break
            if length_header[0] == 0 and length_header[1] == 0:
                continue
            
            length = int.from_bytes(length_header, 'big')
            while length > 0:
                chunk = client.recv(min(length, HEADER))
                if len(chunk) == 0:
                    raise ConnectionError("Socket disconnected")
                try:
                    decrypted = rsa.decrypt(chunk, private_key).decode()
                    if decrypted.strip():
                        print(f"\n[Received]: {decrypted}")
                    length -= len(chunk)
                except Exception as e:
                    print(f"\n[Received] (unencrypted data): " + str(e))
    except (ConnectionError, KeyboardInterrupt, Exception) as e:
        print(f"\nConnection lost: {e}")

def request_user_public_key(target_username):
    try:
        request = f"GET_KEY|{target_username}".encode(FORMAT)
        client.sendall(len(request).to_bytes(4, 'big'))
        client.sendall(request)
        length_header = client.recv(4)
        key_length = int.from_bytes(length_header, 'big')
        if key_length <= 0:
            print(f"No public key found for {target_username}")
            return None
        pem_data = b''
        while len(pem_data) < key_length:
            remaining = key_length - len(pem_data)
            chunk = client.recv(min(remaining, 4096))
            pem_data += chunk
        return rsa.PublicKey.load_pkcs1(pem_data)
    except Exception as e:
        print(f"Error requesting user key: {e}")
        return None

username = input("Enter your username: ").strip()

if not username:
    print("Username cannot be empty")
    sys.exit(1)

send_data(client, f"USER|{username}")
send_data(client, public_key.save_pkcs1("PEM"))

receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()

while True:
    try:
        user_input = input("\nEnter message (Recipient:Message) or 'exit': ").strip()
        if user_input.lower() == 'exit':
            break
            
        if ':' not in user_input:
            print("Invalid format. Use: Recipient:Message")
            continue

        recipient, message = user_input.split(':', 1)
        recipient = recipient.strip()
        if not recipient or not message.strip():
            print("Both recipient and message cannot be empty")
            continue

        recipient_pubkey = request_user_public_key(recipient)
        if not recipient_pubkey:
            continue

        enc_message = rsa.encrypt(message.encode(), recipient_pubkey)
        if enc_message:
            send_data(client, "SEND")
            send_data(client, recipient)
            client.sendall(enc_message)
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        break
    except Exception as e:
        print(f"Error: {e}")
        break

print("Closing connection...")
client.close()