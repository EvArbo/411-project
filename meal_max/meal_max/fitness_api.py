import requests
from typing import Dict, List

class WgerAPI:
    """
    A class to interact with the Wger API for fetching exercise data.
    """

    BASE_URL = "https://wger.de/api/v2/"

    def __init__(self):
        """
        Initialize the API client with default headers.
        """
        self.headers = {
            "Accept": "application/json",
        }

    def get_exercises(self, muscle_group: str = None) -> List[Dict]:
        """
        Fetch exercises, optionally filtered by muscle group.

        Args:
            muscle_group (str): The target muscle group (e.g., 'cardio', 'strength')

        Returns:
            List[Dict]: List of exercises

        Raises:
            ValueError: If the API response is invalid
        """
        url = f"{self.BASE_URL}exercise/"
        params = {}
        if muscle_group:
            params["category"] = muscle_group

        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            raise ValueError(f"Error fetching exercises: {response.status_code}")

        data = response.json()
        return data.get("results", [])

    def search_exercises(self, query: str) -> List[Dict]:
        """
        Search for exercises by name.

        Args:
            query (str): The search keyword

        Returns:
            List[Dict]: List of matching exercises

        Raises:
            ValueError: If the API response is invalid
        """
        url = f"{self.BASE_URL}exercise/"
        params = {"name": query}

        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            raise ValueError(f"Error searching exercises: {response.status_code}")

        data = response.json()
        return data.get("results", [])
