import rsa
import socket
import threading

HEADER = 64
PORT =9999
FORMAT ="utf-8"
DISCONNECTED_MSG ="disconnect"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR =(SERVER,PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

''' Only run this part once to generate new key files
public_key, private_key = rsa.newkeys(1024)
with open("public.pem", "wb") as f:
    f.write(public_key.save_pkcs1("PEM"))
with open("private.pem", "wb") as f:
    f.write(private_key.save_pkcs1("PEM"))
'''
# Now read the keys back (make sure files exist and are correct)
with open("public.pem", "rb") as f:
    public_key_own = rsa.PublicKey.load_pkcs1(f.read())

with open("private.pem", "rb") as f:
    private_key_own = rsa.PrivateKey.load_pkcs1(f.read())

def send_username_and_public_key(sock, username, public_key_own):
    """
    Send your username and PEM-encoded public key to the server.
    """
    payload = f"{username}|".encode("utf-8") + public_key_own.save_pkcs1("PEM")
    length = len(payload)
    sock.sendall(length.to_bytes(4, "big"))  # send length
    sock.sendall(payload)  # send username|PEM

def request_user_public_key(sock, target_username):
    """
    Request the public key of another user from the server.
    """
    request = f"GET_KEY|{target_username}".encode("utf-8")
    length = len(request)
    sock.sendall(length.to_bytes(4, "big"))
    sock.sendall(request)
    # Receive key length and then key
    key_length_bytes = sock.recv(4)
    key_length = int.from_bytes(key_length_bytes, "big")
    pem = b''
    while len(pem) < key_length:
        chunk = sock.recv(key_length - len(pem))
        if not chunk:
            raise ConnectionError("Socket closed during key receive")
        pem += chunk
    return rsa.PublicKey.load_pkcs1(pem)

def receive():
    while True:
        try:
            msg_length_raw = client.recv(HEADER)
            if not msg_length_raw:
                break
            msg_length = int(msg_length_raw.decode(FORMAT).strip())
            if msg_length == 0:
                continue
            msg = client.recv(msg_length).decode(FORMAT)
            print("\n[Received]:", msg)
        except Exception as e:
          print("Connection closed or error:", e)
          break

username = input("Enter your username: ")

threading.Thread(target=receive, daemon=True).start()



encrypted_message = rsa.encrypt(message.encode(),public_key_received)
print(encrypted_message)
#the Received_encrypted message is received from server 
clear_message = rsa.decrypt(Received_encrypted_message,private_key_own)
print(clear_message.decode())




while True:
    msg = input("Format: recipient:message\n")
    if msg == DISCONNECTED_MSG:
        send_msg = DISCONNECTED_MSG.encode(FORMAT)
        send_length = str(len(send_msg)).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(send_msg)
        break
    
    message = rsa.encrypt(msg.encode(),public_key_own)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
client.close()
'''



import rsa
import socket
import threading
import os

HEADER = 64
PORT = 9999
FORMAT = "utf-8"
DISCONNECTED_MSG = "disconnect"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# Generate or load your keypair
if not (os.path.exists("public.pem") and os.path.exists("private.pem")):
    public_key, private_key = rsa.newkeys(1024)
    with open("public.pem", "wb") as f:
        f.write(public_key.save_pkcs1("PEM"))
    with open("private.pem", "wb") as f:
        f.write(private_key.save_pkcs1("PEM"))
else:
    with open("public.pem", "rb") as f:
        public_key = rsa.PublicKey.load_pkcs1(f.read())
    with open("private.pem", "rb") as f:
        private_key = rsa.PrivateKey.load_pkcs1(f.read())

def send_username_and_public_key(sock, username, public_key):
    payload = f"{username}|".encode("utf-8") + public_key.save_pkcs1("PEM")
    length = len(payload)
    sock.sendall(length.to_bytes(4, "big"))
    sock.sendall(payload)

def request_user_public_key(sock, target_username):
    request = f"GET_KEY|{target_username}".encode("utf-8")
    length = len(request)
    sock.sendall(length.to_bytes(4, "big"))
    sock.sendall(request)
    key_length_bytes = sock.recv(4)
    key_length = int.from_bytes(key_length_bytes, "big")
    if key_length == 0:
        print(f"No public key found for user '{target_username}'")
        return None
    pem = b''
    while len(pem) < key_length:
        chunk = sock.recv(key_length - len(pem))
        if not chunk:
            raise ConnectionError("Socket closed during key receive")
        pem += chunk
    return rsa.PublicKey.load_pkcs1(pem)

def receive():
    while True:
        try:
            msg_length_raw = client.recv(HEADER)
            if not msg_length_raw:
                break
            msg_length = int(msg_length_raw.decode(FORMAT).strip())
            if msg_length == 0:
                continue
            encrypted_msg = client.recv(msg_length)
            try:
                msg = rsa.decrypt(encrypted_msg, private_key).decode(FORMAT)
                print("\n[Received]:", msg)
            except Exception:
                print("\n[Received] (could not decrypt):", encrypted_msg)
        except Exception as e:
            print("Connection closed or error:", e)
            break

username = input("Enter your username: ").strip()
send_username_and_public_key(client, username, public_key)
threading.Thread(target=receive, daemon=True).start()

while True:
    msg = input("Format: recipient:message\n")
    if msg == DISCONNECTED_MSG:
        send_msg = DISCONNECTED_MSG.encode(FORMAT)
        send_length = str(len(send_msg)).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(send_msg)
        break

    if ':' not in msg:
        print("Invalid format! Use: recipient:message")
        continue

    recipient, message = msg.split(':', 1)
    recipient = recipient.strip()
    message = message.strip()
    if not recipient or not message:
        print("Recipient and message cannot be empty.")
        continue

    recipient_pubkey = request_user_public_key(client, recipient)
    if not recipient_pubkey:
        continue

    try:
        encrypted_message = rsa.encrypt(message.encode(FORMAT), recipient_pubkey)
    except Exception as e:
        print("Encryption failed:", e)
        continue

    msg_length = len(encrypted_message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(encrypted_message)

client.close()
'''