import asyncio
import websockets
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import rsa
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

uri = "ws://localhost:9999"  # Local test, change to your playit.gg URI when needed

class PersistentWebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        print("Connected to WebSocket server.")
        asyncio.create_task(self.listen())  # Run listener in background

    async def listen(self):
        try:
            async for message in self.websocket:
                print(f"Received from server: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed.")

    async def send(self, message):
        if self.websocket is None:
            raise ConnectionError("WebSocket is not connected.")
        await self.websocket.send(message)

# Create keys
pubkey, privkey = rsa.newkeys(512)
with open("public.pem", "wb") as f:
    f.write(pubkey.save_pkcs1("PEM"))
with open("private.pem", "wb") as f:
    f.write(privkey.save_pkcs1("PEM"))

with open("public.pem", "rb") as f:
    my_pub = rsa.PublicKey.load_pkcs1(f.read())
with open("private.pem", "rb") as f:
    my_priv = rsa.PrivateKey.load_pkcs1(f.read())

# Global WebSocket client
persistent_ws_client = PersistentWebSocketClient(uri)

@app.route('/register', methods=['POST'])
async def register():
    data = request.get_json()
    firebase = {
        "type": "registration",
        "username": data.get('username'),
        "email": data.get('email'),
        "password": data.get('password'),
        "pub_key": my_pub.save_pkcs1("PEM").decode('utf-8')
    }
    await persistent_ws_client.send(json.dumps(firebase))
    return jsonify({'success': True, 'message': 'Registration request sent.'})

@app.route('/login', methods=['POST'])
async def login():
    data = request.json
    fireball = {
        "type": "login",
        "username": data.get('username1'),
        "password": data.get('password1')
    }
    await persistent_ws_client.send(json.dumps(fireball))
    return jsonify({'success': True, 'message': 'Login request sent.'})

@app.route('/', methods=['GET'])
def home():
    if 'username' in session:
        return render_template('chat.html')
    return render_template('login.html')

if __name__ == "__main__":
    if os.environ.get("FLASK_RUN_FROM_CLI") != "true":  # Prevent duplicate connect in reloader
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(persistent_ws_client.connect())
    app.run(debug=True,use_reloader=False)