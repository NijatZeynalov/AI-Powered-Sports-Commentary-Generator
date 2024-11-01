import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class CustomFormatter(logging.Formatter):
    """Custom formatter with color output for console."""

    COLORS = {
        'DEBUG': '\033[0;36m',  # Cyan
        'INFO': '\033[0;32m',  # Green
        'WARNING': '\033[0;33m',  # Yellow
        'ERROR': '\033[0;31m',  # Red
        'CRITICAL': '\033[0;35m',  # Purple
        'RESET': '\033[0m'  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        # Add color to console output only
        if record.levelname in self.COLORS:
            if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
                color = self.COLORS[record.levelname]
                reset = self.COLORS['RESET']
                record.levelname = f"{color}{record.levelname}{reset}"

        return super().format(record)


def get_logger(
        name: str,
        log_file: Optional[str] = None,
        level: str = "INFO"
) -> logging.Logger:
    """
    Create and configure a logger instance.

    Args:
        name: Logger name (typically __name__)
        log_file: Optional path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatters
    console_formatter = CustomFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to create log file: {str(e)}")

    return logger


logger = get_logger(__name__)