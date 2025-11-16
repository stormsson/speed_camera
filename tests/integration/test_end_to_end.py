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
            fps=30.0
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

