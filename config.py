from typing import Dict, Any
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with validation."""

    # API Keys
    GROQ_API_KEY: str = Field(..., description="Groq API key for natural language generation")
    AZURE_SPEECH_KEY: str = Field(..., description="Azure Cognitive Services API key")
    AZURE_SPEECH_REGION: str = Field(..., description="Azure service region")
    GAME_STATS_API_KEY: str = Field(..., description="Sports data API key")

    # Application Settings
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    OUTPUT_DIR: str = Field("output", description="Directory for generated commentary")
    CACHE_DIR: str = Field("cache", description="Directory for temporary files")

    # Commentary Settings
    UPDATE_INTERVAL: int = Field(30, description="Seconds between commentary updates")
    MAX_RETRIES: int = Field(3, description="Maximum API retry attempts")
    COMMENTARY_STYLES: Dict[str, Dict[str, Any]] = Field(
        default={
            "excited": {
                "voice_name": "en-US-ChristopherNeural",
                "rate": 1.1,
                "pitch": 2
            },
            "neutral": {
                "voice_name": "en-US-GuyNeural",
                "rate": 1.0,
                "pitch": 0
            },
            "analytical": {
                "voice_name": "en-US-RogerNeural",
                "rate": 0.9,
                "pitch": -1
            }
        },
        description="Voice profiles for different commentary styles"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()