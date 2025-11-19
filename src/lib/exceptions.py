"""Custom exception classes for car speed detection."""


class CarSpeedDetectionError(Exception):
    """Base exception for car speed detection errors."""

    pass


class VideoLoadError(CarSpeedDetectionError):
    """Raised when video file cannot be loaded or is corrupted."""

    def __init__(self, message: str, video_path: str = None):
        """Initialize video load error."""
        super().__init__(message)
        self.video_path = video_path
        self.message = message

    def __str__(self) -> str:
        """Return error message."""
        if self.video_path:
            return f"Failed to load video file '{self.video_path}': {self.message}"
        return f"Failed to load video file: {self.message}"


class InvalidConfigurationError(CarSpeedDetectionError):
    """Raised when configuration file is invalid or missing required fields."""

    def __init__(self, message: str, config_path: str = None):
        """Initialize configuration error."""
        super().__init__(message)
        self.config_path = config_path
        self.message = message

    def __str__(self) -> str:
        """Return error message."""
        if self.config_path:
            return f"Invalid configuration file '{self.config_path}': {self.message}"
        return f"Invalid configuration: {self.message}"


class NoCarDetectedError(CarSpeedDetectionError):
    """Raised when no car is detected in the video."""

    def __init__(self, video_path: str = None):
        """Initialize no car detected error."""
        message = "No car detected in video"
        super().__init__(message)
        self.video_path = video_path
        self.message = message

    def __str__(self) -> str:
        """Return error message."""
        if self.video_path:
            return f"No car detected in video: {self.video_path}"
        return self.message


class CarNotCrossingBothCoordinatesError(CarSpeedDetectionError):
    """Raised when a car is detected but doesn't cross both measurement coordinates."""

    def __init__(self, video_path: str = None, track_id: int = None):
        """Initialize car not crossing error."""
        message = "Car detected but did not cross both measurement coordinates"
        super().__init__(message)
        self.video_path = video_path
        self.track_id = track_id
        self.message = message

    def __str__(self) -> str:
        """Return error message."""
        parts = [self.message]
        if self.video_path:
            parts.append(f"Video: {self.video_path}")
        if self.track_id is not None:
            parts.append(f"Track ID: {self.track_id}")
        return " - ".join(parts)

