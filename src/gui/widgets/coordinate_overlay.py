"""Coordinate overlay widget for rendering measurement coordinate lines."""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QFont

from src.gui.models import CoordinateOverlayState
from src.models import Configuration


class CoordinateOverlayWidget(QWidget):
    """Widget for rendering coordinate overlay lines on video frames."""

    def __init__(self, parent: QWidget = None):
        """Initialize coordinate overlay widget."""
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._state = CoordinateOverlayState()
        self._video_width: int = 0  # Store video width for scaling

    def set_configuration(self, config: Configuration, video_width: int) -> None:
        """
        Set configuration and calculate scaled coordinates.

        Args:
            config: Configuration with coordinates
            video_width: Video frame width in pixels (after scaling if downsize_video is used)
        """
        self._state.config = config
        self._state.left_coordinate_original = config.left_coordinate
        self._state.right_coordinate_original = config.right_coordinate
        self._video_width = video_width

        # If downsize_video is used, coordinates are already scaled by VideoProcessor
        # So we use the video_width directly (which is already the scaled width)
        # Otherwise, use original coordinates
        if config.downsize_video is not None:
            # Calculate scale factor
            # We need the original video width to calculate scale
            # For now, assume video_width is the scaled width
            # The actual coordinates will be set via set_scaled_coordinates
            self._state.scale_factor = 1.0  # Will be updated by set_scaled_coordinates
            self._state.left_coordinate = config.left_coordinate
            self._state.right_coordinate = config.right_coordinate
        else:
            self._state.scale_factor = 1.0
            self._state.left_coordinate = config.left_coordinate
            self._state.right_coordinate = config.right_coordinate

        # Validate coordinates are within bounds
        if (self._state.left_coordinate < 0 or
            self._state.left_coordinate > video_width or
            self._state.right_coordinate < 0 or
            self._state.right_coordinate > video_width):
            self._state.is_visible = False
        else:
            self._state.is_visible = True

        self.update()

    def set_scaled_coordinates(
        self,
        left_coordinate: int,
        right_coordinate: int,
        video_width: int
    ) -> None:
        """
        Set scaled coordinates directly (from VideoProcessor).

        Args:
            left_coordinate: Scaled left coordinate
            right_coordinate: Scaled right coordinate
            video_width: Video frame width in pixels
        """
        self._state.left_coordinate = left_coordinate
        self._state.right_coordinate = right_coordinate
        self._video_width = video_width

        # Validate coordinates are within bounds
        if (self._state.left_coordinate < 0 or
            self._state.left_coordinate > video_width or
            self._state.right_coordinate < 0 or
            self._state.right_coordinate > video_width):
            self._state.is_visible = False
        else:
            self._state.is_visible = True

        self.update()

    def paintEvent(self, event) -> None:
        """Paint coordinate overlay lines."""
        if not self._state.is_visible:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set pen for coordinate lines
        pen = QPen(QColor(255, 0, 0), 2)  # Red, 2px width
        painter.setPen(pen)

        # Get widget dimensions
        widget_width = self.width()
        widget_height = self.height()

        # Calculate scale factor to map video coordinates to widget coordinates
        # The video display widget scales the pixmap to fit while maintaining aspect ratio
        # We need to get the actual displayed video width from the parent widget
        parent = self.parent()
        offset_x = 0
        offset_y = 0
        
        if parent and hasattr(parent, 'pixmap') and parent.pixmap():
            # Get the scaled pixmap size
            pixmap = parent.pixmap()
            displayed_width = pixmap.width()
            displayed_height = pixmap.height()
            
            # Calculate offset: QLabel with AlignCenter centers the pixmap
            # So we need to add the offset from widget edge to pixmap edge
            offset_x = (widget_width - displayed_width) / 2
            offset_y = (widget_height - displayed_height) / 2
            
            # Use stored video width or fallback to displayed width
            video_width = self._video_width if self._video_width > 0 else displayed_width
            
            if video_width > 0:
                scale_x = displayed_width / video_width
            else:
                scale_x = 1.0
        else:
            # Fallback: assume 1:1 mapping
            scale_x = 1.0

        if self._video_width == 0:
            return
            
        # Draw left coordinate line (add offset to account for centered pixmap)
        left_x = int(self._state.left_coordinate * scale_x + offset_x)
        painter.drawLine(left_x, 0, left_x, widget_height)

        # Draw right coordinate line (add offset to account for centered pixmap)
        right_x = int(self._state.right_coordinate * scale_x + offset_x)
        painter.drawLine(right_x, 0, right_x, widget_height)

        # Draw labels
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255), 1))

        # Label for left coordinate
        label_rect_left = painter.fontMetrics().boundingRect(self._state.left_label)
        painter.fillRect(
            int(left_x - label_rect_left.width() // 2 - 5),
            int(5 + offset_y),
            label_rect_left.width() + 10,
            label_rect_left.height() + 5,
            QColor(255, 0, 0, 200)  # Semi-transparent red background
        )
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawText(
            int(left_x - label_rect_left.width() // 2),
            int(5 + offset_y + label_rect_left.height()),
            self._state.left_label
        )

        # Label for right coordinate
        label_rect_right = painter.fontMetrics().boundingRect(self._state.right_label)
        painter.fillRect(
            int(right_x - label_rect_right.width() // 2 - 5),
            int(5 + offset_y),
            label_rect_right.width() + 10,
            label_rect_right.height() + 5,
            QColor(255, 0, 0, 200)  # Semi-transparent red background
        )
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawText(
            int(right_x - label_rect_right.width() // 2),
            int(5 + offset_y + label_rect_right.height()),
            self._state.right_label
        )

