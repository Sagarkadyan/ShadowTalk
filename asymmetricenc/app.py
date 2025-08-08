from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

messages = []    # List of dicts: {'sender': username, 'content': ..., 'timestamp': ...}
users = set()    # Registered usernames

@app.route('/', methods=['GET'])
def home():
    if 'username' in session:
        return render_template('chat.html', username=session['username'])
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username1')
    password = data.get('password1')
    # For demo: any username/password is valid if username not blank
    if username:
        session['username'] = username
        users.add(username)
        return jsonify({'success': True, 'username': username})
    return jsonify({'success': False, 'error': 'Invalid username'}), 400

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    # For demo: accept anything not blank & not duplicate
    if not username or username in users:
        return jsonify({'success': False, 'error': 'Username taken'}), 400
    users.add(username)
    return jsonify({'success': True, 'username': username})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/send', methods=['POST'])
def send_message():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    content = data.get('message')
    timestamp = data.get('timestamp')
    username = session['username']
    messages.append({'sender': username, 'content': content, 'timestamp': timestamp})
    return jsonify({'status': 'success', 'message': content, 'username': username, 'timestamp': timestamp})

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({'messages': messages})

@app.route('/file-metadata', methods=['POST'])
def file_metadata():
    data = request.json
    # Just echo the received metadata for demo
    return jsonify({'received': data})

if __name__ == "__main__":
    app.run(debug=True)