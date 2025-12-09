import asyncio
import websockets
import json
import sqlite3

# Connect (creates the database file if it doesn't exist)
conns = sqlite3.connect('users.db' ,check_same_thread=False)
cursor = conns.cursor()

# Create users table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    cypher_text TEXT NOT NULL
);
""")
conns.commit()
connected_users = {}  # {websocket: username}
online_users = set()
print("start")
async def handler(websocket):
    print(f"A client connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Server received raw message: {message}")
            response_message = None
            try:
                data = json.loads(message)
                print(f"Server successfully parsed JSON: {data}")

                if data.get("type") == "login":
                    try:
                        username = data.get("username")
                        password = data.get("password")
                        passwd_result = check_password(cursor, username, password)
                        if passwd_result == "correct pass":
                            connected_users[websocket] = username
                            online_users.add(username)
                            print(f"User {username} is now online. Total online: {len(online_users)}")
                        
                        response_message = {
                            "type": "login_ans",
                            "answer": passwd_result,
                            "username": username
                        }
                    except Exception as e:
                        response_message = {"type": "login_ans", "answer": "error", "error": str(e)}

                elif data.get("type") == "registration":
                    print("Registration request received.")
                    try:
                        username = data.get('username')
                        email = data.get('email')
                        password = data.get('password')
                        pub_key = data.get('pub_key')
                        regr_ans=adder(username, email, password, pub_key)
                        print(f"[+] {username} registered successfully.")
                        response_message = {
                            "type": "reg_ans",
                            "answer": regr_ans,
                            "username": username
                        }
                    except Exception as e:
                        print(f" Error during registration processing: {e}")
                        response_message = {"status": "failed", "message": "user not registered"}
                elif data.get("type") == "get_online_users":
                    
                    response_message = {
                        "type": "online_users_list",
                        "users": list(online_users),
                        "count": len(online_users)
                    }
                else:
                    response_message = {"status": "ignored", "message": "Message type not recognized."}

            except json.JSONDecodeError:
                response_message = {"status": "error", "message": "Invalid JSON format."}

            if response_message is not None:
                await websocket.send(json.dumps(response_message))
                print(f"Server sent response: {json.dumps(response_message)}")

    except websockets.exceptions.ConnectionClosedError:
        print("Client connection closed unexpectedly.")

    finally:
    
    
        if websocket in connected_users:
            username = connected_users[websocket]
            online_users.discard(username)
            del connected_users[websocket]
            print(f"User {username} went offline. Total online: {len(online_users)}")
        print("Client disconnected.")


def adder(name, email, password, cypher_text):
    try:
        # Check if email already exists
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            print(f"Registration failed: email {email} already exists.")
            return "no"

        
        cursor.execute(
            "INSERT INTO users (name, email, password, cypher_text) VALUES (?, ?, ?, ?)",
            (name, email, password, cypher_text)
        )
        conns.commit()
        print("Inserted successfully")
        return "yes"

    except Exception as e:
        print(f"Registration failed with error: {e}")
        return "fail"

def check_password(cursor, name, user_password):
    try:
        cursor.execute(
            "SELECT password FROM users WHERE name = ?", (name,)
        )
        row = cursor.fetchone()

        if row:
            stored_password = row[0]  
            if stored_password == user_password:
                print("cpass")
                return "correct pass"
            else:
                print("wpass")
                return "wrong pass"
        else:
            # No user found
            return "user not found"

    except Exception as e:
        print("ipass", e)
        return f"invalid pass: {e}"


def update_pss(name, new_passwd):
    try:
        cursor.execute(
            "UPDATE users SET password = ? WHERE name = ?",
            (new_passwd, name)
        )
        conns.commit()

        if cursor.rowcount == 0:
            return "user does not exist"
        else:
            return "password updated successfully"
    except Exception as e:
        return f"error: {e}"


async def main():
    async with websockets.serve(handler, "127.0.0.1", 9999):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:    
        conns.close()