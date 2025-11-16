"""Unit tests for car tracker."""

import pytest
from src.models import DetectionResult, BoundingBox, TrackedCar


class TestCarTracker:
    """Test car tracking functionality."""

    def test_initialize_tracker(self):
        """Test initializing tracker."""
        from src.services.car_tracker import CarTracker
        
        tracker = CarTracker()
        assert tracker.tracked_cars == {}
        assert tracker.next_track_id == 1

    def test_track_single_car(self):
        """Test tracking a single car across frames."""
        from src.services.car_tracker import CarTracker
        
        tracker = CarTracker()
        
        # First detection
        bbox1 = BoundingBox(x1=100, y1=200, x2=300, y2=400)
        detection1 = DetectionResult(
            frame_number=0,
            bounding_box=bbox1,
            confidence=0.85,
            class_id=2,
            class_name="car"
        )
        
        tracked = tracker.update([detection1], frame_number=0)
        assert len(tracked) == 1
        assert tracked[0].track_id == 1
        assert tracked[0].first_detection_frame == 0
        assert len(tracked[0].detections) == 1

    def test_track_car_across_frames(self):
        """Test tracking same car across multiple frames using IoU."""
        from src.services.car_tracker import CarTracker
        
        tracker = CarTracker()
        
        # Frame 0: Car at position 100
        bbox1 = BoundingBox(x1=100, y1=200, x2=300, y2=400)
        detection1 = DetectionResult(
            frame_number=0,
            bounding_box=bbox1,
            confidence=0.85,
            class_id=2,
            class_name="car"
        )
        
        tracked1 = tracker.update([detection1], frame_number=0)
        track_id = tracked1[0].track_id
        
        # Frame 1: Car moved slightly (high IoU overlap)
        bbox2 = BoundingBox(x1=110, y1=200, x2=310, y2=400)  # Moved 10px right
        detection2 = DetectionResult(
            frame_number=1,
            bounding_box=bbox2,
            confidence=0.87,
            class_id=2,
            class_name="car"
        )
        
        tracked2 = tracker.update([detection2], frame_number=1)
        assert len(tracked2) == 1
        assert tracked2[0].track_id == track_id  # Same track ID
        assert tracked2[0].last_detection_frame == 1
        assert len(tracked2[0].detections) == 2

    def test_track_multiple_cars(self):
        """Test tracking multiple cars simultaneously."""
        from src.services.car_tracker import CarTracker
        
        tracker = CarTracker()
        
        # Two cars in frame 0
        bbox1 = BoundingBox(x1=100, y1=200, x2=300, y2=400)
        detection1 = DetectionResult(0, bbox1, 0.85, 2, "car")
        
        bbox2 = BoundingBox(x1=500, y1=200, x2=700, y2=400)
        detection2 = DetectionResult(0, bbox2, 0.90, 2, "car")
        
        tracked = tracker.update([detection1, detection2], frame_number=0)
        assert len(tracked) == 2
        assert tracked[0].track_id != tracked[1].track_id

    def test_track_id_assignment(self):
        """Test that track IDs are assigned sequentially."""
        from src.services.car_tracker import CarTracker
        
        tracker = CarTracker()
        
        # First car
        bbox1 = BoundingBox(x1=100, y1=200, x2=300, y2=400)
        detection1 = DetectionResult(0, bbox1, 0.85, 2, "car")
        tracked1 = tracker.update([detection1], frame_number=0)
        
        # Second car (different position, low IoU)
        bbox2 = BoundingBox(x1=500, y1=200, x2=700, y2=400)
        detection2 = DetectionResult(0, bbox2, 0.90, 2, "car")
        tracked2 = tracker.update([detection2], frame_number=1)
        
        assert tracked1[0].track_id == 1
        assert tracked2[0].track_id == 2

    def test_track_lost_car_reappears(self):
        """Test handling when a tracked car disappears and reappears."""
        from src.services.car_tracker import CarTracker
        
        tracker = CarTracker()
        
        # Car appears in frame 0
        bbox1 = BoundingBox(x1=100, y1=200, x2=300, y2=400)
        detection1 = DetectionResult(0, bbox1, 0.85, 2, "car")
        tracked1 = tracker.update([detection1], frame_number=0)
        track_id = tracked1[0].track_id
        
        # Car disappears in frame 1
        tracked2 = tracker.update([], frame_number=1)
        assert len(tracked2) == 0
        
        # Car reappears in frame 2 (should get new track ID if IoU too low)
        bbox3 = BoundingBox(x1=600, y1=200, x2=800, y2=400)  # Far away
        detection3 = DetectionResult(2, bbox3, 0.85, 2, "car")
        tracked3 = tracker.update([detection3], frame_number=2)
        
        # Should get new track ID since too far (low IoU)
        assert tracked3[0].track_id != track_id

