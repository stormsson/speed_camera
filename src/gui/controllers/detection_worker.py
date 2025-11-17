"""Worker thread for async detection processing."""

from typing import Tuple, List
import numpy as np
from PySide6.QtCore import QThread, Signal, QObject

from src.models import DetectionResult, TrackedCar, CoordinateCrossingEvent
from src.gui.controllers.detection_controller import DetectionController


class DetectionWorker(QThread):
    """Worker thread for running detection processing asynchronously."""

    # Signals - use object signal to pass Python objects
    detection_complete = Signal(object)  # Pass the results as a single object
    detection_error = Signal(str)  # error message

    def __init__(
        self,
        detection_controller: DetectionController,
        frame: np.ndarray,
        frame_number: int
    ):
        """
        Initialize detection worker.

        Args:
            detection_controller: Detection controller instance
            frame: Video frame as numpy array
            frame_number: Current frame number
        """
        super().__init__()
        self.detection_controller = detection_controller
        self.frame = frame
        self.frame_number = frame_number
        # Store results here to avoid signal serialization issues
        self._results = None

    def run(self) -> None:
        """Run detection processing."""
        try:
            # Check for interruption
            if self.isInterruptionRequested():
                return
                
            detections, tracked_cars, crossing_events = (
                self.detection_controller.process_frame(
                    self.frame,
                    self.frame_number
                )
            )
            
            # Check for interruption again
            if self.isInterruptionRequested():
                return
            
            # Convert tracked_cars list to dictionary
            tracked_cars_dict = {
                car.track_id: car for car in tracked_cars
            }
            
            # Store results in a simple dict structure
            self._results = {
                'detections': detections,
                'tracked_cars': tracked_cars_dict,
                'crossing_events': crossing_events
            }
            
            # Emit with object signal (passes by reference, works within same process)
            self.detection_complete.emit(self._results)
        except Exception as e:
            self.detection_error.emit(str(e))

