import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain,hashed):
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))