
import rsa

# Only run this part once to generate new key files
'''public_key, private_key = rsa.newkeys(1024)
with open("public.pem", "wb") as f:
    f.write(public_key.save_pkcs1("PEM"))
with open("private.pem", "wb") as f:
    f.write(private_key.save_pkcs1("PEM"))
'''
# Now read the keys back (make sure files exist and are correct)
with open("public.pem", "rb") as f:
    public_key = rsa.PublicKey.load_pkcs1(f.read())

with open("private.pem", "rb") as f:
    private_key = rsa.PrivateKey.load_pkcs1(f.read())


message = "hello"