import socket
 
import threading
HEADER = 128
PORT =9999
FORMAT ="utf-8"


DISCONNECTED_MSG ="disconnect"
SERVER =socket.gethostbyname(socket.gethostname())
ADDR =(SERVER,PORT)

client={}
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(ADDR)





def send_with_header(conn, text):
    msg = text.encode(FORMAT)
    msg_length = str(len(msg)).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))
    conn.send(msg_length)
    conn.send(msg)


def handle_client(conn, addr):
    username_length = int(conn.recv(HEADER).decode(FORMAT).strip())
    username = conn.recv(username_length).decode(FORMAT)
    # Receive and store client's public key
    public_key_length = int(conn.recv(HEADER).decode(FORMAT).strip())
    public_key_pem = conn.recv(public_key_length)
    client_keys[username] = public_key_pem  # Store raw PEM
    print(f"[+] Stored public key for {username}")

    client[username] = conn
    print(f"[new connection] {addr} connected as {username}.")
    print(f"key recived of {username} key {client_public_key}")
    connected = True
    while connected:
        try:
            msg_length_raw = conn.recv(HEADER)
            if not msg_length_raw:
                break
            msg_length = int(msg_length_raw.decode(FORMAT).strip())
            if msg_length == 0:
                continue
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECTED_MSG:
                connected = False
                break
            if ":" in msg:
                recipient, actual_msg = msg.split(":", 1)
                if recipient in client:
                    # Step 1: Send recipient's public key to sender

                    recipient_key = client_keys[recipient]
                    recipient_key_length = str(len(recipient_key)).encode(FORMAT)
                    conn.send(recipient_key_length.ljust(HEADER))
                    conn.send(recipient_key)
                else :
                    conn.send("0".encode(FORMAT).ljust(HEADER))
                    print(f"[!] No key for recipient {recipient}")
                    continue  # Skip sending message if recipient has no key

                    try:
                        full_msg = f"[{username}] {actual_msg}".encode(FORMAT)
                        length = str(len(full_msg)).encode(FORMAT)
                        length += b' ' * (HEADER - len(length))
                        client[recipient].send(length)
                        client[recipient].send(full_msg)
                        send_with_header(conn, "Message sent.")
                    except Exception as e:
                        print(f"Error sending to {recipient}: {e}")
                        send_with_header(conn, "Failed to send")
            
                   
                       
            else:
                send_with_header(conn,"Invalid format. Use recipient:message")
        except Exception as e:
            print(f"Error: {e}")
            break
    del client[username]
    conn.close()

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
