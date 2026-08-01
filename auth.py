import bcrypt
from database import create_user, get_user_by_email


def signup(email: str, password: str) -> dict:
    """
    Register a new user.
    - Checks if email already exists in Supabase.
    - Hashes the password with bcrypt.
    - Inserts the new user into the users table.
    """
    existing = get_user_by_email(email)
    if existing:
        return {"error": "An account with this email already exists."}

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        create_user(email, password_hash)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


def login(email: str, password: str) -> dict:
    """
    Verify a user's credentials.
    - Fetches the stored hash from Supabase.
    - Uses bcrypt.checkpw() to compare — never decrypts.
    """
    user = get_user_by_email(email)

    if not user:
        return {"error": "No account found with that email."}

    stored_hash = user["password_hash"].encode()

    if bcrypt.checkpw(password.encode(), stored_hash):
        return {"success": True, "email": email}
    else:
        return {"error": "Incorrect password."}