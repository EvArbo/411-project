import sqlite3
from meal_tracker.utils.sql_utils import get_db_connection
import hashlib
import os
from meal_tracker.utils.sql_utils import initialize_database

initialize_database()

def hash_password(password: str, salt: str) -> str:
    """
    Generate a secure hash of the password using SHA-256 with a salt.

    This function creates a cryptographically secure hash by combining 
    the salt and password before hashing, which helps protect against 
    rainbow table attacks.

    Args:
        password (str): The plain text password to be hashed.
        salt (str): A unique, random string used to enhance password security.

    Returns:
        str: A hexadecimal representation of the SHA-256 hash.

    
    """
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

def create_user(username: str, password: str) -> None:
    """
    Create a new user in the database with a securely hashed password.

    This function generates a unique salt for each user, hashes the 
    password, and stores the username, salt, and hashed password in 
    the database. It prevents duplicate usernames.

    Args:
        username (str): The desired username for the new account.
        password (str): The plain text password for the new account.

    Raises:
        ValueError: If the username is already taken.

    
    """
    salt = os.urandom(16).hex()  # Generate a random salt
    hashed_password = hash_password(password, salt)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, salt, hashed_password)
                VALUES (?, ?, ?)
            """, (username, salt, hashed_password))
            conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"Username '{username}' is already taken.")

def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate a user by verifying their password.

    This function retrieves the stored salt and hashed password for 
    a given username and compares it with the provided password.

    Args:
        username (str): The username of the account to authenticate.
        password (str): The plain text password to verify.

    Returns:
        bool: True if authentication is successful, False otherwise.

   
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT salt, hashed_password FROM users WHERE username = ?
        """, (username,))
        result = cursor.fetchone()
        if not result:
            return False  
        salt, hashed_password = result
        return hash_password(password, salt) == hashed_password

def change_password(username: str, new_password: str) -> None:
    """
    Update a user's password in the database.

    This function generates a new salt and updates the user's 
    password hash in the database. The salt is changed to ensure 
    additional security.

    Args:
        username (str): The username of the account to update.
        new_password (str): The new plain text password.

    
    """
    salt = os.urandom(16).hex()  # Generate a new salt
    hashed_password = hash_password(new_password, salt)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET salt = ?, hashed_password = ? WHERE username = ?
        """, (salt, hashed_password, username))
        conn.commit()
