from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
# from flask_cors import CORS

from meal_max.models.exercises import Exercise
from meal_max.models.workout import WorkoutManager
from meal_max.utils.sql_utils import check_database_connection, check_table_exists
from config import ProductionConfig
from meal_max.db import db
from meal_max.models.mongo_session_model import login_user, logout_user
from meal_max.models.user_model import Users
from datetime import datetime
import logging
import os
wger_api_key = os.getenv("WGER_API_KEY")
workout_manager = WorkoutManager(wger_api_key)
# Load environment variables from .env file
load_dotenv()

    
def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    workout_manager = WorkoutManager(wger_api_key)

    ####################################################
    #
    # Healthchecks
    #
    ####################################################


    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)

    @app.route('/api/db-check', methods=['GET'])
    def db_check() -> Response:
        """
        Route to check if the database connection and workout logs table are functional.

        Returns:
            JSON response indicating the database health status.
        Raises:
            404 error if there is an issue with the database.
        """
        try:
            app.logger.info("Checking database connection...")
            check_database_connection()
            app.logger.info("Database connection is OK.")
            app.logger.info("Checking if workout logs table exists...")
            check_table_exists("workout_logs")
            app.logger.info("Workout logs table exists.")
            return make_response(jsonify({'database_status': 'healthy'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 404)

    ##########################################################
    #
    # User management
    #
    ##########################################################

    @app.route('/api/create-user', methods=['POST'])
    def create_user() -> Response:
        """
        Route to create a new user.

        Expected JSON Input:
            - username (str): The username for the new user.
            - password (str): The password for the new user.

        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the user to the database.
        """
        app.logger.info('Creating new user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)

            # Call the User function to add the user to the database
            app.logger.info('Adding user: %s', username)
            Users.create_user(username, password)

            app.logger.info("User added: %s", username)
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        except Exception as e:
            app.logger.error("Failed to add user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/delete-user', methods=['DELETE'])
    def delete_user() -> Response:
        """
        Route to delete a user.

        Expected JSON Input:
            - username (str): The username of the user to be deleted.

        Returns:
            JSON response indicating the success of user deletion.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue deleting the user from the database.
        """
        app.logger.info('Deleting user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')

            if not username:
                return make_response(jsonify({'error': 'Invalid input, username is required'}), 400)

            # Call the User function to delete the user from the database
            app.logger.info('Deleting user: %s', username)
            Users.delete_user(username)

            app.logger.info("User deleted: %s", username)
            return make_response(jsonify({'status': 'user deleted', 'username': username}), 200)
        except Exception as e:
            app.logger.error("Failed to delete user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/login', methods=['POST'])
    def login():
        """
        Route to log in a user and load their combatants.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's password.

        Returns:
            JSON response indicating the success of the login.

        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username or password).
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            app.logger.error("Invalid request payload for login.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

        username = data['username']
        password = data['password']

        try:
            # Validate user credentials
            if not Users.check_password(username, password):
                app.logger.warning("Login failed for username: %s", username)
                raise Unauthorized("Invalid username or password.")

            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Load user's combatants into the battle model
            login_user(user_id, battle_model)

            app.logger.info("User %s logged in successfully.", username)
            return jsonify({"message": f"User {username} logged in successfully."}), 200

        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500


    @app.route('/api/logout', methods=['POST'])
    def logout():
        """
        Route to log out a user and save their combatants to MongoDB.

        Expected JSON Input:
            - username (str): The username of the user.

        Returns:
            JSON response indicating the success of the logout.

        Raises:
            400 error if input validation fails or user is not found in MongoDB.
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data:
            app.logger.error("Invalid request payload for logout.")
            raise BadRequest("Invalid request payload. 'username' is required.")

        username = data['username']

        try:
            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Save user's combatants and clear the battle model
            logout_user(user_id, battle_model)

            app.logger.info("User %s logged out successfully.", username)
            return jsonify({"message": f"User {username} logged out successfully."}), 200

        except ValueError as e:
            app.logger.warning("Logout failed for username %s: %s", username, str(e))
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error("Error during logout for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500

    ##########################################################
    #
    # Exercise management
    #
    ##########################################################

    @app.route('/api/create-exercise', methods=['POST'])
    def create_exercise() -> Response:
        """
        Route to add a new exercise to the workout.

        Expected JSON Input:
            name (str): Name of the exercise.
            weight (float): Weight used in the exercise.
            repetitions (int): Number of repetitions performed.
            rpe (float): Rating of Perceived Exertion (0-10 scale).
        Returns:
            JSON response indicating the success of the exercise addition.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the exercise to the workout.
        """
        app.logger.info('Adding a new exercise to the catalog')
        try:
            data = request.get_json()

            name = data.get('name')
            weight = data.get('weight')
            repetitions = data.get('repetitions')
            rpe = data.get('rpe')

            if not name or not weight or not repetitions or rpe is None:
                return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

            # Add the exercise to the workout
            app.logger.info('Adding exercise: ', name, weight)
            Exercise.create_exercise(name=name, weight=weight, repetitions=repetitions, rpe=rpe)
            app.logger.info("exercise added to workout: ", name, weight)
            return make_response(jsonify({'status': 'success', 'exercise': name}), 201)
        except Exception as e:
            app.logger.error("Failed to add exercise: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    
        
    @app.route('/api/delete-exercise/<int:exercise_id>', methods=['DELETE'])
    def delete_exercise(exercise_id: int) -> Response:
        """
        Route to delete a exercise by its ID (soft delete).

        Path Parameter:
            - exercise_id (int): The ID of the exercise to delete.

        Returns:
            JSON response indicating success of the operation or error message.
        """
        try:
            app.logger.info(f"Deleting exercise by ID: {exercise_id}")
            Exercise.delete_song(exercise_id)
            return make_response(jsonify({'status': 'success'}), 200)
        except Exception as e:
            app.logger.error(f"Error deleting exercise: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
        
    @app.route('/api/get-all-exercises-from-catalog', methods=['GET'])
    def get_all_exercises() -> Response:
        """
        Route to retrieve all exercises in the catalog (non-deleted).

        Returns:
            JSON response with the list of exercises or error message.
        """
        try:
            
            app.logger.info("Retrieving all exercises from the catalog",)
            exercises = Exercise.get_all_exercises()

            return make_response(jsonify({'status': 'success', 'exercises': exercises}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving exercises: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
        
    @app.route('/api/get-exercise-from-catalog-by-id/<int:exercise_id>', methods=['GET'])
    def get_exercise_by_id(exercise_id: int) -> Response:
        """
        Route to retrieve a exercise by its ID.

        Path Parameter:
            - exercise_id (int): The ID of the exercise.

        Returns:
            JSON response with the exercise details or error message.
        """
        try:
            app.logger.info(f"Retrieving exercise by ID: {exercise_id}")
            exercise = Exercise.get_song_by_id(exercise_id)
            return make_response(jsonify({'status': 'success', 'exercise': exercise}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving exercise by ID: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/update-exercise/<int:exercise_id>', methods=['PUT'])
    def update_exercise_route(exercise_id):
        """
        Flask route to update an exercise.

        Returns:
            JSON response with the exercise updating successfully or error message.
        """
        try:
            # Parse JSON data from the request
            data = request.get_json()

            # Extract optional fields from the request
            weight = data.get('weight')
            repetitions = data.get('repetitions')
            rpe = data.get('rpe')

            # Call the update_exercise function
            Exercise.update_exercise(
                exercise_id=exercise_id,
                weight=weight,
                repetitions=repetitions,
                rpe=rpe
            )

            # Return success response
            return jsonify({
                "message": f"Exercise with ID {exercise_id} updated successfully."
            }), 200
        except Exception as e:
            app.logger.error(f"Error updating exercise: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
    ##########################################################
    #
    # Workout management
    #
    ##########################################################



    exercises_manager = Exercise(123456, "Evan", 140, 1, 1, 5)

    @app.route('/api/add-exercise', methods=['POST'])
    def add_exercise() -> Response:
        """
        Route to add a new exercise to the database.

        Expected JSON Input:
            - name (str): The name of the exercise.
            - weight (float): The numeric weight of the exercise.
            - repetitions (str): Number of repetitions performed.
            - rpe (float): Rating of Perceived Exertion (0-10 scale).
        Returns:
            JSON response indicating the success of the exercise addition or errors in input validation.
        """
        app.logger.info('Creating new exercise')

        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            name = data.get('name')
            weight = data.get('weight')
            repetitions = data.get('repetitions')
            rpe = data.get('rpe')

            # Validate fields
            if not name or weight is None or not repetitions or rpe is None:
                return make_response(jsonify({'error': 'All fields (name, weight, repetitions, rpe) are required'}), 400)

            app.logger.info('Adding exercise: ', name, weight, repetitions, rpe)
            Exercise.create_exercise(name=name, weight=weight, repetitions=repetitions, rpe=rpe)
            app.logger.info('exercise added to workout: ', name, weight, repetitions, rpe)
            return make_response(jsonify({'status': 'success', 'exercise': name}), 201)
        except Exception as e:
            app.logger.error("Failed to add exercise: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)
        
    @app.route('/api/remove-exercise/<int:exercise_id>', methods=['DELETE'])
    def remove_exercise(exercise_id: int) -> Response:
        """
        Route to delete an exercise by its ID. This performs a soft delete by marking it as deleted.

        Path Parameter:
            - exercise_id (int): The ID of the exercise to delete.

        Returns:
            JSON response indicating success of the operation or error message.
        """
        try:
            app.logger.info(f"Deleting exercise by ID: {exercise_id}")

            WorkoutManager.delete_exercise(exercise_id)
            return make_response(jsonify({'status': 'success'}), 200)
        except Exception as e:
            app.logger.error(f"Error deleting exercise: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/clear-workout', methods=['DELETE'])
    def clear_workout() -> Response:
        """
        Route to clear all exercises (recreates the table).

        Returns:
            JSON response indicating success of the operation or error message.
        """
        try:
            app.logger.info("Clearing the exercises")
            WorkoutManager.clear_workout()
            return make_response(jsonify({'status': 'success'}), 200)
        except Exception as e:
            app.logger.error(f"Error clearing catalog: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
        
    @app.route('/api/get-all-exercises', methods=['GET'])
    def get_all_exercises() -> Response:
        """
        Route to retrieve all exercises in the catalog (non-deleted).


        Returns:
            JSON response with the list of exercises or error message.
        """
        try:
            
            app.logger.info("Retrieving all exercises from the workout")
            exercises = WorkoutManager.get_all_exercises()

            return make_response(jsonify({'status': 'success', 'exercises': exercises}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving exercises: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
        
    @app.route('/api/get-exercise-by-id/<int:exercise_id>', methods=['GET'])
    def get_exercise_by_id(exercise_id: int) -> Response:
        """
        Route to get a exercise by its ID.

        Path Parameter:
            - exercise_id (int): The ID of the exercise.

        Returns:
            JSON response with the exercise details or error message.
        """
        try:
            app.logger.info(f"Retrieving exercise by ID: {exercise_id}")

            exercise = WorkoutManager.get_exercise_by_id(exercise_id)
            return make_response(jsonify({'status': 'success', 'exercise': exercise}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving exercise by ID: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-exercise-by-name/<string:exercise_name>', methods=['GET'])
    def get_exercise_by_name(exercise_name: str) -> Response:
        """
        Route to get a exercise by its name.

        Path Parameter:
            - exercise_name (str): The name of the exercise.

        Returns:
            JSON response with the exercise details or error message.
        """
        try:
            app.logger.info(f"Retrieving exercise by name: {exercise_name}")

            if not exercise_name:
                return make_response(jsonify({'error': 'Exercise name is required'}), 400)

            exercise = WorkoutManager.get_exercise_by_name(exercise_name)
            return make_response(jsonify({'status': 'success', 'exercise': exercise}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving exercise by name: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    ############################################################
    #
    # Workout Summary
    #
    ############################################################


    @app.route('/api/get-workout-summary', methods=['GET'])
    def get_workout_summary() -> Response:
        """
        Route to get the workout summary of exercises sorted by wins, battles, or win percentage.

        Query Parameters:
            - sort (str): The field to sort by ('wins', 'battles', or 'win_pct'). Default is 'wins'.

        Returns:
            JSON response with a sorted workout summary of exercises.
        Raises:
            500 error if there is an issue generating the workout summary.
        """
        try:
            
            app.logger.info("Generating workout summary")

            workout_summary_data = WorkoutManager.get_workout_summary()

            return make_response(jsonify({'status': 'success', 'workout summary': workout_summary_data}), 200)
        except Exception as e:
            app.logger.error(f"Error generating workout summary: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    ##########################################################
    #
    # Fetch WgerAPI
    #
    ##########################################################
    @app.route('/api/fetch-categories', methods=['GET'])
    def fetch_exercise_categories() -> Response:
        """
        Fetch exercise categories from the Wger API.

        Returns:
            JSON response with the list of exercise categories or an error message.
        """
        try:
            categories = workout_manager.fetch_exercise_categories()

            if categories:
                return make_response(jsonify({'status': 'success', 'data': categories}), 200)
            else:
                return make_response(jsonify({'status': 'error', 'message': 'No categories found'}), 404)
        except Exception as e:
            app.logger.error(f"Error fetching exercise categories: {e}")
            return make_response(jsonify({'status': 'error', 'message': str(e)}), 500)

    @app.route('/api/fetch-muscles', methods=['GET'])
    def fetch_muscles() -> Response:
        """
        Fetch muscle groups from the Wger API.

        Returns:
            JSON response with the list of muscle groups or an error message.
        """
        try:
            muscles = workout_manager.fetch_muscles()

            if muscles:
                return make_response(jsonify({'status': 'success', 'data': muscles}), 200)
            else:
                return make_response(jsonify({'status': 'error', 'message': 'No muscle groups found'}), 404)
        except Exception as e:
            app.logger.error(f"Error fetching muscles: {e}")
            return make_response(jsonify({'status': 'error', 'message': str(e)}), 500)

    @app.route('/api/fetch-exercises', methods=['GET'])
    def fetch_exercises() -> Response:
        """
        Fetch exercises from the Wger API. Optionally filter by muscle group.

        Query Parameters:
            - muscle_id (optional, int): ID of the muscle group to filter exercises.

        Returns:
            JSON response with the list of exercises or an error message.
        """
        try:
            muscle_id = request.args.get('muscle_id', type=int)
            exercises = workout_manager.fetch_exercises(muscle_id=muscle_id)

            if exercises:
                return make_response(jsonify({'status': 'success', 'data': exercises}), 200)
            else:
                return make_response(jsonify({'status': 'error', 'message': 'No exercises found'}), 404)
        except Exception as e:
            app.logger.error(f"Error fetching exercises: {e}")
            return make_response(jsonify({'status': 'error', 'message': str(e)}), 500)

    @app.route('/api/fetch-equipment', methods=['GET'])
    def fetch_equipment() -> Response:
        """
        Fetch equipment from the Wger API.

        Returns:
            JSON response with the list of equipment or an error message.
        """
        try:
            equipment = workout_manager.fetch_equipment()

            if equipment:
                return make_response(jsonify({'status': 'success', 'data': equipment}), 200)
            else:
                return make_response(jsonify({'status': 'error', 'message': 'No equipment found'}), 404)
        except Exception as e:
            app.logger.error(f"Error fetching equipment: {e}")
            return make_response(jsonify({'status': 'error', 'message': str(e)}), 500)

    @app.route('/api/fetch-images', methods=['GET'])
    def fetch_images() -> Response:
        """
        Fetch exercise images from the Wger API.

        Returns:
            JSON response with the list of images or an error message.
        """
        try:
            images = workout_manager.fetch_images()

            if images:
                return make_response(jsonify({'status': 'success', 'data': images}), 200)
            else:
                return make_response(jsonify({'status': 'error', 'message': 'No images found'}), 404)
        except Exception as e:
            app.logger.error(f"Error fetching images: {e}")
            return make_response(jsonify({'status': 'error', 'message': str(e)}), 500)




    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port=5000)
