from flask import Flask, jsonify, request
from meal_tracker.models.user_model import create_user, authenticate_user, change_password

from meal_tracker.models.food_model import (
    store_ingredient,
    update_ingredient,
    delete_ingredient,
    list_stored_ingredients,
    get_ingredient,
)

app = Flask(__name__)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(), 
    ],
)
@app.route('/health', methods=['GET'])
def health_check():
    """Health check route to verify the app is running."""
    app.logger.info("Health check endpoint was called.")
    return jsonify({"status": "healthy"}), 200

@app.route('/create-account', methods=['POST'])
def create_account():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    try:
        create_user(username, password)
        return jsonify({"message": "Account created successfully."}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if authenticate_user(username, password):
        return jsonify({"message": "Login successful."}), 200
    else:
        return jsonify({"error": "Invalid username or password."}), 401

@app.route('/update-password', methods=['POST'])
def update_password():
    data = request.json
    username = data.get('username')
    new_password = data.get('new_password')

    if not username or not new_password:
        return jsonify({"error": "Username and new password are required."}), 400

    try:
        change_password(username, new_password)
        return jsonify({"message": "Password updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/')
def home():
    return "Welcome to the Meal Tracker App!"


@app.route('/food/add/<int:ingredient_id>', methods=['POST'])
def add_ingredient(ingredient_id):
    result = store_ingredient(ingredient_id)
    if result["status"] == "success":
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/food/update/<int:ingredient_id>', methods=['PUT'])
def update_ingredient_route(ingredient_id):
    updates = request.json
    result = update_ingredient(ingredient_id, updates)
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 404

@app.route('/food/delete/<int:ingredient_id>', methods=['DELETE'])
def delete_ingredient_route(ingredient_id):
    result = delete_ingredient(ingredient_id)
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@app.route('/food/<int:ingredient_id>', methods=['GET'])
def get_ingredient_route(ingredient_id):
    result = get_ingredient(ingredient_id)
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@app.route('/food/list', methods=['GET'])
def list_ingredients():
    return jsonify(list_stored_ingredients()), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

 
