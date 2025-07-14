import socket
import threading
import time
from queue import Queue

HEADER = 64
PORT = 9999
FORMAT = "utf-8"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

# Store client connections and their public keys
clients = {}  # username -> socket
client_keys = {}  # username -> public key PEM

# Debug message queue
debug_queue = Queue()

def print_debug(msg):
    debug_queue.put(f"[DEBUG] {msg}")

# Print handler thread
def print_handler():
    while True:
        while not debug_queue.empty():
            print(debug_queue.get())
        time.sleep(0.1)

def recv_exact(conn, num_bytes):
    """Receive exactly num_bytes from connection"""
    print_debug(f"Receiving exactly {num_bytes} bytes...")
    data = b""
    while len(data) < num_bytes:
        chunk = conn.recv(num_bytes - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data += chunk
    print_debug(f"Received {len(data)} bytes")
    return data

def send_with_header(conn, data):
    """Send data with length header"""
    if isinstance(data, str):
        data = data.encode(FORMAT)
    header = str(len(data)).encode(FORMAT).ljust(HEADER)
    print_debug(f"Sending header: {len(data)} bytes")
    conn.send(header)
    time.sleep(0.05)
    print_debug(f"Sending payload: {len(data)} bytes")
    conn.send(data)

def handle_client(conn, addr):
    """Handle individual client connection"""
    username = None
    try:
        # Get username
        username_length = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
        username = recv_exact(conn, username_length).decode(FORMAT)
        print_debug(f"Client {addr} registering as {username}")

        # Get public key
        key_length = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
        public_key = recv_exact(conn, key_length)
        print_debug(f"Received public key for {username}")

        # Store client info
        clients[username] = conn
        client_keys[username] = public_key
        print_debug(f"Registered {username} (Total clients: {len(clients)})")

        # Main client loop
        while True:
            msg_length = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
            msg = recv_exact(conn, msg_length)
            msg_text = msg.decode(FORMAT, errors='ignore')

            if msg_text == "disconnect":
                break

            if msg_text.startswith("REQUESTKEY:"):
                # Handle key request
                recipient = msg_text.split(":", 1)[1]
                print_debug(f"{username} requesting key for {recipient}")
                
                if recipient in client_keys:
                    # Send KEY message type
                    conn.send(b"KEY")
                    # Send public key
                    send_with_header(conn, client_keys[recipient])
                    print_debug(f"Sent {recipient}'s key to {username}")
                else:
                    conn.send(b"SYS")
                    send_with_header(conn, f"User {recipient} not found")

            elif msg_text.startswith("SENDMSG:"):
                try:
                    # Parse recipient and encrypted message
                    parts = msg_text.split(":", 2)
                    recipient = parts[1]
                    # Get encrypted part as bytes
                    enc_start = msg.find(b':', msg.find(b':')+1) + 1
                    encrypted_msg = msg[enc_start:]

                    print_debug(f"{username} sending encrypted message to {recipient}")

                    if recipient in clients:
                        # Forward encrypted message
                        recipient_conn = clients[recipient]
                        recipient_conn.send(b"MSG")
                        send_with_header(recipient_conn, encrypted_msg)
                        print_debug(f"Forwarded encrypted message to {recipient}")

                        # Send acknowledgment
                        conn.send(b"SYS")
                        send_with_header(conn, "Message delivered")
                    else:
                        conn.send(b"SYS")
                        send_with_header(conn, f"User {recipient} not found")

                except Exception as e:
                    print_debug(f"Error forwarding message: {e}")
                    conn.send(b"SYS")
                    send_with_header(conn, "Failed to forward message")

    except Exception as e:
        print_debug(f"Error handling {username}: {e}")
    finally:
        conn.close()
        if username in clients:
            del clients[username]
        if username in client_keys:
            del client_keys[username]
        print_debug(f"{username} disconnected (Total clients: {len(clients)})")

def start_server():
    """Start the chat server"""
    print_debug("Starting server...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print_debug(f"Server listening on {SERVER}:{PORT}")

    # Start print handler
    print_thread = threading.Thread(target=print_handler, daemon=True)
    print_thread.start()

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print_debug(f"Active connections: {threading.active_count() - 2}")  # -2 for main and print threads
    except KeyboardInterrupt:
        print_debug("Server shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()