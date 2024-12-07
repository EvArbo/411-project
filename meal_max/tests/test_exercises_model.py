from dataclasses import asdict

import pytest

from meal_max.models.exercises import Exercises

@pytest.fixture
def mock_redis_client(mocker):
    return mocker.patch('meal_max.models.exercises.redis_client')

######################################################
#
#    Add and delete
#
######################################################

def test_create_exercise(session):
    """Test creating a new exercise in the catalog."""

    # Call the function to create a new exercise
    Exercises.create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions=4, rpe=7)

    result = Exercises.query.one()
    assert result.name == "Barbell Deadlift"
    assert result.weight == 315
    assert result.sets == 2
    assert result.repetitions == 4
    assert result.rpe == 7


def test_create_exercise_invalid_name():
    """Test error when trying to create a exercise with an invalid name (e.g., not a string)"""

    # Attempt to create a exercise with a invalid name
    with pytest.raises(ValueError, match=r"Invalid name: -1 \(must be a string\)."):
        Exercises.create_exercise(name=-1, weight=315, sets=2, repetitions=4, rpe=7)

def test_create_exercise_invalid_weight():
    """Test error when trying to create a exercise with an invalid weight (e.g., negative weight)"""

    # Attempt to create a exercise with a negative weight
    with pytest.raises(ValueError, match=r"Invalid weight: -315 \(must be non-negative\)."):
        Exercises.create_exercise(name="Barbell Deadlift", weight=-315, sets=2, repetitions=4, rpe=7)

def test_create_exercise_invalid_sets():
    """Test error when trying to create an exercise with an invalid number of sets (e.g., less than 1 or non-integer)."""

    # Attempt to create an exercise with a sets value of less than 1
    with pytest.raises(ValueError, match=r"Invalid number of sets: 0 \(must be at least 1 and an integer\)."):
        Exercises.create_exercise(name="Barbell Deadlift", weight=315, sets=0, repetitions=4, rpe=7)

    # Attempt to create an exercise with a non-integer number of sets
    with pytest.raises(ValueError, match=r"Invalid number of sets: invalid \(must be at least 1 and an integer\)."):
        Exercises.create_exercise(name="Barbell Deadlift", weight=315, sets="invalid", repetitions=4, rpe=7)


def test_create_exercise_invalid_repetitions():
    """Test error when trying to create an exercise with an invalid number of repetitions (e.g., less than 0 or non-integer)."""

    # Attempt to create an exercise with a repetition value of less than 0
    with pytest.raises(ValueError, match=r"Invalid number of repetitions: -1 \(must be at least 0 and an integer\)."):
        Exercises.create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions=-1, rpe=7)

    # Attempt to create an exercise with a non-integer number of repetitions
    with pytest.raises(ValueError, match=r"Invalid number of repetitions: invalid \(must be at least 0 and an integer\)."):
        Exercises.create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions="invalid", rpe=7)


def test_create_exercise_invalid_rpe():
    """Test error when trying to create an exercise with an invalid RPE (e.g., not within the range of 0 and 10)."""

    # Attempt to create an exercise with an RPE less than 0
    with pytest.raises(ValueError, match=r"Invalid RPE: -180 \(must be a float between 0 and 10\)."):
        Exercises.create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions=4, rpe=-180)

    # Attempt to create an exercise with an RPE greater than 10
    with pytest.raises(ValueError, match=r"Invalid RPE: 15 \(must be a float between 0 and 10\)."):
        Exercises.create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions=4, rpe=15)

def test_delete_exercise(session, mock_redi_client):
    """Test soft deleting a exercise from the catalog by exercise ID."""
    Exercises.create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions=4, rpe=7)
    exercise = Exercises.query.one()
    Exercises.delete_exercise(exercise.id)

    result = session.get(Exercises, 1)
    assert result.deleted is True

def test_delete_exercise_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent exercise."""

    # Simulate that no exercise exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent exercise
    with pytest.raises(ValueError, match="Exercise with ID 999 not found"):
        Exercises.delete_exercise(999)

def test_delete_exercise_already_deleted(mock_cursor):
    """Test error when trying to delete a exercise that's already marked as deleted."""

    # Simulate that the exercise exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a exercise that's already been deleted
    with pytest.raises(ValueError, match="Exercise with ID 999 has already been deleted"):
        Exercises.delete_exercise(999)



######################################################
#
#    Get Exercise
#
######################################################

def test_get_exercise_by_id(mock_cursor):
    # Simulate that the exercise exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Barbell Deadlift", 315, 2, 1, 7)


    # Call the function and check the result
    result = Exercises.get_exercise_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Exercise(1, "Barbell Deadlift", 315, 2, 1, 7)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, name, weight, sets, repetitions, rpe FROM workout_log WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_exercise_by_id_bad_id(mock_cursor):
    # Simulate that no exercise exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the exercise is not found
    with pytest.raises(ValueError, match="Exercise with ID 998 not found"):
        get_exercise_by_id(998)

def test_get_all_exercises(mock_cursor):
    """Test retrieving all exercises that are not marked as deleted."""

    # Simulate that there are multiple exercises in the database
    mock_cursor.fetchall.return_value = [
        (1, "Barbell Deadlift", 315, 2, 4, 7, False),
        (2, "Bicep Curls", 25, 3, 12, 6, False),
        (3, "Lat Pulldowns", 110, 4, 12, 6, False)
    ]

    # Call the get_all_exercises function
    exercises = get_all_exercises()

    # Ensure the results match the expected output
    expected_result = [
        {"id": 1, "name": "Barbell Deadlift", "weight": 315, "sets": 2, "repetitions": 4, "rpe": 7},
        {"id": 2, "name": "Bicep Curls", "weight": 25, "sets": 3, "repetitions": 12, "rpe": 6},        
        {"id": 3, "name": "Lat Pulldowns", "weight": 110, "sets": 4, "repetitions": 12, "rpe": 6}            
        ]

    assert exercises == expected_result, f"Expected {expected_result}, but got {exercises}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, name, weight, sets, repetitions, rpe
        FROM workout_log
        WHERE deleted = FALSE
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_all_exercises_empty_catalog(mock_cursor, caplog):
    """Test that retrieving all exercises returns an empty list when the catalog is empty and logs a warning."""

    # Simulate that the catalog is empty (no exercises)
    mock_cursor.fetchall.return_value = []

    # Call the get_all_exercises function
    result = get_all_exercises()

    # Ensure the result is an empty list
    assert result == [], f"Expected empty list, but got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, name, weight, sets, repetitions, rpe FROM workout_log WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
