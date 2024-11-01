from typing import Optional, Dict, List
import azure.cognitiveservices.speech as speechsdk
import tempfile
import os
import json
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)


class VoiceProfile:
    """Configuration for voice characteristics."""

    def __init__(
            self,
            voice_name: str = "en-US-ChristopherNeural",
            style: str = "excited",
            rate: float = 1.1,
            pitch: float = 0
    ):
        self.voice_name = voice_name
        self.style = style
        self.rate = rate
        self.pitch = pitch

    def to_ssml(self, text: str) -> str:
        """Convert text to SSML with voice profile settings."""
        return (
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"'
            f' xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">'
            f'<voice name="{self.voice_name}">'
            f'<prosody rate="{self.rate:+.1f}" pitch="{self.pitch:+.0f}st">'
            f'<mstts:express-as style="{self.style}">'
            f'{text}'
            f'</mstts:express-as>'
            f'</prosody>'
            f'</voice>'
            f'</speak>'
        )


class SpeechSynthesizer:
    """Handles text-to-speech conversion using Azure Cognitive Services."""

    def __init__(
            self,
            subscription_key: str,
            region: str,
            output_dir: Optional[str] = None
    ):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key,
            region=region
        )
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir())
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Define voice profiles for different commentary styles
        self.voice_profiles = {
            "excited": VoiceProfile(
                voice_name="en-US-ChristopherNeural",
                style="excited",
                rate=1.1,
                pitch=2
            ),
            "neutral": VoiceProfile(
                voice_name="en-US-GuyNeural",
                style="neutral",
                rate=1.0,
                pitch=0
            ),
            "analytical": VoiceProfile(
                voice_name="en-US-RogerNeural",
                style="analytical",
                rate=0.9,
                pitch=-1
            )
        }

        # Initialize synthesis stats
        self.stats = {
            "total_synthesized": 0,
            "errors": 0,
            "average_duration": 0
        }

    def synthesize(
            self,
            text: str,
            style: str = "neutral",
            output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            style: Commentary style (excited, neutral, analytical)
            output_file: Optional specific output file path

        Returns:
            Path to the generated audio file or None if synthesis failed
        """
        try:
            # Get appropriate voice profile
            profile = self.voice_profiles.get(style, self.voice_profiles["neutral"])

            # Generate SSML
            ssml = profile.to_ssml(text)

            # Generate output filename if not provided
            if not output_file:
                output_file = self.output_dir / f"commentary_{self.stats['total_synthesized']}.wav"

            # Configure audio output
            audio_config = speechsdk.AudioConfig(filename=str(output_file))

            # Create speech synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            # Execute synthesis
            result = synthesizer.speak_ssml_async(ssml).get()

            # Handle result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self._update_stats(True, result.audio_duration)
                logger.info(f"Speech synthesis completed: {output_file}")
                return str(output_file)
            else:
                self._update_stats(False)
                error_details = result.properties.get(
                    speechsdk.PropertyId.SpeechServiceResponse_JsonErrorDetails
                )
                logger.error(
                    f"Speech synthesis failed: {result.reason} - {error_details}"
                )
                return None

        except Exception as e:
            self._update_stats(False)
            logger.error(f"Error in speech synthesis: {str(e)}")
            return None

    def get_available_voices(self) -> List[Dict]:
        """Retrieve list of available voices from Azure."""
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None
            )
            result = synthesizer.get_voices_async().get()

            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                voices = json.loads(result.json)
                return [
                    {
                        'name': voice['ShortName'],
                        'locale': voice['Locale'],
                        'gender': voice['Gender'],
                        'styles': voice.get('StyleList', [])
                    }
                    for voice in voices
                ]
            else:
                logger.error("Failed to retrieve voices list")
                return []

        except Exception as e:
            logger.error(f"Error retrieving voices: {str(e)}")
            return []

    def update_voice_profile(
            self,
            style: str,
            voice_name: Optional[str] = None,
            rate: Optional[float] = None,
            pitch: Optional[float] = None
    ) -> bool:
        """
        Update voice profile settings.

        Args:
            style: Profile style to update
            voice_name: New voice name (optional)
            rate: New speech rate (optional)
            pitch: New pitch adjustment (optional)

        Returns:
            True if update successful, False otherwise
        """
        try:
            if style not in self.voice_profiles:
                logger.error(f"Invalid style: {style}")
                return False

            profile = self.voice_profiles[style]

            if voice_name:
                profile.voice_name = voice_name
            if rate is not None:
                profile.rate = max(0.5, min(2.0, rate))
            if pitch is not None:
                profile.pitch = max(-12, min(12, pitch))

            return True

        except Exception as e:
            logger.error(f"Error updating voice profile: {str(e)}")
            return False

    def get_synthesis_stats(self) -> Dict:
        """Get current synthesis statistics."""
        return self.stats.copy()

    def _update_stats(self, success: bool, duration: int = 0) -> None:
        """Update synthesis statistics."""
        self.stats["total_synthesized"] += 1
        if not success:
            self.stats["errors"] += 1

        # Update average duration
        if success and duration > 0:
            current_total = self.stats["average_duration"] * (self.stats["total_synthesized"] - 1)
            new_total = current_total + duration
            self.stats["average_duration"] = new_total / self.stats["total_synthesized"]

    def cleanup_old_files(self, max_age_hours: int = 24) -> None:
        """Clean up old audio files."""
        try:
            current_time = Path().stat().st_mtime
            for file in self.output_dir.glob("commentary_*.wav"):
                file_age_hours = (current_time - file.stat().st_mtime) / 3600
                if file_age_hours > max_age_hours:
                    file.unlink()
                    logger.info(f"Cleaned up old file: {file}")
        except Exception as e:
            logger.error(f"Error cleaning up files: {str(e)}")