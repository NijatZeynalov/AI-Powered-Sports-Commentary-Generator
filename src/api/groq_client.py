from typing import Dict, Optional
import requests
import json
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GroqClient:
    """Handles interaction with Groq API for generating commentary."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()

    def generate_commentary(
            self,
            game_stats: Dict,
            style: str = "excited",
            max_tokens: int = 150
    ) -> Optional[str]:
        """
        Generate commentary based on game statistics.

        Args:
            game_stats: Dictionary containing game statistics
            style: Commentary style (excited, neutral, analytical)
            max_tokens: Maximum length of generated commentary

        Returns:
            Generated commentary text or None if generation fails
        """
        endpoint = f"{self.base_url}/chat/completions"

        # Create a prompt based on game statistics and desired style
        prompt = self._create_commentary_prompt(game_stats, style)

        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an experienced sports commentator known for engaging and accurate commentary."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        try:
            response = self.session.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating commentary: {str(e)}")
            return None

    def _create_commentary_prompt(self, game_stats: Dict, style: str) -> str:
        """Create a structured prompt for the commentary generation."""
        # Format game stats into a natural language prompt
        game_situation = (
            f"Game situation: {game_stats['game_time']} remaining, "
            f"Score: {game_stats['home_team']} {game_stats['home_score']} - "
            f"{game_stats['away_team']} {game_stats['away_score']}"
        )

        recent_plays = "Recent plays: " + " ".join(
            play["description"] for play in game_stats.get("recent_plays", [])[:3]
        )

        style_instructions = {
            "excited": "Provide energetic and enthusiastic commentary about this moment",
            "neutral": "Provide balanced and objective commentary about the current situation",
            "analytical": "Analyze the strategic implications of the current game situation"
        }

        return f"{game_situation}\n{recent_plays}\n\n{style_instructions[style]}"