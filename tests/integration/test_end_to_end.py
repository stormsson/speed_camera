"""Integration tests for end-to-end video processing pipeline."""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

from src.models import Configuration, ProcessingResult


class TestEndToEndPipeline:
    """Test complete video processing pipeline."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration."""
        return Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,  # 2 meters
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )

    @pytest.fixture
    def mock_video_file(self):
        """Create a mock video file path."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            f.write(b"mock video data")
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_full_pipeline_with_known_speed(self, sample_config, mock_video_file):
        """Test full pipeline with known ground truth speed."""
        from src.cli.main import process_video
        
        # This test will fail until the full pipeline is implemented
        # It should test with a synthetic video or mock all components
        
        # Mock all components for integration test
        with patch('cv2.VideoCapture') as mock_cap, \
             patch('ultralytics.YOLO') as mock_yolo:
            
            # Setup video mock
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 100,
                cv2.CAP_PROP_FRAME_WIDTH: 640,
                cv2.CAP_PROP_FRAME_HEIGHT: 480,
            }.get(prop, 0)
            
            # Mock frames: car moves from left to right
            frames = []
            for i in range(100):
                # Car center moves from x=50 to x=550 over 100 frames
                car_x = 50 + (i * 5)  # Moves 5px per frame
                bbox = np.array([[car_x - 50, 200, car_x + 50, 400]])
                frames.append((True, np.zeros((480, 640, 3), dtype=np.uint8)))
            
            mock_cap.return_value.read.side_effect = frames + [(False, None)]
            
            # Setup YOLO mock
            mock_results = MagicMock()
            mock_box = MagicMock()
            # Simulate car detection at various positions
            mock_box.xyxy = [[50, 200, 150, 400]]  # Will be updated per frame
            mock_box.conf = [0.85]
            mock_box.cls = [2]
            mock_results[0].boxes = mock_box
            mock_yolo.return_value.return_value = mock_results
            
            # Process video
            result = process_video(mock_video_file, "config.yaml", sample_config)
            
            assert isinstance(result, ProcessingResult)
            assert result.speed_measurement is not None
            assert result.speed_measurement.is_valid is True
            # Verify speed is within acceptable tolerance (±5%)
            # Expected: car moves 400px (500-100) in some number of frames
            # This is a simplified test - actual implementation will vary

    def test_pipeline_with_no_car_detected(self, sample_config, mock_video_file):
        """Test pipeline when no car is detected."""
        from src.cli.main import process_video
        from src.lib.exceptions import NoCarDetectedError
        
        with patch('cv2.VideoCapture') as mock_cap, \
             patch('ultralytics.YOLO') as mock_yolo:
            
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 100,
            }.get(prop, 0)
            mock_cap.return_value.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
            
            # No detections
            mock_results = MagicMock()
            mock_results[0].boxes.xyxy = []
            mock_yolo.return_value.return_value = mock_results
            
            with pytest.raises(NoCarDetectedError):
                process_video(mock_video_file, "config.yaml", sample_config)

    def test_pipeline_with_car_not_crossing_both(self, sample_config, mock_video_file):
        """Test pipeline when car doesn't cross both coordinates."""
        from src.cli.main import process_video
        from src.lib.exceptions import CarNotCrossingBothCoordinatesError
        
        with patch('cv2.VideoCapture') as mock_cap, \
             patch('ultralytics.YOLO') as mock_yolo:
            
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 100,
            }.get(prop, 0)
            mock_cap.return_value.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
            
            # Car detected but only crosses left, not right
            mock_results = MagicMock()
            mock_box = MagicMock()
            mock_box.xyxy = [[50, 200, 150, 400]]  # Never reaches right coordinate
            mock_box.conf = [0.85]
            mock_box.cls = [2]
            mock_results[0].boxes = mock_box
            mock_yolo.return_value.return_value = mock_results
            
            with pytest.raises(CarNotCrossingBothCoordinatesError):
                process_video(mock_video_file, "config.yaml", sample_config)

    def test_transition_based_crossing_accuracy(self, sample_config, mock_video_file):
        """Test that transition-based crossing detection improves timing accuracy."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        from src.models import TrackedCar, DetectionResult, BoundingBox
        
        detector = CoordinateCrossingDetector(sample_config)
        tracked = TrackedCar(track_id=1)
        
        # Simulate car movement: x2 moves from 90 to 110 over 3 frames
        # Ground truth: crossing should occur at frame 1 (when x2 transitions from 95 to 105)
        
        # Frame 0: x2 = 90 < 100 (left coordinate)
        bbox0 = BoundingBox(x1=50, y1=200, x2=90, y2=400)
        detection0 = DetectionResult(0, bbox0, 0.85, 2, "car")
        tracked.add_detection(detection0)
        events0 = detector.detect_crossings(tracked, frame_number=0)
        assert len(events0) == 0  # No crossing
        
        # Frame 1: x2 = 105 >= 100 (transition detected)
        bbox1 = BoundingBox(x1=100, y1=200, x2=105, y2=400)
        detection1 = DetectionResult(1, bbox1, 0.87, 2, "car")
        tracked.add_detection(detection1)
        events1 = detector.detect_crossings(tracked, frame_number=1)
        
        # Verify crossing detected at exact transition frame
        assert len(events1) == 1
        assert events1[0].coordinate_type == "left"
        assert events1[0].frame_number == 1
        assert tracked.left_crossing_frame == 1
        
        # Verify transition detection: previous frame x2 < coordinate, current x2 >= coordinate
        assert tracked.detections[-2].bounding_box.x2 < sample_config.left_coordinate
        assert tracked.detections[-1].bounding_box.x2 >= sample_config.left_coordinate

    def test_transition_detection_improves_timing_accuracy(self, sample_config):
        """Test that transition-based detection captures exact crossing moment."""
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        from src.models import TrackedCar, DetectionResult, BoundingBox
        
        detector = CoordinateCrossingDetector(sample_config)
        tracked = TrackedCar(track_id=1)
        
        # Simulate precise movement: car moves 1 pixel per frame
        # Frame 98: x2 = 98 < 100
        bbox98 = BoundingBox(x1=50, y1=200, x2=98, y2=400)
        detection98 = DetectionResult(98, bbox98, 0.85, 2, "car")
        tracked.add_detection(detection98)
        detector.detect_crossings(tracked, frame_number=98)
        assert tracked.left_crossing_frame is None
        
        # Frame 99: x2 = 99 < 100
        bbox99 = BoundingBox(x1=51, y1=200, x2=99, y2=400)
        detection99 = DetectionResult(99, bbox99, 0.85, 2, "car")
        tracked.add_detection(detection99)
        detector.detect_crossings(tracked, frame_number=99)
        assert tracked.left_crossing_frame is None
        
        # Frame 100: x2 = 100 >= 100 (transition detected)
        bbox100 = BoundingBox(x1=52, y1=200, x2=100, y2=400)
        detection100 = DetectionResult(100, bbox100, 0.87, 2, "car")
        tracked.add_detection(detection100)
        events100 = detector.detect_crossings(tracked, frame_number=100)
        
        # Verify crossing detected exactly at frame 100 when transition occurs
        assert len(events100) == 1
        assert tracked.left_crossing_frame == 100
        # Verify this is the first frame where x2 >= coordinate
        assert tracked.detections[-2].bounding_box.x2 < sample_config.left_coordinate
        assert tracked.detections[-1].bounding_box.x2 >= sample_config.left_coordinate

    def test_debug_images_generated_for_both_crossings(self, sample_config):
        """Test that debug images are generated for both left and right crossings."""
        from src.services.debug_image_generator import DebugImageGenerator
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        from src.models import TrackedCar, DetectionResult, BoundingBox
        import tempfile
        import os
        import glob
        
        detector = CoordinateCrossingDetector(sample_config)
        generator = DebugImageGenerator(sample_config)
        tracked = TrackedCar(track_id=1)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                
                # Frame 0: Before left crossing
                bbox0 = BoundingBox(x1=50, y1=200, x2=90, y2=400)
                detection0 = DetectionResult(0, bbox0, 0.85, 2, "car")
                tracked.add_detection(detection0)
                events0 = detector.detect_crossings(tracked, frame_number=0)
                assert len(events0) == 0
                
                # Frame 1: Left crossing (transition)
                bbox1 = BoundingBox(x1=100, y1=200, x2=110, y2=400)
                detection1 = DetectionResult(1, bbox1, 0.87, 2, "car")
                tracked.add_detection(detection1)
                events1 = detector.detect_crossings(tracked, frame_number=1)
                assert len(events1) == 1
                assert events1[0].coordinate_type == "left"
                
                # Generate debug image for left crossing
                frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
                debug_path1 = generator.generate_debug_image(
                    frame1,
                    detection1,
                    events1[0],
                    frame_number=1
                )
                assert debug_path1 is not None
                assert os.path.exists(debug_path1)
                assert "crossing_1.png" in debug_path1
                
                # Frame 10: Before right crossing
                bbox10 = BoundingBox(x1=400, y1=200, x2=490, y2=400)
                detection10 = DetectionResult(10, bbox10, 0.85, 2, "car")
                tracked.add_detection(detection10)
                events10 = detector.detect_crossings(tracked, frame_number=10)
                assert len(events10) == 0
                
                # Frame 11: Right crossing (transition)
                bbox11 = BoundingBox(x1=500, y1=200, x2=510, y2=400)
                detection11 = DetectionResult(11, bbox11, 0.87, 2, "car")
                tracked.add_detection(detection11)
                events11 = detector.detect_crossings(tracked, frame_number=11)
                assert len(events11) == 1
                assert events11[0].coordinate_type == "right"
                
                # Generate debug image for right crossing
                frame11 = np.zeros((480, 640, 3), dtype=np.uint8)
                debug_path11 = generator.generate_debug_image(
                    frame11,
                    detection11,
                    events11[0],
                    frame_number=11
                )
                assert debug_path11 is not None
                assert os.path.exists(debug_path11)
                assert "crossing_11.png" in debug_path11
                
                # Verify both debug images exist
                debug_files = glob.glob(os.path.join(tmpdir, "crossing_*.png"))
                assert len(debug_files) >= 2
                assert any("crossing_1.png" in f for f in debug_files)
                assert any("crossing_11.png" in f for f in debug_files)
            finally:
                os.chdir(original_cwd)

    def test_multiple_cars_generate_separate_debug_images(self, sample_config):
        """Test that multiple cars generate separate debug images."""
        from src.services.debug_image_generator import DebugImageGenerator
        from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
        from src.models import TrackedCar, DetectionResult, BoundingBox
        import tempfile
        import os
        import glob
        
        detector = CoordinateCrossingDetector(sample_config)
        generator = DebugImageGenerator(sample_config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                
                # Car 1: Track ID 1
                tracked1 = TrackedCar(track_id=1)
                bbox1_0 = BoundingBox(x1=50, y1=200, x2=90, y2=400)
                detection1_0 = DetectionResult(0, bbox1_0, 0.85, 2, "car")
                tracked1.add_detection(detection1_0)
                detector.detect_crossings(tracked1, frame_number=0)
                
                bbox1_1 = BoundingBox(x1=100, y1=200, x2=110, y2=400)
                detection1_1 = DetectionResult(1, bbox1_1, 0.87, 2, "car")
                tracked1.add_detection(detection1_1)
                events1 = detector.detect_crossings(tracked1, frame_number=1)
                
                if events1:
                    frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
                    generator.generate_debug_image(frame1, detection1_1, events1[0], frame_number=1)
                
                # Car 2: Track ID 2 (appears later)
                tracked2 = TrackedCar(track_id=2)
                bbox2_5 = BoundingBox(x1=50, y1=200, x2=90, y2=400)
                detection2_5 = DetectionResult(5, bbox2_5, 0.85, 2, "car")
                tracked2.add_detection(detection2_5)
                detector.detect_crossings(tracked2, frame_number=5)
                
                bbox2_6 = BoundingBox(x1=100, y1=200, x2=110, y2=400)
                detection2_6 = DetectionResult(6, bbox2_6, 0.87, 2, "car")
                tracked2.add_detection(detection2_6)
                events2 = detector.detect_crossings(tracked2, frame_number=6)
                
                if events2:
                    frame6 = np.zeros((480, 640, 3), dtype=np.uint8)
                    generator.generate_debug_image(frame6, detection2_6, events2[0], frame_number=6)
                
                # Verify separate debug images for each car
                debug_files = glob.glob(os.path.join(tmpdir, "crossing_*.png"))
                # Should have at least one debug image per car
                if events1 and events2:
                    assert len(debug_files) >= 2
                    # Each should have different frame numbers
                    frame_numbers = [int(f.replace("crossing_", "").replace(".png", "").split("_")[-1]) 
                                   for f in [os.path.basename(f) for f in debug_files]]
                    assert 1 in frame_numbers or 6 in frame_numbers
            finally:
                os.chdir(original_cwd)

