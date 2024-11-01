from typing import Dict, List, Optional
from dataclasses import dataclass
import random
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CommentaryTemplate:
    """Template for generating commentary."""
    pattern: str
    conditions: Dict[str, float]  # condition -> minimum threshold
    style: str
    priority: int


class CommentaryGenerator:
    """Generates natural language commentary based on game analysis."""

    def __init__(self):
        self.templates = self._load_templates()
        self.last_used_patterns: List[str] = []
        self.max_pattern_memory = 5

    def generate_commentary(
            self,
            analysis: Dict,
            style: str = "neutral",
            max_length: int = 150
    ) -> str:
        """
        Generate commentary based on game analysis.

        Args:
            analysis: Analysis results from GameAnalyzer
            style: Commentary style (excited, neutral, analytical)
            max_length: Maximum length of commentary in characters

        Returns:
            Generated commentary text
        """
        try:
            relevant_templates = self._filter_templates(analysis, style)
            selected_template = self._select_template(relevant_templates)

            if not selected_template:
                return self._generate_fallback_commentary(analysis)

            commentary = self._fill_template(selected_template, analysis)

            # Update pattern memory
            self.last_used_patterns.append(selected_template.pattern)
            if len(self.last_used_patterns) > self.max_pattern_memory:
                self.last_used_patterns.pop(0)

            return commentary[:max_length]

        except Exception as e:
            logger.error(f"Error generating commentary: {str(e)}")
            return self._generate_fallback_commentary(analysis)

    def _load_templates(self) -> List[CommentaryTemplate]:
        """Load and return commentary templates."""
        return [
            CommentaryTemplate(
                pattern="{team} {action} as they {momentum_description}",
                conditions={'momentum': 0.7},
                style="neutral",
                priority=1
            ),
            CommentaryTemplate(
                pattern="What a {intensity} performance by {team}! {key_stat}",
                conditions={'performance': 0.8},
                style="excited",
                priority=2
            ),
            CommentaryTemplate(
                pattern="Looking at the numbers, {team}'s {stat_type} shows {analysis}",
                conditions={'efficiency': 0.6},
                style="analytical",
                priority=1
            ),
            # Add more templates as needed
        ]

    def _filter_templates(
            self,
            analysis: Dict,
            style: str
    ) -> List[CommentaryTemplate]:
        """Filter templates based on analysis and style."""
        relevant_templates = []

        for template in self.templates:
            if template.style != style:
                continue

            conditions_met = all(
                self._check_condition(analysis, condition, threshold)
                for condition, threshold in template.conditions.items()
            )

            if conditions_met and template.pattern not in self.last_used_patterns:
                relevant_templates.append(template)

        return relevant_templates

    def _select_template(
            self,
            templates: List[CommentaryTemplate]
    ) -> Optional[CommentaryTemplate]:
        """Select the most appropriate template from filtered list."""
        if not templates:
            return None

        # Sort by priority and add some randomness for variety
        weighted_templates = []
        for template in templates:
            weight = template.priority * random.uniform(0.8, 1.2)
            weighted_templates.append((template, weight))

        return max(weighted_templates, key=lambda x: x[1])[0]

    def _fill_template(self, template: CommentaryTemplate, analysis: Dict) -> str:
        """Fill template with actual game data."""
        # Extract relevant data from analysis
        momentum = analysis.get('momentum', {})
        performance = analysis.get('performance_metrics', {})
        situation = analysis.get('game_situation', {})

        # Build context for template filling
        context = {
            'team': self._get_leading_team(analysis),
            'action': self._get_team_action(analysis),
            'momentum_description': self._describe_momentum(momentum),
            'intensity': self._get_intensity_descriptor(performance),
            'key_stat': self._get_key_statistic(performance),
            'stat_type': self._get_stat_type(performance),
            'analysis': self._analyze_statistic(performance)
        }

        return template.pattern.format(**context)

    def _generate_fallback_commentary(self, analysis: Dict) -> str:
        """Generate simple fallback commentary when template generation fails."""
        score = f"{analysis.get('home_score', 0)}-{analysis.get('away_score', 0)}"
        return f"The game continues with a score of {score}."

    @staticmethod
    def _check_condition(analysis: Dict, condition: str, threshold: float) -> bool:
        """Check if analysis meets template condition."""
        if condition == 'momentum':
            momentum = max(analysis.get('momentum', {}).values())
            return momentum >= threshold
        elif condition == 'performance':
            performances = analysis.get('performance_metrics', {}).values()
            return any(p.get('efficiency', 0) >= threshold for p in performances)
        elif condition == 'efficiency':
            performances = analysis.get('performance_metrics', {}).values()
            return any(p.get('efficiency', 0) >= threshold for p in performances)
        return False

    @staticmethod
    def _get_leading_team(analysis: Dict) -> str:
        """Get the currently leading team name."""
        home_score = analysis.get('home_score', 0)
        away_score = analysis.get('away_score', 0)

        if home_score > away_score:
            return analysis.get('home_team', 'Home team')
        elif away_score > home_score:
            return analysis.get('away_team', 'Away team')
        return analysis.get('home_team', 'Home team')  # Default to home team if tied

    @staticmethod
    def _describe_momentum(momentum: Dict) -> str:
        """Generate description of current momentum."""
        if not momentum:
            return "continue to play"

        leading_team = max(momentum.items(), key=lambda x: x[1])[0]
        momentum_value = momentum[leading_team]

        if momentum_value > 0.8:
            return "dominate the game"
        elif momentum_value > 0.6:
            return "maintain control"
        else:
            return "push forward"