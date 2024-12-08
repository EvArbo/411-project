import requests
from typing import List, Dict, Optional
from meal_max.models.exercises import Exercise
import logging
from meal_max.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)
import os
from dotenv import load_dotenv
load_dotenv()
class WorkoutManager:
    """
    A class to manage a workout consisting of multiple exercises, with Wger API integration.

    Attributes:
        exercises (List[Exercise]): The list of exercises in the workout.
        wger_api_base_url (str): Base URL for the Wger API.
        wger_api_key (str): API key for the Wger API.
    """

    def __init__(self, wger_api_key):
        """
        Initializes the WorkoutModel with an empty list of exercises and Wger API credentials.

        Args:
            wger_api_key (str): API key for accessing the Wger API.
        """
        self.exercises: List[Exercise] = []
        self.wger_api_base_url = "https://wger.de/api/v2/"
        self.wger_api_key = os.getenv("WGER_API_KEY")

    ##################################################
    # Wger API Integration Functions
    ##################################################
    def create_workout_session(self, session_data: Dict) -> Optional[Dict]:
        """
        Creates a new workout session using the workoutsession_create API call.

        Args:
            session_data (Dict): Data for the workout session, including workout ID, date, notes, impression, start and end times.

        Returns:
            Dict: The created workout session data or None if the o                                                                                                                                                                             peration failed.
        """
        endpoint = f"{self.wger_api_base_url}workoutsession/"
        headers = {"Authorization": f"Token {self.wger_api_key}"}

        try:
            response = requests.post(endpoint, json=session_data, headers=headers)
            response.raise_for_status()
            logger.info("Workout session created successfully")
            return response.json()
        except requests.RequestException as e:
            logger.error("Failed to create workout session: %s", e)
            return None

    def retrieve_workout_session(self, session_id: int) -> Optional[Dict]:
        """
        Retrieves a workout session by ID using the workoutsession_retrieve API call.

        Args:
            session_id (int): ID of the workout session to retrieve.

        Returns:
            Dict: The workout session data or None if not found.
        """
        endpoint = f"{self.wger_api_base_url}workoutsession/{session_id}/"
        headers = {"Authorization": f"Token {self.wger_api_key}"}

        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            logger.info("Workout session retrieved successfully")
            return response.json()
        except requests.RequestException as e:
            logger.error("Failed to retrieve workout session: %s", e)
            return None

    def update_workout_session(self, session_id: int, updated_data: Dict) -> Optional[Dict]:
        """
        Updates a workout session using the workoutsession_update API call.

        Args:
            session_id (int): ID of the workout session to update.
            updated_data (Dict): Updated session data.

        Returns:
            Dict: The updated workout session data or None if the operation failed.
        """
        endpoint = f"{self.wger_api_base_url}workoutsession/{session_id}/"
        headers = {"Authorization": f"Token {self.wger_api_key}"}

        try:
            response = requests.put(endpoint, json=updated_data, headers=headers)
            response.raise_for_status()
            logger.info("Workout session updated successfully")
            return response.json()
        except requests.RequestException as e:
            logger.error("Failed to update workout session: %s", e)
            return None

    def delete_workout_session(self, session_id: int) -> bool:
        """
        Deletes a workout session by ID using the workoutsession_destroy API call.

        Args:
            session_id (int): ID of the workout session to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        endpoint = f"{self.wger_api_base_url}workoutsession/{session_id}/"
        headers = {"Authorization": f"Token {self.wger_api_key}"}

        try:
            response = requests.delete(endpoint, headers=headers)
            response.raise_for_status()
            logger.info("Workout session deleted successfully")
            return True
        except requests.RequestException as e:
            logger.error("Failed to delete workout session: %s", e)
            return False

    def list_workout_sessions(self) -> List[Dict]:
        """
        Lists all workout sessions using the workoutsession_list API call.

        Returns:
            List[Dict]: A list of all workout sessions or an empty list if none found.
        """
        endpoint = f"{self.wger_api_base_url}workoutsession/"
        headers = {"Authorization": f"Token {self.wger_api_key}"}

        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            sessions = response.json().get("results", [])
            logger.info("Successfully retrieved %d workout sessions", len(sessions))
            return sessions
        except requests.RequestException as e:
            logger.error("Failed to list workout sessions: %s", e)
            return []
    