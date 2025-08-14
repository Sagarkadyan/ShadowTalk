from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import socket
import threading
import time
import rsa
import queue
import json 
import logging


HEADER = 4
PORT = 24179  # Playit assigned port
FORMAT = "utf-8"

#LOCAL_MODE = False
SERVER = "ready-lebanon.gl.at.ply.gg"  # Playit assigned address
ADDR = (SERVER, PORT)
# Connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)




app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)


@app.route('/', methods=['GET'])
def home():
    if 'username' in session:
        return render_template('chat.html')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username1')
    password = data.get('password1')
    fireball = {
        "type": "login",
        "username": username,
        "password": password
    }  

    json_bytes = json.dumps(fireball).encode('utf-8')
    send_with_header(client, json_bytes)

    try:
        answer = login_result_queue.get(timeout=3)
    except queue.Empty:
        return jsonify({'success': False, 'error': 'Server did not respond'}), 500

    if answer == "correct pass":
        session['username'] = username
        print("lgdone")
        return jsonify({'success': True})
    elif answer == "wrong pass":
        print("wgpass")
        return jsonify({'success': False, 'error': 'Wrong password'}), 401
    elif answer == "user not found":
        print("wguser")
        return jsonify({'success': False, 'error': 'Invalid username'}), 404
    else:
        print("somethinf is wrong ")
        return jsonify({'success': False, 'error': f'Unexpected: {answer}'}), 500

login_result_queue = queue.Queue()

def listen_to_server():
    while True:
        try:
            header = client.recv(HEADER)
            if not header or header.strip() == b"":
                continue
            try:
                msg_len = int(header.decode(FORMAT).strip())
            except ValueError:
                # Ignore junk/probes
                continue
            if msg_len <= 0:
                continue
            data = recv_exact(client, msg_len)
            if not data:
                continue
            try:
                message = json.loads(data.decode(FORMAT))
            except json.JSONDecodeError:
                continue
            if isinstance(message, dict) and message.get("type") == "login_ans":
                ans = message.get("answer")
                if ans is not None:
                    login_result_queue.put(ans)
        except Exception as e:
            print(f"[CLIENT LISTENER ERROR] {e}")
            break

threading.Thread(target=listen_to_server, daemon=True).start()


 


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    app.logger.info("Flask /register received:", data)

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    firebase = {
        "type": "registration",
        "username": username,
        "email": email,
        "password": password,
        "pub_key": my_pub.save_pkcs1("PEM").decode('utf-8')
    }

    
    #json_bytes = json.dumps(firebase).encode("utf-8")
    #app.logger.info("Client is sending: %r", json_bytes)  # ✅ logger
    print("Client is sending:", json_bytes, flush=True)   # ✅ print

    send_with_header(client, firebase)
    
    return jsonify({'success': True})



@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/send', methods=['POST'])
def send_message():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    content = data.get('message')
    timestamp = data.get('timestamp')
    username = session['username']
    messages.append({'sender': username, 'content': content, 'timestamp': timestamp})
    return jsonify({'status': 'success', 'message': content, 'username': username, 'timestamp': timestamp})

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({'messages': messages})

@app.route('/file-metadata', methods=['POST'])
def file_metadata():
    data = request.json
    if size >= 52428800:
        if type ==  mp4:
            compressor.video_comp(path)
    
    # Just echo the received metadata for demo
    return jsonify({'received': data})

def send_with_header(sock, payload_obj):
    """
    Always send JSON-formatted message with a fixed-size header.
    payload_obj: Python dict/list/serializable object
    """
    try:
        json_str = json.dumps(payload_obj)
        data_bytes = json_str.encode(FORMAT)
        msg_len = str(len(data_bytes)).encode(FORMAT).ljust(HEADER)
        sock.sendall(msg_len)
        sock.sendall(data_bytes)
    except (TypeError, ValueError) as e:
        print(f"[SEND ERROR] Failed to encode JSON: {e}")


def recv_exact(conn, msg_len):
    """
    Receives exactly msg_len bytes from the socket.
    """
    chunks = []
    bytes_recd = 0
    while bytes_recd < msg_len:
        chunk = conn.recv(min(msg_len - bytes_recd, 2048))
        if chunk == b'':
            raise RuntimeError("Socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    return b''.join(chunks)

# ... (The rest of your code) ...

# Inside the handle_client function where you receive the data
try:
    header_bytes = conn.recv(8)  # Assuming the header is 8 bytes
    if not header_bytes:
        # Client disconnected
        return
    msg_len = int.from_bytes(header_bytes, 'big')
    
    data_bytes = recv_exact(conn, msg_len)
    data_str = data_bytes.decode('utf-8')
    data = json.loads(data_str)
    # ... (process the data) ...

except (json.JSONDecodeError, RuntimeError) as e:
    # Handle the specific errors here
    print(f"Error during data reception/decoding: {e}")
pubkey, privkey = rsa.newkeys(512)
with open("public.pem", "wb") as f:
    f.write(pubkey.save_pkcs1("PEM"))

with open("private.pem", "wb") as f:
    f.write(privkey.save_pkcs1("PEM"))

with open("public.pem", "rb") as f:
    my_pub = rsa.PublicKey.load_pkcs1(f.read())
with open("private.pem", "rb") as f:
    my_priv = rsa.PrivateKey.load_pkcs1(f.read())

if __name__ == "__main__":
    app.run(debug=True)