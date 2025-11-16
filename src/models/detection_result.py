"""Data models for car detection and speed measurement."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .config import Configuration


@dataclass
class BoundingBox:
    """Represents the bounding box coordinates of a detected object."""

    x1: int  # Left X coordinate
    y1: int  # Top Y coordinate
    x2: int  # Right X coordinate
    y2: int  # Bottom Y coordinate

    @property
    def width(self) -> int:
        """Compute width of bounding box."""
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        """Compute height of bounding box."""
        return self.y2 - self.y1

    @property
    def center_x(self) -> int:
        """Compute center X coordinate."""
        return (self.x1 + self.x2) // 2

    @property
    def center_y(self) -> int:
        """Compute center Y coordinate."""
        return (self.y1 + self.y2) // 2

    def intersects_x(self, x: int) -> bool:
        """Check if bounding box intersects with vertical line at x."""
        return self.x1 <= x <= self.x2

    def center_x_coordinate(self) -> int:
        """Get center X coordinate for crossing detection."""
        return self.center_x


@dataclass
class DetectionResult:
    """Represents a single car detection in a video frame."""

    frame_number: int  # Frame index where detection occurred
    bounding_box: BoundingBox  # Coordinates of detected car
    confidence: float  # Detection confidence score (0.0 to 1.0)
    class_id: int  # YOLO class ID (should be "car" class)
    class_name: str  # Detected class name (e.g., "car")


@dataclass
class VideoMetadata:
    """Represents metadata about the video file being processed."""

    file_path: str  # Path to the video file
    frame_count: int  # Total number of frames in video
    fps: float  # Actual frame rate of video (may differ from config fps)
    width: int  # Video frame width in pixels
    height: int  # Video frame height in pixels
    duration_seconds: float  # Total video duration


@dataclass
class TrackedCar:
    """Represents a car being tracked across multiple frames."""

    track_id: int  # Unique identifier for this tracked car
    detections: List[DetectionResult] = field(default_factory=list)  # List of detections for this car, ordered by frame
    first_detection_frame: Optional[int] = None  # Frame number of first detection
    last_detection_frame: Optional[int] = None  # Frame number of most recent detection
    left_crossing_frame: Optional[int] = None  # Frame when car crossed left coordinate (None if not crossed)
    right_crossing_frame: Optional[int] = None  # Frame when car crossed right coordinate (None if not crossed)

    def add_detection(self, detection: DetectionResult) -> None:
        """Add a detection to this tracked car."""
        self.detections.append(detection)
        if self.first_detection_frame is None:
            self.first_detection_frame = detection.frame_number
        self.last_detection_frame = detection.frame_number

    def is_complete(self) -> bool:
        """Check if car has crossed both coordinates."""
        return self.left_crossing_frame is not None and self.right_crossing_frame is not None


@dataclass
class CoordinateCrossingEvent:
    """Represents an event when a car crosses a measurement coordinate."""

    track_id: int  # ID of the tracked car that crossed
    frame_number: int  # Frame when crossing occurred
    coordinate_type: str  # "left" or "right"
    coordinate_value: int  # X-coordinate value that was crossed
    car_center_x: int  # X-coordinate of car center when crossing occurred
    confidence: float  # Detection confidence at crossing frame


@dataclass
class SpeedMeasurement:
    """Represents the final calculated speed result."""

    speed_kmh: float  # Calculated speed in kilometers per hour
    speed_ms: float  # Calculated speed in meters per second (for internal use)
    frame_count: int  # Number of frames between left and right crossings
    time_seconds: float  # Time duration in seconds (frame_count / fps)
    distance_meters: float  # Distance in meters (converted from config distance in cm)
    left_crossing_frame: int  # Frame when left coordinate was crossed
    right_crossing_frame: int  # Frame when right coordinate was crossed
    track_id: int  # ID of the tracked car measured
    confidence: float  # Average confidence across detection frames
    is_valid: bool  # Whether measurement is valid (both coordinates crossed)

    def __post_init__(self) -> None:
        """Validate speed measurement after initialization."""
        if not self.is_valid:
            return
        if self.frame_count <= 0:
            raise ValueError("frame_count must be > 0 for valid measurement")
        if self.time_seconds <= 0:
            raise ValueError("time_seconds must be > 0 for valid measurement")
        if self.speed_kmh < 0:
            raise ValueError("speed_kmh must be >= 0")


@dataclass
class ProcessingResult:
    """Represents the overall result of processing a video file."""

    video_path: str  # Path to processed video file
    config_path: str  # Path to configuration file used
    video_metadata: VideoMetadata  # Metadata about the video
    processing_time_seconds: float  # Total time taken to process video
    frames_processed: int  # Total number of frames processed
    detections_count: int  # Total number of car detections made
    speed_measurements: List[SpeedMeasurement] = field(default_factory=list)  # List of calculated speeds
    error_message: Optional[str] = None  # Error message if processing failed (None if successful)
    logs: List[dict] = field(default_factory=list)  # Structured log entries from processing
    config: Optional["Configuration"] = None  # Configuration used for processing

    @property
    def speed_measurement(self) -> Optional[SpeedMeasurement]:
        """Backward compatibility property: returns first measurement if available."""
        return self.speed_measurements[0] if self.speed_measurements else None

