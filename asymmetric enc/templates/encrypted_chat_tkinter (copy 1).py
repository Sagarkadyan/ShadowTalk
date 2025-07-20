import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import rsa
import socket
import time
import random

HEADER = 64
PORT = 9999
FORMAT = "utf-8"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

class EncryptedChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Encrypted Chat")
        self.root.geometry("800x600")
        
        # Network and encryption setup
        self.client_socket = None
        self.response_queue = queue.Queue()
        self.pubkey, self.privkey = rsa.newkeys(512)
        self.peer_pubkey = None
        
        # Set dark theme colors
        self.bg_color = "#0a0f0a"
        self.card_bg = "#1a2a1a"
        self.green_primary = "#22c55e"
        self.green_dark = "#16a34a"
        self.text_color = "#ffffff"
        self.text_secondary = "#9ca3af"
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.username = tk.StringVar(value="")
        self.is_logged_in = False
        self.online_users = []
        self.current_chat_partner = None
        
        # Create matrix background effect
        self.create_matrix_background()
        
        # Create main UI
        self.create_main_interface()
        
        # Start matrix animation
        self.animate_matrix()

    # ... [Keep all your existing UI methods until login() unchanged] ...

    def login(self):
        """Handle login with actual server connection"""
        username = self.username.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        try:
            self.connect_to_server()
            self.is_logged_in = True
            self.chat_frame.pack(pady=20)
            self.add_system_message("Connected to encrypted chat server")
            self.add_system_message("Select a user to start chatting")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")

    def connect_to_server(self):
        """Connect to the chat server"""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(ADDR)
        
        # Send username and public key to server
        self.send_with_header(self.username.get().strip())
        self.send_with_header(self.pubkey.save_pkcs1("PEM"))
        
        # Start receiver thread
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_with_header(self, data):
        """Send data with length header"""
        if isinstance(data, str):
            data = data.encode(FORMAT)
        self.client_socket.send(len(data).to_bytes(4, 'big'))
        self.client_socket.send(data)

    def receive_messages(self):
        """Handle incoming messages from server"""
        while True:
            try:
                msg_type = self.client_socket.recv(3).decode(FORMAT)
                msg_len = int.from_bytes(self.client_socket.recv(4), 'big')
                msg = self.client_socket.recv(msg_len)

                if msg_type == "MSG":
                    decrypted = rsa.decrypt(msg, self.privkey).decode(FORMAT)
                    self.root.after(0, self.add_message, self.current_chat_partner, decrypted, False)
                
                elif msg_type == "KEY":
                    self.peer_pubkey = rsa.PublicKey.load_pkcs1(msg)
                
                elif msg_type == "SYS":
                    self.root.after(0, self.add_system_message, msg.decode(FORMAT))
                
                elif msg_type == "USR":  # Online users update
                    users = msg.decode(FORMAT).split(',')
                    self.root.after(0, self.update_online_users, users)

            except Exception as e:
                self.root.after(0, self.add_system_message, f"Connection error: {e}")
                break

    def update_online_users(self, users):
        """Update online users list from server"""
        self.online_users = [u for u in users if u != self.username.get()]
        self.users_listbox.delete(0, tk.END)
        for user in self.online_users:
            self.users_listbox.insert(tk.END, user)

    def on_user_select(self, event):
        """Handle user selection and request their public key"""
        selection = self.users_listbox.curselection()
        if selection:
            user = self.users_listbox.get(selection[0])
            self.current_chat_partner = user
            self.chat_status.configure(text=f"Chatting with:\n{user}")
            
            # Clear chat and request public key
            self.messages_area.configure(state=tk.NORMAL)
            self.messages_area.delete(1.0, tk.END)
            self.messages_area.configure(state=tk.DISABLED)
            
            self.add_system_message(f"Requesting connection to {user}...")
            self.send_with_header(f"REQUESTKEY:{user}")

    def send_message(self, event=None):
        """Send encrypted message to peer"""
        msg = self.message_entry.get().strip()
        if not msg or msg == "Type a message...":
            return
        
        if not self.current_chat_partner:
            messagebox.showwarning("Warning", "Please select a user to chat with")
            return
        
        if not self.peer_pubkey:
            messagebox.showwarning("Warning", "Waiting for recipient's encryption key...")
            return
        
        try:
            # Encrypt with peer's public key
            encrypted = rsa.encrypt(msg.encode(FORMAT), self.peer_pubkey)
            self.send_with_header(f"SENDMSG:{self.current_chat_partner}:".encode(FORMAT) + encrypted)
            self.add_message("You", msg, is_own=True)
            self.message_entry.delete(0, tk.END)
        except Exception as e:
            self.add_system_message(f"Send failed: {e}")

    # ... [Keep all remaining methods unchanged] ...

def main():
    root = tk.Tk()
    app = EncryptedChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()