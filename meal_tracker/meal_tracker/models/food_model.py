import requests

stored_ingredients = {}
WGER_INGREDIENT_API = "https://wger.de/api/v2/ingredient/"

def fetch_ingredient_by_id(ingredient_id):
    """
    Fetch ingredient details from the Wger API using a specific ingredient ID.

    This function makes an HTTP GET request to the Wger ingredient API to retrieve 
    detailed nutritional information for a given ingredient.

    Args:
        ingredient_id (int): The unique identifier of the ingredient in the Wger API.

    Returns:
        dict or None: A dictionary containing cleaned ingredient details if the 
        API request is successful, including:
        - id: Ingredient's unique identifier
        - name: Name of the ingredient
        - energy: Energy content (typically in kcal)
        - protein: Protein content
        - carbohydrates: Carbohydrate content
        - fat: Fat content
        - fiber: Fiber content
        Returns None if the API request fails.
    
    Example:
        >>> fetch_ingredient_by_id(1234)
        {
            'id': 1234, 
            'name': 'Apple', 
            'energy': 52, 
            'protein': 0.3, 
            'carbohydrates': 14.0, 
            'fat': 0.2, 
            'fiber': 2.4
        }
    """
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
    """
    Store an ingredient's details in the local memory dictionary.

    This function attempts to fetch an ingredient by its ID and store it in 
    the stored_ingredients dictionary if not already present.

    Args:
        ingredient_id (int): The unique identifier of the ingredient to store.

    Returns:
        dict: A status response with the following possible formats:
        - Success: {'status': 'success', 'message': 'Ingredient added.', 'ingredient': {...}}
        - Error (already stored): {'status': 'error', 'message': 'Ingredient already stored.'}
        - Error (not found): {'status': 'error', 'message': 'Ingredient not found in API.'}
    
    Example:
        >>> store_ingredient(1234)
        {'status': 'success', 'message': 'Ingredient added.', 'ingredient': {...}}
    """
    if ingredient_id in stored_ingredients:
        return {"status": "error", "message": "Ingredient already stored."}
    ingredient = fetch_ingredient_by_id(ingredient_id)
    if ingredient:
        stored_ingredients[ingredient_id] = ingredient
        return {"status": "success", "message": "Ingredient added.", "ingredient": ingredient}
    else:
        return {"status": "error", "message": "Ingredient not found in API."}

def update_ingredient(ingredient_id, updates):
    """
    Update the details of a stored ingredient.

    This function allows modifying specific attributes of an already 
    stored ingredient in the local memory dictionary.

    Args:
        ingredient_id (int): The unique identifier of the ingredient to update.
        updates (dict): A dictionary of attributes to update and their new values.

    Returns:
        dict: A status response with the following possible formats:
        - Success: {'status': 'success', 'message': 'Ingredient updated.', 'ingredient': {...}}
        - Error: {'status': 'error', 'message': 'Ingredient not found in memory.'}
    
    Example:
        >>> update_ingredient(1234, {'protein': 0.5, 'fat': 0.3})
        {'status': 'success', 'message': 'Ingredient updated.', 'ingredient': {...}}
    """
    if ingredient_id not in stored_ingredients:
        return {"status": "error", "message": "Ingredient not found in memory."}
    for key, value in updates.items():
        if key in stored_ingredients[ingredient_id]:
            stored_ingredients[ingredient_id][key] = value
    return {"status": "success", "message": "Ingredient updated.", "ingredient": stored_ingredients[ingredient_id]}

def delete_ingredient(ingredient_id):
    """
    Remove an ingredient from the local memory dictionary.

    Args:
        ingredient_id (int): The unique identifier of the ingredient to delete.

    Returns:
        dict: A status response with the following possible formats:
        - Success: {'status': 'success', 'message': 'Ingredient deleted.', 'ingredient': {...}}
        - Error: {'status': 'error', 'message': 'Ingredient not found in memory.'}
    
    Example:
        >>> delete_ingredient(1234)
        {'status': 'success', 'message': 'Ingredient deleted.', 'ingredient': {...}}
    """
    if ingredient_id in stored_ingredients:
        deleted = stored_ingredients.pop(ingredient_id)
        return {"status": "success", "message": "Ingredient deleted.", "ingredient": deleted}
    else:
        return {"status": "error", "message": "Ingredient not found in memory."}

def list_stored_ingredients():
    """
    Retrieve a list of all ingredients currently stored in memory.

    Returns:
        dict: A dictionary containing a list of all stored ingredient details.
    
    Example:
        >>> list_stored_ingredients()
        {'stored_ingredients': [{...}, {...}, ...]}
    """
    return {"stored_ingredients": list(stored_ingredients.values())}

def get_ingredient(ingredient_id):
    """
    Retrieve the details of a single ingredient from local memory.

    Args:
        ingredient_id (int): The unique identifier of the ingredient to retrieve.

    Returns:
        dict: A status response with the following possible formats:
        - Success: {'status': 'success', 'ingredient': {...}}
        - Error: {'status': 'error', 'message': 'Ingredient not found in memory.'}
    
    Example:
        >>> get_ingredient(1234)
        {'status': 'success', 'ingredient': {...}}
    """
    if ingredient_id in stored_ingredients:
        return {"status": "success", "ingredient": stored_ingredients[ingredient_id]}
    else:
        return {"status": "error", "message": "Ingredient not found in memory."}
