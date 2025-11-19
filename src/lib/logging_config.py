"""Structured logging configuration for car speed detection."""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "frame_number"):
            log_data["frame_number"] = record.frame_number
        if hasattr(record, "track_id"):
            log_data["track_id"] = record.track_id
        if hasattr(record, "confidence"):
            log_data["confidence"] = record.confidence
        if hasattr(record, "event_type"):
            log_data["event_type"] = record.event_type
        if hasattr(record, "coordinate_type"):
            log_data["coordinate_type"] = record.coordinate_type
        if hasattr(record, "speed_kmh"):
            log_data["speed_kmh"] = record.speed_kmh
        if hasattr(record, "processing_time"):
            log_data["processing_time"] = record.processing_time

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(
    level: int = logging.INFO,
    log_file: str = None,
    verbose: bool = False,
) -> logging.Logger:
    """
    Setup structured logging for the application.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional path to log file (default: None, logs to stderr)
        verbose: If True, set level to DEBUG (default: False)

    Returns:
        Configured logger instance
    """
    if verbose:
        level = logging.DEBUG

    logger = logging.getLogger("car_speed_detection")
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create JSON formatter
    formatter = JSONFormatter()

    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "car_speed_detection") -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (default: "car_speed_detection")

    Returns:
        Logger instance
    """
    return logging.getLogger(name)

