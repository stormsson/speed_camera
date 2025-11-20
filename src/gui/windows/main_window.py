"""Main window for car detection visualizer application."""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,

    QFileDialog,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QLabel,
    QDockWidget
)
from PySide6.QtCore import Qt, QEvent

from src.gui.widgets.video_display import VideoDisplayWidget
from src.gui.widgets.coordinate_overlay import CoordinateOverlayWidget
from src.gui.widgets.navigation_controls import NavigationControlsWidget
from src.gui.widgets.detection_overlay import DetectionOverlayWidget
from src.gui.widgets.debug_panel import DebugPanelWidget
from src.gui.controllers.detection_controller import DetectionController
from src.gui.controllers.detection_worker import DetectionWorker
from src.gui.controllers.json_loader import JsonLoader
from src.gui.controllers.video_controller import VideoController
from src.models import Configuration
from src.lib.exceptions import InvalidConfigurationError, VideoLoadError
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, parent=None):
        """Initialize main window."""
        super().__init__(parent)

        self.setWindowTitle("Car Detection Visualizer")
        self.setMinimumSize(800, 600)

        # Controllers
        self.json_loader = JsonLoader()
        self.video_controller = VideoController()
        self.detection_controller: DetectionController | None = None
        self.config: Configuration | None = None
        self.current_video_path: str | None = None
        self._video_metadata = None
        self._json_speed_measurements = []
        self._detection_worker: DetectionWorker | None = None

        # Setup UI
        self._setup_menu_bar()
        self._setup_central_widget()
        self._setup_status_bar()
        self._setup_debug_panel()

    def _setup_menu_bar(self) -> None:
        """Setup menu bar with File and View menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # Open JSON Result File action
        open_action = file_menu.addAction("Open JSON Result File...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_json_file)

        # Exit action
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # View menu
        view_menu = menubar.addMenu("View")
        
        # Toggle Debug Panel action (will be set up after debug panel is created)
        self.toggle_debug_action = view_menu.addAction("Show Debug Panel")
        self.toggle_debug_action.setCheckable(True)
        self.toggle_debug_action.setChecked(False)
        self.toggle_debug_action.triggered.connect(self._toggle_debug_panel)

    def _setup_central_widget(self) -> None:
        """Setup central widget with video display and overlay."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Video display widget
        self.video_display = VideoDisplayWidget()
        self.video_display.installEventFilter(self)
        layout.addWidget(self.video_display)

        # Coordinate overlay widget (transparent overlay on top of video display)
        self.coordinate_overlay = CoordinateOverlayWidget(self.video_display)
        # Overlay will be resized when video is loaded

        # Detection overlay widget (transparent overlay on top of video display)
        self.detection_overlay = DetectionOverlayWidget(self.video_display)
        # Overlay will be resized when video is loaded

        # Navigation controls widget
        self.navigation_controls = NavigationControlsWidget()
        self.navigation_controls.previous_frame_requested.connect(self._on_previous_frame)
        self.navigation_controls.next_frame_requested.connect(self._on_next_frame)
        self.navigation_controls.frame_number_changed.connect(self._on_frame_number_changed)
        self.navigation_controls.setMaximumHeight(80)  # Constrain height
        layout.addWidget(self.navigation_controls)

    def _setup_debug_panel(self) -> None:
        """Setup debug panel as dockable widget."""
        # Create debug panel widget
        self.debug_panel = DebugPanelWidget()

        # Create dock widget
        self.debug_dock = QDockWidget("Debug Information", self)
        self.debug_dock.setWidget(self.debug_panel)
        self.debug_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        
        # Add dock to main window
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.debug_dock)
        
        # Initially hide the dock (user can show it via View menu)
        self.debug_dock.setVisible(False)
        
        # Connect dock visibility changes to menu action
        self.debug_dock.visibilityChanged.connect(self._on_debug_panel_visibility_changed)

    def _toggle_debug_panel(self, checked: bool) -> None:
        """Toggle debug panel visibility."""
        if hasattr(self, 'debug_dock'):
            self.debug_dock.setVisible(checked)

    def _on_debug_panel_visibility_changed(self, visible: bool) -> None:
        """Handle debug panel visibility change."""
        if hasattr(self, 'toggle_debug_action'):
            self.toggle_debug_action.setChecked(visible)

    def _setup_status_bar(self) -> None:
        """Setup status bar."""
        self.status_bar = self.statusBar()
        self.detection_status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.detection_status_label)
        self.status_bar.showMessage("Ready")

    def _on_open_json_file(self) -> None:
        """Handle Open JSON Result File menu action."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open JSON Result File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Load JSON file
            json_data = self.json_loader.load_json_file(file_path)

            # Extract paths
            video_path = self.json_loader.extract_video_path(json_data)
            config_path = self.json_loader.extract_config_path(json_data)

            # Resolve relative paths relative to JSON file location
            json_dir = Path(file_path).parent
            if not os.path.isabs(video_path):
                video_path = str(json_dir / video_path)
            if not os.path.isabs(config_path):
                config_path = str(json_dir / config_path)

            # Extract speed measurements from JSON
            self._json_speed_measurements = self.json_loader.extract_speed_measurements(json_data)

            # Load configuration
            try:
                self.config = Configuration.load_from_yaml(config_path)
                
                # Initialize detection controller
                self.detection_controller = DetectionController(self.config)
            except InvalidConfigurationError as e:
                QMessageBox.critical(
                    self,
                    "Configuration Error",
                    f"Failed to load configuration file:\n{str(e)}"
                )
                logger.error("Configuration load error", extra={"error": str(e)})
                return

            # Load video
            try:
                metadata = self.video_controller.load_video(video_path, self.config)
                self.current_video_path = video_path

                # Update window title
                video_name = Path(video_path).name
                self.setWindowTitle(f"Car Detection Visualizer - {video_name}")

                # Display first frame
                first_frame = self.video_controller.get_frame(1)
                if first_frame:
                    self.video_display.display_frame(first_frame)

                # Setup coordinate overlay
                # Resize overlay to match video display widget
                self.coordinate_overlay.setGeometry(self.video_display.geometry())
                
                # Setup detection overlay
                self.detection_overlay.setGeometry(self.video_display.geometry())
                
                # Get scaled coordinates from VideoProcessor if available
                scaled_coords = self.video_controller.video_processor.get_scaled_coordinates()
                if scaled_coords:
                    left_coord, right_coord = scaled_coords
                    self.coordinate_overlay.set_scaled_coordinates(
                        left_coord,
                        right_coord,
                        metadata.width
                    )
                    
                    # Check for out-of-bounds coordinates
                    if (left_coord < 0 or left_coord > metadata.width or
                        right_coord < 0 or right_coord > metadata.width):
                        QMessageBox.warning(
                            self,
                            "Coordinate Warning",
                            f"Warning: Coordinates are outside video frame bounds (0 to {metadata.width}).\n"
                            f"Left: {left_coord}, Right: {right_coord}"
                        )
                else:
                    self.coordinate_overlay.set_configuration(self.config, metadata.width)
                    
                    # Check for out-of-bounds coordinates
                    if (self.config.left_coordinate < 0 or
                        self.config.left_coordinate > metadata.width or
                        self.config.right_coordinate < 0 or
                        self.config.right_coordinate > metadata.width):
                        QMessageBox.warning(
                            self,
                            "Coordinate Warning",
                            f"Warning: Coordinates are outside video frame bounds (0 to {metadata.width}).\n"
                            f"Left: {self.config.left_coordinate}, Right: {self.config.right_coordinate}"
                        )
                
                # Store reference for resize handling
                self._video_metadata = metadata

                # Update navigation controls
                self.navigation_controls.set_frame_info(1, metadata.frame_count)

                # Update status bar
                self.status_bar.showMessage(
                    f"Frame 1 of {metadata.frame_count}"
                )
                
                # Run detection on first frame
                self._run_detection_on_frame(1)

                logger.info(
                    "JSON file loaded successfully",
                    extra={
                        "json_path": file_path,
                        "video_path": video_path,
                        "config_path": config_path
                    }
                )

            except VideoLoadError as e:
                QMessageBox.critical(
                    self,
                    "Video Load Error",
                    f"Failed to load video file:\n{str(e)}"
                )
                logger.error("Video load error", extra={"error": str(e)})
                return

        except FileNotFoundError as e:
            QMessageBox.critical(
                self,
                "File Error",
                f"JSON file not found:\n{str(e)}"
            )
            logger.error("JSON file not found", extra={"error": str(e)})
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load JSON file:\n{str(e)}"
            )
            logger.error("JSON load error", extra={"error": str(e)})

    def _on_previous_frame(self) -> None:
        """Handle Previous Frame button click."""
        if self.video_controller is None:
            return

        frame = self.video_controller.previous_frame()
        if frame:
            self.video_display.display_frame(frame)
            metadata = self.video_controller.get_metadata()
            if metadata:
                current_frame = self.video_controller.current_frame_number
                self.navigation_controls.set_frame_info(current_frame, metadata.frame_count)
                self.status_bar.showMessage(
                    f"Frame {current_frame} of {metadata.frame_count}"
                )
                
                # Run detection on new frame
                self._run_detection_on_frame(current_frame)

    def _on_next_frame(self) -> None:
        """Handle Next Frame button click."""
        if self.video_controller is None:
            return

        frame = self.video_controller.next_frame()
        if frame:
            self.video_display.display_frame(frame)
            metadata = self.video_controller.get_metadata()
            if metadata:
                current_frame = self.video_controller.current_frame_number
                self.navigation_controls.set_frame_info(current_frame, metadata.frame_count)
                self.status_bar.showMessage(
                    f"Frame {current_frame} of {metadata.frame_count}"
                )
                

                # Disable navigation controls
                self.navigation_controls.prev_button.setEnabled(False)
                self.navigation_controls.next_button.setEnabled(False)
                self.navigation_controls.frame_input.setEnabled(False)
                # Run detection on new frame
                self._run_detection_on_frame(current_frame)

    def _on_frame_number_changed(self, frame_number: int) -> None:
        """Handle frame number input change."""
        if self.video_controller is None:
            return

        frame = self.video_controller.navigate_to_frame(frame_number)
        if frame:
            self.video_display.display_frame(frame)
            metadata = self.video_controller.get_metadata()
            if metadata:
                current_frame = self.video_controller.current_frame_number
                self.navigation_controls.set_frame_info(current_frame, metadata.frame_count)
                self.status_bar.showMessage(
                    f"Frame {current_frame} of {metadata.frame_count}"
                )
                
                # Run detection on new frame
                self._run_detection_on_frame(current_frame)

    def _run_detection_on_frame(self, frame_number: int) -> None:
        """Run detection processing on a frame asynchronously."""
        if self.detection_controller is None or self.video_controller is None:
            return

        # Stop any existing detection worker
        if self._detection_worker is not None and self._detection_worker.isRunning():
            self._detection_worker.requestInterruption()
            self._detection_worker.wait(1000)  # Wait up to 1 second
            if self._detection_worker.isRunning():
                self._detection_worker.terminate()
                self._detection_worker.wait()
            self._detection_worker = None

        # Get frame as numpy array
        frame_index = frame_number - 1
        frame_array = self.video_controller.video_processor.get_frame(frame_index)
        if frame_array is None:
            return

        # Update detection status
        self.detection_status_label.setText("Detecting...")
        

        # Create and start detection worker
        # Pass frame_index (0-indexed) to match detection system expectations
        self._detection_worker = DetectionWorker(
            self.detection_controller,
            frame_array,
            frame_index
        )
        self._detection_worker.detection_complete.connect(self._on_detection_complete)
        self._detection_worker.detection_error.connect(self._on_detection_error)
        self._detection_worker.start()

    def _on_detection_complete(self, results: dict) -> None:
        """Handle detection completion."""
        # Extract results from dict
        detections = results.get('detections', [])
        tracked_cars = results.get('tracked_cars', {})
        crossing_events = results.get('crossing_events', [])
        
        # Update detection overlay
        current_frame = self.video_controller.current_frame_number if self.video_controller else 0
        
        # Get video metadata for dimensions (already account for downscaling if used)
        metadata = self.video_controller.get_metadata() if self.video_controller else None
        video_width = metadata.width if metadata else 0
        video_height = metadata.height if metadata else 0
        
        # Get coordinate values for highlighting expected crossings
        left_coord = self.config.left_coordinate if self.config else 0
        right_coord = self.config.right_coordinate if self.config else 0
        
        # Get scaled coordinates if available
        if self.video_controller and self.video_controller.video_processor:
            scaled_coords = self.video_controller.video_processor.get_scaled_coordinates()
            if scaled_coords:
                left_coord, right_coord = scaled_coords
        
        self.detection_overlay.set_detection_data(
            detections,
            tracked_cars,
            crossing_events,
            self._json_speed_measurements,
            current_frame,
            left_coord,
            right_coord,
            video_width,
            video_height
        )
        
        # Update debug panel
        if hasattr(self, 'debug_panel') and self.debug_panel:
            # Get scaled coordinates if available (matching video coordinate space)
            debug_left_coord = left_coord
            debug_right_coord = right_coord
            
            # If no scaled coordinates, use config coordinates
            if debug_left_coord == 0 and self.config:
                debug_left_coord = self.config.left_coordinate
            if debug_right_coord == 0 and self.config:
                debug_right_coord = self.config.right_coordinate
            
            self.debug_panel.update_debug_info(
                current_frame,
                detections,
                tracked_cars,
                crossing_events,
                self.config,
                self._json_speed_measurements,
                left_coordinate=debug_left_coord,
                right_coordinate=debug_right_coord
            )

        # Update detection status
        self.detection_status_label.setText("Complete")

        # Re-enable navigation controls
        self.navigation_controls.prev_button.setEnabled(True)
        self.navigation_controls.next_button.setEnabled(True)
        self.navigation_controls.frame_input.setEnabled(True)

        # Clean up worker
        self._detection_worker = None

    def _on_detection_error(self, error_message: str) -> None:
        """Handle detection error."""
        self.detection_status_label.setText("Error")
        logger.error("Detection processing error", extra={"error": error_message})
        QMessageBox.warning(
            self,
            "Detection Error",
            f"Detection processing failed:\n{error_message}"
        )
        self._detection_worker = None

    def eventFilter(self, obj, event) -> bool:
        """Event filter for video display widget resize."""
        if obj == self.video_display and event.type() == QEvent.Type.Resize:
            # Resize overlays to match video display
            self.coordinate_overlay.setGeometry(self.video_display.geometry())
            self.coordinate_overlay.update()
            self.detection_overlay.setGeometry(self.video_display.geometry())
            self.detection_overlay.update()
        return super().eventFilter(obj, event)

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Stop detection worker if running
        if self._detection_worker is not None:
            if self._detection_worker.isRunning():
                self._detection_worker.requestInterruption()
                self._detection_worker.wait(3000)  # Wait up to 3 seconds
                if self._detection_worker.isRunning():
                    self._detection_worker.terminate()
                    self._detection_worker.wait()
            self._detection_worker = None
        
        # Cleanup resources
        if self.video_controller:
            self.video_controller.close()
        event.accept()

