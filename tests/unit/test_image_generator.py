"""Unit tests for image generator service."""

import pytest
from unittest.mock import MagicMock, patch, Mock
import numpy as np
import cv2
from pathlib import Path

from src.services.image_generator import ImageGenerator
from src.models import (
    TrackedCar,
    DetectionResult,
    BoundingBox,
    Configuration,
    SpeedMeasurement,
)


@pytest.fixture
def sample_config():
    """Create a sample configuration."""
    return Configuration(
        left_coordinate=100,
        right_coordinate=500,
        distance=200.0,
        fps=30.0
    )


@pytest.fixture
def sample_tracked_car():
    """Create a sample tracked car with crossings."""
    car = TrackedCar(track_id=1)
    
    # Add detections
    bbox1 = BoundingBox(x1=50, y1=100, x2=200, y2=250)
    detection1 = DetectionResult(
        frame_number=100,
        bounding_box=bbox1,
        confidence=0.85,
        class_id=2,
        class_name="car"
    )
    car.add_detection(detection1)
    
    bbox2 = BoundingBox(x1=450, y1=100, x2=600, y2=250)
    detection2 = DetectionResult(
        frame_number=130,
        bounding_box=bbox2,
        confidence=0.90,
        class_id=2,
        class_name="car"
    )
    car.add_detection(detection2)
    
    car.left_crossing_frame = 100
    car.right_crossing_frame = 130
    
    return car


@pytest.fixture
def sample_speed_measurement():
    """Create a sample speed measurement."""
    return SpeedMeasurement(
        speed_kmh=45.2,
        speed_ms=12.56,
        frame_count=30,
        time_seconds=1.0,
        distance_meters=2.0,
        left_crossing_frame=100,
        right_crossing_frame=130,
        track_id=1,
        confidence=0.875,
        is_valid=True
    )


class TestImageGenerator:
    """Test image generator service."""

    def test_initialization(self, sample_config):
        """Test image generator initialization."""
        generator = ImageGenerator(sample_config)
        assert generator.config == sample_config
        assert generator.left_coordinate == 100
        assert generator.right_coordinate == 500

    @patch('src.services.image_generator.cv2')
    def test_create_composite_image(self, mock_cv2, sample_config):
        """Test composite image creation."""
        # Setup mocks
        left_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        right_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        mock_cv2.hconcat.return_value = np.zeros((480, 1280, 3), dtype=np.uint8)
        
        generator = ImageGenerator(sample_config)
        result = generator.create_composite_image(left_frame, right_frame)
        
        # Verify cv2.hconcat was called
        mock_cv2.hconcat.assert_called_once()
        assert result is not None

    @patch('src.services.image_generator.cv2')
    def test_draw_vertical_bar(self, mock_cv2, sample_config):
        """Test vertical bar drawing."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        generator = ImageGenerator(sample_config)
        
        annotated_frame = generator.draw_vertical_bar(frame, 100, (0, 255, 0))
        
        # Verify cv2.line was called to draw the vertical bar
        assert mock_cv2.line.called
        call_args = mock_cv2.line.call_args
        assert call_args[0][0] is frame or call_args[0][0] is annotated_frame
        # Check that line is drawn at x=100
        assert call_args[0][1][0] == 100  # x coordinate

    @patch('src.services.image_generator.cv2')
    def test_draw_bounding_box(self, mock_cv2, sample_config):
        """Test bounding box annotation."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        bbox = BoundingBox(x1=50, y1=100, x2=200, y2=250)
        generator = ImageGenerator(sample_config)
        
        annotated_frame = generator.draw_bounding_box(frame, bbox, (255, 0, 0))
        
        # Verify cv2.rectangle was called
        assert mock_cv2.rectangle.called
        call_args = mock_cv2.rectangle.call_args
        # Check bounding box coordinates
        pt1 = call_args[0][1]
        pt2 = call_args[0][2]
        assert pt1 == (50, 100)
        assert pt2 == (200, 250)

    @patch('src.services.image_generator.cv2')
    def test_add_label(self, mock_cv2, sample_config):
        """Test label addition to image."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        generator = ImageGenerator(sample_config)
        
        annotated_frame = generator.add_label(frame, "Left Crossing", (10, 30))
        
        # Verify cv2.putText was called
        assert mock_cv2.putText.called
        call_args = mock_cv2.putText.call_args
        assert "Left Crossing" in str(call_args[0][1])

    @patch('src.services.image_generator.cv2')
    def test_generate_composite_with_annotations(self, mock_cv2, sample_config, sample_tracked_car):
        """Test full composite image generation with annotations."""
        # Setup mocks
        left_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        right_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        mock_cv2.hconcat.return_value = np.zeros((480, 1280, 3), dtype=np.uint8)
        mock_cv2.imwrite.return_value = True
        
        generator = ImageGenerator(sample_config)
        
        # Mock video processor
        mock_video_processor = MagicMock()
        mock_video_processor.get_frame.side_effect = [left_frame, right_frame]
        
        result_path = generator.generate_composite_image(
            mock_video_processor,
            sample_tracked_car,
            "test_output.png"
        )
        
        # Verify frames were extracted
        assert mock_video_processor.get_frame.call_count == 2
        # Verify composite was created
        assert mock_cv2.hconcat.called
        # Verify image was saved
        assert mock_cv2.imwrite.called
        assert result_path == "test_output.png"

    def test_extract_crossing_frames(self, sample_config, sample_tracked_car):
        """Test frame extraction for crossing events."""
        generator = ImageGenerator(sample_config)
        
        mock_video_processor = MagicMock()
        left_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        right_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_video_processor.get_frame.side_effect = [left_frame, right_frame]
        
        left, right = generator.extract_crossing_frames(
            mock_video_processor,
            sample_tracked_car
        )
        
        # Verify correct frames were extracted
        assert mock_video_processor.get_frame.call_count == 2
        assert left is not None
        assert right is not None
        # Verify frames were requested at correct frame numbers
        calls = mock_video_processor.get_frame.call_args_list
        assert calls[0][0][0] == 100  # left crossing frame
        assert calls[1][0][0] == 130  # right crossing frame

