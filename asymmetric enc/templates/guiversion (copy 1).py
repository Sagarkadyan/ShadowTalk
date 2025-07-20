import socket
import rsa
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

# Configuration
HEADER = 4
FORMAT = "utf-8"
SERVER = "127.0.0.1"
PORT = 9999
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# RSA Keys
pubkey, privkey = rsa.newkeys(512)
username = ""
recipient = ""

def send_with_header(sock, data):
    if isinstance(data, str):
        data = data.encode(FORMAT)
    sock.send(str(len(data)).encode(FORMAT).ljust(HEADER))
    sock.send(data)

def recv_exact(sock, num):
    data = b""
    while len(data) < num:
        chunk = sock.recv(num - len(data))
        if not chunk:
            raise ConnectionError("Disconnected")
        data += chunk
    return data

# GUI class
class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Encrypted Chat")
        self.root.geometry("500x500")

        self.chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.recipient_label = tk.Label(root, text="Recipient:")
        self.recipient_label.pack()
        self.recipient_entry = tk.Entry(root)
        self.recipient_entry.pack(padx=10, pady=5)

        self.message_entry = tk.Entry(root)
        self.message_entry.pack(padx=10, pady=5, fill=tk.X)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        self.username = simpledialog.askstring("Username", "Enter your username:")
        if not self.username:
            self.root.destroy()
            return

        self.connect_to_server()

    def connect_to_server(self):
        try:
            client.connect(ADDR)
            send_with_header(client, self.username)
            send_with_header(client, pubkey.save_pkcs1("PEM"))
            self.log(f"[Connected] as {self.username}")
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))
            self.root.destroy()

    def send_message(self):
        try:
            recipient = self.recipient_entry.get().strip()
            message = self.message_entry.get().strip()
            if not recipient or not message:
                return
            # Request public key
            send_with_header(client, f"REQUESTKEY:{recipient}")
            key_type = recv_exact(client, 3).decode(FORMAT)
            key_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
            key_payload = recv_exact(client, key_len)
            if key_type != "KEY":
                self.log(f"[!] {recipient} not found.")
                return
            their_key = rsa.PublicKey.load_pkcs1(key_payload)
            encrypted = rsa.encrypt(message.encode(FORMAT), their_key)
            payload = f"SENDMSG:{recipient}".encode(FORMAT) + b":" + encrypted
            send_with_header(client, payload)
            ack_type = recv_exact(client, 3).decode(FORMAT)
            ack_len = int(recv_exact(client, HEADER).decode(FORMAT).strip())
            ack_msg = recv_exact(client, ack_len).decode(FORMAT)
            self.log(f"[You → {recipient}]: {message} ✅")
        except Exception as e:
            self.log(f"[Error] {e}")

    def log(self, msg):
        self.chat_box.configure(state='normal')
        self.chat_box.insert(tk.END, msg + "\n")
        self.chat_box.configure(state='disabled')
        self.chat_box.yview(tk.END)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
