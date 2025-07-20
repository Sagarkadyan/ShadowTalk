import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import random

class EncryptedChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Encrypted Chat")
        self.root.geometry("800x600")
        
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
        self.username = tk.StringVar(value="sagar")
        self.is_logged_in = False
        self.online_users = []
        self.current_chat_partner = None
        self.messages = []
        
        # Create matrix background effect
        self.create_matrix_background()
        
        # Create main UI
        self.create_main_interface()
        
        # Start matrix animation
        self.animate_matrix()
        
    def create_matrix_background(self):
        """Create animated matrix-like background"""
        self.matrix_canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
        self.matrix_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Create matrix characters
        self.matrix_chars = []
        for i in range(100):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            char = random.choice("01")
            opacity = random.uniform(0.1, 0.3)
            color = f"#{int(opacity * 255):02x}{int(opacity * 255):02x}{int(opacity * 255):02x}"
            
            text_id = self.matrix_canvas.create_text(
                x, y, text=char, fill=color, font=("Courier", 12)
            )
            self.matrix_chars.append({
                'id': text_id,
                'x': x,
                'y': y,
                'speed': random.uniform(0.5, 2.0)
            })
    
    def animate_matrix(self):
        """Animate the matrix background"""
        for char in self.matrix_chars:
            char['y'] += char['speed']
            if char['y'] > 600:
                char['y'] = -20
                char['x'] = random.randint(0, 800)
            
            self.matrix_canvas.coords(char['id'], char['x'], char['y'])
        
        self.root.after(50, self.animate_matrix)
    
    def create_main_interface(self):
        """Create the main chat interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title with lock icon
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(pady=(0, 30))
        
        # Lock icon (using Unicode)
        lock_label = tk.Label(title_frame, text="🔒", font=("Arial", 40), 
                             fg=self.green_primary, bg=self.bg_color)
        lock_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Title text
        title_label = tk.Label(title_frame, text="Encrypted Chat", 
                              font=("Arial", 36, "bold"), fg=self.text_color, bg=self.bg_color)
        title_label.pack(side=tk.LEFT)
        
        # Login section
        login_frame = tk.Frame(main_frame, bg=self.bg_color)
        login_frame.pack(pady=(0, 30))
        
        # Username entry
        username_entry = tk.Entry(login_frame, textvariable=self.username, 
                                 font=("Arial", 14), width=20, bg=self.card_bg, 
                                 fg=self.text_color, insertbackground=self.text_color,
                                 relief=tk.FLAT, bd=5)
        username_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=8)
        
        # Login button
        login_btn = tk.Button(login_frame, text="Log in", command=self.login,
                             font=("Arial", 14, "bold"), bg=self.green_primary, 
                             fg="white", relief=tk.FLAT, padx=20, pady=8,
                             activebackground=self.green_dark, cursor="hand2")
        login_btn.pack(side=tk.LEFT)
        
        # Chat interface (initially hidden)
        self.chat_frame = tk.Frame(main_frame, bg=self.bg_color)
        
        # Left panel - Online users
        left_panel = tk.Frame(self.chat_frame, bg=self.card_bg, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Online users title
        users_title = tk.Label(left_panel, text="Online Users", 
                              font=("Arial", 16, "bold"), fg=self.green_primary, 
                              bg=self.card_bg)
        users_title.pack(pady=10)
        
        # Users list
        self.users_listbox = tk.Listbox(left_panel, bg=self.card_bg, fg=self.text_color,
                                       font=("Arial", 12), relief=tk.FLAT, 
                                       selectbackground=self.green_primary,
                                       activestyle="none", height=8)
        self.users_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.users_listbox.bind('<<ListboxSelect>>', self.on_user_select)
        
        # Chat status
        self.chat_status = tk.Label(left_panel, text="Chatting with:\nNone", 
                                   font=("Arial", 12), fg=self.green_primary, 
                                   bg=self.card_bg, justify=tk.LEFT)
        self.chat_status.pack(pady=10)
        
        # Right panel - Chat area
        right_panel = tk.Frame(self.chat_frame, bg=self.card_bg, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Messages area
        self.messages_area = scrolledtext.ScrolledText(right_panel, 
                                                      bg=self.card_bg, fg=self.text_color,
                                                      font=("Arial", 11), relief=tk.FLAT,
                                                      state=tk.DISABLED, wrap=tk.WORD)
        self.messages_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Message input area
        input_frame = tk.Frame(right_panel, bg=self.card_bg)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Message entry
        self.message_entry = tk.Entry(input_frame, font=("Arial", 12), 
                                     bg=self.bg_color, fg=self.text_secondary,
                                     insertbackground=self.text_color, relief=tk.FLAT,
                                     bd=5)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, 
                               padx=(0, 10), ipady=8)
        self.message_entry.insert(0, "Type a message...")
        self.message_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.message_entry.bind('<FocusOut>', self.on_entry_focus_out)
        self.message_entry.bind('<Return>', self.send_message)
        
        # Send button
        send_btn = tk.Button(input_frame, text="Send", command=self.send_message,
                            font=("Arial", 12, "bold"), bg=self.green_primary, 
                            fg="white", relief=tk.FLAT, padx=20, pady=8,
                            activebackground=self.green_dark, cursor="hand2")
        send_btn.pack(side=tk.RIGHT)
    
    def on_entry_focus_in(self, event):
        """Handle focus in event for message entry"""
        if self.message_entry.get() == "Type a message...":
            self.message_entry.delete(0, tk.END)
            self.message_entry.configure(fg=self.text_color)
    
    def on_entry_focus_out(self, event):
        """Handle focus out event for message entry"""
        if not self.message_entry.get():
            self.message_entry.insert(0, "Type a message...")
            self.message_entry.configure(fg=self.text_secondary)
    
    def login(self):
        """Handle login"""
        username = self.username.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        self.is_logged_in = True
        self.chat_frame.pack(pady=20)
        
        # Simulate getting online users
        self.simulate_online_users()
        
        # Add welcome message
        self.add_system_message("Connected to encrypted chat server")
        self.add_system_message("Select a user to start chatting")
    
    def simulate_online_users(self):
        """Simulate online users"""
        sample_users = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
        self.online_users = random.sample(sample_users, random.randint(2, 4))
        
        # Update users listbox
        self.users_listbox.delete(0, tk.END)
        for user in self.online_users:
            self.users_listbox.insert(tk.END, user)
    
    def on_user_select(self, event):
        """Handle user selection"""
        selection = self.users_listbox.curselection()
        if selection:
            user = self.users_listbox.get(selection[0])
            self.current_chat_partner = user
            self.chat_status.configure(text=f"Chatting with:\n{user}")
            
            # Clear messages and add connection message
            self.messages_area.configure(state=tk.NORMAL)
            self.messages_area.delete(1.0, tk.END)
            self.messages_area.configure(state=tk.DISABLED)
            
            self.add_system_message(f"Connected to {user}")
            self.add_system_message("End-to-end encryption enabled")
    
    def add_system_message(self, message):
        """Add system message to chat"""
        self.messages_area.configure(state=tk.NORMAL)
        self.messages_area.insert(tk.END, f"[SYSTEM] {message}\n", "system")
        self.messages_area.configure(state=tk.DISABLED)
        self.messages_area.see(tk.END)
    
    def add_message(self, sender, message, is_own=False):
        """Add message to chat"""
        self.messages_area.configure(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M")
        if is_own:
            self.messages_area.insert(tk.END, f"[{timestamp}] You: {message}\n", "own")
        else:
            self.messages_area.insert(tk.END, f"[{timestamp}] {sender}: {message}\n", "other")
        
        self.messages_area.configure(state=tk.DISABLED)
        self.messages_area.see(tk.END)
    
    def send_message(self, event=None):
        """Send message"""
        message = self.message_entry.get().strip()
        if not message or message == "Type a message...":
            return
        
        if not self.current_chat_partner:
            messagebox.showwarning("Warning", "Please select a user to chat with")
            return
        
        # Add own message
        self.add_message(self.username.get(), message, is_own=True)
        
        # Clear entry
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, "Type a message...")
        self.message_entry.configure(fg=self.text_secondary)
        
        # Simulate response after delay
        self.root.after(1000, lambda: self.simulate_response(message))
    
    def simulate_response(self, original_message):
        """Simulate response from chat partner"""
        responses = [
            "That's interesting!",
            "I see what you mean.",
            "Thanks for sharing that.",
            "Really? Tell me more.",
            "Haha, that's funny!",
            "I agree with you.",
            "That's a good point.",
            "Wow, I didn't know that."
        ]
        
        response = random.choice(responses)
        self.add_message(self.current_chat_partner, response, is_own=False)

def main():
    root = tk.Tk()
    app = EncryptedChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()