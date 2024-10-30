import bcrypt
import streamlit as st

def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password: str, hashed_password: bytes) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def require_auth():
    """Require authentication to access a page."""
    if not st.session_state.get('is_authenticated', False):
        st.warning("Please log in to access the supervisor dashboard")
        st.stop()
