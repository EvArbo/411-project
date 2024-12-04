import pytest

from meal_max.models.workout import WorkoutManager
from meal_max.models.exercises import Exercise

@pytest.fixture
def workout_manager():
    """
    Fixture to provide a new instance of WorkoutManager for each test.
    This ensures that each test starts with a fresh instance of the class,
    avoiding state leakage between tests.
    """
    return WorkoutManager()

# Fixtures for sample exercises
@pytest.fixture
def sample_exercise1():
    """
    Fixture to create and return a sample exercise (Push-Up).
    
    This exercise is used to test adding and managing exercises in the workout manager.
    """
    exercise = Exercise(
        id=1,
        name="Push-Up",
        category="Strength",
        calories_burned_per_minute=8,
        duration=10
    )
    return exercise

@pytest.fixture
def sample_exercise2():
    """
    Fixture to create and return a sample exercise (Running).
    
    This exercise is used to test adding and managing exercises in the workout manager.
    """
    exercise = Exercise(
        id=2,
        name="Running",
        category="Cardio",
        calories_burned_per_minute=12,
        duration=30
    )
    return exercise

@pytest.fixture
def sample_exercises(sample_exercise1, sample_exercise2):
    """
    Fixture to return a list of sample exercises.
    
    This fixture provides multiple exercises to test the behavior of workout management with multiple items.
    """
    return [sample_exercise1, sample_exercise2]


##########################################################
# Exercise Management
##########################################################

def test_clear_exercises(workout_manager, sample_exercises):
    """
    Test that the clear_workout method empties the exercise list.
    
    This test ensures that the `clear_workout` method correctly removes all exercises
    from the workout manager, leaving the exercise list empty.
    """
    workout_manager.exercises.extend(sample_exercises)

    # Call the clear_workout method
    workout_manager.clear_workout()

    # Assert that the exercises list is now empty
    assert len(workout_manager.exercises) == 0, "Exercises list should be empty after calling clear_workout."

def test_clear_exercises_empty(workout_manager):
    """
    Test that calling clear_workout on an empty list keeps it empty.
    
    This test verifies that the `clear_workout` method does not cause any issues
    when called on an already empty exercise list.
    """
    # Call the clear_workout method with an empty list
    workout_manager.clear_workout()

    # Assert that the exercises list is still empty
    assert len(workout_manager.exercises) == 0, "Exercises list should remain empty if it was already empty."

def test_get_exercises_empty(workout_manager):
    """
    Test that get_all_exercises returns an empty list when there are no exercises.
    
    This ensures that when no exercises are added, the `get_all_exercises` method returns an empty list.
    """
    # Call the function and verify the result
    exercises = workout_manager.get_all_exercises()
    assert exercises == [], "Expected get_all_exercises to return an empty list when there are no exercises."

def test_get_exercises_with_data(workout_manager, sample_exercises):
    """
    Test that get_all_exercises returns the correct list when there are exercises.
    
    This test verifies that the `get_all_exercises` method returns the correct list of exercises
    when they are added to the workout manager.
    """
    workout_manager.exercises.extend(sample_exercises)

    # Call the function and verify the result
    exercises = workout_manager.get_all_exercises()
    assert exercises == workout_manager.exercises, "Expected get_all_exercises to return the correct exercises list."

def test_add_exercise(workout_manager, sample_exercise1):
    """
    Test that an exercise is correctly added to the list.
    
    This test ensures that the `add_exercise` method adds an exercise to the workout manager's
    exercise list, and the exercise is properly added.
    """
    # Call add_exercise with the exercise data
    workout_manager.add_exercise(sample_exercise1)

    # Assert that the exercise was added to the list
    assert len(workout_manager.exercises) == 1, "Exercises list should contain one exercise after calling add_exercise."
    assert workout_manager.exercises[0].name == "Push-Up", "Expected 'Push-Up' in the exercises list."

def test_add_exercise_full(workout_manager, sample_exercises):
    """
    Test that add_exercise raises an error when the list is full.
    
    This test verifies that when the exercise list is full, the `add_exercise` method raises
    a ValueError, preventing more exercises from being added.
    """
    # Mock the exercises list with 2 exercises
    workout_manager.exercises.extend(sample_exercises)

    # Define the exercise data to be passed to add_exercise
    new_exercise = Exercise(3, "Squats", "Strength", 10, 15)

    # Call add_exercise and expect an error since the list is full
    with pytest.raises(ValueError, match="Exercise list is full"):
        workout_manager.add_exercise(new_exercise)

    # Assert that the exercises list still contains only the original 2 exercises
    assert len(workout_manager.exercises) == 2, "Exercises list should still contain only 2 exercises after trying to add a third."


##########################################################
# Workout Statistics
##########################################################

def test_get_total_calories(workout_manager, sample_exercises):
    """
    Test the get_total_calories method.
    
    This test checks that the `get_total_calories` method correctly calculates
    the total calories burned by all exercises in the workout manager.
    """
    workout_manager.exercises.extend(sample_exercises)

    # Calculate expected total calories
    total_calories = (8 * 10) + (12 * 30)  # 80 + 360 = 440

    # Call get_total_calories and verify the result
    assert workout_manager.get_total_calories() == total_calories, f"Expected total calories: {total_calories}, got {workout_manager.get_total_calories()}."

def test_get_total_duration(workout_manager, sample_exercises):
    """
    Test the get_total_duration method.
    
    This test ensures that the `get_total_duration` method correctly calculates
    the total duration of all exercises in the workout manager.
    """
    workout_manager.exercises.extend(sample_exercises)

    # Calculate expected total duration
    total_duration = 10 + 30  # 40

    # Call get_total_duration and verify the result
    assert workout_manager.get_total_duration() == total_duration, f"Expected total duration: {total_duration}, got {workout_manager.get_total_duration()}."

def test_get_total_calories_empty(workout_manager):
    """
    Test get_total_calories when there are no exercises.
    
    This test ensures that when there are no exercises, the `get_total_calories`
    method correctly returns 0 as the total calories burned.
    """
    # Call get_total_calories and verify it returns 0
    assert workout_manager.get_total_calories() == 0, "Expected total calories to be 0 when there are no exercises."

def test_get_total_duration_empty(workout_manager):
    """
    Test get_total_duration when there are no exercises.
    
    This test ensures that when there are no exercises, the `get_total_duration`
    method correctly returns 0 as the total duration of exercises.
    """
    # Call get_total_duration and verify it returns 0
    assert workout_manager.get_total_duration() == 0, "Expected total duration to be 0 when there are no exercises."
