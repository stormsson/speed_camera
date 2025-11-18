"""Unit tests for debug image generator."""

import pytest
import tempfile
import os
from pathlib import Path
import numpy as np
import cv2

from src.models import (
    Configuration,
    DetectionResult,
    BoundingBox,
    CoordinateCrossingEvent,
)


class TestDebugImageGenerator:
    """Test debug image generator functionality."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration."""
        return Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0,
            yolo_model="yolov8n.pt",
            yolo_confidence_threshold=0.5
        )

    @pytest.fixture
    def sample_frame(self):
        """Create a sample frame (640x480 image)."""
        return np.zeros((480, 640, 3), dtype=np.uint8)

    def test_png_file_creation(self, sample_config, sample_frame):
        """Test that PNG file is created when generating debug image."""
        from src.services.debug_image_generator import DebugImageGenerator
        
        generator = DebugImageGenerator(sample_config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            bbox = BoundingBox(x1=50, y1=200, x2=150, y2=400)
            detection = DetectionResult(0, bbox, 0.85, 2, "car")
            event = CoordinateCrossingEvent(
                track_id=1,
                frame_number=10,
                coordinate_type="left",
                coordinate_value=100,
                car_rightmost_x=110,
                confidence=0.85
            )
            
            file_path = generator.generate_debug_image(
                sample_frame,
                detection,
                event,
                frame_number=10
            )
            
            assert file_path is not None
            assert os.path.exists(file_path)
            assert file_path.endswith(".png")
            assert "crossing_10.png" in file_path

    def test_bounding_box_drawing(self, sample_config, sample_frame):
        """Test that bounding box is drawn on debug image."""
        from src.services.debug_image_generator import DebugImageGenerator
        
        generator = DebugImageGenerator(sample_config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            bbox = BoundingBox(x1=50, y1=200, x2=150, y2=400)
            detection = DetectionResult(0, bbox, 0.85, 2, "car")
            event = CoordinateCrossingEvent(
                track_id=1,
                frame_number=10,
                coordinate_type="left",
                coordinate_value=100,
                car_rightmost_x=110,
                confidence=0.85
            )
            
            file_path = generator.generate_debug_image(
                sample_frame,
                detection,
                event,
                frame_number=10
            )
            
            # Load the image and verify bounding box is drawn
            img = cv2.imread(file_path)
            assert img is not None
            
            # Check that image has non-zero pixels (bounding box drawn)
            # Since we start with zeros, any drawing will create non-zero pixels
            assert np.any(img > 0)

    def test_coordinate_line_drawing(self, sample_config, sample_frame):
        """Test that coordinate lines are drawn on debug image."""
        from src.services.debug_image_generator import DebugImageGenerator
        
        generator = DebugImageGenerator(sample_config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            bbox = BoundingBox(x1=50, y1=200, x2=150, y2=400)
            detection = DetectionResult(0, bbox, 0.85, 2, "car")
            event = CoordinateCrossingEvent(
                track_id=1,
                frame_number=10,
                coordinate_type="left",
                coordinate_value=100,
                car_rightmost_x=110,
                confidence=0.85
            )
            
            file_path = generator.generate_debug_image(
                sample_frame,
                detection,
                event,
                frame_number=10
            )
            
            # Load the image
            img = cv2.imread(file_path)
            assert img is not None
            
            # Check that vertical lines are drawn at left and right coordinates
            # Left coordinate should be at x=100, right at x=500
            # We check a column of pixels at these x coordinates
            left_col = img[:, 100, :]
            right_col = img[:, 500, :]
            
            # At least one of these columns should have non-zero pixels (line drawn)
            assert np.any(left_col > 0) or np.any(right_col > 0)

    def test_criteria_text_rendering(self, sample_config, sample_frame):
        """Test that detection criteria text is rendered on debug image."""
        from src.services.debug_image_generator import DebugImageGenerator
        
        generator = DebugImageGenerator(sample_config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            bbox = BoundingBox(x1=50, y1=200, x2=150, y2=400)
            detection = DetectionResult(0, bbox, 0.85, 2, "car")
            event = CoordinateCrossingEvent(
                track_id=1,
                frame_number=10,
                coordinate_type="left",
                coordinate_value=100,
                car_rightmost_x=110,
                confidence=0.85
            )
            
            file_path = generator.generate_debug_image(
                sample_frame,
                detection,
                event,
                frame_number=10
            )
            
            # Load the image
            img = cv2.imread(file_path)
            assert img is not None
            
            # Text should be rendered, which will create non-zero pixels
            # We can't easily verify exact text content without OCR, but we can
            # verify that text area has been modified (non-zero pixels in text region)
            # Text is typically drawn in top-left or bottom area
            text_region = img[-100:, :, :]  # Bottom 100 pixels
            assert np.any(text_region > 0)

    def test_file_naming_convention(self, sample_config, sample_frame):
        """Test that debug images use correct naming convention."""
        from src.services.debug_image_generator import DebugImageGenerator
        
        generator = DebugImageGenerator(sample_config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            bbox = BoundingBox(x1=50, y1=200, x2=150, y2=400)
            detection = DetectionResult(0, bbox, 0.85, 2, "car")
            
            # Test different frame numbers
            for frame_num in [0, 10, 100, 1000]:
                event = CoordinateCrossingEvent(
                    track_id=1,
                    frame_number=frame_num,
                    coordinate_type="left",
                    coordinate_value=100,
                    car_rightmost_x=110,
                    confidence=0.85
                )
                
                file_path = generator.generate_debug_image(
                    sample_frame,
                    detection,
                    event,
                    frame_number=frame_num
                )
                
                expected_name = f"crossing_{frame_num}.png"
                assert file_path.endswith(expected_name)
                assert os.path.basename(file_path) == expected_name

    def test_left_crossing_text_format(self, sample_config, sample_frame):
        """Test that left crossing text format is correct."""
        from src.services.debug_image_generator import DebugImageGenerator
        
        generator = DebugImageGenerator(sample_config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Use consistent values: bbox x2 should match car_rightmost_x
            bbox = BoundingBox(x1=50, y1=200, x2=110, y2=400)
            detection = DetectionResult(0, bbox, 0.85, 2, "car")
            event = CoordinateCrossingEvent(
                track_id=1,
                frame_number=10,
                coordinate_type="left",
                coordinate_value=100,
                car_rightmost_x=110,
                confidence=0.85
            )
            
            # Get the criteria text
            criteria_text = generator._format_criteria_text(event, detection)
            criteria_lower = criteria_text.lower()
            
            assert "bounding box x" in criteria_lower
            assert "left line coord" in criteria_lower
            assert "110" in criteria_text  # car_rightmost_x (from bbox x2)
            assert "100" in criteria_text  # left_coordinate

    def test_right_crossing_text_format(self, sample_config, sample_frame):
        """Test that right crossing text format is correct."""
        from src.services.debug_image_generator import DebugImageGenerator
        
        generator = DebugImageGenerator(sample_config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Use consistent values: bbox x2 should match car_rightmost_x
            bbox = BoundingBox(x1=450, y1=200, x2=510, y2=400)
            detection = DetectionResult(0, bbox, 0.85, 2, "car")
            event = CoordinateCrossingEvent(
                track_id=1,
                frame_number=20,
                coordinate_type="right",
                coordinate_value=500,
                car_rightmost_x=510,
                confidence=0.87
            )
            
            # Get the criteria text
            criteria_text = generator._format_criteria_text(event, detection)
            criteria_lower = criteria_text.lower()
            
            assert "bounding box x" in criteria_lower
            assert "right line coord" in criteria_lower
            assert "510" in criteria_text  # car_rightmost_x (from bbox x2)
            assert "500" in criteria_text  # right_coordinate

    def test_text_includes_frame_and_track_id(self, sample_config, sample_frame):
        """Test that criteria text includes frame number and track ID."""
        from src.services.debug_image_generator import DebugImageGenerator
        
        generator = DebugImageGenerator(sample_config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            bbox = BoundingBox(x1=50, y1=200, x2=150, y2=400)
            detection = DetectionResult(0, bbox, 0.85, 2, "car")
            event = CoordinateCrossingEvent(
                track_id=42,
                frame_number=123,
                coordinate_type="left",
                coordinate_value=100,
                car_rightmost_x=110,
                confidence=0.85
            )
            
            # Get the criteria text
            criteria_text = generator._format_criteria_text(event, detection)
            
            assert "123" in criteria_text  # frame_number
            assert "42" in criteria_text  # track_id

