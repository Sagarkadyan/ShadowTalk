from flask import Flask, render_template, request, jsonify
import socket
import threading
import rsa
import time
from colorama import init, Fore

app = Flask(__name__)
init()

# Configuration
HEADER = 64
PORT = 9999
FORMAT = "utf-8"
SERVER = "127.0.0.1"  # Use localhost
ADDR = (SERVER, PORT)

# Generate RSA keys
pubkey, privkey = rsa.newkeys(512)
with open("public.pem", "wb") as f:
    f.write(pubkey.save_pkcs1("PEM"))
with open("private.pem", "wb") as f:
    f.write(privkey.save_pkcs1("PEM"))

# Global variables
client_socket = None
current_user = ""
online_users = set()
messages = []
server_connected = False

def connect_to_server():
    global client_socket, server_connected
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(ADDR)
        server_connected = True
        print(f"{Fore.GREEN}Connected to server at {ADDR}{Fore.RESET}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Failed to connect to server: {e}{Fore.RESET}")
        return False

def send_with_header(data):
    if isinstance(data, str):
        data = data.encode(FORMAT)
    client_socket.send(str(len(data)).encode(FORMAT).ljust(HEADER))
    time.sleep(0.1)
    client_socket.send(data)
# Add this to your existing Flask app
@app.route('/get_conversation/<recipient>', methods=['GET'])
def get_conversation(recipient):
    conversation = [
        m for m in messages 
        if (m['sender'] == current_user and m['recipient'] == recipient) or
           (m['sender'] == recipient and m['recipient'] == current_user)
    ]
    return jsonify(conversation)

# Modify your receive_handler
def receive_handler():
    while True:
        try:
            msg_type = client_socket.recv(3).decode(FORMAT)
            msg_len = int(client_socket.recv(HEADER).decode(FORMAT).strip())
            msg = client_socket.recv(msg_len)

            if msg_type == "MSG":
                try:
                    decrypted = rsa.decrypt(msg, privkey).decode(FORMAT)
                    if ":" in decrypted:  # Format: "sender:recipient:message"
                        sender, recipient, message = decrypted.split(":", 2)
                        messages.append({
                            'sender': sender,
                            'recipient': recipient,
                            'message': message,
                            'timestamp': time.time(),
                            'is_encrypted': True
                        })
                except Exception as e:
                    print(f"Decryption error: {e}")

            elif msg_type == "USR":
                online_users.clear()
                online_users.update(msg.decode(FORMAT).split(","))

        except Exception as e:
            print(f"Connection error: {e}")
            break
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    global current_user
    username = request.json.get('username')
    if not username:
        return jsonify({"status": "error", "message": "Username required"}), 400

    if not connect_to_server():
        return jsonify({"status": "error", "message": "Could not connect to chat server"}), 500

    current_user = username
    online_users.add(username)
    
    try:
        send_with_header(username)
        time.sleep(0.1)
        send_with_header(pubkey.save_pkcs1("PEM"))
        
        threading.Thread(target=receive_handler, daemon=True).start()
        return jsonify({"status": "success", "username": username})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/users')
def get_users():
    return jsonify(list(online_users))
# Add this endpoint to your Flask app
@app.route('/get_chat_updates', methods=['GET'])
def get_chat_updates():
    return jsonify({
        'users': list(online_users),
        'messages': [m for m in messages if m['recipient'] == current_user or m['sender'] == current_user],
        'current_user': current_user
    })
@app.route('/messages')
def get_messages():
    return jsonify(messages)
@app.route('/get_chat_updates', methods=['GET'])
def get_chat_updates():
    return jsonify({
        'users': list(online_users),
        'current_user': current_user,
        'status': 'success'
    })

@app.route('/get_conversation/<recipient>', methods=['GET'])
def get_conversation(recipient):
    conversation = [
        m for m in messages 
        if (m['sender'] == current_user and m['recipient'] == recipient) or
           (m['sender'] == recipient and m['recipient'] == current_user)
    ]
    return jsonify({
        'messages': conversation,
        'status': 'success'
    })
@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    recipient = data.get('recipient')
    message = data.get('message')
    
    if not recipient or not message:
        return jsonify({"status": "error", "message": "Recipient and message required"}), 400
    
    try:
        # Request recipient's public key
        send_with_header(f"REQUESTKEY:{recipient}")
        time.sleep(0.5)  # Wait briefly for key response
        
        # Encrypt and send (format: "sender:recipient:message")
        full_msg = f"{current_user}:{recipient}:{message}"
        encrypted = rsa.encrypt(full_msg.encode(FORMAT), pubkey)
        send_with_header(f"SENDMSG:{recipient}:".encode(FORMAT) + encrypted)
        
        # Store message locally
        messages.append({
            "sender": current_user,
            "recipient": recipient,
            "message": message,
            "timestamp": time.time()
        })
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)