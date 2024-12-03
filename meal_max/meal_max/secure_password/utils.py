import hashlib

def hash_password(password):
    """" Hash password in SHA256 """
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password
