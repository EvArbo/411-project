from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.exercises import (
    Exercise,
    create_exercise,
    delete_exercise,
    get_exercise_by_id,
    get_all_exercises,
    clear_catalog
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.exercises.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_exercise(mock_cursor):
    """Test creating a new exercise in the catalog."""

    # Call the function to create a new exercise
    create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions=4, rpe=7)

    expected_query = normalize_whitespace("""
        INSERT INTO workout_log (name, weight, sets, repetitions, rpe)
        VALUES (?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Barbell Deadlift", 315, 2, 4, 7)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_exercise_invalid_name():
    """Test error when trying to create a exercise with an invalid name (e.g., not a string)"""

    # Attempt to create a exercise with a invalid name
    with pytest.raises(ValueError, match=r"Invalid name: -1 \(must be a string\)."):
        create_exercise(name=-1, weight=315, sets=2, repetitions=4, rpe=7)

def test_create_exercise_invalid_weight():
    """Test error when trying to create a exercise with an invalid weight (e.g., negative weight)"""

    # Attempt to create a exercise with a negative weight
    with pytest.raises(ValueError, match=r"Invalid weight: -315 \(must be non-negative\)."):
        create_exercise(name="Barbell Deadlift", weight=-315, sets=2, repetitions=4, rpe=7)

def test_create_exercise_invalid_sets():
    """Test error when trying to create an exercise with an invalid number of sets (e.g., less than 1 or non-integer)."""

    # Attempt to create an exercise with a sets value of less than 1
    with pytest.raises(ValueError, match=r"Invalid number of sets: 0 \(must be at least 1 and an integer\)."):
        create_exercise(name="Barbell Deadlift", weight=315, sets=0, repetitions=4, rpe=7)

    # Attempt to create an exercise with a non-integer number of sets
    with pytest.raises(ValueError, match=r"Invalid number of sets: invalid \(must be at least 1 and an integer\)."):
        create_exercise(name="Barbell Deadlift", weight=315, sets="invalid", repetitions=4, rpe=7)


def test_create_exercise_invalid_repetitions():
    """Test error when trying to create an exercise with an invalid number of repetitions (e.g., less than 0 or non-integer)."""

    # Attempt to create an exercise with a repetition value of less than 0
    with pytest.raises(ValueError, match=r"Invalid number of repetitions: -1 \(must be at least 0 and an integer\)."):
        create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions=-1, rpe=7)

    # Attempt to create an exercise with a non-integer number of repetitions
    with pytest.raises(ValueError, match=r"Invalid number of repetitions: invalid \(must be at least 0 and an integer\)."):
        create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions="invalid", rpe=7)


def test_create_exercise_invalid_rpe():
    """Test error when trying to create an exercise with an invalid RPE (e.g., not within the range of 0 and 10)."""

    # Attempt to create an exercise with an RPE less than 0
    with pytest.raises(ValueError, match=r"Invalid RPE: -180 \(must be a float between 0 and 10\)."):
        create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions=4, rpe=-180)

    # Attempt to create an exercise with an RPE greater than 10
    with pytest.raises(ValueError, match=r"Invalid RPE: 15 \(must be a float between 0 and 10\)."):
        create_exercise(name="Barbell Deadlift", weight=315, sets=2, repetitions=4, rpe=15)


def test_clear_catalog(mock_cursor, mocker):
    """Test clearing the entire exercise catalog (removes all exercises)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/init_db.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_catalog()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/init_db.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()

def test_delete_exercise(mock_cursor):
    """Test soft deleting a exercise from the catalog by exercise ID."""

    # Simulate that the exercise exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_exercise function
    delete_exercise(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM workout_log WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE workout_log SET deleted = TRUE WHERE id = ?")
    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_exercise_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent exercise."""

    # Simulate that no exercise exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent exercise
    with pytest.raises(ValueError, match="Exercise with ID 999 not found"):
        delete_exercise(999)

def test_delete_exercise_already_deleted(mock_cursor):
    """Test error when trying to delete a exercise that's already marked as deleted."""

    # Simulate that the exercise exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a exercise that's already been deleted
    with pytest.raises(ValueError, match="Exercise with ID 999 has already been deleted"):
        delete_exercise(999)



######################################################
#
#    Get Exercise
#
######################################################

def test_get_exercise_by_id(mock_cursor):
    # Simulate that the exercise exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Barbell Deadlift", 315, 2, 1, 7)


    # Call the function and check the result
    result = get_exercise_by_id(1)

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
