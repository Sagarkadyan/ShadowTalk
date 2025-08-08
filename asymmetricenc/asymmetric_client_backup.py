import socket
import threading
import time
import rsa
import queue


HEADER = 4
PORT = 24179  # Playit assigned port
FORMAT = "utf-8"

LOCAL_MODE = False
SERVER = "ready-lebanon.gl.at.ply.gg"  # Playit assigned address
ADDR = (SERVER, PORT)




pubkey, privkey = rsa.newkeys(512)
with open("public.pem", "wb") as f:
    f.write(pubkey.save_pkcs1("PEM"))

with open("private.pem", "wb") as f:
    f.write(privkey.save_pkcs1("PEM"))




# Load keys
with open("public.pem", "rb") as f:
    my_pub = rsa.PublicKey.load_pkcs1(f.read())
with open("private.pem", "rb") as f:
    my_priv = rsa.PrivateKey.load_pkcs1(f.read())

# Connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# Message queue for system responses (KEY, SYS)
response_queue = queue.Queue()

# Receive exactly N bytes
def recv_exact(sock, num):
    data = b""
    while len(data) < num:
        chunk = sock.recv(num - len(data))
        if not chunk:
            raise ConnectionError("Socket closed")
        data += chunk
    return data

# Send message with header
def send_with_header(sock, data):
    if isinstance(data, str):
        data = data.encode(FORMAT)
    sock.send(str(len(data)).encode(FORMAT).ljust(HEADER))
    time.sleep(0.01)
    sock.send(data)

# Receiver thread: handles all messages
def receive():
    while True:
        try:
            msg_type = recv_exact(client, 3).decode(FORMAT)
            if msg_type == "MSG":
                # 1. Get sender name
                sender_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
                sender = recv_exact(client, sender_len).decode(FORMAT)
                # 2. Get encrypted message
                msg_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
                encrypted_msg = recv_exact(client, msg_len)
                decrypted = rsa.decrypt(encrypted_msg, my_priv).decode(FORMAT)
                print(f"\n[{sender}]: {decrypted}")
            else:
                msg_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
                msg = recv_exact(client, msg_len)
                if msg_type in ["SYS", "KEY"]:
                    response_queue.put((msg_type, msg))  # Store response for main thread
        except Exception as e:
            print(f"[Receiver Error]: {e}")
            break
# Login: username and public key
username = input(f"Enter your username: ").strip()
send_with_header(client, username)
time.sleep(0.05)
send_with_header(client, my_pub.save_pkcs1("PEM"))

# Start the receiver thread
threading.Thread(target=receive, daemon=True).start()

# Main loop: prompt user, send request, wait for queued response
while True:
    to = input(f"Recipient username: ").strip()
    msg = input(f"Message: ").strip()

    if msg.lower() == "disconnect":
        send_with_header(client, "disconnect")
        break

    # Step 1: Ask server for public key
    send_with_header(client, f"REQUESTKEY:{to}")

    # Step 2: Wait for KEY or SYS in queue
    try:
        msg_type, payload = response_queue.get(timeout=5)
    except queue.Empty:
        print(f"[Error]: No response from server.")
        continue

    if msg_type == "KEY":
        try:
            their_key = rsa.PublicKey.load_pkcs1(payload, format="PEM")
            encrypted = rsa.encrypt(msg.encode(FORMAT), their_key)
            payload_msg = f"SENDMSG:{to}".encode(FORMAT) + b":" + encrypted
            send_with_header(client, payload_msg)

            # Step 3: Wait for SYS confirmation
            try:
                ack_type, ack_msg = response_queue.get(timeout=5)
                if ack_type == "SYS":
                    print(f"[System]: {ack_msg.decode(FORMAT)}")
            except queue.Empty:
                print(f"[Error]: No delivery confirmation.")
        except Exception as e:
            print(f"[Encrypt Error]: {e}")
    elif msg_type == "SYS":
        print(f"[System]: {payload.decode(FORMAT)}")
