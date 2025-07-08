import socket
import threading

HEADER = 64
PORT = 9999
FORMAT = "utf-8"
DISCONNECTED_MSG = "disconnect"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()

print(f"[SERVER] Listening on {SERVER}:{PORT}")

# Store client info: username -> (conn, addr, public_key_pem)
clients = {}  # {username: (conn, addr)}
user_pubkeys = {}  # {username: public_key_pem}

def handle_client(conn, addr):
    try:
        # Receive username and public key
        length_bytes = conn.recv(4)
        if not length_bytes:
            conn.close()
            return
        length = int.from_bytes(length_bytes, "big")
        data = b''
        while len(data) < length:
            chunk = conn.recv(length - len(data))
            if not chunk:
                conn.close()
                return
            data += chunk
        if b'|' not in data:
            conn.close()
            return
        username_bytes, pem = data.split(b'|', 1)
        username = username_bytes.decode(FORMAT).strip()
        print(f"[SERVER] {username} joined from {addr}")

        # Register client
        clients[username] = (conn, addr)
        user_pubkeys[username] = pem

        while True:
            # Wait for key request or message
            req_length_bytes = conn.recv(4)
            if not req_length_bytes:
                break
            req_length = int.from_bytes(req_length_bytes, "big")
            req = b''
            while len(req) < req_length:
                chunk = conn.recv(req_length - len(req))
                if not chunk:
                    break
                req += chunk
            if not req:
                break

            # Key request protocol
            if req.startswith(b"GET_KEY|"):
                target_username = req[8:].decode(FORMAT).strip()
                key_to_send = user_pubkeys.get(target_username, b"")
                conn.sendall(len(key_to_send).to_bytes(4, "big"))
                if key_to_send:
                    conn.sendall(key_to_send)
            else:
                # Message relay: expects encrypted message in req
                # Message should be sent in format: recipient_username:encrypted_message
                try:
                    # Try to decode the encrypted message header
                    # We'll assume the client sends: recipient: (plaintext) + encrypted bytes
                    req_decoded = req.decode(FORMAT, errors="ignore")
                    if ':' not in req_decoded:
                        continue  # skip invalid
                    recipient, _ = req_decoded.split(':', 1)
                    recipient = recipient.strip()
                    if recipient in clients:
                        # Forward to recipient
                        recipient_conn, _ = clients[recipient]
                        # Forward as-is: first send length, then message
                        msg_length = len(req)
                        msg_length_bytes = str(msg_length).encode(FORMAT)
                        msg_length_bytes += b' ' * (HEADER - len(msg_length_bytes))
                        recipient_conn.send(msg_length_bytes)
                        recipient_conn.send(req)
                except Exception as e:
                    print(f"[SERVER] Could not relay message: {e}")
                    continue

    except Exception as e:
        print(f"[SERVER] Exception for client {addr}: {e}")
    finally:
        # Remove client from lists
        for uname, (c, a) in list(clients.items()):
            if c == conn:
                print(f"[SERVER] {uname} disconnected")
                clients.pop(uname)
                user_pubkeys.pop(uname, None)
                break
        conn.close()

def start():
    print("[SERVER] Waiting for connections...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

if __name__ == "__main__":
    start()