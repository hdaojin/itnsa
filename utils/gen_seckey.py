<<<<<<< HEAD
import secrets

def generate_secret_key(length=24):
    return secrets.token_hex(length)

secrets_key = generate_secret_key()
=======
import secrets

def generate_secret_key(length=24):
    return secrets.token_hex(length)

secrets_key = generate_secret_key()
>>>>>>> 279dc5b0ffc97c1ad8d4ecb4f9f5b8196032a309
print(f"Generated SECRET_KEY = '{secrets_key}'")