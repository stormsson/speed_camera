"""Coordinate crossing detection service."""

from typing import List, Optional, TYPE_CHECKING
from src.models import TrackedCar, CoordinateCrossingEvent, Configuration, DetectionResult
from src.lib.logging_config import get_logger

if TYPE_CHECKING:
    from src.services.video_processor import VideoProcessor
    from src.services.debug_image_generator import DebugImageGenerator

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
        frame_number: int,
        debug: bool = False,
        video_processor: Optional["VideoProcessor"] = None,
        debug_image_generator: Optional["DebugImageGenerator"] = None
    ) -> List[CoordinateCrossingEvent]:
        """
        Detect coordinate crossings for a tracked car using transition-based detection.
        
        Crossing is detected on the first frame where the rightmost edge transitions
        from being less than the coordinate to being greater than or equal to it.

        Args:
            tracked_car: Tracked car to check
            frame_number: Current frame number
            debug: If True, generate debug images for crossing events
            video_processor: Video processor for extracting frames (required if debug=True)
            debug_image_generator: Debug image generator instance (required if debug=True)

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

        # Get previous frame's rightmost x for transition detection
        previous_rightmost_x = None
        if len(tracked_car.detections) > 1:
            previous_detection = tracked_car.detections[-2]
            previous_rightmost_x = previous_detection.bounding_box.x2

        # Check left coordinate crossing
        if tracked_car.left_crossing_frame is None:
            # Car hasn't crossed left yet
            # Crossing occurs on transition: previous x2 < coordinate AND current x2 >= coordinate
            if previous_rightmost_x is not None:
                # Transition-based detection: check if crossing occurred
                if previous_rightmost_x < self.left_coordinate and car_rightmost_x >= self.left_coordinate:
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
                            "previous_rightmost_x": previous_rightmost_x,
                            "confidence": latest_detection.confidence,
                            "event_type": "left_crossing",
                            "transition_detected": True
                        }
                    )
                    
                    # Generate debug image if debug mode is enabled
                    if debug and debug_image_generator and video_processor:
                        try:
                            # Get the current frame from video processor
                            frame = video_processor.get_frame(frame_number)
                            if frame is not None:
                                debug_image_generator.generate_debug_image(
                                    frame,
                                    latest_detection,
                                    event,
                                    frame_number
                                )
                        except Exception as e:
                            logger.error(
                                "Failed to generate debug image for left crossing",
                                extra={
                                    "frame_number": frame_number,
                                    "track_id": tracked_car.track_id,
                                    "error": str(e)
                                },
                                exc_info=True
                            )
                else:
                    # No transition detected - log why crossing was skipped
                    logger.debug(
                        "Left crossing skipped - no transition detected",
                        extra={
                            "frame_number": frame_number,
                            "track_id": tracked_car.track_id,
                            "previous_rightmost_x": previous_rightmost_x,
                            "current_rightmost_x": car_rightmost_x,
                            "left_coordinate": self.left_coordinate,
                            "transition_condition": f"{previous_rightmost_x} < {self.left_coordinate} and {car_rightmost_x} >= {self.left_coordinate}"
                        }
                    )
            else:
                # Edge case: first detection, no previous frame to compare
                # If car already past coordinate on first detection, we can't detect transition
                # This is acceptable - car appeared after the line
                if car_rightmost_x >= self.left_coordinate:
                    logger.debug(
                        "Car first detected past left coordinate - no transition to detect",
                        extra={
                            "frame_number": frame_number,
                            "track_id": tracked_car.track_id,
                            "car_rightmost_x": car_rightmost_x,
                            "left_coordinate": self.left_coordinate
                        }
                    )

        # Check right coordinate crossing (only if left was already crossed)
        if tracked_car.left_crossing_frame is not None and tracked_car.right_crossing_frame is None:
            # Car has crossed left but not right yet
            # Crossing occurs on transition: previous x2 < coordinate AND current x2 >= coordinate
            if previous_rightmost_x is not None:
                # Transition-based detection: check if crossing occurred
                if previous_rightmost_x < self.right_coordinate and car_rightmost_x >= self.right_coordinate:
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
                            "previous_rightmost_x": previous_rightmost_x,
                            "confidence": latest_detection.confidence,
                            "event_type": "right_crossing",
                            "transition_detected": True
                        }
                    )
                    
                    # Generate debug image if debug mode is enabled
                    if debug and debug_image_generator and video_processor:
                        try:
                            # Get the current frame from video processor
                            frame = video_processor.get_frame(frame_number)
                            if frame is not None:
                                debug_image_generator.generate_debug_image(
                                    frame,
                                    latest_detection,
                                    event,
                                    frame_number
                                )
                        except Exception as e:
                            logger.error(
                                "Failed to generate debug image for right crossing",
                                extra={
                                    "frame_number": frame_number,
                                    "track_id": tracked_car.track_id,
                                    "error": str(e)
                                },
                                exc_info=True
                            )
                else:
                    # No transition detected - log why crossing was skipped
                    logger.debug(
                        "Right crossing skipped - no transition detected",
                        extra={
                            "frame_number": frame_number,
                            "track_id": tracked_car.track_id,
                            "previous_rightmost_x": previous_rightmost_x,
                            "current_rightmost_x": car_rightmost_x,
                            "right_coordinate": self.right_coordinate,
                            "transition_condition": f"{previous_rightmost_x} < {self.right_coordinate} and {car_rightmost_x} >= {self.right_coordinate}"
                        }
                    )
            else:
                # Edge case: first detection after left crossing, no previous frame to compare
                # If car already past coordinate on first detection, we can't detect transition
                if car_rightmost_x >= self.right_coordinate:
                    logger.debug(
                        "Car first detected past right coordinate - no transition to detect",
                        extra={
                            "frame_number": frame_number,
                            "track_id": tracked_car.track_id,
                            "car_rightmost_x": car_rightmost_x,
                            "right_coordinate": self.right_coordinate
                        }
                    )

        return events

