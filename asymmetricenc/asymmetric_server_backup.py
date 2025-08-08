import socket
import threading

import sqlite3

# Connect (creates the database file if it doesn't exist)
conns = sqlite3.connect('users.db')
cursor = conns.cursor()

HEADER = 4
PORT = 9999
FORMAT = "utf-8"
SERVER =  "127.0.0.1"
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
def adder(name,email,password,cypher_text):
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, cypher_text) VALUES (?, ?, ?, ?)",
            (name, email, password, cypher_text)
        )
        conns.commit()
        return("Inserted successfully!")
    except sqlite3.IntegrityError:
        return("Email already exists.")


def password(name):
    try:
        cursor.execute(
            "SELECT password FROM users WHERE name = ?", (name,)
        )
        result=cursor.fetchone()
        if result:
            return(result[0])
        else :
            return("user does not exist")    
        
    except:
        return("error")   

def update_pss(name, new_passwd):
    try:
        cursor.execute(
            "UPDATE users SET password = ? WHERE name = ?",
            (new_passwd, name)
        )
        conns.commit()

        if cursor.rowcount == 0:
            return "user does not exist"
        else:
            return "password updated successfully"
    except Exception as e:
        return f"error: {e}"

def handle_client(conn, addr):
    username = None
    try:
        username_len = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
        username = recv_exact(conn, username_len).decode(FORMAT)

        email_len = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
        email = recv_exact(conn, email_len).decode(FORMAT)
        
        password_len = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
        password = recv_exact(conn, password_len).decode(FORMAT)

        key_len = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
        pub_key = recv_exact(conn, key_len).decode(FORMAT)
        
        adder(username,email,password,pub_key)
        
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
                    send_with_header(clients[recipient], username)
                    send_with_header(clients[recipient], encrypted)

                    conn.send(b"SYS")
                    send_with_header(conn, "Message delivered")
                else:
                    conn.send(b"SYS")
                    send_with_header(conn, "Recipient not online")

            elif msg.decode(FORMAT).strip() == "disconnect":
                break
            elif msg == b"LISTUSERS":
                conn.send(b"USR")
                send_with_header(conn, "\n".join(client_keys.keys()))
    except Exception as e:
        print(f"[ERR] {username}: {e}")
   
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[Server] Listening on {SERVER}:{PORT}")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
conns.close()