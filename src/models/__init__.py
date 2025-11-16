"""Data models for car speed detection."""

from .config import Configuration
from .detection_result import (
    BoundingBox,
    CoordinateCrossingEvent,
    DetectionResult,
    ProcessingResult,
    SpeedMeasurement,
    TrackedCar,
    VideoMetadata,
)

__all__ = [
    "Configuration",
    "BoundingBox",
    "DetectionResult",
    "VideoMetadata",
    "TrackedCar",
    "SpeedMeasurement",
    "CoordinateCrossingEvent",
    "ProcessingResult",
]
