"""Debug panel widget for displaying detailed detection analysis information."""

from typing import List, Dict, Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLabel,
    QScrollArea
)
from PySide6.QtCore import Qt

from src.models import (
    DetectionResult,
    TrackedCar,
    CoordinateCrossingEvent,
    SpeedMeasurement,
    Configuration,
    BoundingBox
)
from src.gui.models import TrackedCarAnalysis, CrossingAnalysis


class DebugPanelWidget(QWidget):
    """Widget for displaying detailed detection analysis information."""

    def __init__(self, parent: QWidget = None):
        """Initialize debug panel widget."""
        super().__init__(parent)
        self.setWindowTitle("Debug Information")
        self.setMinimumWidth(400)
        self.setMaximumWidth(600)

        # Setup UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title label
        self.title_label = QLabel("Debug Information")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Scrollable text area for debug information
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.debug_text = QTextEdit()
        self.debug_text.setReadOnly(True)
        self.debug_text.setFontFamily("Courier")
        self.debug_text.setFontPointSize(9)
        scroll_area.setWidget(self.debug_text)

        layout.addWidget(scroll_area)

        # Initialize with empty state
        self._show_empty_state()

    def _show_empty_state(self) -> None:
        """Show empty state message."""
        self.debug_text.setText("No detection data available.\nNavigate to a frame to see debug information.")

    def update_debug_info(
        self,
        frame_number: int,
        detections: List[DetectionResult],
        tracked_cars: Dict[int, TrackedCar],
        crossing_events: List[CoordinateCrossingEvent],
        config: Optional[Configuration],
        json_measurements: List[SpeedMeasurement],
        left_coordinate: Optional[int] = None,
        right_coordinate: Optional[int] = None
    ) -> None:
        """
        Update debug panel with current frame data.

        Args:
            frame_number: Current frame number
            detections: Live detection results for current frame
            tracked_cars: Dictionary of tracked cars by track_id
            crossing_events: Live crossing events for current frame
            config: Configuration with coordinate values
            json_measurements: Expected speed measurements from JSON
            left_coordinate: Scaled left coordinate (after downsize_video if applicable). If None, uses config.left_coordinate
            right_coordinate: Scaled right coordinate (after downsize_video if applicable). If None, uses config.right_coordinate
        """
        if not detections and not tracked_cars:
            self._show_empty_state()
            return

        # Build debug information text
        debug_text = f"Frame {frame_number} - Debug Information\n"
        debug_text += "=" * 50 + "\n\n"

        # Process each tracked car
        for track_id, tracked_car in tracked_cars.items():
            # Find detection for this track_id in current frame
            detection = None
            for det in detections:
                # Match by finding detection that belongs to this tracked car
                if det.frame_number == frame_number:
                    # Check if this detection is part of the tracked car's detections
                    if det in tracked_car.detections:
                        detection = det
                        break

            # If no detection found, use the latest detection from tracked car
            if detection is None and tracked_car.detections:
                detection = tracked_car.detections[-1]

            # Format car analysis
            vehicle_analysis = self._format_vehicle_analysis(tracked_car, detection)
            debug_text += vehicle_analysis

            # Compute and format crossing analysis
            if config:
                # Use scaled coordinates if provided, otherwise use config coordinates
                left_coord = left_coordinate if left_coordinate is not None else config.left_coordinate
                right_coord = right_coordinate if right_coordinate is not None else config.right_coordinate
                
                crossing_analysis = self._compute_crossing_analysis(
                    track_id, tracked_car, detection, left_coord, right_coord, crossing_events, frame_number
                )
                crossing_text = self._format_crossing_explanation(crossing_analysis)
                debug_text += crossing_text

            # Format comparison with JSON expected results
            json_comparison = self._format_comparison(tracked_car, json_measurements)
            debug_text += json_comparison

            debug_text += "\n" + "-" * 50 + "\n\n"

        self.debug_text.setText(debug_text)

    def _format_vehicle_analysis(
        self,
        tracked_car: TrackedCar,
        detection: Optional[DetectionResult]
    ) -> str:
        """
        Format per-car analysis display.

        Args:
            tracked_car: Tracked car to analyze
            detection: Detection result for current frame (if available)

        Returns:
            Formatted string with car analysis
        """
        text = f"Track ID: {tracked_car.track_id}\n"
        text += "-" * 30 + "\n"

        if detection:
            bb = detection.bounding_box
            text += "Detection:\n"
            text += f"  Bounding Box: (x1={bb.x1}, y1={bb.y1}, x2={bb.x2}, y2={bb.y2})\n"
            text += f"  Confidence: {detection.confidence:.2f}\n"
            text += f"  Class: {detection.class_name}\n"
            text += f"  Car Rightmost X: {bb.x2}\n"
        else:
            text += "Detection: No detection in current frame\n"

        text += "\nTracking:\n"
        text += f"  Track ID: {tracked_car.track_id}\n"
        text += f"  Left Crossing Frame: {tracked_car.left_crossing_frame if tracked_car.left_crossing_frame else 'None'}\n"
        text += f"  Right Crossing Frame: {tracked_car.right_crossing_frame if tracked_car.right_crossing_frame else 'None'}\n"
        text += "\n"

        return text

    def _compute_crossing_analysis(
        self,
        track_id: int,
        tracked_car: TrackedCar,
        detection: Optional[DetectionResult],
        left_coordinate: int,
        right_coordinate: int,
        crossing_events: List[CoordinateCrossingEvent],
        frame_number: int
    ) -> Dict[str, CrossingAnalysis]:
        """
        Compute crossing analysis for a tracked car.

        Args:
            track_id: Track ID of the car
            tracked_car: Tracked car to analyze
            detection: Detection result for current frame
            left_coordinate: Left coordinate value (scaled to match video coordinate space)
            right_coordinate: Right coordinate value (scaled to match video coordinate space)
            crossing_events: List of crossing events for current frame
            frame_number: Current frame number

        Returns:
            Dictionary mapping coordinate_type to CrossingAnalysis
        """
        analysis = {}

        if not detection:
            # No detection, can't compute crossing analysis
            return analysis

        vehicle_rightmost_x = detection.bounding_box.x2

        # Analyze left coordinate
        left_crossing_detected = any(
            event.track_id == track_id and
            event.coordinate_type == "left" and
            event.frame_number == frame_number
            for event in crossing_events
        )

        left_condition_met = vehicle_rightmost_x >= left_coordinate
        left_comparison = f"{vehicle_rightmost_x} >= {left_coordinate}" if left_condition_met else f"{vehicle_rightmost_x} < {left_coordinate}"

        if tracked_car.left_crossing_frame is None:
            left_state = "left_crossing_frame is None"
        else:
            left_state = f"Left already crossed at frame {tracked_car.left_crossing_frame}"

        analysis["left"] = CrossingAnalysis(
            track_id=track_id,
            coordinate_type="left",
            coordinate_value=left_coordinate,
            vehicle_rightmost_x=vehicle_rightmost_x,
            comparison_result=left_comparison,
            condition_met=left_condition_met,
            crossing_state=left_state,
            crossing_detected=left_crossing_detected
        )

        # Analyze right coordinate (only if left was already crossed)
        if tracked_car.left_crossing_frame is not None:
            right_crossing_detected = any(
                event.track_id == track_id and
                event.coordinate_type == "right" and
                event.frame_number == frame_number
                for event in crossing_events
            )

            right_condition_met = vehicle_rightmost_x >= right_coordinate
            right_comparison = f"{vehicle_rightmost_x} >= {right_coordinate}" if right_condition_met else f"{vehicle_rightmost_x} < {right_coordinate}"

            if tracked_car.right_crossing_frame is None:
                right_state = "Left already crossed, waiting for right"
            else:
                right_state = f"Right already crossed at frame {tracked_car.right_crossing_frame}"

            analysis["right"] = CrossingAnalysis(
                track_id=track_id,
                coordinate_type="right",
                coordinate_value=right_coordinate,
                vehicle_rightmost_x=vehicle_rightmost_x,
                comparison_result=right_comparison,
                condition_met=right_condition_met,
                crossing_state=right_state,
                crossing_detected=right_crossing_detected
            )
        else:
            # Left not crossed yet, can't check right
            analysis["right"] = CrossingAnalysis(
                track_id=track_id,
                coordinate_type="right",
                coordinate_value=right_coordinate,
                vehicle_rightmost_x=vehicle_rightmost_x,
                comparison_result=f"{vehicle_rightmost_x} < {right_coordinate} (left not crossed yet)",
                condition_met=False,
                crossing_state="Left not crossed yet, cannot check right",
                crossing_detected=False
            )

        return analysis

    def _format_crossing_explanation(
        self,
        crossing_analysis: Dict[str, CrossingAnalysis]
    ) -> str:
        """
        Format crossing detection explanation.

        Args:
            crossing_analysis: Dictionary mapping coordinate_type to CrossingAnalysis

        Returns:
            Formatted string with crossing explanation
        """
        text = ""

        for coord_type in ["left", "right"]:
            if coord_type not in crossing_analysis:
                continue

            analysis = crossing_analysis[coord_type]
            text += f"Crossing Analysis ({coord_type.capitalize()}):\n"

            if analysis.crossing_detected:
                text += f"  Coordinate Value: {analysis.coordinate_value}\n"
                text += f"  Car Rightmost X: {analysis.vehicle_rightmost_x}\n"
                text += f"  Comparison: {analysis.comparison_result}\n"
                text += f"  Condition Met: {'Yes' if analysis.condition_met else 'No'}\n"
                # Find the actual frame number from crossing events
                crossing_frame = "current frame"
                text += f"  Crossing Detected: Yes ({crossing_frame})\n"
            else:
                text += f"  Coordinate Value: {analysis.coordinate_value}\n"
                text += f"  Car Rightmost X: {analysis.vehicle_rightmost_x}\n"
                text += f"  Comparison: {analysis.comparison_result}\n"
                text += f"  Condition Met: {'Yes' if analysis.condition_met else 'No'}\n"
                text += f"  Crossing State: {analysis.crossing_state}\n"

            text += "\n"

        return text

    def _format_comparison(
        self,
        tracked_car: TrackedCar,
        json_measurements: List[SpeedMeasurement]
    ) -> str:
        """
        Format live vs JSON comparison.

        Args:
            tracked_car: Tracked car to compare
            json_measurements: Expected speed measurements from JSON

        Returns:
            Formatted string with comparison
        """
        text = "JSON Expected:\n"

        # Find matching JSON measurement by track_id
        json_match = None
        for measurement in json_measurements:
            if measurement.track_id == tracked_car.track_id:
                json_match = measurement
                break

        if json_match:
            text += f"  Left Crossing Frame: {json_match.left_crossing_frame}"
            if tracked_car.left_crossing_frame == json_match.left_crossing_frame:
                text += " (matches)\n"
            else:
                text += f" (expected, live: {tracked_car.left_crossing_frame})\n"

            text += f"  Right Crossing Frame: {json_match.right_crossing_frame}"
            if tracked_car.right_crossing_frame == json_match.right_crossing_frame:
                text += " (matches)\n"
            else:
                text += f" (expected, live: {tracked_car.right_crossing_frame})\n"

            text += f"  Speed: {json_match.speed_kmh:.2f} km/h\n"
        else:
            text += "  No expected measurement found for this track_id\n"

        return text

