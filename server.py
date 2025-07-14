import socket

import threading
HEADER = 64
PORT =9999
FORMAT ="utf-8"


DISCONNECTED_MSG ="disconnect"
SERVER =socket.gethostbyname(socket.gethostname())
ADDR =(SERVER,PORT)

client_keys = {}  # Stores public keys per username
clients = {}      # Rename from `client` to `clients` for clarity

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(ADDR)





def send_with_header(conn, text):
    msg = text.encode(FORMAT)
    msg_length = str(len(msg)).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))
    conn.send(msg_length)
    conn.send(msg)


def handle_client(conn, addr):
    username = None 
    try:
        username_length = int(recv_exact(conn,HEADER).decode(FORMAT).strip())
        username = recv_exact(conn,username_length).decode(FORMAT)
        
        
        public_key_length = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
        public_key_pem = recv_exact(conn, public_key_length)


        clients[username] = conn
        client_keys[username] = public_key_pem

        print(f"[+] {username} connected from {addr}")
        print(f"[+] Stored public key for {username}")

        connected = True
        while connected:
            msg_length_raw = recv_exact(conn,HEADER)
            if not msg_length_raw:
                break
            msg_length = int(msg_length_raw.decode(FORMAT).strip())
            if msg_length == 0:
                continue
            msg = conn.recv(msg_length)

            if msg.decode(FORMAT) == DISCONNECTED_MSG:
                print(f"[!] {username} disconnected.")
                connected = False
                break

            # Receive format: recipient:message
            try:
                message_text = msg.decode(FORMAT)
                if ":" not in message_text:
                    send_with_header(conn, "Invalid format. Use recipient:message")
                    continue

                recipient, actual_msg = message_text.split(":", 1)

                if recipient not in clients or recipient not in client_keys:
                    send_with_header(conn, f"Recipient '{recipient}' not found.")
                    continue

                # Step 1: Send recipient's public key to sender
                recipient_key = client_keys[recipient]
                recipient_key_length = str(len(recipient_key)).encode(FORMAT)
                conn.send(b"KEY")
                conn.send(str(len(recipient_key)).encode(FORMAT).ljust(HEADER))
                conn.send(recipient_key)
                print(f"[DEBUG] Sent recipient public key PEM to {username} ({len(recipient_key)} bytes)")
                print(f"[DEBUG] First 30 bytes: {recipient_key[:30]}")
                # Step 2: Wait for encrypted message from sender
                encrypted_msg_len = int(conn.recv(HEADER).decode(FORMAT).strip())
               
                encrypted_msg = recv_exact(conn,encrypted_msg_len)

                # Step 3: Forward to recipient
                # Send real header and encrypted message
                clients[recipient].send(b"MSG") 
                msg_len_encoded = str(len(encrypted_msg)).encode(FORMAT).ljust(HEADER)
                clients[recipient].send(msg_len_encoded)
                clients[recipient].send(encrypted_msg)

                send_with_header(conn, "Message sent.")
                print(f"[MSG] {username} ➜ {recipient}")

            except Exception as e:
                print(f"[ERR] Message handling failed: {e}")
                send_with_header(conn, "Failed to process message")

    except Exception as e:
        print(f"[ERR] Connection error: {e}")

    finally:
        conn.close()
        if username and username in clients:
            del clients[username]
        if username and username in client_keys:
            del client_keys[username]
        print(f"[Cleanup] Removed {username}")

def recv_exact(conn, num_bytes):
    data = b""
    while len(data) < num_bytes:
        chunk = conn.recv(num_bytes - len(data))
        if not chunk:
            raise ConnectionError("Connection closed during recv_exact")
        data += chunk
    return data


def start():
    server.listen()
    print(f"[listing] server is listing {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target = handle_client, args=(conn, addr))
        thread.start()
        print(f"[Activate connections] {threading.active_count()-1}")

print("[starting] serever is starting ")

start()
