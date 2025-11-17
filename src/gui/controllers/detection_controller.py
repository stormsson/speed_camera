"""Detection controller for coordinating Feature 001's detection services."""

from typing import List, Dict, Optional
import numpy as np
from PySide6.QtGui import QImage

from src.models import (
    DetectionResult,
    TrackedCar,
    CoordinateCrossingEvent,
    Configuration
)
from src.services.car_detector import CarDetector
from src.services.car_tracker import CarTracker
from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class DetectionController:
    """Controller for coordinating car detection, tracking, and crossing detection."""

    def __init__(
        self,
        config: Configuration,
        confidence_threshold: float = 0.5
    ):
        """
        Initialize detection controller.

        Args:
            config: Configuration with coordinates
            confidence_threshold: Minimum confidence for detections
        """
        self.config = config
        self.car_detector = CarDetector(confidence_threshold=confidence_threshold)
        self.car_tracker = CarTracker()
        self.crossing_detector = CoordinateCrossingDetector(config)

    def detect_cars(
        self,
        frame: np.ndarray,
        frame_number: int
    ) -> List[DetectionResult]:
        """
        Detect cars in a frame.

        Args:
            frame: Video frame as numpy array
            frame_number: Current frame number

        Returns:
            List of DetectionResult objects
        """
        detections = self.car_detector.detect(frame, frame_number)
        return detections

    def update_tracking(
        self,
        detections: List[DetectionResult],
        frame_number: int
    ) -> List[TrackedCar]:
        """
        Update tracking state with new detections.

        Args:
            detections: List of detections in current frame
            frame_number: Current frame number

        Returns:
            List of TrackedCar objects
        """
        tracked_cars = self.car_tracker.update(detections, frame_number)
        return tracked_cars

    def detect_crossings(
        self,
        tracked_cars: List[TrackedCar],
        frame_number: int
    ) -> List[CoordinateCrossingEvent]:
        """
        Detect coordinate crossings for tracked cars.

        Args:
            tracked_cars: List of tracked cars
            frame_number: Current frame number

        Returns:
            List of CoordinateCrossingEvent objects
        """
        events = []

        for tracked_car in tracked_cars:
            crossing_events = self.crossing_detector.detect_crossings(
                tracked_car,
                frame_number
            )
            events.extend(crossing_events)

        return events

    def process_frame(
        self,
        frame: np.ndarray,
        frame_number: int
    ) -> tuple[List[DetectionResult], List[TrackedCar], List[CoordinateCrossingEvent]]:
        """
        Process a frame: detect cars, update tracking, detect crossings.

        Args:
            frame: Video frame as numpy array
            frame_number: Current frame number

        Returns:
            Tuple of (detections, tracked_cars, crossing_events)
        """
        # Detect cars
        detections = self.detect_cars(frame, frame_number)

        # Update tracking
        tracked_cars = self.update_tracking(detections, frame_number)

        # Detect crossings
        crossing_events = self.detect_crossings(tracked_cars, frame_number)

        return detections, tracked_cars, crossing_events

    def get_tracked_cars_dict(self) -> Dict[int, TrackedCar]:
        """
        Get dictionary of tracked cars by track_id.

        Returns:
            Dictionary mapping track_id to TrackedCar
        """
        return self.car_tracker.tracked_cars.copy()

    def reset_tracking(self) -> None:
        """Reset tracking state (create new CarTracker instance)."""
        self.car_tracker = CarTracker()
        logger.info("Tracking state reset")

