import socket
import threading
import time
import rsa
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

HEADER = 64
PORT = 9999
FORMAT = "utf-8"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

# Load your keys (make sure public.pem and private.pem exist in this folder)
with open("public.pem", "rb") as f:
    my_pub = rsa.PublicKey.load_pkcs1(f.read())
with open("private.pem", "rb") as f:
    my_priv = rsa.PrivateKey.load_pkcs1(f.read())

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def recv_exact(sock, num):
    data = b""
    while len(data) < num:
        chunk = sock.recv(num - len(data))
        if not chunk:
            raise ConnectionError("Socket closed")
        data += chunk
    return data

def send_with_header(sock, data):
    if isinstance(data, str):
        data = data.encode(FORMAT)
    sock.send(str(len(data)).encode(FORMAT).ljust(HEADER))
    time.sleep(0.01)
    sock.send(data)

# GUI setup
root = tk.Tk()
root.title("Encrypted Chat Client")

chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, state='disabled')
chat_log.pack(padx=10, pady=10)

frame = tk.Frame(root)
frame.pack()

recipient_entry = tk.Entry(frame, width=20)
recipient_entry.pack(side=tk.LEFT, padx=(10, 5))
recipient_entry.insert(0, "Recipient")

message_entry = tk.Entry(frame, width=40)
message_entry.pack(side=tk.LEFT, padx=(5, 5))

def add_message(text):
    chat_log.config(state='normal')
    chat_log.insert(tk.END, text + "\n")
    chat_log.yview(tk.END)
    chat_log.config(state='disabled')

def receive():
    while True:
        try:
            msg_type = recv_exact(client, 3).decode(FORMAT)
            msg_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
            msg = recv_exact(client, msg_len)

            if msg_type == "MSG":
                try:
                    decrypted = rsa.decrypt(msg, my_priv).decode(FORMAT)
                    add_message(f"[Message]: {decrypted}")
                except Exception as e:
                    add_message(f"[!] Decryption failed: {e}")
            elif msg_type == "SYS":
                add_message(f"[System]: {msg.decode(FORMAT)}")
            elif msg_type == "KEY":
                pending_queue.put(msg)  # Only the last requested key goes here
        except Exception as e:
            add_message(f"[Receiver Error]: {e}")
            break

pending_queue = queue.Queue()

def send_message():
    to = recipient_entry.get().strip()
    msg = message_entry.get().strip()
    message_entry.delete(0, tk.END)

    if not to or not msg:
        return

    # Request recipient's key
    send_with_header(client, f"REQUESTKEY:{to}")

    try:
        msg_type = recv_exact(client, 3).decode(FORMAT)
        if msg_type != "KEY":
            err_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
            err_msg = recv_exact(client, err_len).decode(FORMAT)
            add_message(f"[System]: {err_msg}")
            return

        key_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
        key_pem = recv_exact(client, key_len)
        their_key = rsa.PublicKey.load_pkcs1(key_pem, format="PEM")
        encrypted = rsa.encrypt(msg.encode(FORMAT), their_key)
        payload = f"SENDMSG:{to}".encode(FORMAT) + b":" + encrypted
        send_with_header(client, payload)

        ack_type = recv_exact(client, 3).decode(FORMAT)
        if ack_type == "SYS":
            ack_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
            ack_msg = recv_exact(client, ack_len).decode(FORMAT)
            add_message(f"[System]: {ack_msg}")
    except Exception as e:
        add_message(f"[Error]: {e}")

# Login prompt
username = simpledialog.askstring("Login", "Enter your username:", parent=root)
if not username:
    messagebox.showerror("Error", "Username is required.")
    root.quit()

send_with_header(client, username)
time.sleep(0.05)
send_with_header(client, my_pub.save_pkcs1("PEM"))

# Receiver thread
threading.Thread(target=receive, daemon=True).start()

send_button = tk.Button(frame, text="Send", width=10, command=send_message)
send_button.pack(side=tk.LEFT, padx=(5, 10))

root.protocol("WM_DELETE_WINDOW", lambda: (send_with_header(client, "disconnect"), root.destroy()))
root.mainloop()
