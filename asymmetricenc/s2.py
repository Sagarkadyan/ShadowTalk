import asyncio
import websockets
import json
import sqlite3

# Connect (creates the database file if it doesn't exist)
conns = sqlite3.connect('users.db' ,check_same_thread=False)
cursor = conns.cursor()

async def handler(websocket):
    print(f"A client connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Server received raw message: {message}")

            try:
                data = json.loads(message)
                print(f"Server successfully parsed JSON: {data}")

                if data.get("type") == "login":
                    username = data.get("username", "guest")
                    response_message = {"status": "success", "message": f"Welcome, {username}!"}

                elif data.get("type") == "registration":
                    print("Registration request received.")
                    try:
                        username = data.get('username')
                        email = data.get('email')
                        password = data.get('password')
                        pub_key = data.get('pub_key')
                        adder(username, email, password, pub_key)
                        print(f"[+] {username} registered successfully.")
                        response_message = {"status": "success", "message": "User registered."}
                    except Exception as e:
                        print(f"[{addr}] Error during registration processing: {e}")
                        response_message = {"status":"failed","message": "user not registered"}
                    

                else:
                    response_message = {"status": "ignored", "message": "Message type not recognized."}

                await websocket.send(json.dumps(response_message))
                print(f"Server sent response: {json.dumps(response_message)}")

            except json.JSONDecodeError:
                error_response = {"status": "error", "message": "Invalid JSON format."}
                await websocket.send(json.dumps(error_response))

    except websockets.exceptions.ConnectionClosedError:
        print("Client connection closed unexpectedly.")
    finally:
        print("Client disconnected.")

def adder(name, email, password, cypher_text):
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, cypher_text) VALUES (?, ?, ?, ?)",
            (name, email, password, cypher_text)
        )
        conns.commit()
        print("Inserted successfully!")
        return "Inserted successfully!"
    except sqlite3.IntegrityError:
        return "Email already exists."
        print("Email already exists.")
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
    async with websockets.serve(handler, "localhost", 9999):
        await asyncio.Future()  # Run forever
conns.close()
if __name__ == "__main__":
    asyncio.run(main())
