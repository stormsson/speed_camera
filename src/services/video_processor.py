"""Video processing service for loading and extracting frames from video files."""

import cv2
from typing import Iterator, Tuple, Optional
import numpy as np

from src.models import VideoMetadata, Configuration
from src.lib.exceptions import VideoLoadError


class VideoProcessor:
    """Processes video files and extracts frames."""

    def __init__(self, video_path: str, config: Optional[Configuration] = None):
        """
        Initialize video processor.

        Args:
            video_path: Path to the video file
            config: Optional configuration for video resizing

        Raises:
            VideoLoadError: If video cannot be opened
        """
        self.video_path = video_path
        self.config = config
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise VideoLoadError(
                f"Cannot open video file: {video_path}",
                video_path=video_path
            )

        # Cache metadata
        self._metadata: Optional[VideoMetadata] = None
        self._scale_factor: Optional[float] = None
        self._scaled_coordinates: Optional[Tuple[int, int]] = None

    def get_metadata(self) -> VideoMetadata:
        """
        Extract and return video metadata.

        Returns:
            VideoMetadata object with video information (with resized dimensions if downsize_video is set)
        """
        if self._metadata is None:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration_seconds = frame_count / fps if fps > 0 else 0.0

            # Calculate resized dimensions if downsize_video is specified
            if self.config and self.config.downsize_video is not None:
                target_width = self.config.downsize_video
                if original_width != target_width:
                    # Calculate scale factor and new height (maintaining aspect ratio)
                    self._scale_factor = target_width / original_width
                    new_height = int(original_height * self._scale_factor)
                    
                    # Scale coordinates
                    scaled_left = int(self.config.left_coordinate * self._scale_factor)
                    scaled_right = int(self.config.right_coordinate * self._scale_factor)
                    self._scaled_coordinates = (scaled_left, scaled_right)
                    
                    width = target_width
                    height = new_height
                else:
                    # No resizing needed
                    width = original_width
                    height = original_height
                    self._scale_factor = 1.0
                    self._scaled_coordinates = (self.config.left_coordinate, self.config.right_coordinate)
            else:
                # No resizing
                width = original_width
                height = original_height

            self._metadata = VideoMetadata(
                file_path=self.video_path,
                frame_count=frame_count,
                fps=fps,
                width=width,
                height=height,
                duration_seconds=duration_seconds
            )

        return self._metadata

    def get_scaled_coordinates(self) -> Optional[Tuple[int, int]]:
        """
        Get scaled coordinates if video was resized.

        Returns:
            Tuple of (scaled_left_coordinate, scaled_right_coordinate) or None if not resized
        """
        # Ensure metadata is calculated
        self.get_metadata()
        return self._scaled_coordinates

    def get_frame(self, frame_number: int) -> Optional[np.ndarray]:
        """
        Get a specific frame by frame number.

        Args:
            frame_number: Frame index to retrieve

        Returns:
            Frame as numpy array (resized if downsize_video is set), or None if frame cannot be read
        """
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        
        if not ret or frame is None:
            return None
        
        # Resize frame if downsize_video is specified
        if self.config and self.config.downsize_video is not None:
            # Ensure metadata is calculated to get scale factor
            if self._scale_factor is None:
                self.get_metadata()
            
            if self._scale_factor is not None and self._scale_factor != 1.0:
                target_width = self.config.downsize_video
                target_height = int(frame.shape[0] * self._scale_factor)
                frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        
        return frame

    def iter_frames(self) -> Iterator[Tuple[int, np.ndarray]]:
        """
        Iterate through all frames in the video.

        Yields:
            Tuple of (frame_number, frame_array) where frame_array is resized if downsize_video is set
        """
        # Reset to beginning
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_number = 0

        # Ensure metadata is calculated to get scale factor
        if self.config and self.config.downsize_video is not None:
            self.get_metadata()

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Resize frame if downsize_video is specified
            if self.config and self.config.downsize_video is not None and self._scale_factor is not None and self._scale_factor != 1.0:
                target_width = self.config.downsize_video
                target_height = int(frame.shape[0] * self._scale_factor)
                frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
            
            yield (frame_number, frame)
            frame_number += 1

    def close(self) -> None:
        """Release video capture resources."""
        if self.cap is not None:
            self.cap.release()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

