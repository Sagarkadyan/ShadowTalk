import rsa

public_key, private_key = rsa.newkeys(1024)

print(private_key)

with open("public.pem","rb") as f:
    public_key =rsa.PublicKey.load_pkcs1(f.read())


with open("private.pem","rb") as f:
    public_key=rsa.Private_key.load_pkcs1(f.read())

message = "hello"

encrypted_message= rsa.encrypt(message.encode(),public_key)
print(encrypted_message)