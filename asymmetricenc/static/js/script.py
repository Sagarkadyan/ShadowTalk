from pyscript import Element, display
from pyodide.http import pyfetch
import asyncio, json, js

backend_config = {
    "baseUrl": "http://127.0.0.1:5000",
    "endpoints": {
        "conversations": "/conversations",
        "messages": "/messages",
        "sendMessage": "/messages/send",
        "uploadFile": "/files/upload",
        "user": "/user",
        "onlineuser": "/chat/onlineusers"
    },
    "headers": {"Content-Type": "application/json"}
}

current_conversation = "default"

# ================= THEME TOGGLE ==================
def theme_toggle_click(event=None):
    body = js.document.body
    body.dataset.theme = "light" if body.dataset.theme == "dark" else "dark"

# ================= EMOJI PICKER ==================
def emoji_picker(event=None):
    emojis = {
        "smileys": ['😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😉', '😊', '😍']
    }
    emoji_grid = Element("emojiGrid")
    emoji_grid.clear()
    message_input = Element("messageInput")
    for cat in emojis.values():
        for symbol in cat:
            span = js.document.createElement("span")
            span.textContent = symbol
            span.style.cursor = "pointer"
            def emoji_click(evt, symbol=symbol):
                message_input.element.value += symbol
                js.document.getElementById("emojiPickerModal").style.display = "none"
            span.addEventListener("click", emoji_click)
            emoji_grid.element.appendChild(span)

# ================= AUTH ==================
async def login(username, password):
    res = await pyfetch(
        url="/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"username1": username, "password1": password})
    )
    data = await res.json()
    if data.get("success"):
        js.window.location.href = data["redirect"]
    else:
        js.window.alert(data.get("error", "Login failed"))

async def register(username, email, password):
    res = await pyfetch(
        url="/register",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"username": username, "email": email, "password": password})
    )
    data = await res.json()
    js.window.alert(data.get("message", "Registered"))

# ================= MESSAGES ==================
async def load_messages(conversation_id):
    res = await pyfetch(f"/messages?conversation_id={conversation_id}")
    data = await res.json()
    container = Element("messagesContainer")
    container.clear()
    for msg in data:
        sender = msg.get("sender", "Unknown")
        text = msg.get("text", "")
        container.write(f"{sender}: {text}<br>")

async def send_message(event=None):
    message_input = Element("messageInput")
    message = message_input.element.value.strip()
    if not message:
        return
    res = await pyfetch(
        url="/messages/send",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"message": message, "conversation_id": current_conversation})
    )
    data = await res.json()
    if data.get("success"):
        container = Element("messagesContainer")
        container.write(f"You: {message}<br>")
        message_input.element.value = ""
    else:
        js.window.alert("Message send failed")

# ================= CONVERSATIONS ==================
async def load_conversations():
    res = await pyfetch("/conversations")
    data = await res.json()
    container = Element("conversationsList")
    container.clear()
    if not data:
        container.write("<p>No conversations</p>")
        return
    for conv in data:
        conv_id = conv.get("id")
        title = conv.get("title", conv_id)
        div = js.document.createElement("div")
        div.textContent = title
        def conv_click(evt, conv_id=conv_id):
            global current_conversation
            current_conversation = conv_id
            asyncio.ensure_future(load_messages(conv_id))
        div.addEventListener("click", conv_click)
        container.element.appendChild(div)

# ================= ONLINE USERS ==================
async def get_online_users():
    url = backend_config["baseUrl"] + backend_config["endpoints"]["onlineuser"]
    res = await pyfetch(url)
    data = await res.json()
    sidebar = Element("online-users")
    sidebar.clear()
    users = data.get("users", [])
    if users:
        for user in users:
            sidebar.write(f"<div class='user-item'>{user}</div>")
    else:
        sidebar.write("<div class='no-users-message'>No users online.</div>")

# ================= FILE UPLOAD ==================
async def upload_files(files):
    form_data = js.FormData.new()
    for f in files:
        form_data.append("file", f)
    res = await pyfetch(url="/files/upload", method="POST", body=form_data)
    data = await res.json()
    print("Files uploaded:", data)

# ================= EVENT SETUP ==================
def setup():
    # Buttons
    Element("sendBtn").element.onclick = lambda e: asyncio.ensure_future(send_message())
    Element("messageInput").element.onkeypress = lambda e: asyncio.ensure_future(send_message()) if e.key == "Enter" else None
    
    js.document.querySelector(".emoji-btn").onclick = emoji_picker
    js.document.querySelector(".theme-toggle").onclick = theme_toggle_click
    
    # Initial load
    asyncio.ensure_future(load_conversations())
    asyncio.ensure_future(get_online_users())
    # Refresh
    def refresh():
        asyncio.ensure_future(get_online_users())
        if current_conversation:
            asyncio.ensure_future(load_messages(current_conversation))
    js.setInterval(refresh, 5000)  # refresh every 5 sec

setup()
