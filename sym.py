from cryptography.fernet import Fernet

import  socket
import threading

HEADER = 128
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
            try:
              msg = client.recv(msg_length)
              #print("\n[Received - raw bytes]:", msg)
              try:
    # Split at first space; the second part is the Fernet token
                    fernet_token = msg.split(b" ", 1)[1]
                    decoded_message = encrypted_object.decrypt(fernet_token)
                    print("[Decrypted]:", decoded_message.decode(FORMAT))
              except Exception as e:
                 print("Decryption error:", e)
            except Exception as e:
                print(e)    
        except Exception as e:
            print(e)

           
username = input("Enter your username: ")
username_encoded = username.encode(FORMAT)
username_length = str(len(username_encoded)).encode(FORMAT)
username_length += b' ' * (HEADER - len(username_length))
client.send(username_length)
client.send(username_encoded)

threading.Thread(target=receive, daemon=True).start()

key = b'nNRXpoM32tgtx1hE9YzUPTaf4b_yfNQyNAyI3Kg5Nm0='

encrypted_object = Fernet(key)

print(key)



threading.Thread(target=receive, daemon=True).start()

while True:
    username1=input("write the rexipent name")
    username1= username1.encode(FORMAT)
    msg = input("input the message")
    encrypted_messssage = encrypted_object.encrypt(msg.encode())


    if msg == DISCONNECTED_MSG:
        send_msg = DISCONNECTED_MSG.encode(FORMAT)
        send_length = str(len(send_msg)).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(send_msg)
        break
    
    message =   username1 + b":" +encrypted_messssage
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(message)
client.close()    

