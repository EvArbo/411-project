import logging
from typing import Any, List

from meal_max.clients.mongo_client import sessions_collection
from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


def login_user(user_id: int, workout) -> None:
    """
    Load the user's exercises from MongoDB into the WorkoutManager's exercise list.

    Checks if a session document exists for the given `user_id` in MongoDB.
    If it exists, clears any current exercises in `workout` and loads
    the stored exercises from MongoDB into `workout`.

    If no session is found, it creates a new session document for the user
    with an empty excerise list in MongoDB.

    Args:
        user_id (int): The ID of the user whose session is to be loaded.
        workout (WorkoutManager): An instance of `WorkoutManager` where the user's exercises
                                    will be loaded.
    """
    logger.info("Attempting to log in user with ID %d.", user_id)
    session = sessions_collection.find_one({"user_id": user_id})

    if session:
        logger.info("Session found for user ID %d. Loading exercises into WorkoutManager.", user_id)
        workout.clear_workout()
        for exercise in session.get("exercises", []):
            logger.debug("Preparing combatant: %s", exercise)
            workout.add_exercise(exercise)
        logger.info("Combatants successfully loaded for user ID %d.", user_id)
    else:
        logger.info("No session found for user ID %d. Creating a new session with empty combatants list.", user_id)
        sessions_collection.insert_one({"user_id": user_id, "exercises": []})
        logger.info("New session created for user ID %d.", user_id)

def logout_user(user_id: int, workout) -> None:
    """
    Store the current exercises from the WorkoutManager back into MongoDB.

    Retrieves the current exercises from `workout` and attempts to store them in
    the MongoDB session document associated with the given `user_id`. If no session
    document exists for the user, raises a `ValueError`.

    After saving the exercises to MongoDB, the exercise list in `workout` is
    cleared to ensure a fresh state for the next login.

    Args:
        user_id (int): The ID of the user whose session data is to be saved.
        workout (WorkoutManager): An instance of `WorkoutManager` from which the user's
                                    current exercises are retrieved.

    Raises:
        ValueError: If no session document is found for the user in MongoDB.
    """
    logger.info("Attempting to log out user with ID %d.", user_id)
    exercises_data = workout.get_all_exerises()
    logger.debug("Current exercises for user ID %d: %s", user_id, exercises_data)

    result = sessions_collection.update_one(
        {"user_id": user_id},
        {"$set": {"exercises": exercises_data}},
        upsert=False  # Prevents creating a new document if not found
    )

    if result.matched_count == 0:
        logger.error("No session found for user ID %d. Logout failed.", user_id)
        raise ValueError(f"User with ID {user_id} not found for logout.")

    logger.info("Exercises successfully saved for user ID %d. Clearing WorkoutManager exercises.", user_id)
    workout.clear_workout()
    logger.info("WorkoutManager exercises cleared for user ID %d.", user_id)