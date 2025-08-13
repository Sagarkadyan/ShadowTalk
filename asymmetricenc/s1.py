import asyncio
import websockets
import json

# This is the corrected function definition.
# We have removed ', path' from the arguments.
async def handler(websocket):
    print(f"A client connected from {websocket.remote_address}")
    try:
        # Loop indefinitely to receive messages from the client
        async for message in websocket:
            print(f"Server received raw message: {message}")

            try:
                # 1. Parse the incoming message string as JSON
                data = json.loads(message)
                print(f"Server successfully parsed JSON: {data}")

                # 2. Process the data (example: check the type)
                if data.get("type") == "login":
                    username = data.get("username", "guest")
                    response_message = {"status": "success", "message": f"Welcome, {username}!"}
                else:
                    response_message = {"status": "ignored", "message": "Message type not recognized."}

                # 3. Send a JSON response back to the client
                await websocket.send(json.dumps(response_message))
                print(f"Server sent response: {json.dumps(response_message)}")

            except json.JSONDecodeError:
                # Handle cases where the message is not valid JSON
                print("Error: Received message was not valid JSON.")
                error_response = {"status": "error", "message": "Invalid JSON format."}
                await websocket.send(json.dumps(error_response))

    except websockets.exceptions.ConnectionClosedError:
        print("Client connection closed unexpectedly.")
    finally:
        print("Client disconnected.")

# This function starts the server (no changes needed here)
async def main():
    # Start the WebSocket server on localhost, port 8765
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server started at ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
