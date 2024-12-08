from flask import Flask, request, jsonify
from meal_max.models.user_model import create_user, authenticate_user, change_password
from meal_max.models.fitness_tracker_model import WorkoutManager  # Import the WorkoutManager class

app = Flask(__name__)

# Initialize the WorkoutManager with the API key
wger_api_key = "your_wger_api_key_here"  # You should securely store this in environment variables or a config file
workout_manager = WorkoutManager(wger_api_key)

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


# Workout Session Routes
@app.route('/workoutsession', methods=['POST'])
def create_workout_session():
    session_data = request.json
    created_session = workout_manager.create_workout_session(session_data)
    
    if created_session:
        return jsonify({"message": "Workout session created successfully", "session": created_session}), 201
    else:
        return jsonify({"error": "Failed to create workout session"}), 500

@app.route('/workoutsession/<int:session_id>', methods=['GET'])
def retrieve_workout_session(session_id):
    session = workout_manager.retrieve_workout_session(session_id)
    
    if session:
        return jsonify({"session": session}), 200
    else:
        return jsonify({"error": "Workout session not found"}), 404

@app.route('/workoutsession/<int:session_id>', methods=['PUT'])
def update_workout_session(session_id):
    updated_data = request.json
    updated_session = workout_manager.update_workout_session(session_id, updated_data)
    
    if updated_session:
        return jsonify({"message": "Workout session updated successfully", "session": updated_session}), 200
    else:
        return jsonify({"error": "Failed to update workout session"}), 500

@app.route('/workoutsession/<int:session_id>', methods=['DELETE'])
def delete_workout_session(session_id):
    if workout_manager.delete_workout_session(session_id):
        return jsonify({"message": "Workout session deleted successfully"}), 200
    else:
        return jsonify({"error": "Failed to delete workout session"}), 500

@app.route('/workoutsessions', methods=['GET'])
def list_workout_sessions():
    sessions = workout_manager.list_workout_sessions()
    return jsonify({"sessions": sessions}), 200

@app.route('/')
def home():
    return "Welcome to the Fitness Tracker App!"


if __name__ == "__main__":
    app.run(debug=True)
