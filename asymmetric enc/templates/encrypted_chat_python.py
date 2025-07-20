import tkinter as tk
from tkinter import ttk, scrolledtext
import random
import math
import threading
import time

class EncryptedChatUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Encrypted Chat")
        self.root.geometry("700x800")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom colors
        self.bg_color = '#1a1a2e'
        self.container_bg = '#10142b'
        self.input_bg = '#1e2346'
        self.border_color = '#4f46e5'
        self.text_color = '#ffffff'
        self.accent_color = '#ff6b9d'
        
        # Particles for animation
        self.particles = []
        self.animation_running = True
        
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.container_bg, relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg=self.container_bg)
        header_frame.pack(fill='x', pady=(20, 30))
        
        # Lock icon and title
        title_frame = tk.Frame(header_frame, bg=self.container_bg)
        title_frame.pack(anchor='w')
        
        lock_label = tk.Label(title_frame, text="🔒", font=('Arial', 24), 
                             bg=self.container_bg, fg='#feca57')
        lock_label.pack(side='left', padx=(0, 10))
        
        title_label = tk.Label(title_frame, text="Encrypted Chat", 
                              font=('Arial', 28, 'bold'), 
                              bg=self.container_bg, fg=self.text_color)
        title_label.pack(side='left')
        
        # Login section
        login_frame = tk.Frame(main_frame, bg=self.container_bg)
        login_frame.pack(fill='x', pady=(0, 30))
        
        # Username input
        self.username_var = tk.StringVar(value="sagar")
        username_entry = tk.Entry(login_frame, textvariable=self.username_var,
                         font=('Arial', 14), bg=self.input_bg,
                         fg=self.text_color, relief='flat',
                         insertbackground=self.text_color,
                         bd=2, highlightthickness=2,
                         highlightcolor=self.border_color,
                         highlightbackground='#4f46e5')
        username_entry.pack(side='left', fill='x', expand=True,                   # Removed alpha channel
                         padx=(0, 10), ipady=12)
        
        # Login button
        self.login_btn = tk.Button(login_frame, text="Log in", 
                                  font=('Arial', 14, 'bold'),
                                  bg=self.border_color, fg=self.text_color,
                                  relief='flat', bd=0, padx=30, pady=12,
                                  cursor='hand2', command=self.login_clicked)
        self.login_btn.pack(side='right')
        
        # Online users section
        users_label = tk.Label(main_frame, text="Online Users", 
                              font=('Arial', 16, 'bold'),
                              bg=self.container_bg, fg=self.accent_color)
        users_label.pack(anchor='w', pady=(0, 10))
        
        # Users display area
        users_frame = tk.Frame(main_frame, bg=self.input_bg, relief='flat', bd=2)
        users_frame.pack(fill='x', pady=(0, 20))
        
        self.users_label = tk.Label(users_frame, text="No users online", 
                                   font=('Arial', 12),
                                   bg=self.input_bg, fg='#888888',
                                   pady=40)
        self.users_label.pack(fill='both', expand=True)
        
        # Chat section
        chat_info_frame = tk.Frame(main_frame, bg=self.container_bg)
        chat_info_frame.pack(fill='x', pady=(0, 10))
        
        chat_label = tk.Label(chat_info_frame, text="Chatting with:", 
                             font=('Arial', 14),
                             bg=self.container_bg, fg='#c084fc')
        chat_label.pack(side='left')
        
        chat_status = tk.Label(chat_info_frame, text="None", 
                              font=('Arial', 14),
                              bg=self.container_bg, fg='#888888')
        chat_status.pack(side='left', padx=(8, 0))
        
        # Chat area
        self.chat_area = scrolledtext.ScrolledText(main_frame, 
                                                  font=('Arial', 12),
                                                  bg=self.input_bg,
                                                  fg=self.text_color,
                                                  relief='flat', bd=2,
                                                  height=12,
                                                  wrap=tk.WORD,
                                                  insertbackground=self.text_color,
                                                  selectbackground=self.border_color,
                                                  state='disabled')
        self.chat_area.pack(fill='both', expand=True, pady=(0, 20))
        
        # Message input section
        message_frame = tk.Frame(main_frame, bg=self.container_bg)
        message_frame.pack(fill='x')
        
        # Message input
        self.message_var = tk.StringVar()
        message_entry = tk.Entry(message_frame, textvariable=self.message_var,
                                font=('Arial', 14), bg=self.input_bg,
                                fg=self.text_color, relief='flat',
                                insertbackground=self.text_color,
                                bd=2, highlightthickness=2,
                                highlightcolor=self.border_color,
                                highlightbackground='#4f46e533')
        message_entry.pack(side='left', fill='x', expand=True, 
                          padx=(0, 10), ipady=12)
        message_entry.bind('<Return>', self.send_message)
        
        # Send button
        send_btn = tk.Button(message_frame, text="Send", 
                            font=('Arial', 14, 'bold'),
                            bg=self.accent_color, fg=self.text_color,
                            relief='flat', bd=0, padx=30, pady=12,
                            cursor='hand2', command=self.send_message)
        send_btn.pack(side='right')
        
        # Add some placeholder text to chat area
        self.add_system_message("Welcome to Encrypted Chat!")
        
    def setup_animations(self):
        # Create animated particles
        self.canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.canvas.lower()  # Put canvas behind other widgets
        
        # Create particles
        for _ in range(15):
            x = random.randint(0, 700)
            y = random.randint(0, 800)
            size = random.randint(2, 6)
            color = random.choice(['#ff6b9d', '#4ecdc4', '#45b7d1', '#96ceb4', 
                                 '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd'])
            speed = random.uniform(0.5, 2)
            direction = random.uniform(0, 2 * math.pi)
            
            particle = {
                'x': x, 'y': y, 'size': size, 'color': color,
                'speed': speed, 'direction': direction,
                'id': self.canvas.create_oval(x, y, x+size, y+size, 
                                            fill=color, outline=color)
            }
            self.particles.append(particle)
        
        # Start animation
        self.animate_particles()
        
    def animate_particles(self):
        if not self.animation_running:
            return
            
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        for particle in self.particles:
            # Move particle
            particle['x'] += math.cos(particle['direction']) * particle['speed']
            particle['y'] += math.sin(particle['direction']) * particle['speed']
            
            # Bounce off edges
            if particle['x'] <= 0 or particle['x'] >= width:
                particle['direction'] = math.pi - particle['direction']
            if particle['y'] <= 0 or particle['y'] >= height:
                particle['direction'] = -particle['direction']
                
            # Keep particles in bounds
            particle['x'] = max(0, min(width, particle['x']))
            particle['y'] = max(0, min(height, particle['y']))
            
            # Update particle position
            self.canvas.coords(particle['id'], 
                             particle['x'], particle['y'],
                             particle['x'] + particle['size'],
                             particle['y'] + particle['size'])
        
        # Schedule next animation frame
        self.root.after(50, self.animate_particles)
        
    def login_clicked(self):
        username = self.username_var.get().strip()
        if username:
            # Change button appearance temporarily
            self.login_btn.config(text="Logged in", bg='#22c55e')
            self.add_system_message(f"User '{username}' logged in!")
            
            # Reset button after 2 seconds
            self.root.after(2000, lambda: self.login_btn.config(
                text="Log in", bg=self.border_color))
            
    def send_message(self, event=None):
        message = self.message_var.get().strip()
        if message:
            self.add_message(self.username_var.get(), message)
            self.message_var.set("")
            
    def add_message(self, username, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{username}: {message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
        
    def add_system_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"[System] {message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
        
    def run(self):
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        self.animation_running = False
        self.root.destroy()

if __name__ == "__main__":
    app = EncryptedChatUI()
    app.run()