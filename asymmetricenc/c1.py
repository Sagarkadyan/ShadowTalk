import asyncio
import websockets
import json

async def send_json_data():
    # The address of the WebSocket server
    uri = "ws://localhost:8765"
    
    try:
        # Connect to the server
        async with websockets.connect(uri) as websocket:
            print(f"Client connected to {uri}")

            # 1. Create a Python dictionary with the data you want to send
            my_data = {
                "type": "login",
                "username": "Sagar",
                "token": "xyz123abc"
            }

            # 2. Convert the dictionary to a JSON string
            json_message = json.dumps(my_data)

            # 3. Send the JSON string to the server
            await websocket.send(json_message)
            print(f"Client sent: {json_message}")

            # 4. Wait for a response from the server
            response = await websocket.recv()
            print(f"Client received response: {response}")
            
            # You can parse the server's response as well
            response_data = json.loads(response)
            print(f"Client parsed response: {response_data}")

    except ConnectionRefusedError:
        print("Connection failed. Is the server running?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(send_json_data())
