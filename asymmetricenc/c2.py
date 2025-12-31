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

uri = "ws://127.0.0.1:8080"
main_loop = asyncio.new_event_loop()
asyncio.set_event_loop(main_loop)
my_pub, my_priv = rsa.newkeys(512)
init(autoreset=True)

console = Console()
selected_user=""
current_user= None

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

def run_async(coro):
    return main_loop.run_until_complete(coro)

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
                try:
                    data = json.loads(message)
                    if data.get("type") == "private_message":
                        sender = data.get("sender", "Unknown")
                        msg_text = data.get("message", "")
                        console.print(f"\n[bold magenta]{sender}:[/bold magenta] {msg_text}")
                    else:
                        await self.response_queue.put(message)
                except json.JSONDecodeError:
                    console.print(f"[dim]Received non-JSON message from server: {message}[/dim]")
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
    elif answer == "already online":
        print(f"User '{username}' is already logged in. Please try a different username.")
        login()
    else:
        return {'success': False, 'error': f'Unexpected: {answer}'}

def user_select():
    global selected_user, current_user
    print("\nFetching online users...")
    users_raw = get_online_users_api()
    
    available_users = [user for user in users_raw.get('users', []) if user != current_user]
    
    if not available_users:
        print("No other users are currently online. Waiting for someone to connect...")
        while not available_users:
            try:
                time.sleep(5)
                print("Refreshing user list...")
                users_raw = get_online_users_api()
                available_users = [user for user in users_raw.get('users', []) if user != current_user]
            except KeyboardInterrupt:
                print("\nExiting.")
                return
    
    print("Available users to chat with:", available_users)
    
    selected_user_input = input("Select the person you want to chat with: ")
    if selected_user_input in available_users:
        print(f"User '{selected_user_input}' found.")
        selected_user = selected_user_input
        chatting()
    else:
        print("User not found or is not available. Please try again.")
        user_select()

def chatting():
    console.print(f"\n[bold green]You are now chatting with {selected_user}. Press Ctrl+C to return to user selection.[/bold green]")
    while True:
        try:
            message = input("")
            if not message.strip():
                continue
            
            message_ball = {
                'type': "message",
                'receiver': selected_user,
                'message': message
            }
            run_async(persistent_ws_client.send_and_wait_response(json.dumps(message_ball)))

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Leaving chat...[/bold yellow]")
            user_select()
            break
        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")
            break

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
    with open("public.pem", "wb") as f:
        f.write(my_pub.save_pkcs1("PEM"))

    with open("private.pem", "wb") as f:
        f.write(my_priv.save_pkcs1("PEM"))

    loop = main_loop
    try:
        loop.run_until_complete(persistent_ws_client.connect())
        if persistent_ws_client.websocket:
            initial()
        else:
            print("Could not connect to the server. Exiting.")
    except KeyboardInterrupt:
        print("\nExiting...")