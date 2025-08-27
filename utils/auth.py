import bcrypt
import os

def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password: str, hashed_password: bytes) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def check_supervisor_password(password: str) -> bool:
    """Check if the provided password matches the supervisor password."""
    # Get supervisor password from environment variable or use default
    supervisor_password = os.environ.get('SUPERVISOR_PASSWORD', 'admin123')
    
    # For simplicity, we'll do a plain text comparison
    # In production, you should store and compare hashed passwords
    return password == supervisor_password
