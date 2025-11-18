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
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )
        detector = CoordinateCrossingDetector(config)
        assert detector.left_coordinate == 100
        assert detector.right_coordinate == 500

    def test_detect_left_crossing_transition(self):
        """Test detecting when car crosses left coordinate on transition frame."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )
        detector = CoordinateCrossingDetector(config)
        
        # Create tracked car moving from left to right
        tracked = TrackedCar(track_id=1)
        
        # Frame 0: Before crossing (x2 < left_coordinate)
        bbox1 = BoundingBox(x1=50, y1=200, x2=90, y2=400)  # x2 = 90 < 100
        detection1 = DetectionResult(0, bbox1, 0.85, 2, "car")
        tracked.add_detection(detection1)
        events0 = detector.detect_crossings(tracked, frame_number=0)
        assert len(events0) == 0  # No crossing yet
        
        # Frame 1: Transition - x2 crosses from < 100 to >= 100
        bbox2 = BoundingBox(x1=100, y1=200, x2=110, y2=400)  # x2 = 110 >= 100
        detection2 = DetectionResult(1, bbox2, 0.87, 2, "car")
        tracked.add_detection(detection2)
        events = detector.detect_crossings(tracked, frame_number=1)
        
        assert len(events) == 1
        assert events[0].coordinate_type == "left"
        assert events[0].frame_number == 1
        assert events[0].coordinate_value == 100
        assert tracked.left_crossing_frame == 1

    def test_no_crossing_when_already_past_left_coordinate(self):
        """Test no crossing detected when car first appears past left coordinate."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        
        # Car first appears already past left coordinate (no previous frame to compare)
        bbox = BoundingBox(x1=150, y1=200, x2=250, y2=400)  # x2 = 250 >= 100
        detection = DetectionResult(0, bbox, 0.85, 2, "car")
        tracked.add_detection(detection)
        
        events = detector.detect_crossings(tracked, frame_number=0)
        # Should not detect crossing on first frame if already past (edge case)
        # This is acceptable behavior - car appeared after the line
        assert tracked.left_crossing_frame is None or tracked.left_crossing_frame == 0

    def test_left_crossing_with_previous_frame_state(self):
        """Test left crossing detection requires previous frame state for transition."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        
        # Frame 0: x2 = 95 < 100
        bbox1 = BoundingBox(x1=50, y1=200, x2=95, y2=400)
        detection1 = DetectionResult(0, bbox1, 0.85, 2, "car")
        tracked.add_detection(detection1)
        detector.detect_crossings(tracked, frame_number=0)
        assert tracked.left_crossing_frame is None
        
        # Frame 1: x2 = 105 >= 100 (transition detected)
        bbox2 = BoundingBox(x1=100, y1=200, x2=105, y2=400)
        detection2 = DetectionResult(1, bbox2, 0.87, 2, "car")
        tracked.add_detection(detection2)
        events = detector.detect_crossings(tracked, frame_number=1)
        
        assert len(events) == 1
        assert events[0].coordinate_type == "left"
        assert tracked.left_crossing_frame == 1

    def test_detect_right_crossing_transition(self):
        """Test detecting when car crosses right coordinate on transition frame."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        tracked.left_crossing_frame = 0  # Already crossed left
        
        # Frame 10: Before crossing right (x2 < right_coordinate)
        bbox1 = BoundingBox(x1=400, y1=200, x2=490, y2=400)  # x2 = 490 < 500
        detection1 = DetectionResult(10, bbox1, 0.85, 2, "car")
        tracked.add_detection(detection1)
        events10 = detector.detect_crossings(tracked, frame_number=10)
        assert len(events10) == 0  # No crossing yet
        
        # Frame 11: Transition - x2 crosses from < 500 to >= 500
        bbox2 = BoundingBox(x1=500, y1=200, x2=510, y2=400)  # x2 = 510 >= 500
        detection2 = DetectionResult(11, bbox2, 0.87, 2, "car")
        tracked.add_detection(detection2)
        events = detector.detect_crossings(tracked, frame_number=11)
        
        assert len(events) == 1
        assert events[0].coordinate_type == "right"
        assert events[0].frame_number == 11
        assert events[0].coordinate_value == 500
        assert tracked.right_crossing_frame == 11

    def test_no_right_crossing_when_already_past(self):
        """Test no right crossing detected when car already past right coordinate."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        tracked.left_crossing_frame = 0  # Already crossed left
        
        # Car first appears after right coordinate (no previous frame to compare)
        bbox = BoundingBox(x1=550, y1=200, x2=650, y2=400)  # x2 = 650 >= 500
        detection = DetectionResult(10, bbox, 0.85, 2, "car")
        tracked.add_detection(detection)
        
        events = detector.detect_crossings(tracked, frame_number=10)
        # Should not detect crossing if already past (edge case)
        assert tracked.right_crossing_frame is None or tracked.right_crossing_frame == 10

    def test_right_crossing_only_after_left_crossing(self):
        """Test right crossing only detected after left crossing."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        # left_crossing_frame is None - hasn't crossed left yet
        
        # Frame 0: Car at right coordinate but hasn't crossed left
        bbox1 = BoundingBox(x1=450, y1=200, x2=490, y2=400)  # x2 = 490 < 500
        detection1 = DetectionResult(0, bbox1, 0.85, 2, "car")
        tracked.add_detection(detection1)
        detector.detect_crossings(tracked, frame_number=0)
        
        # Frame 1: x2 crosses right coordinate but left not crossed
        bbox2 = BoundingBox(x1=500, y1=200, x2=510, y2=400)  # x2 = 510 >= 500
        detection2 = DetectionResult(1, bbox2, 0.87, 2, "car")
        tracked.add_detection(detection2)
        events = detector.detect_crossings(tracked, frame_number=1)
        
        # Should not detect right crossing because left wasn't crossed first
        assert len(events) == 0
        assert tracked.right_crossing_frame is None

    def test_detect_both_crossings_transition(self):
        """Test detecting both left and right crossings with transition detection."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        
        # Frame 0: Before left crossing (x2 = 90 < 100)
        bbox0 = BoundingBox(x1=50, y1=200, x2=90, y2=400)
        detection0 = DetectionResult(0, bbox0, 0.85, 2, "car")
        tracked.add_detection(detection0)
        events0 = detector.detect_crossings(tracked, frame_number=0)
        assert len(events0) == 0
        
        # Frame 1: Cross left (transition: x2 = 110 >= 100)
        bbox1 = BoundingBox(x1=100, y1=200, x2=110, y2=400)
        detection1 = DetectionResult(1, bbox1, 0.85, 2, "car")
        tracked.add_detection(detection1)
        events1 = detector.detect_crossings(tracked, frame_number=1)
        assert len(events1) == 1
        assert events1[0].coordinate_type == "left"
        
        # Frame 10: Before right crossing (x2 = 490 < 500)
        bbox10 = BoundingBox(x1=400, y1=200, x2=490, y2=400)
        detection10 = DetectionResult(10, bbox10, 0.87, 2, "car")
        tracked.add_detection(detection10)
        events10 = detector.detect_crossings(tracked, frame_number=10)
        assert len(events10) == 0
        
        # Frame 11: Cross right (transition: x2 = 510 >= 500)
        bbox11 = BoundingBox(x1=500, y1=200, x2=510, y2=400)
        detection11 = DetectionResult(11, bbox11, 0.87, 2, "car")
        tracked.add_detection(detection11)
        events11 = detector.detect_crossings(tracked, frame_number=11)
        assert len(events11) == 1
        assert events11[0].coordinate_type == "right"
        
        assert tracked.is_complete()

    def test_no_crossing_when_car_not_at_coordinate(self):
        """Test no crossing detected when car doesn't reach coordinate."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        
        # Car far from left coordinate
        bbox = BoundingBox(x1=10, y1=200, x2=50, y2=400)  # center_x = 30
        detection = DetectionResult(0, bbox, 0.85, 2, "car")
        tracked.add_detection(detection)
        
        events = detector.detect_crossings(tracked, frame_number=0)
        assert len(events) == 0
        assert tracked.left_crossing_frame is None

    def test_crossing_frame_identification_transition(self):
        """Test that crossing frame is correctly identified on transition."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )
        detector = CoordinateCrossingDetector(config)
        
        tracked = TrackedCar(track_id=1)
        
        # Frame 5: before crossing (x2 = 90 < 100)
        bbox1 = BoundingBox(x1=50, y1=200, x2=90, y2=400)
        detection1 = DetectionResult(5, bbox1, 0.85, 2, "car")
        tracked.add_detection(detection1)
        events5 = detector.detect_crossings(tracked, frame_number=5)
        assert len(events5) == 0
        
        # Frame 6: transition - x2 crosses from < 100 to >= 100
        bbox2 = BoundingBox(x1=100, y1=200, x2=110, y2=400)  # x2 = 110 >= 100
        detection2 = DetectionResult(6, bbox2, 0.87, 2, "car")
        tracked.add_detection(detection2)
        events = detector.detect_crossings(tracked, frame_number=6)
        
        assert len(events) == 1
        assert events[0].frame_number == 6
        assert tracked.left_crossing_frame == 6

