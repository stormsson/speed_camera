"""Video controller for handling video loading, frame extraction, and metadata management."""

import cv2
import numpy as np
from typing import Optional
from PySide6.QtGui import QPixmap, QImage

from src.models import VideoMetadata, Configuration
from src.services.video_processor import VideoProcessor
from src.lib.exceptions import VideoLoadError
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class VideoController:
    """Controller for video loading and frame navigation."""

    def __init__(self):
        """Initialize video controller."""
        self.video_processor: Optional[VideoProcessor] = None
        self.config: Optional[Configuration] = None
        self.current_frame_number: int = 1
        self.frame_cache: dict[int, QPixmap] = {}
        self.frame_cache_size: int = 10

    def load_video(
        self,
        video_path: str,
        config: Optional[Configuration] = None
    ) -> VideoMetadata:
        """
        Load video file and extract metadata.

        Args:
            video_path: Path to video file
            config: Optional configuration for video resizing

        Returns:
            VideoMetadata object

        Raises:
            VideoLoadError: If video cannot be loaded
        """
        try:
            # Close previous video if open
            if self.video_processor is not None:
                self.video_processor.close()

            self.config = config
            self.video_processor = VideoProcessor(video_path, config)
            metadata = self.video_processor.get_metadata()

            # Reset frame position
            self.current_frame_number = 1
            self.frame_cache.clear()

            logger.info(
                "Video loaded",
                extra={
                    "video_path": video_path,
                    "frame_count": metadata.frame_count,
                    "width": metadata.width,
                    "height": metadata.height,
                    "fps": metadata.fps
                }
            )

            return metadata

        except Exception as e:
            raise VideoLoadError(
                f"Failed to load video: {str(e)}",
                video_path=video_path
            ) from e

    def get_frame(self, frame_number: int) -> Optional[QPixmap]:
        """
        Get a specific frame as QPixmap.

        Args:
            frame_number: Frame number to retrieve (1-indexed)

        Returns:
            QPixmap of the frame, or None if frame cannot be read
        """
        if self.video_processor is None:
            return None

        # Check cache first
        if frame_number in self.frame_cache:
            return self.frame_cache[frame_number]

        # Convert to 0-indexed for OpenCV
        frame_index = frame_number - 1

        # Get frame from video processor
        frame_array = self.video_processor.get_frame(frame_index)

        if frame_array is None:
            return None

        # Convert numpy array to QPixmap
        height, width, channels = frame_array.shape
        bytes_per_line = channels * width

        # Convert BGR to RGB for Qt
        rgb_frame = cv2.cvtColor(frame_array, cv2.COLOR_BGR2RGB)

        q_image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(q_image)

        # Cache the frame
        self._add_to_cache(frame_number, pixmap)

        return pixmap

    def _add_to_cache(self, frame_number: int, pixmap: QPixmap) -> None:
        """Add frame to cache, removing oldest if cache is full."""
        self.frame_cache[frame_number] = pixmap

        # Remove oldest frames if cache is full
        if len(self.frame_cache) > self.frame_cache_size:
            # Remove the frame with the smallest frame number
            oldest_frame = min(self.frame_cache.keys())
            del self.frame_cache[oldest_frame]

    def navigate_to_frame(self, frame_number: int) -> Optional[QPixmap]:
        """
        Navigate to a specific frame number.

        Args:
            frame_number: Frame number to navigate to (1-indexed)

        Returns:
            QPixmap of the frame, or None if frame cannot be read
        """
        if self.video_processor is None:
            return None

        metadata = self.video_processor.get_metadata()

        # Validate frame number
        if frame_number < 1 or frame_number > metadata.frame_count:
            logger.warning(
                "Frame number out of bounds",
                extra={
                    "frame_number": frame_number,
                    "total_frames": metadata.frame_count
                }
            )
            return None

        self.current_frame_number = frame_number
        return self.get_frame(frame_number)

    def next_frame(self) -> Optional[QPixmap]:
        """
        Navigate to next frame.

        Returns:
            QPixmap of the next frame, or None if at last frame
        """
        if self.video_processor is None:
            return None

        metadata = self.video_processor.get_metadata()

        if self.current_frame_number >= metadata.frame_count:
            return None

        self.current_frame_number += 1
        return self.get_frame(self.current_frame_number)

    def previous_frame(self) -> Optional[QPixmap]:
        """
        Navigate to previous frame.

        Returns:
            QPixmap of the previous frame, or None if at first frame
        """
        if self.video_processor is None:
            return None

        if self.current_frame_number <= 1:
            return None

        self.current_frame_number -= 1
        return self.get_frame(self.current_frame_number)

    def get_metadata(self) -> Optional[VideoMetadata]:
        """
        Get video metadata.

        Returns:
            VideoMetadata object, or None if no video loaded
        """
        if self.video_processor is None:
            return None

        return self.video_processor.get_metadata()

    def close(self) -> None:
        """Close video and release resources."""
        if self.video_processor is not None:
            self.video_processor.close()
            self.video_processor = None
        self.frame_cache.clear()
        self.current_frame_number = 1

