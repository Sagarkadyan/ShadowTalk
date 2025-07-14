import socket
import threading

HEADER = 64
PORT = 9999
FORMAT = "utf-8"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

clients = {}
client_keys = {}

def send_with_header(conn, data):
    if isinstance(data, str):
        data = data.encode(FORMAT)
    msg_len = str(len(data)).encode(FORMAT).ljust(HEADER)
    conn.send(msg_len)
    conn.send(data)

def recv_exact(conn, num_bytes):
    data = b""
    while len(data) < num_bytes:
        packet = conn.recv(num_bytes - len(data))
        if not packet:
            raise ConnectionError("Disconnected")
        data += packet
    return data

def handle_client(conn, addr):
    username = None
    try:
        username_len = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
        username = recv_exact(conn, username_len).decode(FORMAT)

        key_len = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
        pubkey = recv_exact(conn, key_len)

        clients[username] = conn
        client_keys[username] = pubkey

        print(f"[+] {username} connected.")

        while True:
            msg_len = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
            msg = recv_exact(conn, msg_len)

            if msg.startswith(b"REQUESTKEY:"):
                recipient = msg.decode(FORMAT).split(":")[1]
                if recipient in client_keys:
                    conn.send(b"KEY")
                    send_with_header(conn, client_keys[recipient])
                else:
                    conn.send(b"SYS")
                    send_with_header(conn, "User not found")

            elif msg.startswith(b"SENDMSG:"):
                parts = msg.split(b":", 2)
                recipient = parts[1].decode(FORMAT)
                encrypted = parts[2]
                if recipient in clients:
                    clients[recipient].send(b"MSG")
                    send_with_header(clients[recipient], encrypted)

                    conn.send(b"SYS")
                    send_with_header(conn, "Message delivered")
                else:
                    conn.send(b"SYS")
                    send_with_header(conn, "Recipient not online")

            elif msg.decode(FORMAT).strip() == "disconnect":
                break

    except Exception as e:
        print(f"[ERR] {username}: {e}")
    finally:
        if username:
            clients.pop(username, None)
            client_keys.pop(username, None)
        conn.close()
        print(f"[-] {username} disconnected")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[Server] Listening on {SERVER}:{PORT}")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
