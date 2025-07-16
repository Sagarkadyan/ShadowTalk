
import os
import socket
import rsa
import time
from flask import Flask, request, jsonify, render_template

# === CONFIG ===
HEADER = 64
FORMAT = "utf-8"
SERVER = "127.0.0.1"  # replace with your TCP server IP
PORT = 9999            # match your TCP server port
ADDR = (SERVER, PORT)

# === RSA Key Generation ===
pubkey, privkey = rsa.newkeys(512)
with open("public.pem", "wb") as f:
    f.write(pubkey.save_pkcs1("PEM"))
with open("private.pem", "wb") as f:
    f.write(privkey.save_pkcs1("PEM"))

# === Flask App ===
app = Flask(__name__)
online_users = set()

# === Helpers ===
def send_with_header(sock, data):
    if isinstance(data, str):
        data = data.encode(FORMAT)
    sock.send(str(len(data)).encode(FORMAT).ljust(HEADER))
    time.sleep(0.01)
    sock.send(data)

def recv_exact(sock, num):
    data = b""
    while len(data) < num:
        chunk = sock.recv(num - len(data))
        if not chunk:
            raise ConnectionError("Socket closed")
        data += chunk
    return data

def save_chat_history(sender, recipient, message):
    fname = f"history_{sender}_{recipient}.txt"
    with open(fname, "a", encoding="utf-8") as f:
        f.write(f"{sender}: {message}\n")

# === Routes ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    try:
        data = request.get_json()
        username = data.get("username")
        recipient = data.get("recipient")
        message = data.get("message")

        if not all([username, recipient, message]):
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        # Register sender
        online_users.add(username)

        # 🔁 Create TCP socket connection here
        global client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)

        # Step 1: send username and public key
        send_with_header(client, username)
        time.sleep(0.05)
        send_with_header(client, pubkey.save_pkcs1("PEM"))

        # Step 2: request recipient public key
        send_with_header(client, f"REQUESTKEY:{recipient}")
        key_type = recv_exact(client, 3).decode(FORMAT)
        key_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
        key_payload = recv_exact(client, key_len)

        if key_type != "KEY":
            client.close()
            return jsonify({"status": "error", "message": "User not found"}), 404

        their_key = rsa.PublicKey.load_pkcs1(key_payload)
        encrypted = rsa.encrypt(message.encode(FORMAT), their_key)

        # Step 3: send encrypted message
        payload = f"SENDMSG:{recipient}".encode(FORMAT) + b":" + encrypted
        send_with_header(client, payload)

        ack_type = recv_exact(client, 3).decode(FORMAT)
        ack_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
        ack_msg = recv_exact(client, ack_len).decode(FORMAT)

        save_chat_history(username, recipient, message)
        client.close()
        return jsonify({"status": "ok", "message": ack_msg})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/history")
def history():
    user1 = request.args.get("user1")
    user2 = request.args.get("user2")
    fname = f"history_{user1}_{user2}.txt"
    if not os.path.exists(fname):
        return jsonify({"history": []})
    with open(fname, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return jsonify({"history": lines})

@app.route("/online")
def get_online():
    return jsonify(sorted(list(online_users)))

@app.route("/register", methods=["POST"])
def register():
    username = request.get_json().get("username")
    online_users.add(username)
    return jsonify({"status": "ok"})

@app.route("/disconnect", methods=["POST"])
def disconnect():
    return jsonify({"status": "disconnected"})

if __name__ == "__main__":
    app.run(debug=True, port=8060)