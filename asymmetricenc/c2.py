import asyncio
import websockets
import rsa
import json
import os
import threading
from rich.console import Console
from rich.text import Text
from rich.table import Table
from colorama import Fore, Style, init
from alive_progress import alive_bar
import pyfiglet
import time

uri = "ws://127.0.0.1:9999"
main_loop = asyncio.new_event_loop()  # global event loop for websocket
my_pub, my_priv = rsa.newkeys(512)
init(autoreset=True)

console = Console()


def print_banner():
    banner = r"""
  _____ ___ __ __ ____ ___    _____  __   ____    _______   ____  _      __  _ 
 / ___/|  T  T /    T|   \   /   \ |  T__T  T    |      T /    T| T    |  l/ ]
(   \_ |  l  |Y  o  ||    \ Y     Y|  |  |  |    |      |Y  o  || |    |  ' / 
 \__  T|  _  ||     ||  D  Y|  O  ||  |  |  |    l_j  l_j|     || l___ |    \ 
 /  \ ||  |  ||  _  ||     ||     |l  `  '  !      |  |  |  _  ||     T|     Y
 \    ||  |  ||  |  ||     |l     ! \      /       |  |  |  |  ||     ||  .  |
  \___jl__j__jl__j__jl_____j \___/   \_/\_/        l__j  l__j__jl_____jl__j\_j
                                                                              


                 ENCRYPTED CYBERLINK — SHADOWTALK v1.0

    """
    
    for line in banner.splitlines():
        print(Fore.CYAN + Style.BRIGHT + line + Style.RESET_ALL)
        time.sleep(0.05)
print_banner()
def initial():
            print("What will you choose")
            print("1. Register")
            print("2. Login")
            print("Press 1 or 2")
            initial_input = int(input("ENTER"))
            if initial_input == 1:
                print("register")
                register()
            elif initial_input == 2:
                print("login")
            else:
                print("Wrong input re enter choice")
                initial()        
initial()                
with open("public.pem", "wb") as f:
    f.write(my_pub.save_pkcs1("PEM"))

with open("private.pem", "wb") as f:
    f.write(my_priv.save_pkcs1("PEM"))

class PersistentWebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.response_queue = asyncio.Queue()

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        print("Connected to WebSocket server.")
        asyncio.create_task(self.listen())
        asyncio.create_task(self.keepalive())

    async def listen(self):
        try:
            async for message in self.websocket:
                print(f"Received from server: {message}")
                data = json.loads(message)
                if data.get("type") == "pong":
                    continue
                await self.response_queue.put(message)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed.")

    async def send(self, message):
        if self.websocket is None:
            raise ConnectionError("WebSocket is not connected.")
        await self.websocket.send(message)

    async def send_and_wait_response(self, message):
        await self.send(message)
        response = await self.response_queue.get()
        return response
    async def keepalive(self, interval=30):
        """Send a ping every <interval> seconds to keep the connection alive."""
        try:
            while True:
                if self.websocket:
                    try:
                        await self.websocket.send(json.dumps({"type": "ping"}))
                        print("Ping sent to server")
                    except Exception as e:
                        print("Ping failed:", e)
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            print("Keepalive task cancelled")
    

persistent_ws_client = PersistentWebSocketClient(uri)


def register():
    username = input("Enter you usename")
    email = input("Enter your email")
    password = input("Enter you password")
    firebase = {
        "type": "registration",
        "username": data.get('username'),
        "email": data.get('email'),
        "password": data.get('password'),
        "pub_key": my_pub.save_pkcs1("PEM").decode('utf-8')
    }
    run_async(persistent_ws_client.send(json.dumps(firebase)))
    return jsonify({'success': True, 'message': 'Registration request sent.'})

def login():
    print("Incoming login request. Data:", request.json)
    data = request.json
    fireball = {
        "type": "login",
        "username": data.get('username1'),
        "password": data.get('password1')
    }

    response_raw = run_async(persistent_ws_client.send_and_wait_response(json.dumps(fireball)))
    print(f"WebSocket response_raw: {response_raw}")
    response = json.loads(response_raw)
    answer = response.get("answer")
    username = response.get("username")

    if answer == "correct pass":
        session['username'] = username
        return jsonify({'success': True, 'redirect': '/chat'})
    elif answer == "wrong pass":
        return jsonify({'success': False, 'error': 'Wrong password'}), 401
    elif answer == "user not found":
        return jsonify({'success': False, 'error': 'Invalid username'}), 404
    else:
        return jsonify({'success': False, 'error': f'Unexpected: {answer}'}), 500

def chat():
    if 'username' not in session:   # protect the route
        return redirect('/')
    return render_template('fchat.html', username=session['username'])





def get_online_users_api():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        request_data = {"type": "get_online_users"}
        response_raw = run_async(persistent_ws_client.send_and_wait_response(json.dumps(request_data)))
        response = json.loads(response_raw)
        
        if response.get("type") == "online_users_list":
            return jsonify({
                'users': response.get('users', []),
                'count': response.get('count', 0)
            })
        else:
            return jsonify({'users': [], 'count': 0})
    except Exception as e:
        print(f"Error getting online users: {e}")
        return jsonify({'error': 'Failed to get online users'}), 500


def get_conversations():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify([])

def get_messages():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conversation_id = request.args.get('conversation_id')
    # Return messages for the conversation
    return jsonify([])

def send_message():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    message = data.get('message')
    conversation_id = data.get('conversation_id')
    
    # Process and send message via WebSocket
    # Return the sent message data
    return jsonify({'success': True})

def upload_file():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Handle file upload
    return jsonify({'success': True, 'file_url': 'path/to/file'})

def get_user():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({'username': session['username']})

def home():
    return render_template('login.html')


if __name__ == "__main__":
    # start websocket client inside the main loop
    def start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(persistent_ws_client.connect())
        loop.run_forever()

