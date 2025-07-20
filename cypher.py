import tkinter as tk
from tkinter import scrolledtext

# Function to log in
def login():
    username = entry_username.get()
    label_chatting.config(text=f"Chatting with: {username}")
    # Clear the entry field
    entry_username.delete(0, tk.END)

# Function to send message
def send_message():
    message = entry_message.get()
    if message:
        chat_display.configure(state='normal')
        chat_display.insert(tk.END, f"You: {message}\n")
        chat_display.configure(state='disabled')
        entry_message.delete(0, tk.END)

# Create main window
root = tk.Tk()
root.title("Encrypted Chat")
root.geometry("400x600")
root.configure(bg='#1E1E2F')

# Entry for username
entry_username = tk.Entry(root, width=30)
entry_username.pack(pady=10)
button_login = tk.Button(root, text="Log in", command=login, bg='lightblue')
button_login.pack(pady=5)

# Online Users label
label_online_users = tk.Label(root, text="Online Users:", bg='#1E1E2F', fg='pink')
label_online_users.pack(pady=5)

# Online users display
users_display = scrolledtext.ScrolledText(root, width=20, height=5, state='normal')
users_display.pack(pady=5)

# Chatting with label
label_chatting = tk.Label(root, text="Chatting with: None", bg='#1E1E2F', fg='pink')
label_chatting.pack(pady=5)

# Chat display
chat_display = scrolledtext.ScrolledText(root, width=50, height=15, state='disabled')
chat_display.pack(pady=5)

# Entry for message
entry_message = tk.Entry(root, width=30)
entry_message.pack(pady=5)
button_send = tk.Button(root, text="Send", command=send_message, bg='pink')
button_send.pack(pady=5)

# Run the application
root.mainloop()

