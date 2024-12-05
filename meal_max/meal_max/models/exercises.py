from dataclasses import dataclass
from datetime import datetime
import logging
import os
import sqlite3

from meal_max.utils.logger import configure_logger
from meal_max.utils.sql_utils import get_db_connection

# Configure logger
logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Exercise:
    id: int
    name: str
    weight: float
    sets: int
    repetitions: int
    rpe: float

    def __post_init__(self):
        if self.weight < 0:
            raise ValueError(f"Weight must be non-negative, got {self.weight}")
        if self.repetitions < 0:
            raise ValueError(f"Repetitions must be at least 1, got {self.repetitions}")
        if self.sets < 0:
            raise ValueError(f"Sets must be at least 1, got {self.sets}")
        if not (0 <= self.rpe <= 10):
            raise ValueError(f"RPE must be between 0 and 10, got {self.rpe}")
        


def create_exercise(name: str, weight: float, sets: int, repetitions: int, rpe: float) -> None:
    """
    Creates a new exercise in the workout logs table.

    Args:
        name (str): Name of the exercise.
        weight (float): Weight used in the exercise.
        sets (int): Number of sets performed.
        repetitions (int): Number of repetitions performed.
        rpe (float): Rating of Perceived Exertion (0-10 scale).

    Raises:
        ValueError: If any field is invalid.
        sqlite3.IntegrityError: If an exercise with the same compound key already exists.
        sqlite3.Error: For any other database errors.
    """
    if not isinstance(name, str):
        raise ValueError(f"Invalid name: {name} (must be a string).")
    if weight < 0:
        raise ValueError(f"Invalid weight: {weight} (must be non-negative).")
    if not isinstance(sets, int) or sets < 1:
        raise ValueError(f"Invalid number of sets: {sets} (must be at least 1 and an integer).")
    if not isinstance(repetitions, int) or repetitions < 0:
        raise ValueError(f"Invalid number of repetitions: {repetitions} (must be at least 0 and an integer).")
    if not (0 <= rpe <= 10):
        raise ValueError(f"Invalid RPE: {rpe} (must be a float between 0 and 10).")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workout_log (name, weight, sets, repetitions, rpe)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, sets, repetitions, rpe))
            conn.commit()

            logger.info("Exercise created successfully: %s", name)
    except sqlite3.Error as e:
        logger.error("Database error while creating exercise: %s", str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")


    
def delete_exercise(exercise_id: int) -> None:
    """
    Deletes an exercise from the catalog by its ID (soft delete by setting deleted to TRUE).

    Args:
        exercise_id (int): The ID of the exercise to delete.

    Raises:
        ValueError: If the exercise with the given ID does not exist or is already deleted.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the exercise exists and is already deleted
            cursor.execute("SELECT deleted FROM workout_log WHERE id = ?", (exercise_id,))
            result = cursor.fetchone()

            if not result:
                raise ValueError(f"Exercise with ID {exercise_id} not found")
            if result[0]:  # If `deleted` is True
                raise ValueError(f"Exercise with ID {exercise_id} has already been deleted")

            # Perform the soft delete
            cursor.execute("UPDATE workout_log SET deleted = TRUE WHERE id = ?", (exercise_id,))
            conn.commit()

            logger.info("Exercise with ID %s marked as deleted.", exercise_id)

    except sqlite3.Error as e:
        logger.error("Database error while deleting exercise: %s", str(e))
        raise e


def get_all_exercises() -> list[Exercise]:
    """
    Retrieves all exercises from the catalog.

    Returns:
        list[Exercise]: A list of all Exercise objects.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, sets, repetitions, rpe
                FROM workout_log
                WHERE deleted = FALSE

            """)
            rows = cursor.fetchall()
            exercises = [
                {
                    "id": row[0],
                    "name": row[1],
                    "weight": row[2],
                    "sets": row[3],
                    "repetitions": row[4],
                    "rpe": row[5],
                }
                for row in rows
            ]
            return exercises

    except sqlite3.Error as e:
        logger.error("Database error while retrieving all exercises: %s", str(e))
        raise e
    
    
def get_exercise_by_id(exercise_id: int) -> Exercise:
    """
    Retrieves an exercise by its ID.

    Args:
        exercise_id (int): The ID of the exercise to retrieve.

    Returns:
        Exercise: The Exercise object.

    Raises:
        ValueError: If the exercise is not found.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, sets, repetitions, rpe
                FROM workout_log
                WHERE id = ?
            """, (exercise_id,))
            row = cursor.fetchone()

            if row:
                return Exercise(id=row[0], name=row[1], weight = row[2], sets=row[3], repetitions=row[4], rpe=row[5])
            else:
                raise ValueError(f"Exercise with ID {exercise_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving exercise by ID: %s", str(e))
        raise e


