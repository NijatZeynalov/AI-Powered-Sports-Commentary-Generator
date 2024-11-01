from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GameMoment:
    """Represents a significant moment in the game."""
    timestamp: str
    event_type: str
    importance: float  # 0.0 to 1.0
    description: str
    teams_involved: List[str]
    score_change: bool
    momentum_shift: bool


class GameAnalyzer:
    """Analyzes game statistics to identify significant moments and patterns."""

    def __init__(self):
        self.previous_stats: Optional[Dict] = None
        self.momentum_threshold = 0.6
        self.significant_events = {
            'score_change': 0.8,
            'possession_change': 0.4,
            'timeout': 0.5,
            'injury': 0.7,
            'penalty': 0.6
        }

    def analyze_game_state(self, current_stats: Dict) -> Dict:
        """
        Analyze current game state and identify key patterns.

        Args:
            current_stats: Current game statistics

        Returns:
            Dictionary containing analysis results
        """
        analysis = {
            'key_moments': self._identify_key_moments(current_stats),
            'momentum': self._calculate_momentum(current_stats),
            'performance_metrics': self._analyze_performance(current_stats),
            'game_situation': self._assess_game_situation(current_stats)
        }

        self.previous_stats = current_stats
        return analysis

    def _identify_key_moments(self, stats: Dict) -> List[GameMoment]:
        """Identify significant moments from recent game events."""
        key_moments = []

        for event in stats.get('recent_events', []):
            importance = self._calculate_event_importance(event)
            if importance >= self.momentum_threshold:
                key_moments.append(
                    GameMoment(
                        timestamp=event['timestamp'],
                        event_type=event['type'],
                        importance=importance,
                        description=event['description'],
                        teams_involved=event['teams'],
                        score_change='score' in event['type'].lower(),
                        momentum_shift=importance > 0.7
                    )
                )

        return sorted(key_moments, key=lambda x: x.importance, reverse=True)

    def _calculate_momentum(self, stats: Dict) -> Dict:
        """Calculate current momentum based on recent events and statistics."""
        if not self.previous_stats:
            return {'home': 0.5, 'away': 0.5}

        home_momentum = 0.5
        away_momentum = 0.5

        # Analyze scoring trends
        recent_scores = stats.get('recent_scores', [])
        for score in recent_scores:
            if score['team'] == stats['home_team']:
                home_momentum += 0.1
                away_momentum -= 0.1
            else:
                away_momentum += 0.1
                home_momentum -= 0.1

        # Consider possession and field position
        if 'possession' in stats:
            possession_bonus = 0.05
            if stats['possession'] == stats['home_team']:
                home_momentum += possession_bonus
            else:
                away_momentum += possession_bonus

        # Normalize values between 0 and 1
        total = home_momentum + away_momentum
        return {
            'home': round(home_momentum / total, 2),
            'away': round(away_momentum / total, 2)
        }

    def _analyze_performance(self, stats: Dict) -> Dict:
        """Analyze team performance metrics."""
        return {
            'home': {
                'efficiency': self._calculate_efficiency(stats, 'home'),
                'pressure': self._calculate_pressure(stats, 'home'),
                'defense': self._calculate_defense(stats, 'home')
            },
            'away': {
                'efficiency': self._calculate_efficiency(stats, 'away'),
                'pressure': self._calculate_pressure(stats, 'away'),
                'defense': self._calculate_defense(stats, 'away')
            }
        }

    def _assess_game_situation(self, stats: Dict) -> Dict:
        """Assess the current game situation and its significance."""
        time_remaining = self._parse_time_remaining(stats['game_time'])
        score_difference = abs(stats['home_score'] - stats['away_score'])

        return {
            'criticality': self._calculate_criticality(time_remaining, score_difference),
            'phase': self._determine_game_phase(time_remaining),
            'context': self._generate_situation_context(stats)
        }

    def _calculate_event_importance(self, event: Dict) -> float:
        """Calculate the importance of a game event."""
        base_importance = self.significant_events.get(event['type'].lower(), 0.3)

        # Adjust importance based on game context
        if 'time_remaining' in event:
            time_factor = min(1.0, 1.5 - float(event['time_remaining']) / 3600)
            base_importance *= (1 + time_factor)

        return min(1.0, base_importance)

    @staticmethod
    def _calculate_efficiency(stats: Dict, team: str) -> float:
        """Calculate team's efficiency rating."""
        attempts = stats.get(f'{team}_attempts', 1)  # Avoid division by zero
        successes = stats.get(f'{team}_successes', 0)
        return round(successes / attempts, 3)

    @staticmethod
    def _calculate_pressure(stats: Dict, team: str) -> float:
        """Calculate team's pressure rating."""
        return min(1.0, stats.get(f'{team}_pressure', 0) / 100)

    @staticmethod
    def _calculate_defense(stats: Dict, team: str) -> float:
        """Calculate team's defensive rating."""
        return min(1.0, stats.get(f'{team}_defense', 0) / 100)

    @staticmethod
    def _parse_time_remaining(time_str: str) -> int:
        """Convert time string to seconds remaining."""
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])