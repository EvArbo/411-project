from contextlib import contextmanager
import re
import pytest
from meal_max.models.workout import WorkoutManager
from meal_max.models.exercises import (
    Exercise,
    create_exercise,
    delete_exercise,
    get_exercise_by_id,
    get_all_exercises
    #clear_catalog
)

######################################################
# Utility Functions
######################################################

def normalize_whitespace(sql_query: str) -> str:
    """
    Normalize whitespace in an SQL query for comparison in tests.
    """
    return re.sub(r'\s+', ' ', sql_query).strip()

######################################################
# Fixtures
######################################################

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("meal_max.models.exercises.get_db_connection", mock_get_db_connection)

    return mock_cursor

@pytest.fixture
def workout_manager():
    """
    Fixture to provide a new instance of WorkoutManager for each test.
    """
    wger_api_key = 'test_api_key'
    return WorkoutManager(wger_api_key=wger_api_key)

@pytest.fixture
def sample_exercise1():
    """
    Fixture to create a sample exercise (Push-Up).
    """
    return Exercise(
        id=1,
        name="Push-Up",
        weight=0,  # Example value for unweighted exercise
        sets=3,    # Example sets
        repetitions=15,  # Example repetitions
        rpe=7,     # Example RPE
    )

@pytest.fixture
def sample_exercise2():
    """
    Fixture to create a sample exercise (Running).
    """
    return Exercise(
        id=2,
        name="Running",
        weight=0,  # Example value for unweighted exercise
        sets=1,    # Example sets
        repetitions=30,  # Example repetitions
        rpe=6,     # Example RPE
    )

@pytest.fixture
def sample_exercises(sample_exercise1, sample_exercise2):
    """
    Fixture to provide a list of sample exercises.
    """
    return [sample_exercise1, sample_exercise2]

##########################################################
# Exercise Management Tests
##########################################################

def test_get_exercises_empty(workout_manager):
    """
    Test that get_all_exercises returns an empty list when no exercises exist.
    """
    assert workout_manager.get_all_exercises() == [], "Expected empty list when there are no exercises."

def test_get_exercises_with_data(workout_manager, sample_exercises):
    """
    Test that get_all_exercises returns the correct list of exercises.
    """
    workout_manager.exercises.extend(sample_exercises)
    assert workout_manager.get_all_exercises() == workout_manager.exercises, "Expected exercises to match the list."

def test_add_exercise(workout_manager, sample_exercise1):
    """
    Test that add_exercise adds a new exercise to the list.
    """
    workout_manager.add_exercise(sample_exercise1)
    assert len(workout_manager.exercises) == 1, "List should have one exercise after add_exercise."
    assert workout_manager.exercises[0].name == "Push-Up", "Expected 'Push-Up' in the list."


##########################################################
# Additional Exercise Management Tests
##########################################################

def test_add_exercise_invalid_type(workout_manager):
    """
    Test that adding an invalid type to the workout raises a TypeError.
    """
    with pytest.raises(TypeError, match="Input is not a valid Exercise instance"):
        workout_manager.add_exercise("Invalid Exercise")

def test_add_exercise_duplicate_id(workout_manager, sample_exercise1):
    """
    Test that adding an exercise with a duplicate ID raises a ValueError.
    """
    workout_manager.add_exercise(sample_exercise1)
    with pytest.raises(ValueError, match=f"Exercise with ID {sample_exercise1.id} already exists in the workout"):
        workout_manager.add_exercise(sample_exercise1)

def test_remove_exercise(workout_manager, sample_exercise1):
    """
    Test that removing an exercise works as expected.
    """
    workout_manager.add_exercise(sample_exercise1)
    workout_manager.remove_exercise(sample_exercise1.id)
    assert len(workout_manager.exercises) == 0, "List should be empty after removing exercise."

def test_remove_exercise_not_found(workout_manager):
    """
    Test that attempting to remove a non-existing exercise raises a ValueError.
    """
    with pytest.raises(ValueError, match="Exercise with ID 999 not found in the workout"):
        workout_manager.remove_exercise(999)

def test_clear_workout(workout_manager, sample_exercises):
    """
    Test that clearing the workout removes all exercises.
    """
    workout_manager.exercises.extend(sample_exercises)
    workout_manager.clear_workout()
    assert len(workout_manager.exercises) == 0, "List should be empty after clearing workout."


