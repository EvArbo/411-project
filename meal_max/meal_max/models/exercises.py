from dataclasses import dataclass
from datetime import datetime
import logging
import os
import sqlite3

from utils.logger import configure_logger
from utils.sql_utils import get_db_connection

# Configure logger
logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Exercise:
    id: int
    name: str
    weight: float
    repetitions: int
    rpe: float

    def __post_init__(self):
        if self.weight < 0:
            raise ValueError(f"Weight must be non-negative, got {self.weight}")
        if self.repetitions < 1:
            raise ValueError(f"Repetitions must be at least 1, got {self.repetitions}")
        if not (0 <= self.rpe <= 10):
            raise ValueError(f"RPE must be between 0 and 10, got {self.rpe}")


def create_exercise(name: str, weight: float, repetitions: int, rpe: float) -> None:
    """
    Creates a new exercise in the workout logs table.

    Args:
        name (str): Name of the exercise.
        weight (float): Weight used in the exercise.
        repetitions (int): Number of repetitions performed.
        rpe (float): Rating of Perceived Exertion (0-10 scale).

    Raises:
        ValueError: If any field is invalid.
        sqlite3.IntegrityError: If an exercise with the same compound key already exists.
        sqlite3.Error: For any other database errors.
    """
    if weight < 0:
        raise ValueError(f"Invalid weight: {weight} (must be non-negative).")
    if repetitions < 1:
        raise ValueError(f"Invalid repetitions: {repetitions} (must be at least 1).")
    if not (0 <= rpe <= 10):
        raise ValueError(f"Invalid RPE: {rpe} (must be between 0 and 10).")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workout_logs (name, weight, repetitions, rpe)
                VALUES (?, ?, ?, ?)
            """, (name, weight, repetitions, rpe))
            conn.commit()

            logger.info("Exercise created successfully: %s", name)

    except sqlite3.IntegrityError as e:
        logger.error("Exercise with name '%s' already exists.", name)
        raise ValueError(f"Exercise with name '{name}' already exists.") from e
    except sqlite3.Error as e:
        logger.error("Database error while creating exercise: %s", str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")


def delete_exercise(exercise_id: int) -> None:
    """
    Deletes an exercise from the catalog by its ID.

    Args:
        exercise_id (int): The ID of the exercise to delete.

    Raises:
        ValueError: If the exercise with the given ID does not exist.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the exercise exists
            cursor.execute("SELECT id FROM workout_logs WHERE id = ?", (exercise_id,))
            if not cursor.fetchone():
                raise ValueError(f"Exercise with ID {exercise_id} not found")

            # Perform the delete
            cursor.execute("DELETE FROM workout_logs WHERE id = ?", (exercise_id,))
            conn.commit()

            logger.info("Exercise with ID %s deleted.", exercise_id)

    except sqlite3.Error as e:
        logger.error("Database error while deleting exercise: %s", str(e))
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
                SELECT id, name, weight, repetitions, rpe
                FROM workout_logs
                WHERE id = ?
            """, (exercise_id,))
            row = cursor.fetchone()

            if row:
                return Exercise(id=row[0], name=row[1], weight=row[2], repetitions=row[3], rpe=row[4])
            else:
                raise ValueError(f"Exercise with ID {exercise_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving exercise by ID: %s", str(e))
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
                SELECT id, name, weight, repetitions, rpe
                FROM workout_logs
            """)
            rows = cursor.fetchall()

            return [Exercise(id=row[0], name=row[1], weight=row[2], repetitions=row[3], rpe=row[4]) for row in rows]

    except sqlite3.Error as e:
        logger.error("Database error while retrieving all exercises: %s", str(e))
        raise e


def update_exercise(exercise_id: int, weight: float = None, repetitions: int = None, rpe: float = None) -> None:
    """
    Updates the weight, repetitions, or RPE of an exercise.

    Args:
        exercise_id (int): The ID of the exercise to update.
        weight (float): The new weight (optional).
        repetitions (int): The new repetitions (optional).
        rpe (float): The new RPE (optional).

    Raises:
        ValueError: If the exercise does not exist or any value is invalid.
        sqlite3.Error: If any database error occurs.
    """
    try:
        if weight is not None and weight < 0:
            raise ValueError(f"Invalid weight: {weight} (must be non-negative).")
        if repetitions is not None and repetitions < 1:
            raise ValueError(f"Invalid repetitions: {repetitions} (must be at least 1).")
        if rpe is not None and not (0 <= rpe <= 10):
            raise ValueError(f"Invalid RPE: {rpe} (must be between 0 and 10).")

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the exercise exists
            cursor.execute("SELECT id FROM workout_logs WHERE id = ?", (exercise_id,))
            if not cursor.fetchone():
                raise ValueError(f"Exercise with ID {exercise_id} not found")

            # Update fields dynamically
            update_fields = []
            update_values = []

            if weight is not None:
                update_fields.append("weight = ?")
                update_values.append(weight)
            if repetitions is not None:
                update_fields.append("repetitions = ?")
                update_values.append(repetitions)
            if rpe is not None:
                update_fields.append("rpe = ?")
                update_values.append(rpe)

            update_values.append(exercise_id)

            query = f"UPDATE exercises SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, update_values)
            conn.commit()

            logger.info("Exercise with ID %s updated.", exercise_id)

    except sqlite3.Error as e:
        logger.error("Database error while updating exercise: %s", str(e))
        raise e
