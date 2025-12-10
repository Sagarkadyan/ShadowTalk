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
                                                                              


    """
    
    for line in banner.splitlines():
        print(Fore.CYAN + Style.BRIGHT + line + Style.RESET_ALL)
        time.sleep(0.05)
#print_banner()
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

current_user= None
class PersistentWebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.response_queue = asyncio.Queue()

    async def connect(self):
        self.websocket = await websockets.connect(self.uri, ping_interval=10)
        print("Connected to WebSocket server.")
        asyncio.create_task(self.listen())

    async def listen(self):
        try:
            async for message in self.websocket:
                print(f"Received from server: {message}")
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
        "username": username,
        "email": email,
        "password": password,
        "pub_key": my_pub.save_pkcs1("PEM").decode('utf-8')
    }
    print(firebase)
    response_raw = run_async(persistent_ws_client.send_and_wait_response(json.dumps(firebase)))

    response= json.loads(response_raw)
    answer= response.get("answer")
    if answer == "yes":
        print("Registration done")
        print("you can login now ")
        login()
    elif answer == "no":
        print("email already taken  ")
        register()    
    else:
        print("registration failed retry ")
        register()    

def login():
    print("Incoming login ")
    username = input("enter your username")
    password = input ("enter your password")
    
    fireball = {
        "type": "login",
        "username": username,
        "password": password
    }

    response_raw = run_async(persistent_ws_client.send_and_wait_response(json.dumps(fireball)))
    print(f"WebSocket response_raw: {response_raw}")
    response = json.loads(response_raw)
    answer = response.get("answer")
   

    if answer == "correct pass":
        global current_user
        current_user = username
        print(get_online_users_api())
        user_select()
        
    elif answer == "wrong pass":
        print("wrong password")
        login()
    elif answer == "user not found":
        print("user not found")
        login()
    else:
        return {'success': False, 'error': f'Unexpected: {answer}'}



def user_select():
    user=input("enter the name of user you want to chat")        

def get_online_users_api():
    if current_user is None:
        return {'error': 'Not authenticated'}
    
    try:
        request_data = {"type": "get_online_users"}
        response_raw = run_async(persistent_ws_client.send_and_wait_response(json.dumps(request_data)))
        response = json.loads(response_raw)
        
        if response.get("type") == "online_users_list":
            return {
                'users': response.get('users', []),
                'count': response.get('count', 0)
            }
        else:
            return {'users': [], 'count': 0}
    except Exception as e:
        print(f"Error getting online users: {e}")
        return {'error': 'Failed to get online users'}


def get_conversations():
    if current_user is None:
        return {'error': 'Not authenticated'}
    
    return []

def get_messages():
    if current_user is None:
        return {'error': 'Not authenticated'}
    
    # conversation_id = request.args.get('conversation_id') # 'request' is not defined in this CLI context
    # Return messages for the conversation
    return []

def send_message():
    if current_user is None:
        return {'error': 'Not authenticated'}
    
    # data = request.get_json() # 'request' is not defined in this CLI context
    # message = data.get('message')
    # conversation_id = data.get('conversation_id')
    
    # Process and send message via WebSocket
    # Return the sent message data
    return {'success': True}



def upload_file():
    if current_user is None:
        return {'error': 'Not authenticated'}
    
    # Handle file upload
    return {'success': True, 'file_url': 'path/to/file'}

def get_user():
    if current_user is None:
        return {'error': 'Not authenticated'}
    
    return {'username': current_user}

def home():
    # return render_template('login.html') # 'render_template' is not defined in this CLI context
    pass

def initial():
            run_async(persistent_ws_client.connect())
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
                login()
            else:
                print("Wrong input re enter choice")
                initial()        
initial()                
with open("public.pem", "wb") as f:
    f.write(my_pub.save_pkcs1("PEM"))

with open("private.pem", "wb") as f:
    f.write(my_priv.save_pkcs1("PEM"))





initial()                
with open("public.pem", "wb") as f:
    f.write(my_pub.save_pkcs1("PEM"))

with open("private.pem", "wb") as f:
    f.write(my_priv.save_pkcs1("PEM"))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(persistent_ws_client.connect())
    initial()
