import pytest
from unittest.mock import patch, MagicMock
from meal_max.models.fitness_tracker_model import WorkoutManager


# Fixture to initialize the WorkoutManager
@pytest.fixture
def workout_manager():
    return WorkoutManager(wger_api_key="fake_api_key")


@pytest.fixture
def headers(workout_manager):
    return {"Authorization": f"Token {workout_manager.wger_api_key}"}


def test_create_workout_session_success(workout_manager, headers):
    session_data = {
        "workout": 1,
        "date": "2024-12-08",
        "notes": "Test session",
        "impression": "3",
        "time_start": "10:00:00",
        "time_end": "11:00:00",
    }

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 123, **session_data}

    with patch("requests.post", return_value=mock_response) as mock_post:
        result = workout_manager.create_workout_session(session_data)

        assert result["id"] == 123
        assert result["notes"] == "Test session"
        mock_post.assert_called_once_with(
            f"{workout_manager.wger_api_base_url}workoutsession/",
            json=session_data,
            headers=headers,
        )


def test_retrieve_workout_session_success(workout_manager, headers):
    session_id = 123
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": session_id,
        "workout": 1,
        "date": "2024-12-08",
        "notes": "Retrieved session",
        "impression": "2",
        "time_start": "10:00:00",
        "time_end": "11:00:00",
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = workout_manager.retrieve_workout_session(session_id)

        assert result["id"] == session_id
        assert result["notes"] == "Retrieved session"
        mock_get.assert_called_once_with(
            f"{workout_manager.wger_api_base_url}workoutsession/{session_id}/",
            headers=headers,
        )


def test_update_workout_session_success(workout_manager, headers):
    session_id = 123
    updated_data = {
        "workout": 1,
        "date": "2024-12-08",
        "notes": "Updated session notes",
        "impression": "3",
        "time_start": "10:30:00",
        "time_end": "11:30:00",
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {**updated_data, "id": session_id}

    with patch("requests.put", return_value=mock_response) as mock_put:
        result = workout_manager.update_workout_session(session_id, updated_data)

        assert result["id"] == session_id
        assert result["notes"] == "Updated session notes"
        mock_put.assert_called_once_with(
            f"{workout_manager.wger_api_base_url}workoutsession/{session_id}/",
            json=updated_data,
            headers=headers,
        )


def test_delete_workout_session_success(workout_manager, headers):
    session_id = 123
    mock_response = MagicMock()
    mock_response.status_code = 204

    with patch("requests.delete", return_value=mock_response) as mock_delete:
        result = workout_manager.delete_workout_session(session_id)

        assert result is True
        mock_delete.assert_called_once_with(
            f"{workout_manager.wger_api_base_url}workoutsession/{session_id}/",
            headers=headers,
        )


def test_list_workout_sessions_success(workout_manager, headers):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "id": 1,
                "workout": 1,
                "date": "2024-12-08",
                "notes": "First session",
                "impression": "2",
                "time_start": "09:00:00",
                "time_end": "10:00:00",
            },
            {
                "id": 2,
                "workout": 2,
                "date": "2024-12-09",
                "notes": "Second session",
                "impression": "3",
                "time_start": "10:00:00",
                "time_end": "11:00:00",
            },
        ]
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = workout_manager.list_workout_sessions()

        assert len(result) == 2
        assert result[0]["notes"] == "First session"
        assert result[1]["notes"] == "Second session"
        mock_get.assert_called_once_with(
            f"{workout_manager.wger_api_base_url}workoutsession/",
            headers=headers,
        )


@pytest.mark.parametrize(
    "status_code, expected_result",
    [
        (400, False),
        (404, False),
        (500, False),
    ],
)
def test_delete_workout_session_failure(workout_manager, headers, status_code, expected_result):
    session_id = 123
    mock_response = MagicMock()
    mock_response.status_code = status_code

    with patch("requests.delete", return_value=mock_response) as mock_delete:
        result = workout_manager.delete_workout_session(session_id)

        assert result is expected_result
        mock_delete.assert_called_once_with(
            f"{workout_manager.wger_api_base_url}workoutsession/{session_id}/",
            headers=headers,
        )
