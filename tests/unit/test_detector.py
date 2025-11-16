"""Unit tests for car detector."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from src.models import DetectionResult, BoundingBox


class TestCarDetector:
    """Test car detection functionality."""

    def test_initialize_detector(self):
        """Test initializing YOLO detector."""
        from src.services.car_detector import CarDetector
        
        detector = CarDetector(confidence_threshold=0.5)
        assert detector.confidence_threshold == 0.5

    def test_detect_cars_in_frame(self):
        """Test detecting cars in a frame."""
        from src.services.car_detector import CarDetector
        
        # Mock YOLO model
        mock_results = MagicMock()
        mock_box = MagicMock()
        mock_box.xyxy = [[100, 200, 300, 400]]  # x1, y1, x2, y2
        mock_box.conf = [0.85]
        mock_box.cls = [2]  # Car class ID
        mock_results[0].boxes = mock_box
        
        with patch('ultralytics.YOLO') as mock_yolo:
            mock_yolo.return_value.return_value = mock_results
            
            detector = CarDetector(confidence_threshold=0.5)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            detections = detector.detect(frame, frame_number=0)
            
            assert len(detections) == 1
            assert isinstance(detections[0], DetectionResult)
            assert detections[0].confidence == 0.85
            assert detections[0].class_id == 2

    def test_filter_by_confidence_threshold(self):
        """Test filtering detections by confidence threshold."""
        from src.services.car_detector import CarDetector
        
        # Mock YOLO with low confidence detection
        mock_results = MagicMock()
        mock_box = MagicMock()
        mock_box.xyxy = [[100, 200, 300, 400]]
        mock_box.conf = [0.3]  # Below threshold
        mock_box.cls = [2]
        mock_results[0].boxes = mock_box
        
        with patch('ultralytics.YOLO') as mock_yolo:
            mock_yolo.return_value.return_value = mock_results
            
            detector = CarDetector(confidence_threshold=0.5)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            detections = detector.detect(frame, frame_number=0)
            
            assert len(detections) == 0  # Should be filtered out

    def test_filter_by_car_class(self):
        """Test filtering to only car class."""
        from src.services.car_detector import CarDetector
        
        # Mock YOLO with non-car class
        mock_results = MagicMock()
        mock_box = MagicMock()
        mock_box.xyxy = [[100, 200, 300, 400]]
        mock_box.conf = [0.85]
        mock_box.cls = [0]  # Not car class
        mock_results[0].boxes = mock_box
        
        with patch('ultralytics.YOLO') as mock_yolo:
            mock_yolo.return_value.return_value = mock_results
            
            detector = CarDetector(confidence_threshold=0.5)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            detections = detector.detect(frame, frame_number=0)
            
            assert len(detections) == 0  # Should be filtered out (not a car)

    def test_multiple_cars_detection(self):
        """Test detecting multiple cars in a frame."""
        from src.services.car_detector import CarDetector
        
        # Mock YOLO with multiple detections
        mock_results = MagicMock()
        mock_box = MagicMock()
        mock_box.xyxy = [[100, 200, 300, 400], [500, 200, 700, 400]]
        mock_box.conf = [0.85, 0.90]
        mock_box.cls = [2, 2]  # Both cars
        mock_results[0].boxes = mock_box
        
        with patch('ultralytics.YOLO') as mock_yolo:
            mock_yolo.return_value.return_value = mock_results
            
            detector = CarDetector(confidence_threshold=0.5)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            detections = detector.detect(frame, frame_number=0)
            
            assert len(detections) == 2
            assert all(isinstance(d, DetectionResult) for d in detections)

    def test_detection_result_structure(self):
        """Test that detection results have correct structure."""
        from src.services.car_detector import CarDetector
        
        mock_results = MagicMock()
        mock_box = MagicMock()
        mock_box.xyxy = [[100, 200, 300, 400]]
        mock_box.conf = [0.85]
        mock_box.cls = [2]
        mock_results[0].boxes = mock_box
        
        with patch('ultralytics.YOLO') as mock_yolo:
            mock_yolo.return_value.return_value = mock_results
            
            detector = CarDetector(confidence_threshold=0.5)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            detections = detector.detect(frame, frame_number=10)
            
            assert len(detections) == 1
            detection = detections[0]
            assert detection.frame_number == 10
            assert isinstance(detection.bounding_box, BoundingBox)
            assert detection.bounding_box.x1 == 100
            assert detection.bounding_box.y1 == 200
            assert detection.bounding_box.x2 == 300
            assert detection.bounding_box.y2 == 400
            assert detection.confidence == 0.85
            assert detection.class_id == 2
            assert detection.class_name == "car"

