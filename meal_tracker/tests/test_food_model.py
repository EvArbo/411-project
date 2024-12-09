import unittest
from app import app
from meal_tracker.models.food_model import stored_ingredients

class TestFoodModel(unittest.TestCase):
    def setUp(self):
        """Set up the Flask test client and reset stored ingredients."""
        self.app = app.test_client()
        self.app.testing = True
        stored_ingredients.clear()

    def test_add_ingredient(self):
        """Test adding a valid ingredient."""
        response = self.app.post('/food/add/129981')
        self.assertEqual(response.status_code, 201)
        self.assertIn("Ingredient added.", response.json["message"])
        self.assertIn("ingredient", response.json)

    def test_add_duplicate_ingredient(self):
        """Test adding the same ingredient twice."""
        self.app.post('/food/add/129981')
        response = self.app.post('/food/add/129981')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Ingredient already stored.", response.json["message"])

    def test_get_ingredient(self):
        """Test retrieving a stored ingredient."""
        self.app.post('/food/add/129981')
        response = self.app.get('/food/129981')
        self.assertEqual(response.status_code, 200)
        self.assertIn("ingredient", response.json)
        self.assertEqual(response.json["ingredient"]["name"], " Beef Madras")

    def test_get_nonexistent_ingredient(self):
        """Test retrieving an ingredient that is not stored."""
        response = self.app.get('/food/123456')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Ingredient not found in memory.", response.json["message"])

    def test_update_ingredient(self):
        """Test updating a stored ingredient."""
        self.app.post('/food/add/129981')
        response = self.app.put(
            '/food/update/129981',
            json={"name": "Updated Beef Madras", "energy": 150}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ingredient updated.", response.json["message"])
        self.assertEqual(response.json["ingredient"]["name"], "Updated Beef Madras")

    def test_update_nonexistent_ingredient(self):
        """Test updating an ingredient that is not stored."""
        response = self.app.put(
            '/food/update/123456',
            json={"name": "Updated Ingredient"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Ingredient not found in memory.", response.json["message"])

    def test_delete_ingredient(self):
        """Test deleting a stored ingredient."""
        self.app.post('/food/add/129981')
        response = self.app.delete('/food/delete/129981')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ingredient deleted.", response.json["message"])

    def test_delete_nonexistent_ingredient(self):
        """Test deleting an ingredient that is not stored."""
        response = self.app.delete('/food/delete/123456')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Ingredient not found in memory.", response.json["message"])

    def test_list_stored_ingredients(self):
        """Test listing all stored ingredients."""
        self.app.post('/food/add/129981')
        self.app.post('/food/add/199636')
        response = self.app.get('/food/list')
        self.assertEqual(response.status_code, 200)
        self.assertIn("stored_ingredients", response.json)
        self.assertEqual(len(response.json["stored_ingredients"]), 2)


if __name__ == "__main__":
    unittest.main()