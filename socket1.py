import  socket
import threading

HEADER = 64
PORT =9999
FORMAT ="utf-8"
DISCONNECTED_MSG ="disconnect"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR =(SERVER,PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def receive():
    while True:
        try:
            msg_length_raw = client.recv(HEADER)
            if not msg_length_raw:
                break
            msg_length = int(msg_length_raw.decode(FORMAT).strip())
            if msg_length == 0:
                continue
            msg = client.recv(msg_length).decode(FORMAT)
            print("\n[Received]:", msg)
        except Exception as e:
          print("Connection closed or error:", e)
          break


username = input("Enter your username: ")
username_encoded = username.encode(FORMAT)
username_length = str(len(username_encoded)).encode(FORMAT)
username_length += b' ' * (HEADER - len(username_length))
client.send(username_length)
client.send(username_encoded)

threading.Thread(target=receive, daemon=True).start()

while True:
    msg = input("Format: recipient:message\n")
    if msg == DISCONNECTED_MSG:
        send_msg = DISCONNECTED_MSG.encode(FORMAT)
        send_length = str(len(send_msg)).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(send_msg)
        break
    
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
client.close()    