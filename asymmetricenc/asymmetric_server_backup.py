import socket
import threading
import json
import sqlite3
import time
import queue

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
        print("Inserted successfully!")
        return "Inserted successfully!"
    except sqlite3.IntegrityError:
        return "Email already exists."
        print("Email already exists.")

def check_password(cursor, name, user_password):
    try:
        cursor.execute(
            "SELECT password FROM users WHERE name = ?", (name,)
        )
        row = cursor.fetchone()
        
        if stored_password == user_password:
            return "correct pass"
            print("cpass")
        else:
            return "wrong pass"
            print("wpass")
    except Exception as e:
        return f"invalid pass: {e}"
        print("ipass")
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



# In asymmetric_server_backup.py
def handle_client(conn, addr):
    """
    Handles a single client connection, processing messages and managing errors.
    """
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        while True:
            # Step 1: Receive the message header
            header_raw = conn.recv(HEADER)
            time.sleep(0.01)
            if not header_raw:
                print(f"[{addr}] Client disconnected gracefully.")
                break

            try:
                msg_len = int(header_raw.decode(FORMAT).strip())
            except ValueError:
                print(f"[{addr}] Received invalid header. Discarding.")
                continue

            if msg_len <= 0:
                continue

            # Step 2: Receive the message body
            data_bytes = recv_exact(conn, msg_len)
            if not data_bytes:
                break

            data_str = data_bytes.decode(FORMAT)

            # Step 3: Process the JSON data
            try:
                data = json.loads(data_str)

                if data.get('type') == 'registration':
                    try:
                        username = data.get('username')
                        email = data.get('email')
                        password = data.get('password')
                        pub_key = data.get('pub_key')
                        adder(username, email, password, pub_key)
                        print(f"[+] {username} registered successfully.")
                        client_keys[username] = pub_key
                        clients[username] = conn
                    except Exception as e:
                        print(f"[{addr}] Error during registration processing: {e}")

                elif data.get('type') == 'login':
                    try:
                        username = data.get('username')
                        password = data.get('password')
                        passwd_result = check_password(cursor, username, password)
                        
                        # --- FIX: The closing brace '}' was missing here ---
                        response = {
                            "type": "login_ans",
                            "answer": passwd_result
                        } # <--- This brace was missing

                        json_str = json.dumps(response)
                        send_with_header(conn, json_str)
                        print(f"[{addr}] Login response sent for {username}")
                    except Exception as e:
                        print(f"[{addr}] Error during login processing: {e}")

            except json.JSONDecodeError:
                print(f"[{addr}] Received non-JSON data: '{data_str}'")
                continue

    except ConnectionResetError:
        print(f"[{addr}] Connection was forcibly closed by the client.")
    except Exception as e:
        print(f"[{addr}] An unexpected error occurred: {e}")
    finally:
        print(f"[{addr}] Closing connection.")
        # ... (cleanup logic is fine) ...
        conn.close()


                      
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[Server] Listening on {SERVER}:{PORT}")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
conns.close()