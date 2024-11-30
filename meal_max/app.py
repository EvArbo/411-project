from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
# from flask_cors import CORS

from exercise_max.models import Exercise
from exercise_max.models.workout import WorkoutManager
from exercise_max.utils.sql_utils import check_database_connection, check_table_exists


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# This bypasses standard security stuff we'll talk about later
# If you get errors that use words like cross origin or flight,
# uncomment this
# CORS(app)

# Initialize the Exercise
exercise = Exercise()

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
# Exercises
#
##########################################################

from flask import request, jsonify, make_response, Response
from datetime import datetime
import logging

exercises_manager = Exercise()

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
        app.logger.info('Song added to playlist: ', name, weight, repetitions, rpe)
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
# Battle
#
############################################################


@app.route('/api/battle', methods=['GET'])
def battle() -> Response:
    """
    Route to initiate a battle between the two currently prepared exercises.

    Returns:
        JSON response indicating the result of the battle and the winner.
    Raises:
        500 error if there is an issue during the battle.
    """
    try:
        app.logger.info('Two exercises enter, one exercise leaves!')

        winner = exercises_manager.battle()

        return make_response(jsonify({'status': 'success', 'winner': winner}), 200)
    except Exception as e:
        app.logger.error(f"Battle error: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/clear-combatants', methods=['POST'])
def clear_combatants() -> Response:
    """
    Route to clear the list of combatants for the battle.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue clearing combatants.
    """
    try:
        app.logger.info('Clearing all combatants...')
        exercises_manager.clear_combatants()
        app.logger.info('Combatants cleared.')
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error("Failed to clear combatants: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-combatants', methods=['GET'])
def get_combatants() -> Response:
    """
    Route to get the list of combatants for the battle.

    Returns:
        JSON response with the list of combatants.
    """
    try:
        app.logger.info('Getting combatants...')
        combatants = exercises_manager.get_combatants()
        return make_response(jsonify({'status': 'success', 'combatants': combatants}), 200)
    except Exception as e:
        app.logger.error("Failed to get combatants: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/prep-combatant', methods=['POST'])
def prep_combatant() -> Response:
    """
    Route to prepare a prep a exercise making it a combatant for a battle.

    Parameters:
        - exercise (str): The name of the exercise

    Returns:
        JSON response indicating the success of combatant preparation.
    Raises:
        500 error if there is an issue preparing combatants.
    """
    try:
        data = request.json
        exercise = data.get('exercise')
        app.logger.info("Preparing combatant: %s", exercise)

        if not exercise:
            return make_response(jsonify({'error': 'You must name a combatant'}), 400)

        try:
            exercise = WorkoutManager.get_exercise_by_name(exercise)
            exercises_manager.prep_combatant(exercise)
            combatants = exercises_manager.get_combatants()
        except Exception as e:
            app.logger.error("Failed to prepare combatant: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)
        return make_response(jsonify({'status': 'success', 'combatants': combatants}), 200)

    except Exception as e:
        app.logger.error("Failed to prepare combatants: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)


############################################################
#
# Leaderboard
#
############################################################


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard() -> Response:
    """
    Route to get the leaderboard of exercises sorted by wins, battles, or win percentage.

    Query Parameters:
        - sort (str): The field to sort by ('wins', 'battles', or 'win_pct'). Default is 'wins'.

    Returns:
        JSON response with a sorted leaderboard of exercises.
    Raises:
        500 error if there is an issue generating the leaderboard.
    """
    try:
        sort_by = request.args.get('sort', 'wins')  # Default sort by wins
        app.logger.info("Generating leaderboard sorted by %s", sort_by)

        leaderboard_data = WorkoutManager.get_leaderboard(sort_by)

        return make_response(jsonify({'status': 'success', 'leaderboard': leaderboard_data}), 200)
    except Exception as e:
        app.logger.error(f"Error generating leaderboard: {e}")
        return make_response(jsonify({'error': str(e)}), 500)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)