import requests

stored_ingredients = {}

WGER_INGREDIENT_API = "https://wger.de/api/v2/ingredient/"


def fetch_ingredient_by_id(ingredient_id):
    """Fetch ingredient details from the API using ID."""
    url = f"{WGER_INGREDIENT_API}{ingredient_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        ingredient = response.json()
        cleaned_ingredient = {
            "id": ingredient.get("id"),
            "name": ingredient.get("name"),
            "energy": ingredient.get("energy"),
            "protein": ingredient.get("protein"),
            "carbohydrates": ingredient.get("carbohydrates"),
            "fat": ingredient.get("fat"),
            "fiber": ingredient.get("fiber"),
        }
        return cleaned_ingredient
    else:
        return None


def store_ingredient(ingredient_id):
    """Store ingredient details in memory."""
    if ingredient_id in stored_ingredients:
        return {"status": "error", "message": "Ingredient already stored."}

    ingredient = fetch_ingredient_by_id(ingredient_id)
    if ingredient:
        stored_ingredients[ingredient_id] = ingredient
        return {"status": "success", "message": "Ingredient added.", "ingredient": ingredient}
    else:
        return {"status": "error", "message": "Ingredient not found in API."}


def update_ingredient(ingredient_id, updates):
    """Update an ingredient's details in memory."""
    if ingredient_id not in stored_ingredients:
        return {"status": "error", "message": "Ingredient not found in memory."}

    for key, value in updates.items():
        if key in stored_ingredients[ingredient_id]:
            stored_ingredients[ingredient_id][key] = value

    return {"status": "success", "message": "Ingredient updated.", "ingredient": stored_ingredients[ingredient_id]}


def delete_ingredient(ingredient_id):
    """Delete an ingredient from memory."""
    if ingredient_id in stored_ingredients:
        deleted = stored_ingredients.pop(ingredient_id)
        return {"status": "success", "message": "Ingredient deleted.", "ingredient": deleted}
    else:
        return {"status": "error", "message": "Ingredient not found in memory."}


def list_stored_ingredients():
    """List all stored ingredients."""
    return {"stored_ingredients": list(stored_ingredients.values())}


def get_ingredient(ingredient_id):
    """Retrieve a single ingredient's details from memory."""
    if ingredient_id in stored_ingredients:
        return {"status": "success", "ingredient": stored_ingredients[ingredient_id]}
    else:
        return {"status": "error", "message": "Ingredient not found in memory."}