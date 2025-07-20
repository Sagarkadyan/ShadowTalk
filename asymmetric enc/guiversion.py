import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
import rsa
import time
import queue
from datetime import datetime

class EncryptedChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Encrypted Chat")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f2f5")
        self.style.configure("TButton", font=("Segoe UI", 10), padding=6)
        self.style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 10))
        self.style.configure("TEntry", font=("Segoe UI", 10), padding=5)
        
        # Generate RSA keys
        self.pubkey, self.privkey = rsa.newkeys(512)
        
        # Network configuration
        self.HEADER = 4
        self.PORT = 9999
        self.FORMAT = "utf-8"
        self.SERVER = "127.0.0.1"
        self.ADDR = (self.SERVER, self.PORT)
        
        # Chat state
        self.username = ""
        self.current_recipient = ""
        self.online_users = set()
        self.messages = []
        self.client_socket = None
        self.response_queue = queue.Queue()
        
        # Create UI
        self.create_login_ui()
        
    def create_login_ui(self):
        """Create the login interface"""
        self.clear_window()
        
        self.login_frame = ttk.Frame(self.root, style="TFrame")
        self.login_frame.pack(expand=True, padx=20, pady=20)
        
        ttk.Label(self.login_frame, text="Encrypted Chat", font=("Segoe UI", 16, "bold")).pack(pady=20)
        
        login_container = ttk.Frame(self.login_frame, style="TFrame")
        login_container.pack(pady=10)
        
        ttk.Label(login_container, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = ttk.Entry(login_container, width=25)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.username_entry.bind("<Return>", lambda e: self.handle_login())
        
        login_btn = ttk.Button(
            login_container, 
            text="Login", 
            command=self.handle_login,
            style="Accent.TButton"
        )
        login_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Configure accent button style
        self.style.configure("Accent.TButton", background="#4a6fa5", foreground="white")
        
    def create_chat_ui(self):
        """Create the main chat interface"""
        self.clear_window()
        
        # Main container
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Online users panel
        self.users_frame = ttk.Frame(self.main_frame, width=200, style="TFrame")
        self.users_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(
            self.users_frame, 
            text="Online Users", 
            font=("Segoe UI", 11, "bold")
        ).pack(pady=10)
        
        # Treeview for users list
        self.users_tree = ttk.Treeview(
            self.users_frame,
            columns=("status", "username"),
            show="headings",
            height=20,
            selectmode="browse"
        )
        self.users_tree.heading("status", text="")
        self.users_tree.heading("username", text="User")
        self.users_tree.column("status", width=30, stretch=False)
        self.users_tree.column("username", width=150)
        self.users_tree.pack(fill=tk.BOTH, expand=True)
        self.users_tree.bind("<<TreeviewSelect>>", self.select_user)
        
        # Chat area
        self.chat_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chat header
        self.chat_header = ttk.Label(
            self.chat_frame,
            text="Select a user to chat",
            font=("Segoe UI", 11, "bold"),
            style="TLabel"
        )
        self.chat_header.pack(fill=tk.X, pady=10)
        
        # Message display
        self.message_display = scrolledtext.ScrolledText(
            self.chat_frame,
            font=("Segoe UI", 10),
            state=tk.DISABLED,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            bg="white",
            bd=0,
            highlightthickness=1,
            highlightbackground="#ddd"
        )
        self.message_display.pack(fill=tk.BOTH, expand=True)
        
        # Message input
        self.input_frame = ttk.Frame(self.chat_frame, style="TFrame")
        self.input_frame.pack(fill=tk.X, pady=5)
        
        self.message_entry = ttk.Entry(
            self.input_frame,
            font=("Segoe UI", 10)
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        self.send_button = ttk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message,
            style="Accent.TButton"
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Disable input until user is selected
        self.message_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        
        # Configure tags for message styling
        self.message_display.tag_config("you", foreground="#2c7be5")
        self.message_display.tag_config("them", foreground="#6e84a3")
        self.message_display.tag_config("time", foreground="#95aac9")
        self.message_display.tag_config("message", lmargin1=20, lmargin2=20)
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def handle_login(self):
        """Handle the login process"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        self.username = username
        
        try:
            # Connect to server
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(self.ADDR)
            
            # Send login info
            self.send_with_header(username)
            time.sleep(0.1)
            self.send_with_header(self.pubkey.save_pkcs1("PEM"))
            
            # Start receiver thread
            threading.Thread(target=self.receive_handler, daemon=True).start()
            
            # Create chat UI
            self.create_chat_ui()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
    
    def send_with_header(self, data):
        """Send data with length header"""
        if isinstance(data, str):
            data = data.encode(self.FORMAT)
        self.client_socket.send(str(len(data)).encode(self.FORMAT).ljust(self.HEADER))
        time.sleep(0.1)
        self.client_socket.send(data)
    
    def receive_handler(self):
        """Handle incoming messages"""
        while True:
            try:
                msg_type = self.client_socket.recv(3).decode(self.FORMAT)
                msg_len = int(self.client_socket.recv(self.HEADER).decode(self.FORMAT).strip())
                msg = self.client_socket.recv(msg_len)

                if msg_type == "MSG":
                    try:
                        decrypted = rsa.decrypt(msg, self.privkey).decode(self.FORMAT)
                        if ":" in decrypted:  # Format: "sender:recipient:message"
                            sender, recipient, message = decrypted.split(":", 2)
                            self.messages.append({
                                'sender': sender,
                                'recipient': recipient,
                                'message': message,
                                'timestamp': time.time(),
                                'encrypted': True
                            })
                            
                            # Update UI if this message is relevant to current view
                            if recipient == self.username or sender == self.current_recipient:
                                self.update_message_display()
                                
                    except Exception as e:
                        print(f"Decryption error: {e}")

                elif msg_type == "USR":
                    users = msg.decode(self.FORMAT).split(",")
                    self.online_users = set(users)
                    self.update_users_list()

            except Exception as e:
                print(f"Connection error: {e}")
                break
    
    def update_users_list(self):
        """Update the online users list"""
        if not hasattr(self, 'users_tree'):
            return
            
        # Clear current items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        # Add online users
        for user in sorted(self.online_users):
            if user != self.username:
                self.users_tree.insert("", tk.END, values=("●", user), tags=("online",))
        
        # Highlight current recipient if any
        if self.current_recipient and self.current_recipient in self.online_users:
            for child in self.users_tree.get_children():
                if self.users_tree.item(child)["values"][1] == self.current_recipient:
                    self.users_tree.selection_set(child)
                    break
    
    def select_user(self, event):
        """Handle user selection from the list"""
        selection = self.users_tree.selection()
        if selection:
            self.current_recipient = self.users_tree.item(selection[0])["values"][1]
            self.chat_header.config(text=f"Chat with {self.current_recipient}")
            self.message_entry.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.message_entry.focus()
            self.update_message_display()
    
    def update_message_display(self):
        """Update the message display with current conversation"""
        if not hasattr(self, 'message_display'):
            return
            
        self.message_display.config(state=tk.NORMAL)
        self.message_display.delete(1.0, tk.END)
        
        # Filter messages for current conversation
        conversation = [
            m for m in self.messages 
            if (m['sender'] == self.username and m['recipient'] == self.current_recipient) or
               (m['sender'] == self.current_recipient and m['recipient'] == self.username)
        ]
        
        # Sort by timestamp and display
        for msg in sorted(conversation, key=lambda x: x['timestamp']):
            timestamp = datetime.fromtimestamp(msg['timestamp']).strftime("%H:%M")
            is_you = msg['sender'] == self.username
            
            # Format message display
            self.message_display.insert(tk.END, f"{timestamp} ", "time")
            self.message_display.insert(tk.END, "You" if is_you else msg['sender'], "you" if is_you else "them")
            self.message_display.insert(tk.END, ":\n", "time")
            self.message_display.insert(tk.END, f"{msg['message']}\n\n", "message")
        
        self.message_display.config(state=tk.DISABLED)
        self.message_display.see(tk.END)
    
    def send_message(self):
        """Send a message to the selected user"""
        message = self.message_entry.get().strip()
        if not message or not self.current_recipient:
            return
            
        try:
            # Request recipient's public key
            self.send_with_header(f"REQUESTKEY:{self.current_recipient}")
            time.sleep(0.5)  # Wait briefly for key response
            
            # Encrypt and send message
            full_msg = f"{self.username}:{self.current_recipient}:{message}"
            encrypted = rsa.encrypt(full_msg.encode(self.FORMAT), self.pubkey)
            self.send_with_header(f"SENDMSG:{self.current_recipient}:".encode(self.FORMAT) + encrypted)
            
            # Add to local messages
            self.messages.append({
                'sender': self.username,
                'recipient': self.current_recipient,
                'message': message,
                'timestamp': time.time(),
                'encrypted': True
            })
            
            # Update display and clear input
            self.update_message_display()
            self.message_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Send Error", f"Failed to send message: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set theme (requires ttkthemes or similar)
    try:
        from ttkthemes import ThemedStyle
        style = ThemedStyle(root)
        style.set_theme("arc")
    except ImportError:
        pass
    
    app = EncryptedChatApp(root)
    root.mainloop()