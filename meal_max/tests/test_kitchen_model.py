from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
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

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the meals table."""

    # Call the function to create a new meal
    create_meal(meal="Meal Name", cuisine="Cuisine Name", price=20.0, difficulty="MED")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name", "Cuisine Name", 20.0, "MED")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate name (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Meal Name' already exists"):
        create_meal(meal="Meal Name", cuisine="Cuisine Name", price=20.0, difficulty="MED")

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty (e.g not 'LOW', 'MED', 'HIGH')"""

    # Attempt to create a song with an invalid difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level: SUPER. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Meal Name", cuisine="Cuisine Name", price=20.0, difficulty="SUPER")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (e.g., negative)."""

    # Attempt to create a meal with negative price
    with pytest.raises(ValueError, match="Invalid price: -20.0. Price must be a positive number."):
        create_meal(meal="Meal Name", cuisine="Cuisine Name", price=-20.0, difficulty="MED")

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the meal table by meal ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_song function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

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

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no song exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meals table (removes all meals)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_meals()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()


######################################################
#
#    Get Meal
#
######################################################

def test_get_meal_by_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Meal Cuisine", 20.0, "MED", False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal Name", "Meal Cuisine", 20.0, "MED")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_id_already_deleted(mock_cursor):
    """Test error when trying to get a meal by id that's already marked as deleted."""

    # Simulate that the meal exists (id = 1) but has been deleted
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Meal Cuisine", 20.0, "MED", True)

    # Expect a ValueError when attempting to get a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(1)

def test_get_meal_by_name(mock_cursor):
    # Simulate that the meal exists (meal_name = "Meal Name")
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Meal Cuisine", 20.0, "MED", False)

    # Call the function and check the result
    result = get_meal_by_name("Meal Name")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal Name", "Meal Cuisine", 20.0, "MED")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_name_bad_name(mock_cursor):
    # Simulate that no meal exists for the given name
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with name Meal Name not found"):
        get_meal_by_name("Meal Name")

def test_get_meal_by_name_already_deleted(mock_cursor):
    """Test error when trying to get a meal by id that's already marked as deleted."""

    # Simulate that the meal exists (id = 1) but has been deleted
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Meal Cuisine", 20.0, "MED", True)

    # Expect a ValueError when attempting to get a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with name Meal Name has been deleted"):
        get_meal_by_name("Meal Name")

def test_get_leaderboard(mock_cursor):
    """Test retrieving all meals that are not marked as deleted from the catalog sorted by the number of wins or the win to battle percentage."""

    # Simulate that there are multiple meals in the database
    mock_cursor.fetchall.return_value = [
        (1, "Meal A", "Cuisine A", 20.20, "MED", 5, 2, 0.4, False),
        (2, "Meal B", "Cuisine B", 20.21, "MED", 2, 2, 1, False),
        (3, "Meal C", "Cuisine C", 20.22, "MED", 4, 1, 0.25, False)
    ]

    # Call the get_all_songs function
    meals = get_leaderboard()

    # Ensure the results match the expected output
    expected_result = [
        {"id": 1, "meal": "Meal A", "cuisine": "Cuisine A", "price": 20.20, "difficulty": "MED", "battles": 5, "wins": 2, "win_pct": 40.0},
        {"id": 2, "meal": "Meal B", "cuisine": "Cuisine B", "price": 20.21, "difficulty": "MED", "battles": 2, "wins": 2, "win_pct": 100},
        {"id": 3, "meal": "Meal C", "cuisine": "Cuisine C", "price": 20.22, "difficulty": "MED", "battles": 4, "wins": 1, "win_pct": 25.0}
    ]

    assert meals == expected_result, f"Expected {expected_result}, but got {meals}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_by_win_pct(mock_cursor):
    """Test retrieving all meals that are not marked as deleted from the catalog sorted by the number of wins or the win to battle percentage."""

    # Simulate that there are multiple meals in the database
    mock_cursor.fetchall.return_value = [
        (1, "Meal A", "Cuisine A", 20.20, "MED", 5, 2, 0.4, False),
        (2, "Meal B", "Cuisine B", 20.21, "MED", 2, 2, 1, False),
        (3, "Meal C", "Cuisine C", 20.22, "MED", 4, 1, 0.25, False)
    ]

    # Call the get_all_songs function
    meals = get_leaderboard("win_pct")

    # Ensure the results match the expected output
    expected_result = [
        {"id": 1, "meal": "Meal A", "cuisine": "Cuisine A", "price": 20.20, "difficulty": "MED", "battles": 5, "wins": 2, "win_pct": 40.0},
        {"id": 2, "meal": "Meal B", "cuisine": "Cuisine B", "price": 20.21, "difficulty": "MED", "battles": 2, "wins": 2, "win_pct": 100},
        {"id": 3, "meal": "Meal C", "cuisine": "Cuisine C", "price": 20.22, "difficulty": "MED", "battles": 4, "wins": 1, "win_pct": 25.0}
    ]

    assert meals == expected_result, f"Expected {expected_result}, but got {meals}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY win_pct DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_invalid_sort_by(mock_cursor):
    """Test retrieving all meals that are not marked as deleted from the catalog sorted improperly."""

    # Simulate that there are multiple meals in the database
    mock_cursor.fetchall.return_value = [
        (1, "Meal A", "Cuisine A", 20.20, "MED", 5, 2, 0.4, False),
        (2, "Meal B", "Cuisine B", 20.21, "MED", 2, 2, 1, False),
        (3, "Meal C", "Cuisine C", 20.22, "MED", 4, 1, 0.25, False)
    ]

    # Expect a ValueError when attempting to get leaderboard with invalid sorting method
    with pytest.raises(ValueError, match="Invalid sort_by parameter: losses"):
        get_leaderboard("losses")

def test_update_meal_stats_win(mock_cursor):
    """Test updating the stats of a meal after a win."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = (False,)
    # Call the update_meal_stats function with a sample meal ID
    meal_id = 1
    update_meal_stats(meal_id, "win")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
    UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_loss(mock_cursor):
    """Test updating the stats of a meal after a loss."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = (False,)
    # Call the update_meal_stats function with a sample meal ID
    meal_id = 1
    update_meal_stats(meal_id, "loss")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
    UPDATE meals SET battles = battles + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_invalid_result(mock_cursor):
    """Test updating the stats of a meal with invalid results."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = (False,)
    # Call the update_meal_stats function with a sample meal ID but invalid result
    meal_id = 1
    # Expect a ValueError when attempting to get leaderboard with invalid sorting method
    with pytest.raises(ValueError, match="Invalid result: tie. Expected 'win' or 'loss'."):
        update_meal_stats(meal_id, "tie")

def test_update_meal_stats_invalid_meal_id(mock_cursor):
    """Test updating the stats of a meal with invalid meal_id."""

     # Simulate that no song exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        update_meal_stats(999, "win")

def test_update_meal_stats_deleted(mock_cursor):
    """Test updating the stats of a meal that has been deleted."""

    # Simulate that the meal exists but is deleted (id = 0)
    mock_cursor.fetchone.return_value = (True,)
    # Call the update_meal_stats function with a sample meal ID but invalid result
    meal_id = 1
    # Expect a ValueError when attempting to get leaderboard with invalid sorting method
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(meal_id, "tie")
