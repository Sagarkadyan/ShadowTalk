import rsa
import socket
import threading
import time 

HEADER = 64
PORT =9999
FORMAT ="utf-8"
DISCONNECTED_MSG ="disconnect"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR =(SERVER,PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

''' Only run this part once to generate new key files
public_key, private_key = rsa.newkeys(1024)
with open("public.pem", "wb") as f:
    f.write(public_key.save_pkcs1("PEM"))
with open("private.pem", "wb") as f:
    f.write(private_key.save_pkcs1("PEM"))
'''
#Now read the keys back (make sure files exist and are correct)
with open("public.pem", "rb") as f:
    public_key_own = rsa.PublicKey.load_pkcs1(f.read())

with open("private.pem", "rb") as f:
    private_key_own = rsa.PrivateKey.load_pkcs1(f.read())

def recv_exact(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            raise ConnectionError("Connection closed during recv_exact")
        data += packet
    return data

def receive():
    while True:
        try:
            msg_type = recv_exact(client, 3).decode(FORMAT)

            msg_length = int(recv_exact(client, HEADER).decode(FORMAT).strip())
            msg = recv_exact(client, msg_length)

            if msg_type == "MSG":
                decrypted = rsa.decrypt(msg, private_key_own).decode(FORMAT)
                sender, recipient, content = decrypted.split(":", 2)
                print(f"\n[From {sender} ]: {content}")

            elif msg_type == "SYS":
                print(f"[System]: {msg.decode(FORMAT)}")

            elif msg_type == "KEY":
                print("[!] Unexpected key message received in background — skipping.")
                continue

            else:
                print(f"[?] Unknown message type '{msg_type}'")

        except Exception as e:
            print("Connection closed or error:", e)
            break


username = input("Enter your username: ")
username_encoded = username.encode(FORMAT)
username_length = str(len(username_encoded)).encode(FORMAT)
#username_length += b' ' * (HEADER - len(username_length))
client.send(username_length.ljust(HEADER))
time.sleep(0.05)  # import time
client.send(username_encoded)
time.sleep(0.05)
key_encoded = public_key_own.save_pkcs1(format='PEM')
key_length =str(len(key_encoded)).encode(FORMAT)       
key_length += b' '  * (HEADER - len(key_length))
client.send(key_length)
time.sleep(0.05)
client.send(key_encoded)

threading.Thread(target=receive, daemon=True).start()



while True:
    username1=input("write the recipient name")
    username1= username1.encode(FORMAT)
    msg = input("enter the message\n")

    if msg == DISCONNECTED_MSG:
        send_msg = DISCONNECTED_MSG.encode(FORMAT)
        send_length = str(len(send_msg)).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        time.time.sleep(0.05)
        client.send(send_msg)
        break
  
  
    if not username1 or not msg:
     print("[!] Recipient name or message is empty.")
     continue  # Skip and prompt again


    # Step 1: Send plaintext recipient:message string
    full_message = f"{username1.decode(FORMAT)}:{msg}"
    full_encoded = full_message.encode(FORMAT)
    client.send(str(len(full_encoded)).encode(FORMAT).ljust(HEADER))
    client.send(full_encoded)
     # First, read message type from server
    msg_type = recv_exact(client, 3).decode(FORMAT)

    if msg_type != "KEY":
        print("[!] Expected public key, but got:", msg_type)
        continue

# Now it's safe to read key length
    otherkey_length = int(recv_exact(client, HEADER).decode(FORMAT).strip())
    print("[+] Other public key length:", otherkey_length)

# Read the key itself
    other_public_key_pem = recv_exact(client, otherkey_length)
    print("[+] Received PEM:\n", other_public_key_pem.decode(FORMAT))

   # Receive the length of the other user's public key
    

    
   

    # Convert PEM bytes to PublicKey object
    other_public_key = rsa.PublicKey.load_pkcs1(other_public_key_pem, format='PEM')
    formatted = f"{username}:{username1}:{msg}"
    # Encrypt the message using the other user's public key
    message = rsa.encrypt(formatted.encode(FORMAT), other_public_key)

    
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))

    client.send(send_length)
    time.sleep(0.05)
    client.send(message)
client.close()


