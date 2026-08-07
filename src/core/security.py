from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Hash a password using the recommended hashing algorithm."""
    return password_hash.hash(password)