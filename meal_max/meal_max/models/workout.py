import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fitness_tracker.api.fitness_api import WgerAPI
from fitness_tracker.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class WorkoutManager:
    """
    Manages workout sessions and provides exercise recommendations.

    Attributes:
        api (WgerAPI): Instance of WgerAPI to fetch exercise data.
        workout_logs (List[Dict]): A list of dictionaries logging workout sessions.
    """

    def __init__(self):
        """
        Initialize the WorkoutManager with a WgerAPI instance and an empty list for workout logs.
        """
        self.api = WgerAPI()
        self.workout_logs = []
        logger.info("WorkoutManager initialized successfully.")

    def get_recommendations(self, goal_type: str) -> List[Dict]:
        """
        Fetch recommended exercises based on a user's fitness goal.

        Args:
            goal_type (str): The type of goal (e.g., "weight_loss", "muscle_gain").

        Returns:
            List[Dict]: A list of dictionaries containing exercise details.

        Raises:
            ValueError: If the goal_type is invalid.
        """
        logger.info("Fetching recommendations for goal type: %s", goal_type)

        if goal_type == "weight_loss":
            exercises = self.api.get_exercises(muscle_group="cardio")
        elif goal_type == "muscle_gain":
            exercises = self.api.get_exercises(muscle_group="strength")
        else:
            logger.warning("Invalid goal type provided: %s. Defaulting to general exercises.", goal_type)
            exercises = self.api.get_exercises()

        logger.info("Retrieved %d recommended exercises.", len(exercises))
        return exercises

    def log_workout(self, exercise_name: str, duration: int, intensity: str, notes: Optional[str] = None) -> str:
        """
        Record a workout session with relevant details.

        Args:
            exercise_name (str): The name of the exercise performed.
            duration (int): The duration of the workout in minutes.
            intensity (str): The intensity level of the workout ("low", "medium", "high").
            notes (Optional[str]): Additional notes about the session (e.g., feedback, conditions).

        Returns:
            str: A unique log ID for the recorded workout session.

        Raises:
            ValueError: If `exercise_name` is empty or `duration` is not positive.
        """
        if not exercise_name:
            error_msg = "Exercise name cannot be empty."
            logger.error(error_msg)
            raise ValueError(error_msg)

        if duration <= 0:
            error_msg = "Duration must be a positive value."
            logger.error(error_msg)
            raise ValueError(error_msg)

        log_id = f"workout_{len(self.workout_logs) + 1}"
        workout_data = {
            "id": log_id,
            "date": datetime.now(),
            "exercise": exercise_name,
            "duration": duration,
            "intensity": intensity,
            "notes": notes
        }

        self.workout_logs.append(workout_data)
        logger.info("Logged workout - ID: %s, Exercise: %s, Duration: %d minutes.", log_id, exercise_name, duration)
        return log_id

    def get_workout_history(self, days: Optional[int] = None) -> List[Dict]:
        """
        Retrieve the history of logged workouts, optionally filtered by a time period.

        Args:
            days (Optional[int]): The number of past days to filter the workout logs. If None, returns all logs.

        Returns:
            List[Dict]: A list of dictionaries representing the filtered workout logs.
        """
        if days is None:
            logger.info("Returning complete workout history.")
            return self.workout_logs

        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_logs = [log for log in self.workout_logs if log["date"] >= cutoff_date]

        logger.info("Retrieved %d workout logs from the past %d days.", len(filtered_logs), days)
        return filtered_logs

    def calculate_workout_stats(self) -> Dict:
        """
        Calculate and summarize workout statistics from logged sessions.

        Returns:
            Dict: A dictionary containing workout statistics, including total sessions, total duration,
                  average duration, and breakdown by intensity levels.
        """
        if not self.workout_logs:
            logger.info("No workout logs available. Returning empty statistics.")
            return {"total_workouts": 0}

        total_duration = sum(log["duration"] for log in self.workout_logs)
        stats = {
            "total_workouts": len(self.workout_logs),
            "total_duration": total_duration,
            "avg_duration": total_duration / len(self.workout_logs),
            "workouts_by_intensity": {
                "low": len([log for log in self.workout_logs if log["intensity"] == "low"]),
                "medium": len([log for log in self.workout_logs if log["intensity"] == "medium"]),
                "high": len([log for log in self.workout_logs if log["intensity"] == "high"])
            }
        }

        logger.info("Calculated workout statistics: %s", stats)
        return stats

    def get_exercise_details(self, exercise_name: str) -> Dict:
        """
        Retrieve detailed information for a specific exercise.

        Args:
            exercise_name (str): The name of the exercise to look up.

        Returns:
            Dict: A dictionary containing details of the exercise.

        Raises:
            ValueError: If the exercise is not found in the API.
        """
        logger.info("Searching for details of exercise: %s", exercise_name)
        exercises = self.api.search_exercises(exercise_name)

        if not exercises:
            error_msg = f"Exercise '{exercise_name}' not found in the database."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Successfully retrieved exercise details: %s", exercise_name)
        return exercises[0]
