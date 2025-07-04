from cryptography.hazmat.backends import default_backends
from cryptography.hazmat.primitives.asymmetric import rsa

private_key=  rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
    backend=default_backends()
)

public_key= private_key.public_key()

private_key_pem = private_key.private_bytes(
    encoding = serializations.Encoding.PEM,
    
)
