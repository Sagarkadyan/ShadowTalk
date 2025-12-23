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
from pynput import keyboard
i=0
uri = "ws://iyjr7jcamj.loclx.io"
main_loop = asyncio.new_event_loop()  # global event loop for websocket
my_pub, my_priv = rsa.newkeys(512)
init(autoreset=True)

console = Console()
selected_user=""

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
        try:
            self.websocket = await websockets.connect(self.uri, ping_interval=10, open_timeout=20)
            print("Connected to WebSocket server.")
            asyncio.create_task(self.listen())
        except (asyncio.TimeoutError, websockets.exceptions.WebSocketException) as e:
            print(f"Failed to connect to WebSocket server at {self.uri}: {e}")
            self.websocket = None
        except Exception as e:
            print(f"An unexpected error occurred during connection: {e}")
            self.websocket = None

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
        global selected_user
        users_raw=get_online_users_api()
        users = users_raw['users']
        print("list of users",users)

        
        
        selected_user_input = input("select the person you want to chat")
        if selected_user_input in users:
            print("user found")
            selected_user = selected_user_input
            chatting()
        else:
            print("User not found. Please try again.")
            user_select()

def chatting():
        while True :
            message=input("")
            message_ball={
                'type':" message",
                'receiver':selected_user,
                'message':message
            }
            response_raw=run_async(persistent_ws_client.send_and_wait_response(json.dumps(message_ball)))
            print(response_raw)

    
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
def on_press(key):
    global i
    try:
        # print('alphanumeric key {0} pressed'.format(key.char))
        b=key.char
        if b=="/":
            # print("command is starting")
            i+=1
            
            if i>1:
                # print("command is perfect")
                user_select()
                i=0
            else:
                # print("value need more ")
                pass
                
        else:
            if i>0:
                i=0
                # print("value reset")           


    except AttributeError:
        # print('special key {0} pressed'.format(key))
        pass

def on_release(key):
    # print('{0} released'.format(key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def initial():
            print_banner()
            print("What will you choose")
            print("1. Register")
            print("2. Login")
            print("Press 1 or 2")
            try:
                initial_input = int(input("ENTER: "))
                if initial_input == 1:
                    print("register")
                    register()
                elif initial_input == 2:
                    print("login")
                    login()
                else:
                    print("Wrong input, re-enter choice")
                    initial()
            except ValueError:
                print("Invalid input. Please enter 1 or 2.")
                initial()

if __name__ == "__main__":
    # Start key listener in a non-blocking way
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

    with open("public.pem", "wb") as f:
        f.write(my_pub.save_pkcs1("PEM"))

    with open("private.pem", "wb") as f:
        f.write(my_priv.save_pkcs1("PEM"))

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(persistent_ws_client.connect())
        if persistent_ws_client.websocket:
            initial()
        else:
            print("Could not connect to the server. Exiting.")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        listener.stop()

