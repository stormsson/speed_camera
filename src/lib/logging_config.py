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

        # Add all extra fields from the record
        # Exclude standard LogRecord attributes to avoid noise
        standard_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs', 'message',
            'pathname', 'process', 'processName', 'relativeCreated', 'thread',
            'threadName', 'exc_info', 'exc_text', 'stack_info', 'getMessage'
        }
        
        # Include all non-standard attributes (these are the extra fields)
        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                log_data[key] = value

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

    # Get root logger to configure all loggers
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create JSON formatter
    formatter = JSONFormatter()

    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str = "vehicle_speed_detection") -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (default: "vehicle_speed_detection")

    Returns:
        Logger instance
    """
    return logging.getLogger(name)

