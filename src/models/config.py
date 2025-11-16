"""Configuration model for car speed detection."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

import yaml

from src.lib.exceptions import InvalidConfigurationError


@dataclass
class Configuration:
    """Represents the measurement parameters loaded from the configuration file."""

    left_coordinate: int  # X-coordinate in pixels where left measurement line is drawn
    right_coordinate: int  # X-coordinate in pixels where right measurement line is drawn
    distance: float  # Real-world distance between left and right coordinates in centimeters
    fps: float  # Frames per second of the video/camera
    downsize_video: Optional[int] = None  # Optional target width in pixels for video resizing (for performance optimization)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate configuration parameters."""
        errors = []

        # Validate left_coordinate
        if self.left_coordinate < 0:
            errors.append("left_coordinate must be >= 0")

        # Validate right_coordinate
        if self.right_coordinate <= self.left_coordinate:
            errors.append(
                f"right_coordinate ({self.right_coordinate}) must be > left_coordinate ({self.left_coordinate})"
            )

        # Validate distance
        if self.distance <= 0:
            errors.append("distance must be > 0")

        # Validate fps
        if self.fps <= 0:
            errors.append("fps must be > 0")

        # Validate downsize_video (if present)
        if self.downsize_video is not None and self.downsize_video <= 0:
            errors.append("downsize_video must be > 0 if specified")

        if errors:
            error_message = "Invalid configuration: " + "; ".join(errors)
            raise InvalidConfigurationError(error_message)

    @classmethod
    def load_from_yaml(cls, file_path: str) -> "Configuration":
        """
        Load configuration from a YAML file.

        Args:
            file_path: Path to the YAML configuration file

        Returns:
            Configuration instance

        Raises:
            InvalidConfigurationError: If file cannot be read, YAML is invalid,
                or configuration values are invalid
        """
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            raise InvalidConfigurationError(
                f"Configuration file not found: {file_path}",
                config_path=file_path
            )

        # Check if file is readable
        if not os.access(path, os.R_OK):
            raise InvalidConfigurationError(
                f"Cannot read configuration file: {file_path}",
                config_path=file_path
            )

        # Load and parse YAML
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise InvalidConfigurationError(
                f"Invalid YAML syntax in configuration file: {str(e)}",
                config_path=file_path
            ) from e
        except Exception as e:
            raise InvalidConfigurationError(
                f"Error reading configuration file: {str(e)}",
                config_path=file_path
            ) from e

        # Validate that data is a dictionary
        if not isinstance(data, dict):
            raise InvalidConfigurationError(
                "Configuration file must contain a YAML dictionary/mapping",
                config_path=file_path
            )

        # Extract and validate required fields
        required_fields = ['left_coordinate', 'right_coordinate', 'distance', 'fps']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise InvalidConfigurationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                config_path=file_path
            )

        # Extract values with type conversion
        try:
            left_coordinate = int(data['left_coordinate'])
            right_coordinate = int(data['right_coordinate'])
            distance = float(data['distance'])
            fps = float(data['fps'])
            # Optional downsize_video parameter
            downsize_video = None
            if 'downsize_video' in data:
                downsize_video = int(data['downsize_video'])
        except (ValueError, TypeError) as e:
            raise InvalidConfigurationError(
                f"Invalid value type in configuration: {str(e)}",
                config_path=file_path
            ) from e

        # Create and validate configuration
        try:
            config = cls(
                left_coordinate=left_coordinate,
                right_coordinate=right_coordinate,
                distance=distance,
                fps=fps,
                downsize_video=downsize_video
            )
        except InvalidConfigurationError as e:
            # Re-raise with config_path context
            raise InvalidConfigurationError(
                f"{str(e)} (in file: {file_path})",
                config_path=file_path
            ) from e

        return config

