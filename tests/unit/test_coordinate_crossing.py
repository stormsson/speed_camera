"""Unit tests for coordinate crossing detector."""

import pytest
from src.models import (
    TrackedCar,
    DetectionResult,
    BoundingBox,
    CoordinateCrossingEvent,
    Configuration,
)


class TestCoordinateCrossingDetector:
    """Test coordinate crossing detection functionality."""

    def test_initialize_detector(self):
        """Test initializing coordinate crossing detector."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0
        )
        detector = CoordinateCrossingDetector(config)
        assert detector.left_coordinate == 100
        assert detector.right_coordinate == 500

    def test_detect_left_crossing(self):
        """Test detecting when car crosses left coordinate."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(100, 500, 200.0, 30.0)
        detector = CoordinateCrossingDetector(config)
        
        # Create tracked car moving from left to right
        tracked = TrackedCar(track_id=1)
        
        # Before crossing (center_x < left_coordinate)
        bbox1 = BoundingBox(x1=50, y1=200, x2=150, y2=400)  # center_x = 100
        detection1 = DetectionResult(0, bbox1, 0.85, 2, "car")
        tracked.add_detection(detection1)
        
        # Crossing left coordinate (center_x >= left_coordinate)
        bbox2 = BoundingBox(x1=100, y1=200, x2=200, y2=400)  # center_x = 150
        detection2 = DetectionResult(1, bbox2, 0.87, 2, "car")
        tracked.add_detection(detection2)
        
        events = detector.detect_crossings(tracked, frame_number=1)
        
        assert len(events) == 1
        assert events[0].coordinate_type == "left"
        assert events[0].frame_number == 1
        assert events[0].coordinate_value == 100
        assert tracked.left_crossing_frame == 1

    def test_detect_right_crossing(self):
        """Test detecting when car crosses right coordinate."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(100, 500, 200.0, 30.0)
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        tracked.left_crossing_frame = 0  # Already crossed left
        
        # Before crossing right (center_x < right_coordinate)
        bbox1 = BoundingBox(x1=400, y1=200, x2=500, y2=400)  # center_x = 450
        detection1 = DetectionResult(10, bbox1, 0.85, 2, "car")
        tracked.add_detection(detection1)
        
        # Crossing right coordinate (center_x >= right_coordinate)
        bbox2 = BoundingBox(x1=500, y1=200, x2=600, y2=400)  # center_x = 550
        detection2 = DetectionResult(11, bbox2, 0.87, 2, "car")
        tracked.add_detection(detection2)
        
        events = detector.detect_crossings(tracked, frame_number=11)
        
        assert len(events) == 1
        assert events[0].coordinate_type == "right"
        assert events[0].frame_number == 11
        assert events[0].coordinate_value == 500
        assert tracked.right_crossing_frame == 11

    def test_detect_both_crossings(self):
        """Test detecting both left and right crossings."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(100, 500, 200.0, 30.0)
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        
        # Cross left
        bbox1 = BoundingBox(x1=50, y1=200, x2=150, y2=400)  # center_x = 100
        detection1 = DetectionResult(0, bbox1, 0.85, 2, "car")
        tracked.add_detection(detection1)
        events1 = detector.detect_crossings(tracked, frame_number=0)
        assert len(events1) == 1
        assert events1[0].coordinate_type == "left"
        
        # Cross right
        bbox2 = BoundingBox(x1=500, y1=200, x2=600, y2=400)  # center_x = 550
        detection2 = DetectionResult(10, bbox2, 0.87, 2, "car")
        tracked.add_detection(detection2)
        events2 = detector.detect_crossings(tracked, frame_number=10)
        assert len(events2) == 1
        assert events2[0].coordinate_type == "right"
        
        assert tracked.is_complete()

    def test_no_crossing_when_car_not_at_coordinate(self):
        """Test no crossing detected when car doesn't reach coordinate."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(100, 500, 200.0, 30.0)
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        
        # Car far from left coordinate
        bbox = BoundingBox(x1=10, y1=200, x2=50, y2=400)  # center_x = 30
        detection = DetectionResult(0, bbox, 0.85, 2, "car")
        tracked.add_detection(detection)
        
        events = detector.detect_crossings(tracked, frame_number=0)
        assert len(events) == 0
        assert tracked.left_crossing_frame is None

    def test_crossing_frame_identification(self):
        """Test that crossing frame is correctly identified."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(100, 500, 200.0, 30.0)
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        
        # Frame 5: before crossing
        bbox1 = BoundingBox(x1=50, y1=200, x2=90, y2=400)  # center_x = 70
        detection1 = DetectionResult(5, bbox1, 0.85, 2, "car")
        tracked.add_detection(detection1)
        detector.detect_crossings(tracked, frame_number=5)
        
        # Frame 6: crosses left coordinate
        bbox2 = BoundingBox(x1=100, y1=200, x2=200, y2=400)  # center_x = 150
        detection2 = DetectionResult(6, bbox2, 0.87, 2, "car")
        tracked.add_detection(detection2)
        events = detector.detect_crossings(tracked, frame_number=6)
        
        assert len(events) == 1
        assert events[0].frame_number == 6
        assert tracked.left_crossing_frame == 6

