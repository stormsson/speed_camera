"""Detection overlay widget for rendering bounding boxes, tracking, and crossing events."""

from typing import List, Dict, Set
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QBrush

from src.models import (
    DetectionResult,
    TrackedCar,
    CoordinateCrossingEvent,
    SpeedMeasurement,
    BoundingBox
)


class DetectionOverlayWidget(QWidget):
    """Widget for rendering detection visualization overlays."""

    def __init__(self, parent: QWidget = None):
        """Initialize detection overlay widget."""
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Detection data
        self._detections: List[DetectionResult] = []
        self._tracked_cars: Dict[int, TrackedCar] = {}
        self._crossing_events: List[CoordinateCrossingEvent] = []
        self._json_speed_measurements: List[SpeedMeasurement] = []
        self._current_frame_number: int = 0
        
        # Video dimensions for scaling (already account for downscaling if used)
        self._video_width: int = 0
        self._video_height: int = 0

        # Color mapping for track IDs
        self._track_colors: Dict[int, QColor] = {}
        self._color_palette = [
            QColor(255, 0, 0),      # Red
            QColor(0, 255, 0),      # Green
            QColor(0, 0, 255),      # Blue
            QColor(255, 255, 0),     # Yellow
            QColor(255, 0, 255),     # Magenta
            QColor(0, 255, 255),     # Cyan
            QColor(255, 128, 0),     # Orange
            QColor(128, 0, 255),     # Purple
        ]

    def set_detection_data(
        self,
        detections: List[DetectionResult],
        tracked_cars: Dict[int, TrackedCar],
        crossing_events: List[CoordinateCrossingEvent],
        json_speed_measurements: List[SpeedMeasurement],
        current_frame_number: int,
        left_coordinate: int = 0,
        right_coordinate: int = 0,
        video_width: int = 0,
        video_height: int = 0
    ) -> None:
        """
        Set detection data for rendering.

        Args:
            detections: Live detections for current frame
            tracked_cars: Dictionary of tracked cars
            crossing_events: Live crossing events for current frame
            json_speed_measurements: Expected speed measurements from JSON
            current_frame_number: Current frame number
            left_coordinate: Left coordinate value (already scaled if downsize_video used)
            right_coordinate: Right coordinate value (already scaled if downsize_video used)
            video_width: Video frame width (already scaled if downsize_video used)
            video_height: Video frame height (already scaled if downsize_video used)
        """
        self._detections = detections
        self._tracked_cars = tracked_cars
        self._crossing_events = crossing_events
        self._json_speed_measurements = json_speed_measurements
        self._current_frame_number = current_frame_number
        self._left_coordinate = left_coordinate
        self._right_coordinate = right_coordinate
        self._video_width = video_width
        self._video_height = video_height

        # Update color mapping for track IDs
        for track_id in tracked_cars.keys():
            if track_id not in self._track_colors:
                # Assign color from palette
                color_index = track_id % len(self._color_palette)
                self._track_colors[track_id] = self._color_palette[color_index]

        self.update()

    def paintEvent(self, event) -> None:
        """Paint detection overlays."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

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
            # Get the scaled pixmap size (this is the displayed size in the widget)
            pixmap = parent.pixmap()
            displayed_width = pixmap.width()
            displayed_height = pixmap.height()
            
            # Calculate offset: QLabel with AlignCenter centers the pixmap
            # So we need to add the offset from widget edge to pixmap edge
            offset_x = (widget_width - displayed_width) / 2
            offset_y = (widget_height - displayed_height) / 2
            
            # Use stored video dimensions (already account for downscaling if used)
            # Bounding boxes are in these coordinates
            video_width = self._video_width if self._video_width > 0 else displayed_width
            video_height = self._video_height if self._video_height > 0 else displayed_height
            
            if video_width > 0:
                scale_x = displayed_width / video_width
            else:
                scale_x = 1.0
                
            if video_height > 0:
                scale_y = displayed_height / video_height
            else:
                scale_y = 1.0
        else:
            # Fallback: assume 1:1 mapping
            scale_x = 1.0
            scale_y = 1.0

        # Get expected track IDs from JSON
        expected_track_ids: Set[int] = {
            sm.track_id for sm in self._json_speed_measurements
        }

        # Draw live detection bounding boxes
        for detection in self._detections:
            bbox = detection.bounding_box
            track_id = self._get_track_id_for_detection(detection)
            
            # Determine if this is an expected car from JSON
            is_expected = track_id in expected_track_ids
            
            # Get color for this track
            color = self._track_colors.get(track_id, QColor(255, 255, 255))
            
            # Draw bounding box (add offset to account for centered pixmap)
            x1 = int(bbox.x1 * scale_x + offset_x)
            y1 = int(bbox.y1 * scale_y + offset_y)
            x2 = int(bbox.x2 * scale_x + offset_x)
            y2 = int(bbox.y2 * scale_y + offset_y)
            
            if is_expected:
                # Draw dashed outline for expected cars
                pen = QPen(color, 3, Qt.PenStyle.DashLine)
            else:
                # Draw solid outline for live detections
                pen = QPen(color, 2, Qt.PenStyle.SolidLine)
            
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)
            
            # Draw tracking ID label
            if track_id is not None:
                font = QFont()
                font.setPointSize(10)
                font.setBold(True)
                painter.setFont(font)
                
                label_text = f"ID: {track_id}"
                label_rect = painter.fontMetrics().boundingRect(label_text)
                
                # Draw background for label
                painter.fillRect(
                    x1,
                    y1 - label_rect.height() - 5,
                    label_rect.width() + 10,
                    label_rect.height() + 5,
                    QColor(0, 0, 0, 180)  # Semi-transparent black
                )
                
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                painter.drawText(
                    x1 + 5,
                    y1 - 5,
                    label_text
                )
            
            # Draw confidence score
            confidence_text = f"{int(detection.confidence * 100)}%"
            conf_rect = painter.fontMetrics().boundingRect(confidence_text)
            
            # Draw background for confidence
            painter.fillRect(
                x2 - conf_rect.width() - 10,
                y1,
                conf_rect.width() + 10,
                conf_rect.height() + 5,
                QColor(0, 0, 0, 180)  # Semi-transparent black
            )
            
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(
                x2 - conf_rect.width() - 5,
                y1 + conf_rect.height(),
                confidence_text
            )

        # Draw live crossing event markers
        for event in self._crossing_events:
            if event.frame_number == self._current_frame_number:
                color = QColor(255, 255, 0)  # Yellow
                x = int(event.coordinate_value * scale_x + offset_x)
                y = int(widget_height // 2 + offset_y)  # Center vertically within pixmap
                
                # Draw circle marker (non-filled)
                painter.setPen(QPen(color, 2))
                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                painter.drawEllipse(int(x - 10), int(y - 10), 15, 15)

        # Highlight expected crossing frames from JSON
        for sm in self._json_speed_measurements:
            if (self._current_frame_number == sm.left_crossing_frame or
                self._current_frame_number == sm.right_crossing_frame):
                
                # Draw highlight marker at coordinate position
                color = QColor(255, 255, 0)  # Yellow for expected crossings
                
                if self._current_frame_number == sm.left_crossing_frame:
                    x = int(self._left_coordinate * scale_x + offset_x)
                elif self._current_frame_number == sm.right_crossing_frame:
                    x = int(self._right_coordinate * scale_x + offset_x)
                else:
                    continue
                
                y = int(widget_height // 2 + offset_y)  # Center vertically within pixmap
                
                # Draw larger circle marker for expected crossings
                painter.setPen(QPen(color, 4))
                painter.setBrush(QBrush(color))
                painter.drawEllipse(int(x - 15), int(y - 15), 30, 30)

    def _get_track_id_for_detection(self, detection: DetectionResult) -> int | None:
        """
        Get track ID for a detection by finding matching tracked car.

        Args:
            detection: Detection result

        Returns:
            Track ID or None if not tracked
        """
        for track_id, tracked_car in self._tracked_cars.items():
            if tracked_car.detections and tracked_car.detections[-1] == detection:
                return track_id
        return None

