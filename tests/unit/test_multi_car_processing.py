"""Unit tests for multi-car processing feature."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np

from src.models import (
    Configuration, DetectionResult, BoundingBox, TrackedCar,
    SpeedMeasurement, ProcessingResult, VideoMetadata
)


class TestMultiCarProcessing:
    """Test sequential multi-car detection and processing."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration."""
        return Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,  # 2 meters
            fps=30.0
        )

    def test_sequential_car_detection(self, sample_config):
        """Test that multiple cars can be detected sequentially."""
        from src.services.car_tracker import CarTracker
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        tracker = CarTracker()
        crossing_detector = CoordinateCrossingDetector(sample_config)
        
        # First car: frames 0-50, crosses left at 10, right at 40
        car1_detections = []
        for frame in range(0, 51):
            x_pos = 50 + (frame * 10)  # Moves right
            bbox = BoundingBox(x1=x_pos-50, y1=200, x2=x_pos+50, y2=400)
            detection = DetectionResult(
                frame_number=frame,
                bounding_box=bbox,
                confidence=0.85,
                class_id=2,
                class_name="car"
            )
            car1_detections.append(detection)
        
        # Process first car
        tracked_cars = []
        for detection in car1_detections:
            cars = tracker.update([detection], detection.frame_number)
            for car in cars:
                if car.track_id == 1:
                    crossing_detector.detect_crossings(car, detection.frame_number)
                    tracked_cars = cars
        
        car1 = [c for c in tracked_cars if c.track_id == 1][0]
        assert car1.is_complete(), "First car should complete crossing"
        assert car1.left_crossing_frame is not None
        assert car1.right_crossing_frame is not None
        
        # Second car: frames 60-110, crosses left at 70, right at 100
        car2_detections = []
        for frame in range(60, 111):
            x_pos = 50 + ((frame - 60) * 10)
            bbox = BoundingBox(x1=x_pos-50, y1=200, x2=x_pos+50, y2=400)
            detection = DetectionResult(
                frame_number=frame,
                bounding_box=bbox,
                confidence=0.85,
                class_id=2,
                class_name="car"
            )
            car2_detections.append(detection)
        
        # Process second car
        for detection in car2_detections:
            cars = tracker.update([detection], detection.frame_number)
            for car in cars:
                if car.track_id == 2:
                    crossing_detector.detect_crossings(car, detection.frame_number)
        
        # Verify both cars are tracked
        all_tracked = tracker.update([], 111)
        car2 = [c for c in all_tracked if c.track_id == 2][0]
        assert car2.is_complete(), "Second car should complete crossing"
        assert len([c for c in all_tracked if c.is_complete()]) == 2

    def test_multiple_speed_measurements(self, sample_config):
        """Test that multiple speed measurements can be calculated."""
        from src.services.speed_calculator import SpeedCalculator
        
        calculator = SpeedCalculator(sample_config)
        
        # Create two completed cars
        car1 = TrackedCar(track_id=1)
        car1.left_crossing_frame = 10
        car1.right_crossing_frame = 40
        for i in range(10, 41):
            bbox = BoundingBox(x1=i*10, y1=200, x2=i*10+100, y2=400)
            detection = DetectionResult(
                frame_number=i,
                bounding_box=bbox,
                confidence=0.85,
                class_id=2,
                class_name="car"
            )
            car1.add_detection(detection)
        
        car2 = TrackedCar(track_id=2)
        car2.left_crossing_frame = 70
        car2.right_crossing_frame = 100
        for i in range(70, 101):
            bbox = BoundingBox(x1=i*10, y1=200, x2=i*10+100, y2=400)
            detection = DetectionResult(
                frame_number=i,
                bounding_box=bbox,
                confidence=0.80,
                class_id=2,
                class_name="car"
            )
            car2.add_detection(detection)
        
        # Calculate speeds
        speed1 = calculator.calculate_from_tracked_car(car1)
        speed2 = calculator.calculate_from_tracked_car(car2)
        
        assert speed1.is_valid
        assert speed2.is_valid
        assert speed1.track_id == 1
        assert speed2.track_id == 2
        assert speed1.speed_kmh > 0
        assert speed2.speed_kmh > 0

    def test_continuation_after_car_completion(self, sample_config):
        """Test that processing continues after a car completes crossing."""
        from src.services.car_tracker import CarTracker
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        tracker = CarTracker()
        crossing_detector = CoordinateCrossingDetector(sample_config)
        
        completed_cars = []
        
        # Simulate processing frames with multiple cars
        # Car 1: frames 0-50
        for frame in range(0, 51):
            x_pos = 50 + (frame * 10)
            bbox = BoundingBox(x1=x_pos-50, y1=200, x2=x_pos+50, y2=400)
            detection = DetectionResult(
                frame_number=frame,
                bounding_box=bbox,
                confidence=0.85,
                class_id=2,
                class_name="car"
            )
            cars = tracker.update([detection], frame)
            for car in cars:
                if car.track_id == 1:
                    crossing_detector.detect_crossings(car, frame)
                    if car.is_complete() and car not in completed_cars:
                        completed_cars.append(car)
        
        # Verify first car completed
        assert len(completed_cars) == 1
        assert completed_cars[0].track_id == 1
        
        # Car 2: frames 60-110 (gap between cars)
        for frame in range(60, 111):
            x_pos = 50 + ((frame - 60) * 10)
            bbox = BoundingBox(x1=x_pos-50, y1=200, x2=x_pos+50, y2=400)
            detection = DetectionResult(
                frame_number=frame,
                bounding_box=bbox,
                confidence=0.85,
                class_id=2,
                class_name="car"
            )
            cars = tracker.update([detection], frame)
            for car in cars:
                if car.track_id == 2:
                    crossing_detector.detect_crossings(car, frame)
                    if car.is_complete() and car not in completed_cars:
                        completed_cars.append(car)
        
        # Verify both cars completed
        assert len(completed_cars) == 2
        assert completed_cars[1].track_id == 2

