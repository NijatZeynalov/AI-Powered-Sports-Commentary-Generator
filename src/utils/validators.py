import json
from typing import Dict, Any, Union, Optional
import requests
from datetime import datetime
from .logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_response(
        response: requests.Response,
        expected_status: Optional[int] = None
) -> None:
    """
    Validate API response.

    Args:
        response: Response object from requests
        expected_status: Optional specific status code to expect

    Raises:
        ValidationError: If response validation fails
    """
    try:
        if expected_status and response.status_code != expected_status:
            raise ValidationError(
                f"Unexpected status code: {response.status_code}, "
                f"expected: {expected_status}"
            )

        response.raise_for_status()

        # Validate content type
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            try:
                response.json()
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON response: {str(e)}")

    except requests.RequestException as e:
        raise ValidationError(f"Request failed: {str(e)}")


def validate_game_data(data: Dict[str, Any]) -> bool:
    """
    Validate game data structure and content.

    Args:
        data: Game data dictionary to validate

    Returns:
        True if valid, raises ValidationError otherwise
    """
    required_fields = {
        'game_id': str,
        'timestamp': str,
        'home_team': str,
        'away_team': str,
        'home_score': (int, float),
        'away_score': (int, float),
        'period': (int, str),
        'game_time': str
    }

    try:
        # Check required fields and types
        for field, expected_type in required_fields.items():
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

            if not isinstance(data[field], expected_type):
                raise ValidationError(
                    f"Invalid type for {field}: expected {expected_type}, "
                    f"got {type(data[field])}"
                )

        # Validate timestamp format
        try:
            datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValidationError(
                "Invalid timestamp format. Expected: YYYY-MM-DD HH:MM:SS"
            )

        # Validate score values
        if data['home_score'] < 0 or data['away_score'] < 0:
            raise ValidationError("Scores cannot be negative")

        # Validate game time format (MM:SS)
        game_time = data['game_time']
        if ':' not in game_time:
            raise ValidationError("Invalid game time format. Expected: MM:SS")

        minutes, seconds = game_time.split(':')
        if not (minutes.isdigit() and seconds.isdigit()):
            raise ValidationError("Game time must contain valid numbers")

        if int(seconds) >= 60:
            raise ValidationError("Seconds must be less than 60")

        return True

    except ValidationError as e:
        logger.error(f"Game data validation failed: {str(e)}")
        raise


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration settings.

    Args:
        config: Configuration dictionary to validate

    Returns:
        True if valid, raises ValidationError otherwise
    """
    required_settings = {
        'GROQ_API_KEY': str,
        'AZURE_SPEECH_KEY': str,
        'AZURE_SPEECH_REGION': str,
        'GAME_STATS_API_KEY': str
    }

    try:
        # Check required settings and types
        for setting, expected_type in required_settings.items():
            if setting not in config:
                raise ValidationError(f"Missing required setting: {setting}")

            if not isinstance(config[setting], expected_type):
                raise ValidationError(
                    f"Invalid type for {setting}: expected {expected_type}, "
                    f"got {type(config[setting])}"
                )

            if not config[setting]:
                raise ValidationError(f"Empty value for required setting: {setting}")

        # Validate API keys format
        for key in ['GROQ_API_KEY', 'AZURE_SPEECH_KEY', 'GAME_STATS_API_KEY']:
            if not _is_valid_api_key(config[key]):
                raise ValidationError(f"Invalid format for {key}")

        # Validate Azure region
        if not _is_valid_azure_region(config['AZURE_SPEECH_REGION']):
            raise ValidationError("Invalid Azure region format")

        return True

    except ValidationError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise


def _is_valid_api_key(key: str) -> bool:
    """Check if API key format is valid."""
    # Basic validation - can be customized based on specific API key formats
    return (
            isinstance(key, str) and
            len(key) >= 32 and
            not key.isspace()
    )


def _is_valid_azure_region(region: str) -> bool:
    """Check if Azure region format is valid."""
    valid_regions = {
        'eastus', 'eastus2', 'westus', 'westus2', 'northeurope',
        'westeurope', 'southeastasia', 'eastasia'
    }
    return region.lower() in valid_regions