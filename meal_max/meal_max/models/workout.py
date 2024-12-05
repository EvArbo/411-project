import requests
from typing import List, Dict, Optional
from meal_max.models.exercises import Exercise
import logging
from meal_max.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class WorkoutManager:
    """
    A class to manage a workout consisting of multiple exercises, with Wger API integration.

    Attributes:
        exercises (List[Exercise]): The list of exercises in the workout.
        wger_api_base_url (str): Base URL for the Wger API.
        wger_api_key (str): API key for the Wger API.
    """

    def __init__(self, wger_api_key: str):
        """
        Initializes the WorkoutModel with an empty list of exercises and Wger API credentials.

        Args:
            wger_api_key (str): API key for accessing the Wger API.
        """
        self.exercises: List[Exercise] = []
        self.wger_api_base_url = "https://wger.de/api/v2/"
        self.wger_api_key = wger_api_key

    ##################################################
    # Wger API Integration Functions
    ##################################################
    def fetch_exercise_categories(self) -> List[Dict]:  
        """
        Fetches exercise categories from the Wger API.

        Returns:
            List[Dict]: A list of exercise categories.
        """
        logger.info("Fetching exercise categories from Wger API")
        endpoint = f"{self.wger_api_base_url}exercisecategory/"
        headers = {"Authorization": f"Token {self.wger_api_key}"}

        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            exercises = response.json().get("results", [])
            logger.info("Successfully fetched %d exercise categories", len(exercises))
            return exercises
        except requests.RequestException as e:
            logger.error("Failed to fetch exercise categories from Wger API: %s", e)
            return []
    
    def fetch_muscles(self) -> List[Dict]:
        """
        Fetches muscle groups from the Wger API.

        Returns:
            List[Dict]: A list of muscle groups.
        """
        logger.info("Fetching muscle groups from Wger API")
        endpoint = f"{self.wger_api_base_url}muscle/"
        headers = {"Authorization": f"Token {self.wger_api_key}"}

        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            muscles = response.json().get("results", [])
            logger.info("Successfully fetched %d muscle groups", len(muscles))
            return muscles
        except requests.RequestException as e:
            logger.error("Failed to fetch muscle groups from Wger API: %s", e)
            return []
        
    def fetch_exercises(self, muscle_id: Optional[int] = None) -> List[Dict]:
        """
        Fetches exercises from the Wger API. Optionally filters by muscle group.

        Args:
            muscle_id (Optional[int]): ID of the muscle group to filter exercises. Defaults to None.

        Returns:
            List[Dict]: A list of exercises with their details.
        """
        logger.info("Fetching exercises from Wger API")
        endpoint = f"{self.wger_api_base_url}exercise/"
        params = {"language": 2}  # English language
        if muscle_id:
            params["muscles"] = muscle_id

        headers = {"Authorization": f"Token {self.wger_api_key}"}

        try:
            response = requests.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            exercises = response.json().get("results", [])
            logger.info("Successfully fetched %d exercises", len(exercises))
            return exercises
        except requests.RequestException as e:
            logger.error("Failed to fetch exercises from Wger API: %s", e)
            return []

    def fetch_equipment(self) -> List[Dict]:
        """
        Fetches equipment from the Wger API.

        Returns:
            List[Dict]: A list of equipment with their details.
        """
        logger.info("Fetching equipment from Wger API")
        endpoint = f"{self.wger_api_base_url}equipment/"
        
        headers = {"Authorization": f"Token {self.wger_api_key}"}

        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            equipment = response.json().get("results", [])
            logger.info("Successfully fetched %d equipment items", len(equipment))
            return equipment
        except requests.RequestException as e:
            logger.error("Failed to fetch equipment from Wger API: %s", e)
            return []



    ##################################################
    # Exercise Management Functions
    ##################################################

    def add_exercise(self, exercise: Exercise) -> None:
        """
        Adds an exercise to the workout.

        Args:
            exercise (Exercise): The exercise to add.

        Raises:
            TypeError: If the input is not a valid Exercise instance.
            ValueError: If an exercise with the same ID already exists.
        """
        logger.info("Adding exercise to workout")
        if not isinstance(exercise, Exercise):
            logger.error("Input is not a valid Exercise instance")
            raise TypeError("Input is not a valid Exercise instance")

        if exercise.id in [existing_exercise.id for existing_exercise in self.exercises]:
            logger.error("Exercise with ID %d already exists in the workout", exercise.id)
            raise ValueError(f"Exercise with ID {exercise.id} already exists in the workout")

        self.exercises.append(exercise)
        logger.info("Exercise added: %s", exercise.name)

    def remove_exercise(self, exercise_id: int) -> None:
        """
        Removes an exercise from the workout by its ID.

        Args:
            exercise_id (int): The ID of the exercise to remove.

        Raises:
            ValueError: If the exercise is not found.
        """
        logger.info("Removing exercise with ID %d from workout", exercise_id)
        exercise = next((ex for ex in self.exercises if ex.id == exercise_id), None)

        if exercise is None:
            logger.error("Exercise with ID %d not found in the workout", exercise_id)
            raise ValueError(f"Exercise with ID {exercise_id} not found in the workout")

        self.exercises.remove(exercise)
        logger.info("Exercise removed: %s", exercise.name)

    def clear_workout(self) -> None:
        """
        Clears all exercises from the workout.
        """
        logger.info("Clearing all exercises from the workout")
        self.exercises.clear()
        logger.info("Workout cleared")

    ##################################################
    # Workout Retrieval Functions
    ##################################################

    def get_all_exercises(self) -> List[Exercise]:
        """
        Retrieves all exercises in the workout.

        Returns:
            List[Exercise]: A list of all exercises.
        """
        logger.info("Retrieving all exercises in the workout")
        return self.exercises

    def get_exercise_by_id(self, exercise_id: int) -> Exercise:
        """
        Retrieves an exercise by its ID.

        Args:
            exercise_id (int): The ID of the exercise to retrieve.

        Returns:
            Exercise: The exercise with the specified ID.

        Raises:
            ValueError: If the exercise is not found.
        """
        logger.info("Retrieving exercise with ID %d", exercise_id)
        exercise = next((ex for ex in self.exercises if ex.id == exercise_id), None)

        if exercise is None:
            logger.error("Exercise with ID %d not found", exercise_id)
            raise ValueError(f"Exercise with ID {exercise_id} not found")

        return exercise

    def get_exercise_by_name(self, exercise_name: str) -> Exercise:
        """
        Retrieves an exercise by its name.

        Args:
            exercise_name (str): The name of the exercise to retrieve.

        Returns:
            Exercise: The exercise with the specified name.

        Raises:
            ValueError: If the exercise is not found.
        """
        logger.info("Retrieving exercise with name %s", exercise_name)
        exercise = next((ex for ex in self.exercises if ex.name.lower() == exercise_name.lower()), None)

        if exercise is None:
            logger.error("Exercise with name %s not found", exercise_name)
            raise ValueError(f"Exercise with name {exercise_name} not found")

        return exercise


    def get_workout_summary(self) -> Dict:
        """
        Summarizes the workout.

        Returns:
            Dict: Summary of the workout, including the total number of exercises and the total weight lifted.
        """
        logger.info("Generating workout summary")
        total_exercises = len(self.exercises)
        total_weight = sum(exercise.weight for exercise in self.exercises)

        summary = {
            "Exercises in the workout": total_exercises,
            "Total Volume of Workout": total_weight,
        }
        logger.info("Workout summary: %s", summary)
        return summary
