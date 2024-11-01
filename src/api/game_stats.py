from typing import Dict, List, Optional
import requests
from datetime import datetime
import json
from ..utils.logger import get_logger
from ..utils.validators import validate_response

logger = get_logger(__name__)


class GameStatsAPI:
    """Handles interaction with sports data API to fetch real-time game statistics."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.sportsdataservice.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()

    def get_live_games(self) -> List[Dict]:
        """Fetch all currently live games."""
        endpoint = f"{self.base_url}/games/live"

        try:
            response = self.session.get(endpoint, headers=self.headers)
            validate_response(response)
            return response.json()["games"]
        except Exception as e:
            logger.error(f"Error fetching live games: {str(e)}")
            return []

    def get_game_stats(self, game_id: str) -> Optional[Dict]:
        """Fetch detailed statistics for a specific game."""
        endpoint = f"{self.base_url}/games/{game_id}/stats"

        try:
            response = self.session.get(endpoint, headers=self.headers)
            validate_response(response)
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching game stats for game {game_id}: {str(e)}")
            return None

    def get_play_by_play(self, game_id: str, last_sequence: int = 0) -> List[Dict]:
        """Fetch play-by-play data for a specific game since the last sequence number."""
        endpoint = f"{self.base_url}/games/{game_id}/plays"
        params = {"since_sequence": last_sequence}

        try:
            response = self.session.get(endpoint, headers=self.headers, params=params)
            validate_response(response)
            return response.json()["plays"]
        except Exception as e:
            logger.error(f"Error fetching play-by-play for game {game_id}: {str(e)}")
            return []

    def get_team_stats(self, game_id: str) -> Dict:
        """Fetch team-specific statistics for a game."""
        endpoint = f"{self.base_url}/games/{game_id}/team-stats"

        try:
            response = self.session.get(endpoint, headers=self.headers)
            validate_response(response)
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching team stats for game {game_id}: {str(e)}")
            return {}