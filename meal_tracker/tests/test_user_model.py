import unittest
import sqlite3
from meal_tracker.models.user_model import create_user, authenticate_user, change_password
from meal_tracker.utils.sql_utils import initialize_database, get_db_connection

class TestUserModel(unittest.TestCase):
    def setUp(self):
        """
        Prepare test environment before each test:
        - Initialize the database
        - Clear existing user data to ensure clean test state
        """
        initialize_database()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users")
            conn.commit()

    def test_create(self):
        """
        Verify user creation functionality:
        - Create a new user
        - Check that user is successfully stored in database
        - Confirm username matches the created user
        """
        create_user("alice", "securepassword")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username = ?", ("alice",))
            user = cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[0], "alice")

    def test_create_dupe(self):
        """
        Test prevention of duplicate username registration:
        - Create a user with an existing username
        - Verify that a ValueError is raised
        - Check the specific error message
        """
        create_user("bob", "mypassword")
        with self.assertRaises(ValueError) as context:
            create_user("bob", "anotherpassword")
        self.assertEqual(str(context.exception), "Username 'bob' is already taken.")

    def test_authenticate(self):
        """
        Verify successful user authentication:
        - Create a user
        - Attempt to authenticate with correct password
        - Confirm authentication succeeds
        """
        create_user("charlie", "charliepass")
        self.assertTrue(authenticate_user("charlie", "charliepass"))

    def test_authenticate_invalid(self):
        """
        Test authentication with incorrect password:
        - Create a user
        - Attempt to authenticate with wrong password
        - Confirm authentication fails
        """
        create_user("dave", "davepassword")
        self.assertFalse(authenticate_user("dave", "wrongpassword"))

    def test_authenticate_nonexistent(self):
        """
        Verify authentication handling for non-existent users:
        - Attempt to authenticate with a username that doesn't exist
        - Confirm authentication fails
        """
        self.assertFalse(authenticate_user("eve", "nonexistentpass"))

    def test_change_password(self):
        """
        Test password change functionality:
        - Create a user with initial password
        - Change the password
        - Verify:
          1. New password works for authentication
          2. Old password no longer authenticates
        """
        create_user("frank", "initialpassword")
        change_password("frank", "updatedpassword")
        self.assertTrue(authenticate_user("frank", "updatedpassword"))
        self.assertFalse(authenticate_user("frank", "initialpassword"))

if __name__ == "__main__":
    unittest.main()
