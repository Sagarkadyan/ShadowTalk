import asyncio
import websockets
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import rsa
import json
import os
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

uri = "ws://localhost:9999"
main_loop = asyncio.new_event_loop()  # global event loop for websocket

class PersistentWebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.response_queue = asyncio.Queue()

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
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

persistent_ws_client = PersistentWebSocketClient(uri)

# Utility to run coroutines on the main loop safely
def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, main_loop).result()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    firebase = {
        "type": "registration",
        "username": data.get('username'),
        "email": data.get('email'),
        "password": data.get('password'),
        "pub_key": my_pub.save_pkcs1("PEM").decode('utf-8')
    }
    run_async(persistent_ws_client.send(json.dumps(firebase)))
    return jsonify({'success': True, 'message': 'Registration request sent.'})

@app.route('/login', methods=['POST'])
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

@app.route('/')
def home():
    return render_template('login.html')

def start_flask():
    app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    # start websocket client inside the main loop
    def start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(persistent_ws_client.connect())
        loop.run_forever()

    threading.Thread(target=start_loop, args=(main_loop,), daemon=True).start()
    start_flask()
