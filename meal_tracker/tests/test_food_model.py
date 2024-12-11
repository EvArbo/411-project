import unittest
from app import app
from meal_tracker.models.food_model import stored_ingredients

class TestFoodModel(unittest.TestCase):
    def setUp(self):
        """
        Set up test environment before each test method:
        - Create a test client for making API requests
        - Enable testing mode
        - Clear any existing stored ingredients to ensure a clean slate
        """
        self.app = app.test_client()
        self.app.testing = True
        stored_ingredients.clear()

    def test_add_ingredient(self):
        """
        Verify successful ingredient addition:
        - Ensure the API returns a 201 status code
        - Check for successful addition message
        - Confirm ingredient details are returned
        """
        response = self.app.post('/food/add/129981')
        self.assertEqual(response.status_code, 201)
        self.assertIn("Ingredient added.", response.json["message"])
        self.assertIn("ingredient", response.json)

    def test_add_duplicate_ingredient(self):
        """
        Test prevention of duplicate ingredient storage:
        - Add an ingredient first
        - Attempt to add the same ingredient again
        - Verify that a 400 error is returned
        - Confirm error message about duplicate ingredient
        """
        self.app.post('/food/add/129981')
        response = self.app.post('/food/add/129981')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Ingredient already stored.", response.json["message"])

    def test_get_ingredient(self):
        """
        Check retrieval of a stored ingredient:
        - Add an ingredient to storage
        - Retrieve the ingredient by its ID
        - Verify successful retrieval with correct details
        """
        self.app.post('/food/add/129981')
        response = self.app.get('/food/129981')
        self.assertEqual(response.status_code, 200)
        self.assertIn("ingredient", response.json)
        self.assertEqual(response.json["ingredient"]["name"], " Beef Madras")

    def test_get_nonexistent_ingredient(self):
        """
        Verify handling of requests for non-stored ingredients:
        - Attempt to retrieve an ingredient that doesn't exist
        - Confirm 404 status code
        - Check for appropriate error message
        """
        response = self.app.get('/food/123456')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Ingredient not found in memory.", response.json["message"])

    def test_update_ingredient(self):
        """
        Test updating an existing ingredient:
        - Add an ingredient to storage
        - Update the ingredient's details
        - Verify successful update with new information
        """
        self.app.post('/food/add/129981')
        response = self.app.put(
            '/food/update/129981',
            json={"name": "Updated Beef Madras", "energy": 150}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ingredient updated.", response.json["message"])
        self.assertEqual(response.json["ingredient"]["name"], "Updated Beef Madras")

    def test_update_nonexistent_ingredient(self):
        """
        Verify handling of updates for non-stored ingredients:
        - Attempt to update an ingredient that doesn't exist
        - Confirm 404 status code
        - Check for appropriate error message
        """
        response = self.app.put(
            '/food/update/123456',
            json={"name": "Updated Ingredient"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Ingredient not found in memory.", response.json["message"])

    def test_delete_ingredient(self):
        """
        Test deleting a stored ingredient:
        - Add an ingredient to storage
        - Delete the ingredient
        - Verify successful deletion
        """
        self.app.post('/food/add/129981')
        response = self.app.delete('/food/delete/129981')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ingredient deleted.", response.json["message"])

    def test_delete_nonexistent_ingredient(self):
        """
        Verify handling of deletion requests for non-stored ingredients:
        - Attempt to delete an ingredient that doesn't exist
        - Confirm 404 status code
        - Check for appropriate error message
        """
        response = self.app.delete('/food/delete/123456')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Ingredient not found in memory.", response.json["message"])

    def test_list_stored_ingredients(self):
        """
        Test listing all stored ingredients:
        - Add multiple ingredients to storage
        - Retrieve the list of ingredients
        - Verify correct number of ingredients is returned
        """
        self.app.post('/food/add/129981')
        self.app.post('/food/add/199636')
        response = self.app.get('/food/list')
        self.assertEqual(response.status_code, 200)
        self.assertIn("stored_ingredients", response.json)
        self.assertEqual(len(response.json["stored_ingredients"]), 2)

if __name__ == "__main__":
    unittest.main()
