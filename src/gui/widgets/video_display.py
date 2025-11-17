"""Video display widget for showing video frames."""

from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from src.gui.models import VideoDisplayState


class VideoDisplayWidget(QLabel):
    """Widget for displaying video frames with aspect ratio preservation."""

    def __init__(self, parent: QWidget = None):
        """Initialize video display widget."""
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
        self._state = VideoDisplayState()
        self._show_empty_state()

    def display_frame(self, pixmap: QPixmap) -> None:
        """
        Display a video frame.

        Args:
            pixmap: QPixmap of the frame to display
        """
        if pixmap is None:
            self._show_empty_state()
            return

        # Scale pixmap to fit widget while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled_pixmap)
        self._state.current_frame_image = pixmap
        self._state.is_loaded = True

    def _show_empty_state(self) -> None:
        """Show placeholder message when no video is loaded."""
        self.setText("No video loaded")
        self._state.is_loaded = False
        self._state.current_frame_image = None

    def resizeEvent(self, event) -> None:
        """Handle widget resize to maintain aspect ratio."""
        super().resizeEvent(event)
        # Redisplay current frame if available
        if self._state.current_frame_image is not None:
            self.display_frame(self._state.current_frame_image)

