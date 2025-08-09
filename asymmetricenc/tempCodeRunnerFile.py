from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import socket
import threading
import time
import rsa
import queue
import json 


HEADER = 4
PORT = 24179  # Playit assigned port
FORMAT = "utf-8"

LOCAL_MODE = False
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
        return render_template('chat.html', username=session['username'])
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username1')
    password = data.get('password1')
    # For demo: any username/password is valid if username not blank
    firebase={
        "type": "login",
        "username": username,
        "password": password
    }
    json_str = json.dumps(firebase)
    json_bytes = json_str.encode('utf-8')
    send_with_header(client, json_bytes)
    return jsonify({'success': False, 'error': 'Invalid username'}), 400

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    firebase={
        "type": "registration",
        "username": username,
        "email": email,
        "password": password,
        "pub_key": my_pub.save_pkcs1("PEM").decode('utf-8')
    }
    json_str = json.dumps(firebase)
    json_bytes = json_str.encode('utf-8')

    send_with_header(client,json_bytes)
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

def send_with_header(sock,data):

    if isinstance(data, str):
        data = data.encode(FORMAT)
    sock.send(str(len(data)).encode(FORMAT).ljust(HEADER))
    time.sleep(0.01)
    sock.send(data)


pubkey, privkey = rsa.newkeys(512)
with open("public.pem", "wb") as f:
    f.write(pubkey.save_pkcs1("PEM"))

with open("private.pem", "wb") as f:
    f.write(privkey.save_pkcs1("PEM"))




with open("public.pem", "rb") as f:
    my_pub = rsa.PublicKey.load_pkcs1(f.read())
with open("private.pem", "rb") as f:
    my_priv = rsa.PrivateKey.load_pkcs1(f.read())


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)



if __name__ == "__main__":
    app.run(debug=True)