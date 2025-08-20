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
            response_message = None
            try:
                data = json.loads(message)
                print(f"Server successfully parsed JSON: {data}")

                if data.get("type") == "login":
                    try:
                        username = data.get("username")
                        password = data.get("password")
                        passwd_result = check_password(cursor, username, password)
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
                        adder(username, email, password, pub_key)
                        print(f"[+] {username} registered successfully.")
                        response_message = {"status": "success", "message": "user added"}
                    except Exception as e:
                        print(f" Error during registration processing: {e}")
                        response_message = {"status": "failed", "message": "user not registered"}
                elif data.get("type") == "ping":
                    response_message = {"type": "pong"}

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

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:    
        conns.close()