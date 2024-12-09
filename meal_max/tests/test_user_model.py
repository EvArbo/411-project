import unittest
from meal_max.models.user_model import create_user, authenticate_user, change_password
from meal_max.utils.sql_utils import initialize_database, get_db_connection


class TestUserModel(unittest.TestCase):

    def init(self):
        """Initialize the database and clear any existing data."""
        initialize_database()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users")
            conn.commit()

    def test_create(self):
        """Test creating a new user successfully."""
        create_user("alice", "securepassword")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username = ?", ("alice",))
            user = cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[0], "alice")

    def test_create_dupe(self):
        """Test creating a user with a duplicate username."""
        create_user("bob", "mypassword")
        with self.assertRaises(ValueError) as context:
            create_user("bob", "anotherpassword")
        self.assertEqual(str(context.exception), "Username 'bob' is already taken.")

    def test_authenticate(self):
        """Test authenticating a user with the correct password."""
        create_user("charlie", "charliepass")
        self.assertTrue(authenticate_user("charlie", "charliepass"))

    def test_authenticate_invalid(self):
        """Test authenticating a user with an incorrect password."""
        create_user("dave", "davepassword")
        self.assertFalse(authenticate_user("dave", "wrongpassword"))

    def test_authenticate_nonexistent(self):
        """Test authenticating a nonexistent user."""
        self.assertFalse(authenticate_user("eve", "nonexistentpass"))

    def test_change_password(self):
        """Test changing a user's password successfully."""
        create_user("frank", "initialpassword")
        change_password("frank", "updatedpassword")
        self.assertTrue(authenticate_user("frank", "updatedpassword"))
        self.assertFalse(authenticate_user("frank", "initialpassword"))


if __name__ == "__main__":
    unittest.main()
