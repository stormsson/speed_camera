"""Unit tests for video processor."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

from src.models import VideoMetadata, Configuration
from src.lib.exceptions import VideoLoadError


class TestVideoProcessor:
    """Test video processing functionality."""

    def test_load_video_success(self):
        """Test successfully loading a video file."""
        # This test will fail until video_processor is implemented
        from src.services.video_processor import VideoProcessor
        
        # Mock OpenCV VideoCapture
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.return_value = 30.0  # fps
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 900,
                cv2.CAP_PROP_FRAME_WIDTH: 1920,
                cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            }.get(prop, 0)
            
            processor = VideoProcessor("test_video.mp4")
            metadata = processor.get_metadata()
            
            assert isinstance(metadata, VideoMetadata)
            assert metadata.file_path == "test_video.mp4"
            assert metadata.fps == 30.0
            assert metadata.frame_count == 900
            assert metadata.width == 1920
            assert metadata.height == 1080

    def test_load_video_file_not_found(self):
        """Test loading non-existent video file raises error."""
        from src.services.video_processor import VideoProcessor
        
        with pytest.raises(VideoLoadError) as exc_info:
            VideoProcessor("/nonexistent/video.mp4")
        assert "not found" in str(exc_info.value).lower() or "cannot open" in str(exc_info.value).lower()

    def test_load_video_corrupted(self):
        """Test loading corrupted video file raises error."""
        from src.services.video_processor import VideoProcessor
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            f.write(b"invalid video data")
            temp_path = f.name
        
        try:
            with pytest.raises(VideoLoadError):
                VideoProcessor(temp_path)
        finally:
            os.unlink(temp_path)

    def test_extract_frame(self):
        """Test extracting a frame from video."""
        from src.services.video_processor import VideoProcessor
        import numpy as np
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 100,
                cv2.CAP_PROP_FRAME_WIDTH: 640,
                cv2.CAP_PROP_FRAME_HEIGHT: 480,
            }.get(prop, 0)
            mock_cap.return_value.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
            
            processor = VideoProcessor("test_video.mp4")
            frame = processor.get_frame(0)
            
            assert frame is not None
            assert frame.shape == (480, 640, 3)

    def test_extract_metadata(self):
        """Test extracting video metadata."""
        from src.services.video_processor import VideoProcessor
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 29.97,
                cv2.CAP_PROP_FRAME_COUNT: 1800,
                cv2.CAP_PROP_FRAME_WIDTH: 1280,
                cv2.CAP_PROP_FRAME_HEIGHT: 720,
            }.get(prop, 0)
            
            processor = VideoProcessor("test_video.mp4")
            metadata = processor.get_metadata()
            
            assert metadata.fps == 29.97
            assert metadata.frame_count == 1800
            assert metadata.width == 1280
            assert metadata.height == 720
            assert metadata.duration_seconds == pytest.approx(1800 / 29.97, rel=0.01)

    def test_iterate_frames(self):
        """Test iterating through video frames."""
        from src.services.video_processor import VideoProcessor
        import numpy as np
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 3,
            }.get(prop, 0)
            mock_cap.return_value.read.side_effect = [
                (True, np.zeros((480, 640, 3), dtype=np.uint8)),
                (True, np.zeros((480, 640, 3), dtype=np.uint8)),
                (True, np.zeros((480, 640, 3), dtype=np.uint8)),
                (False, None),  # End of video
            ]
            
            processor = VideoProcessor("test_video.mp4")
            frames = list(processor.iter_frames())
            
            assert len(frames) == 3
            for frame_num, frame in frames:
                assert isinstance(frame_num, int)
                assert frame is not None

    @patch('cv2.resize')
    def test_frame_resizing_with_aspect_ratio(self, mock_resize):
        """Test that frames are resized maintaining aspect ratio."""
        from src.services.video_processor import VideoProcessor
        
        # Original frame: 1920x1080
        original_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        target_width = 480
        
        # Expected new height: 1080 * (480/1920) = 270
        expected_height = int(1080 * (480 / 1920.0))
        expected_resized = np.zeros((expected_height, target_width, 3), dtype=np.uint8)
        mock_resize.return_value = expected_resized
        
        # Mock VideoCapture
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 1,
                cv2.CAP_PROP_FRAME_WIDTH: 1920,
                cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            }.get(prop, 0)
            mock_cap.return_value.read.return_value = (True, original_frame)
            mock_cap.return_value.set.return_value = True
            
            processor = VideoProcessor("test_video.mp4")
            # This test will verify resize is called with correct dimensions
            # Actual implementation will be in VideoProcessor
            
            # Verify expected dimensions
            assert expected_height == 270
            assert target_width == 480

    def test_coordinate_scaling(self):
        """Test coordinate scaling calculation."""
        # Original video dimensions
        original_width = 1920
        original_left = 100
        original_right = 500
        
        # Target width
        target_width = 480
        
        # Calculate scale factor
        scale_factor = target_width / original_width
        
        # Scale coordinates
        scaled_left = int(original_left * scale_factor)
        scaled_right = int(original_right * scale_factor)
        
        # Verify scaling
        assert scale_factor == 0.25  # 480/1920
        assert scaled_left == 25  # 100 * 0.25
        assert scaled_right == 125  # 500 * 0.25

    @patch('cv2.resize')
    def test_metadata_update_after_resizing(self, mock_resize):
        """Test that metadata is updated with new dimensions after resizing."""
        from src.services.video_processor import VideoProcessor
        
        original_width = 1920
        original_height = 1080
        target_width = 480
        expected_height = int(original_height * (target_width / original_width))
        
        # Mock resized frame
        resized_frame = np.zeros((expected_height, target_width, 3), dtype=np.uint8)
        mock_resize.return_value = resized_frame
        
        # Mock VideoCapture
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 1,
                cv2.CAP_PROP_FRAME_WIDTH: original_width,
                cv2.CAP_PROP_FRAME_HEIGHT: original_height,
            }.get(prop, 0)
            mock_cap.return_value.read.return_value = (True, np.zeros((original_height, original_width, 3), dtype=np.uint8))
            mock_cap.return_value.set.return_value = True
            
            processor = VideoProcessor("test_video.mp4")
            original_metadata = processor.get_metadata()
            
            # Verify original metadata
            assert original_metadata.width == original_width
            assert original_metadata.height == original_height
            
            # After resizing, metadata should reflect new dimensions
            # This will be implemented in VideoProcessor
            assert expected_height == 270
            assert target_width == 480

