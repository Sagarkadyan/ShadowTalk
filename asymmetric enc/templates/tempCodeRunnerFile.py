 def connect_to_server(self):
        """Connect to the chat server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('localhost', 9999))  # Update with your server IP
            
            # Send username and public key to server
            self.send_with_header(self.username.get().strip())
            self.send_with_header(self.pubkey.save_pkcs1("PEM"))
            
            # Start receiver thread
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")

    def send_with_header(self, data):
        """Send data with length header"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.client_socket.send(len(data).to_bytes(4, 'big'))
        self.client_socket.send(data)

    def receive_messages(self):
        """Handle incoming messages from server"""
        while True:
            try:
                msg_type = self.client_socket.recv(3).decode('utf-8')
                msg_len = int.from_bytes(self.client_socket.recv(4), 'big')
                msg = self.client_socket.recv(msg_len)

                if msg_type == "MSG":
                    decrypted = rsa.decrypt(msg, self.privkey).decode('utf-8')
                    self.root.after(0, self.add_message, "Peer", decrypted, False)
                
                elif msg_type == "KEY":
                    self.peer_pubkey = rsa.PublicKey.load_pkcs1(msg)
                
                elif msg_type == "SYS":
                    self.root.after(0, self.add_system_message, msg.decode('utf-8'))

            except Exception as e:
                self.root.after(0, self.add_system_message, f"Connection error: {e}")
                break

    def send_message(self, event=None):
        """Send encrypted message to peer"""
        msg = self.message_entry.get().strip()
        if not msg or not self.current_chat_partner:
            return
        
        try:
            # Encrypt with peer's public key
            encrypted = rsa.encrypt(msg.encode('utf-8'), self.peer_pubkey)
            self.send_with_header(f"SENDMSG:{self.current_chat_partner}".encode('utf-8') + b":" + encrypted)
            self.add_message("You", msg, is_own=True)
            self.message_entry.delete(0, tk.END)
            
        except Exception as e:
            self.add_system_message(f"Send failed: {e}")
