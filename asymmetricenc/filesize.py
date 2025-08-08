import rsa

my_pub=None
my_priv=None
def keygen():
    pubkey, privkey = rsa.newkeys(512)
    with open("public.pem", "wb") as f:
        f.write(pubkey.save_pkcs1("PEM"))

    with open("private.pem", "wb") as f:
        f.write(privkey.save_pkcs1("PEM"))



with open("public.pem", "rb") as f:
        my_pub = rsa.PublicKey.load_pkcs1(f.read())
with open("private.pem", "rb") as f:
        my_priv = rsa.PrivateKey.load_pkcs1(f.read())

   
keygen()

 
print(my_priv,my_pub)     



