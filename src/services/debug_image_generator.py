"""Debug image generator service for creating debug images on crossing events."""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional
import os

from src.models import Configuration, DetectionResult, CoordinateCrossingEvent
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class DebugImageGenerator:
    """Generates debug images showing crossing events with bounding boxes, coordinate lines, and criteria text."""

    def __init__(self, config: Configuration):
        """
        Initialize debug image generator.

        Args:
            config: Configuration with left and right coordinates
        """
        self.config = config
        self.left_coordinate = config.left_coordinate
        self.right_coordinate = config.right_coordinate

    def _format_criteria_text(
        self,
        event: CoordinateCrossingEvent,
        detection: DetectionResult
    ) -> str:
        """
        Format detection criteria text string.

        Args:
            event: Crossing event
            detection: Detection result for the crossing frame

        Returns:
            Formatted criteria text string
        """
        car_rightmost_x = detection.bounding_box.x2
        
        if event.coordinate_type == "left":
            criteria_text = (
                f"Frame: {event.frame_number} | Track ID: {event.track_id}\n"
                f"Bounding box X: {car_rightmost_x} - Left line coord: {self.left_coordinate}"
            )
        else:  # right
            criteria_text = (
                f"Frame: {event.frame_number} | Track ID: {event.track_id}\n"
                f"Bounding box X: {car_rightmost_x} - Right line coord: {self.right_coordinate}"
            )
        
        return criteria_text

    def _draw_bounding_box(
        self,
        img: np.ndarray,
        detection: DetectionResult,
        color: tuple = (0, 255, 0),
        thickness: int = 2
    ) -> None:
        """
        Draw bounding box on image.

        Args:
            img: Image to draw on
            detection: Detection result with bounding box
            color: BGR color tuple for bounding box
            thickness: Line thickness
        """
        bbox = detection.bounding_box
        cv2.rectangle(
            img,
            (bbox.x1, bbox.y1),
            (bbox.x2, bbox.y2),
            color,
            thickness
        )

    def _draw_coordinate_lines(
        self,
        img: np.ndarray,
        color: tuple = (255, 0, 0),
        thickness: int = 2
    ) -> None:
        """
        Draw vertical lines for left and right coordinates.

        Args:
            img: Image to draw on
            color: BGR color tuple for coordinate lines
            thickness: Line thickness
        """
        height = img.shape[0]
        
        # Draw left coordinate line
        cv2.line(
            img,
            (self.left_coordinate, 0),
            (self.left_coordinate, height),
            color,
            thickness
        )
        
        # Draw right coordinate line
        cv2.line(
            img,
            (self.right_coordinate, 0),
            (self.right_coordinate, height),
            color,
            thickness
        )

    def _draw_text(
        self,
        img: np.ndarray,
        text: str,
        position: tuple = (10, 30),
        font_scale: float = 0.6,
        color: tuple = (255, 255, 255),
        thickness: int = 1
    ) -> None:
        """
        Draw text on image.

        Args:
            img: Image to draw on
            text: Text string to draw
            position: (x, y) position for text
            font_scale: Font scale factor
            color: BGR color tuple for text
            thickness: Text thickness
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Split text into lines and draw each line
        lines = text.split('\n')
        y_offset = position[1]
        line_height = 25
        
        for line in lines:
            cv2.putText(
                img,
                line,
                (position[0], y_offset),
                font,
                font_scale,
                color,
                thickness,
                cv2.LINE_AA
            )
            y_offset += line_height

    def generate_debug_image(
        self,
        frame: np.ndarray,
        detection: DetectionResult,
        event: CoordinateCrossingEvent,
        frame_number: int
    ) -> Optional[str]:
        """
        Generate debug image for a crossing event.

        Args:
            frame: Video frame as numpy array
            detection: Detection result for the crossing
            event: Crossing event
            frame_number: Frame number for file naming

        Returns:
            Path to saved PNG file, or None if saving failed
        """
        try:
            # Create a copy of the frame to avoid modifying the original
            debug_img = frame.copy()
            
            # Draw bounding box (green)
            self._draw_bounding_box(debug_img, detection, color=(0, 255, 0), thickness=2)
            
            # Draw coordinate lines (red)
            self._draw_coordinate_lines(debug_img, color=(0, 0, 255), thickness=1)
            
            # Format and draw criteria text (white)
            criteria_text = self._format_criteria_text(event, detection)
            self._draw_text(debug_img, criteria_text, position=(10, 30), color=(0, 0, 0))
            
            # Generate filename
            filename = f"crossing_{frame_number}.png"

            # check if output folder exists and if not, create it
            output_folder = os.path.join(os.getcwd(), "output")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            
            # Save to current working directory (project folder)
            file_path = os.path.join(output_folder, filename)
            
            # Save image
            success = cv2.imwrite(file_path, debug_img)
            
            if success:
                logger.info(
                    "Debug image saved",
                    extra={
                        "file_path": file_path,
                        "frame_number": frame_number,
                        "coordinate_type": event.coordinate_type,
                        "track_id": event.track_id
                    }
                )
                return file_path
            else:
                logger.error(
                    "Failed to save debug image",
                    extra={
                        "file_path": file_path,
                        "frame_number": frame_number
                    }
                )
                return None
                
        except Exception as e:
            logger.error(
                "Error generating debug image",
                extra={
                    "frame_number": frame_number,
                    "error": str(e)
                },
                exc_info=True
            )
            return None

