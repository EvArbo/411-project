import logging
from datetime import datetime
from typing import Dict, List, Optional

from meal_max.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class GoalsManager:
    """
    Manages fitness and nutritional goals for users, including setting, updating, 
    and tracking progress.

    Attributes:
        goals (Dict[str, Dict]): Stores all goals with unique IDs as keys. Each goal includes
                                details such as type, target, deadline, and progress.
        active_goals (Dict[str, Dict]): Tracks only the currently active goals.
    """

    def __init__(self):
        """
        Initialize the GoalsManager with empty dictionaries for goals and active goals.
        """
        self.goals = {}
        self.active_goals = {}
        logger.info("GoalsManager initialized")

    def set_goal(self, goal_type: str, target_value: float, deadline: datetime) -> str:
        """
        Create a new goal with specified type, target value, and deadline.

        Args:
            goal_type (str): The category of the goal (e.g., "weight_loss", "muscle_gain", "calorie_intake").
            target_value (float): The numeric target value the user aims to achieve.
            deadline (datetime): The date and time by which the goal should be achieved.

        Returns:
            str: A unique identifier (ID) for the newly created goal.

        Raises:
            ValueError: If the target value is negative or the deadline is in the past.
        """
        if target_value < 0:
            error_msg = "Target value cannot be negative."
            logger.error(error_msg)
            raise ValueError(error_msg)

        if deadline < datetime.now():
            error_msg = "Deadline cannot be in the past."
            logger.error(error_msg)
            raise ValueError(error_msg)

        goal_id = f"goal_{len(self.goals) + 1}"
        goal_data = {
            "type": goal_type,
            "target": target_value,
            "deadline": deadline,
            "current_value": 0,
            "created_at": datetime.now(),
            "status": "active"
        }

        self.goals[goal_id] = goal_data
        self.active_goals[goal_id] = goal_data
        
        logger.info("New goal set - ID: %s, Type: %s, Target: %.2f",
                    goal_id, goal_type, target_value)
        return goal_id

    def view_goals(self) -> Dict[str, Dict]:
        """
        Retrieve all goals with their details.

        Returns:
            Dict[str, Dict]: A dictionary of all goals, each identified by a unique ID.
        """
        logger.info("Retrieving all goals")
        return self.goals

    def update_goal(self, goal_id: str, new_target: Optional[float] = None,
                    new_deadline: Optional[datetime] = None) -> None:
        """
        Modify the target value or deadline of an existing goal.

        Args:
            goal_id (str): The unique ID of the goal to update.
            new_target (Optional[float]): The new target value for the goal (if updating).
            new_deadline (Optional[datetime]): The new deadline for the goal (if updating).

        Raises:
            ValueError: If the goal ID is not found or invalid parameters are provided.
        """
        if goal_id not in self.goals:
            error_msg = f"Goal ID {goal_id} not found."
            logger.error(error_msg)
            raise ValueError(error_msg)

        if new_target is not None:
            self.goals[goal_id]["target"] = new_target
            logger.info("Updated target for goal %s: %.2f", goal_id, new_target)

        if new_deadline is not None:
            self.goals[goal_id]["deadline"] = new_deadline
            logger.info("Updated deadline for goal %s: %s", goal_id, new_deadline)

    def track_progress(self, goal_id: str) -> Dict:
        """
        Provide detailed progress information for a specific goal.

        Args:
            goal_id (str): The unique ID of the goal to track.

        Returns:
            Dict: A dictionary containing the progress details, such as target, 
                  current value, percentage progress, and days remaining.

        Raises:
            ValueError: If the goal ID is not found.
        """
        if goal_id not in self.goals:
            error_msg = f"Goal ID {goal_id} not found."
            logger.error(error_msg)
            raise ValueError(error_msg)

        goal = self.goals[goal_id]
        progress = {
            "goal_type": goal["type"],
            "target": goal["target"],
            "current_value": goal["current_value"],
            "progress_percentage": (goal["current_value"] / goal["target"]) * 100,
            "days_remaining": (goal["deadline"] - datetime.now()).days
        }
        
        logger.info("Retrieved progress for goal %s", goal_id)
        return progress

    def check_goal_status(self, goal_id: str) -> str:
        """
        Determine the current status of a goal (active, completed, or expired).

        Args:
            goal_id (str): The unique ID of the goal.

        Returns:
            str: The status of the goal ("active", "completed", or "expired").

        Raises:
            ValueError: If the goal ID is not found.
        """
        if goal_id not in self.goals:
            error_msg = f"Goal ID {goal_id} not found."
            logger.error(error_msg)
            raise ValueError(error_msg)

        goal = self.goals[goal_id]
        
        if goal["current_value"] >= goal["target"]:
            status = "completed"
        elif datetime.now() > goal["deadline"]:
            status = "expired"
        else:
            status = "active"

        logger.info("Goal %s status: %s", goal_id, status)
        return status

    def update_progress_value(self, goal_id: str, new_value: float) -> None:
        """
        Update the current progress value of a goal.

        Args:
            goal_id (str): The unique ID of the goal to update.
            new_value (float): The updated current value for the goal.

        Raises:
            ValueError: If the goal ID is not found.
        """
        if goal_id not in self.goals:
            error_msg = f"Goal ID {goal_id} not found."
            logger.error(error_msg)
            raise ValueError(error_msg)

        self.goals[goal_id]["current_value"] = new_value
        logger.info("Updated current value for goal %s: %.2f", goal_id, new_value)
