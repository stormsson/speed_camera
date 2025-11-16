"""Speed calculation service."""

from src.models import SpeedMeasurement, Configuration, TrackedCar
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class SpeedCalculator:
    """Calculates car speed from crossing events."""

    def __init__(self, config: Configuration):
        """
        Initialize speed calculator.

        Args:
            config: Configuration with distance and fps
        """
        self.config = config
        self.distance_meters = config.distance / 100.0  # Convert cm to meters
        self.fps = config.fps

    def calculate(
        self,
        left_crossing_frame: int,
        right_crossing_frame: int,
        track_id: int,
        confidence: float
    ) -> SpeedMeasurement:
        """
        Calculate speed from crossing frames.

        Args:
            left_crossing_frame: Frame when left coordinate was crossed
            right_crossing_frame: Frame when right coordinate was crossed
            track_id: ID of the tracked car
            confidence: Average confidence across detections

        Returns:
            SpeedMeasurement object

        Raises:
            ValueError: If frame_count <= 0 or time <= 0
        """
        frame_count = right_crossing_frame - left_crossing_frame

        if frame_count <= 0:
            raise ValueError(f"frame_count must be > 0, got {frame_count}")

        time_seconds = frame_count / self.fps

        if time_seconds <= 0:
            raise ValueError(f"time_seconds must be > 0, got {time_seconds}")

        # Calculate speed: distance / time
        speed_ms = self.distance_meters / time_seconds

        # Convert to km/h: m/s * 3.6 = km/h
        speed_kmh = speed_ms * 3.6

        measurement = SpeedMeasurement(
            speed_kmh=speed_kmh,
            speed_ms=speed_ms,
            frame_count=frame_count,
            time_seconds=time_seconds,
            distance_meters=self.distance_meters,
            left_crossing_frame=left_crossing_frame,
            right_crossing_frame=right_crossing_frame,
            track_id=track_id,
            confidence=confidence,
            is_valid=True
        )

        logger.info(
            "Speed calculated",
            extra={
                "track_id": track_id,
                "speed_kmh": speed_kmh,
                "speed_ms": speed_ms,
                "frame_count": frame_count,
                "time_seconds": time_seconds,
                "distance_meters": self.distance_meters,
                "left_crossing_frame": left_crossing_frame,
                "right_crossing_frame": right_crossing_frame,
                "confidence": confidence,
                "event_type": "speed_calculation"
            }
        )

        return measurement

    def calculate_from_tracked_car(self, tracked_car: TrackedCar) -> SpeedMeasurement:
        """
        Calculate speed from a tracked car that has crossed both coordinates.

        Args:
            tracked_car: TrackedCar with both coordinates crossed

        Returns:
            SpeedMeasurement object

        Raises:
            ValueError: If car hasn't crossed both coordinates
        """
        if not tracked_car.is_complete():
            raise ValueError("TrackedCar must have crossed both coordinates")
            
        if tracked_car.right_crossing_frame <= tracked_car.left_crossing_frame:
            raise ValueError("Right crossing frame must be greater than left crossing frame")

        # Calculate average confidence
        if tracked_car.detections:
            avg_confidence = sum(d.confidence for d in tracked_car.detections) / len(tracked_car.detections)
        else:
            avg_confidence = 0.0

        

        return self.calculate(
            left_crossing_frame=tracked_car.left_crossing_frame,
            right_crossing_frame=tracked_car.right_crossing_frame,
            track_id=tracked_car.track_id,
            confidence=avg_confidence
        )

