"""Coordinate crossing detection service."""

from typing import List
from src.models import TrackedCar, CoordinateCrossingEvent, Configuration
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class CoordinateCrossingDetector:
    """Detects when cars cross measurement coordinates."""

    def __init__(self, config: Configuration):
        """
        Initialize coordinate crossing detector.

        Args:
            config: Configuration with left and right coordinates
        """
        self.left_coordinate = config.left_coordinate
        self.right_coordinate = config.right_coordinate

    def detect_crossings(
        self,
        tracked_car: TrackedCar,
        frame_number: int
    ) -> List[CoordinateCrossingEvent]:
        """
        Detect coordinate crossings for a tracked car.

        Args:
            tracked_car: Tracked car to check
            frame_number: Current frame number

        Returns:
            List of crossing events detected in this frame
        """
        events = []

        if not tracked_car.detections:
            return events

        # Get the most recent detection
        latest_detection = tracked_car.detections[-1]
        # Use rightmost edge of bounding box (x2) for crossing detection
        car_rightmost_x = latest_detection.bounding_box.x2

        # Check left coordinate crossing
        if tracked_car.left_crossing_frame is None:
            # Car hasn't crossed left yet
            # Crossing occurs when rightmost edge of bounding box intersects the coordinate
            if car_rightmost_x >= self.left_coordinate:
                tracked_car.left_crossing_frame = frame_number
                event = CoordinateCrossingEvent(
                    track_id=tracked_car.track_id,
                    frame_number=frame_number,
                    coordinate_type="left",
                    coordinate_value=self.left_coordinate,
                    car_rightmost_x=car_rightmost_x,  # Store rightmost x for logging
                    confidence=latest_detection.confidence
                )
                events.append(event)

                logger.info(
                    "Left coordinate crossed",
                    extra={
                        "frame_number": frame_number,
                        "track_id": tracked_car.track_id,
                        "coordinate_type": "left",
                        "coordinate_value": self.left_coordinate,
                        "car_rightmost_x": car_rightmost_x,
                        "confidence": latest_detection.confidence,
                        "event_type": "left_crossing"
                    }
                )

        # Check right coordinate crossing (only if left was already crossed)
        if tracked_car.left_crossing_frame is not None and tracked_car.right_crossing_frame is None:
            # Car has crossed left but not right yet
            # Crossing occurs when rightmost edge of bounding box intersects the coordinate
            if car_rightmost_x >= self.right_coordinate:
                tracked_car.right_crossing_frame = frame_number
                event = CoordinateCrossingEvent(
                    track_id=tracked_car.track_id,
                    frame_number=frame_number,
                    coordinate_type="right",
                    coordinate_value=self.right_coordinate,
                    car_rightmost_x=car_rightmost_x,  # Store rightmost x for logging
                    confidence=latest_detection.confidence
                )
                events.append(event)

                logger.info(
                    "Right coordinate crossed",
                    extra={
                        "frame_number": frame_number,
                        "track_id": tracked_car.track_id,
                        "coordinate_type": "right",
                        "coordinate_value": self.right_coordinate,
                        "car_rightmost_x": car_rightmost_x,
                        "confidence": latest_detection.confidence,
                        "event_type": "right_crossing"
                    }
                )

        return events

