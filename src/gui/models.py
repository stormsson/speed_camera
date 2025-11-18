"""GUI state models for car detection visualizer."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from PySide6.QtGui import QPixmap

from src.models import (
    DetectionResult,
    TrackedCar,
    CoordinateCrossingEvent,
    SpeedMeasurement,
    Configuration,
    VideoMetadata,
    BoundingBox
)
from src.services.car_tracker import CarTracker


@dataclass
class VideoDisplayState:
    """Represents the current state of video display in the GUI."""

    current_frame_number: int = 1
    total_frames: int = 0
    video_width: int = 0
    video_height: int = 0
    current_frame_image: Optional[QPixmap] = None
    is_loaded: bool = False
    video_metadata: Optional[VideoMetadata] = None


@dataclass
class CoordinateOverlayState:
    """Represents the state of coordinate overlay rendering."""

    left_coordinate: int = 0
    right_coordinate: int = 0
    left_coordinate_original: int = 0
    right_coordinate_original: int = 0
    scale_factor: float = 1.0
    is_visible: bool = True
    left_label: str = "Left"
    right_label: str = "Right"
    config: Optional[Configuration] = None


@dataclass
class DetectionVisualizationState:
    """Represents the state of detection visualization on the current frame."""

    detections: List[DetectionResult] = field(default_factory=list)
    tracked_cars: Dict[int, TrackedCar] = field(default_factory=dict)
    crossing_events: List[CoordinateCrossingEvent] = field(default_factory=list)
    json_speed_measurements: List[SpeedMeasurement] = field(default_factory=list)
    is_detection_running: bool = False
    tracking_state: Optional[CarTracker] = None


@dataclass
class FrameNavigationState:
    """Represents the current position and navigation state in video playback."""

    current_frame_number: int = 1
    total_frames: int = 0
    can_go_previous: bool = False
    can_go_next: bool = False
    frame_cache: Dict[int, QPixmap] = field(default_factory=dict)
    frame_cache_size: int = 10


@dataclass
class TrackedCarAnalysis:
    """Analysis data for a single tracked car."""

    track_id: int
    bounding_box: Optional[BoundingBox] = None
    confidence: float = 0.0
    class_name: str = ""
    left_crossing_frame: Optional[int] = None
    right_crossing_frame: Optional[int] = None
    car_rightmost_x: int = 0


@dataclass
class CrossingAnalysis:
    """Analysis data for coordinate crossing detection."""

    track_id: int
    coordinate_type: str  # "left" or "right"
    coordinate_value: int
    car_rightmost_x: int
    comparison_result: str  # e.g., "car_rightmost_x >= coordinate_value"
    condition_met: bool
    crossing_state: str  # Explanation of current crossing state
    crossing_detected: bool


@dataclass
class DebugInformationState:
    """Represents detailed detection analysis data displayed in the debug panel."""

    current_frame_number: int = 0
    detection_results: List[DetectionResult] = field(default_factory=list)
    tracked_cars_analysis: Dict[int, TrackedCarAnalysis] = field(default_factory=dict)
    coordinate_crossing_analysis: Dict[int, List[CrossingAnalysis]] = field(default_factory=dict)
    configuration_values: Optional[Configuration] = None
    json_expected_results: List[SpeedMeasurement] = field(default_factory=list)

