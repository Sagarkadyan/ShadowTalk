import socket
import threading
import json
import sqlite3
import database

# Connect (creates the database file if it doesn't exist)
conns = sqlite3.connect('users.db' ,check_same_thread=False)
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
def adder(name, email, password, cypher_text):
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, cypher_text) VALUES (?, ?, ?, ?)",
            (name, email, password, cypher_text)
        )
        conns.commit()
        return "Inserted successfully!"
    except sqlite3.IntegrityError:
        return "Email already exists."

def check_password(cursor, name, user_password):
    try:
        cursor.execute(
            "SELECT password FROM users WHERE name = ?", (name,)
        )
        row = cursor.fetchone()
        if row is None:
            return "user not found"
        stored_password = row[0]
        if stored_password == user_password:
            return "correct pass"
        else:
            return "wrong pass"
    except Exception as e:
        return f"invalid pass: {e}"
 
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
    try:
        while True:
            try:
                header_raw = recv_exact(conn, HEADER)
                msg_len = int(header_raw.decode(FORMAT).strip())
                data_bytes = recv_exact(conn, msg_len)
    # Decode JSON
                try:
                    data = json.loads(data_bytes.decode(FORMAT))
                    if data.get('type') == 'registration':
                        username = data.get('username')
                        email = data.get('email')
                        password = data.get('password')
                        pub_key = data.get('pub_key')
                        adder(username, email, password, pub_key)
                        print(f"[+] {username} registered.")
                        client_keys[username] = pub_key
                        clients[username] = conn

            
        

     
                    elif data.get('type') == 'login':
                        username = data.get('username')
                        password = data.get('password')
                        check_password(cursor,usename,password)
                    
        
                except Exception as e:
                    print(f"[ERR] Failed to parse registration JSON: {e}")
                    conn.close()
                    return

                    while True:
            
                        try:
                            header_raw = recv_exact(conn, HEADER)
                            msg_len = int(header_raw.decode(FORMAT).strip())
                            msg = recv_exact(conn, msg_len)
                            # ...handle your message here...
                        except ConnectionError:
                            print(f"[{addr}] Client disconnected")
                            break
                        except Exception as e:
                            print(f"[{addr}] Unexpected error: {e}")
                            break
            except Exception as e:
                        print(f"[{addr}] Error during handling: {e}")
    finally:
                        conn.close()
                        print(f"[{addr}] Connection closed")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[Server] Listening on {SERVER}:{PORT}")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
conns.close()