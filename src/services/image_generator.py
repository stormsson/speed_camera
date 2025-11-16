"""Image generation service for creating composite visualization images."""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, List

from src.models import Configuration, TrackedCar
from src.services.video_processor import VideoProcessor


class ImageGenerator:
    """Generates composite images showing car crossings with boundary annotations."""

    def __init__(self, config: Configuration):
        """
        Initialize image generator.

        Args:
            config: Configuration with left and right coordinates
        """
        self.config = config
        self.left_coordinate = config.left_coordinate
        self.right_coordinate = config.right_coordinate

    def extract_crossing_frames(
        self,
        video_processor: VideoProcessor,
        tracked_car: TrackedCar
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Extract frames at left and right crossing points.

        Args:
            video_processor: Video processor instance
            tracked_car: Tracked car with crossing frame numbers

        Returns:
            Tuple of (left_frame, right_frame) or (None, None) if frames cannot be extracted
        """
        if tracked_car.left_crossing_frame is None or tracked_car.right_crossing_frame is None:
            return None, None

        left_frame = video_processor.get_frame(tracked_car.left_crossing_frame)
        right_frame = video_processor.get_frame(tracked_car.right_crossing_frame)

        return left_frame, right_frame

    def draw_vertical_bar(
        self,
        frame: np.ndarray,
        x_coordinate: int,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw a vertical bar at the specified x coordinate.

        Args:
            frame: Input frame
            x_coordinate: X coordinate for the vertical line
            color: RGB color tuple (default: green)
            thickness: Line thickness

        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        height = frame.shape[0]
        cv2.line(
            annotated,
            (x_coordinate, 0),
            (x_coordinate, height),
            color,
            thickness
        )
        return annotated

    def draw_bounding_box(
        self,
        frame: np.ndarray,
        bbox,
        color: Tuple[int, int, int] = (255, 0, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw a bounding box on the frame.

        Args:
            frame: Input frame
            bbox: BoundingBox object
            color: RGB color tuple (default: red)
            thickness: Line thickness

        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        cv2.rectangle(
            annotated,
            (bbox.x1, bbox.y1),
            (bbox.x2, bbox.y2),
            color,
            thickness
        )
        return annotated

    def add_label(
        self,
        frame: np.ndarray,
        text: str,
        position: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        font_scale: float = 0.7,
        thickness: int = 2
    ) -> np.ndarray:
        """
        Add text label to frame.

        Args:
            frame: Input frame
            text: Label text
            position: (x, y) position for text
            color: RGB color tuple (default: white)
            font_scale: Font scale
            thickness: Text thickness

        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        cv2.putText(
            annotated,
            text,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )
        return annotated

    def create_composite_image(
        self,
        left_frame: np.ndarray,
        right_frame: np.ndarray
    ) -> np.ndarray:
        """
        Create a side-by-side composite image from two frames.

        Args:
            left_frame: Left frame
            right_frame: Right frame

        Returns:
            Composite image with frames side-by-side
        """
        # Ensure frames have the same height
        if left_frame.shape[0] != right_frame.shape[0]:
            # Resize to match the smaller height
            min_height = min(left_frame.shape[0], right_frame.shape[0])
            left_frame = cv2.resize(left_frame, (left_frame.shape[1], min_height))
            right_frame = cv2.resize(right_frame, (right_frame.shape[1], min_height))

        # Concatenate horizontally
        composite = cv2.hconcat([left_frame, right_frame])
        return composite

    def annotate_frame(
        self,
        frame: np.ndarray,
        coordinate: int,
        bbox,
        label: str,
        coordinate_color: Tuple[int, int, int] = (0, 255, 0),
        bbox_color: Tuple[int, int, int] = (255, 0, 0)
    ) -> np.ndarray:
        """
        Annotate a frame with vertical bar, bounding box, and label.

        Args:
            frame: Input frame
            coordinate: X coordinate for vertical bar
            bbox: BoundingBox object for car
            label: Text label
            coordinate_color: Color for vertical bar
            bbox_color: Color for bounding box

        Returns:
            Fully annotated frame
        """
        annotated = frame.copy()

        # Draw vertical boundary line
        annotated = self.draw_vertical_bar(annotated, coordinate, coordinate_color)

        # Draw bounding box if provided
        if bbox is not None:
            annotated = self.draw_bounding_box(annotated, bbox, bbox_color)

        # Add label
        label_pos = (10, 30)
        annotated = self.add_label(annotated, label, label_pos)

        return annotated

    def annotate_frame_with_both_bars(
        self,
        frame: np.ndarray,
        bbox,
        label: str,
        left_color: Tuple[int, int, int] = (0, 255, 0),  # Green
        right_color: Tuple[int, int, int] = (0, 255, 0),  # Green
        bbox_color: Tuple[int, int, int] = (255, 0, 0),  # Red
        left_coord: Optional[int] = None,
        right_coord: Optional[int] = None
    ) -> np.ndarray:
        """
        Annotate a frame with both left and right coordinate vertical bars, bounding box, and label.

        Args:
            frame: Input frame
            bbox: BoundingBox object for car
            label: Text label
            left_color: Color for left coordinate bar
            right_color: Color for right coordinate bar
            bbox_color: Color for bounding box
            left_coord: Optional left coordinate (uses self.left_coordinate if not provided)
            right_coord: Optional right coordinate (uses self.right_coordinate if not provided)

        Returns:
            Fully annotated frame with both coordinate bars
        """
        annotated = frame.copy()

        # Use provided coordinates or fall back to config coordinates
        left_coord_to_use = left_coord if left_coord is not None else self.left_coordinate
        right_coord_to_use = right_coord if right_coord is not None else self.right_coordinate

        # Draw both vertical boundary lines
        annotated = self.draw_vertical_bar(annotated, left_coord_to_use, left_color)
        annotated = self.draw_vertical_bar(annotated, right_coord_to_use, right_color)

        # Draw bounding box if provided
        if bbox is not None:
            annotated = self.draw_bounding_box(annotated, bbox, bbox_color)

        # Add label
        label_pos = (10, 30)
        annotated = self.add_label(annotated, label, label_pos)

        return annotated

    def generate_composite_image(
        self,
        video_processor: VideoProcessor,
        tracked_car: TrackedCar,
        output_path: str
    ) -> str:
        """
        Generate and save composite image showing car crossings.

        Args:
            video_processor: Video processor instance
            tracked_car: Tracked car with crossing information
            output_path: Path to save the output image

        Returns:
            Path to saved image file

        Raises:
            ValueError: If tracked car doesn't have both crossing frames
        """
        if not tracked_car.is_complete():
            raise ValueError("TrackedCar must have crossed both coordinates")

        # Get scaled coordinates if video was resized
        scaled_coords = video_processor.get_scaled_coordinates()
        if scaled_coords:
            # Use scaled coordinates for annotation
            left_coord = scaled_coords[0]
            right_coord = scaled_coords[1]
        else:
            # Use original coordinates
            left_coord = self.left_coordinate
            right_coord = self.right_coordinate

        # Extract frames at crossing points
        left_frame, right_frame = self.extract_crossing_frames(video_processor, tracked_car)

        if left_frame is None or right_frame is None:
            raise ValueError("Could not extract crossing frames from video")

        # Get detections at crossing points
        left_detection = None
        right_detection = None

        for detection in tracked_car.detections:
            if detection.frame_number == tracked_car.left_crossing_frame:
                left_detection = detection
            if detection.frame_number == tracked_car.right_crossing_frame:
                right_detection = detection

        # Annotate left frame with both vertical bars (using appropriate coordinates)
        left_annotated = self.annotate_frame_with_both_bars(
            left_frame,
            left_detection.bounding_box if left_detection else None,
            "Left Crossing",
            left_coord=left_coord,
            right_coord=right_coord
        )

        # Annotate right frame with both vertical bars (using appropriate coordinates)
        right_annotated = self.annotate_frame_with_both_bars(
            right_frame,
            right_detection.bounding_box if right_detection else None,
            "Right Crossing",
            left_coord=left_coord,
            right_coord=right_coord
        )

        # Create composite
        composite = self.create_composite_image(left_annotated, right_annotated)

        # Save image
        output_file = Path(output_path)
        success = cv2.imwrite(str(output_file), composite)

        if not success:
            raise IOError(f"Failed to save image to {output_path}")

        return str(output_file)

    def generate_multi_car_composite_image(
        self,
        video_processor: VideoProcessor,
        tracked_cars: list,
        output_path: str
    ) -> str:
        """
        Generate and save composite image showing multiple cars vertically stacked.

        Args:
            video_processor: Video processor instance
            tracked_cars: List of TrackedCar objects that completed crossing
            output_path: Path to save the output image

        Returns:
            Path to saved image file

        Raises:
            ValueError: If no tracked cars provided or cars don't have both crossing frames
        """
        if not tracked_cars:
            raise ValueError("At least one tracked car must be provided")

        # Get scaled coordinates if video was resized
        scaled_coords = video_processor.get_scaled_coordinates()
        if scaled_coords:
            left_coord = scaled_coords[0]
            right_coord = scaled_coords[1]
        else:
            left_coord = self.left_coordinate
            right_coord = self.right_coordinate

        car_images = []

        # Generate composite image for each car
        for idx, tracked_car in enumerate(tracked_cars, 1):
            if not tracked_car.is_complete():
                continue

            # Extract frames at crossing points
            left_frame, right_frame = self.extract_crossing_frames(video_processor, tracked_car)

            if left_frame is None or right_frame is None:
                continue

            # Get detections at crossing points
            left_detection = None
            right_detection = None

            for detection in tracked_car.detections:
                if detection.frame_number == tracked_car.left_crossing_frame:
                    left_detection = detection
                if detection.frame_number == tracked_car.right_crossing_frame:
                    right_detection = detection

            # Annotate left frame with both vertical bars
            left_annotated = self.annotate_frame_with_both_bars(
                left_frame,
                left_detection.bounding_box if left_detection else None,
                f"Car {idx} - Left Crossing",
                left_coord=left_coord,
                right_coord=right_coord
            )

            # Annotate right frame with both vertical bars
            right_annotated = self.annotate_frame_with_both_bars(
                right_frame,
                right_detection.bounding_box if right_detection else None,
                f"Car {idx} - Right Crossing",
                left_coord=left_coord,
                right_coord=right_coord
            )

            # Create side-by-side composite for this car
            car_composite = self.create_composite_image(left_annotated, right_annotated)
            car_images.append(car_composite)

        if not car_images:
            raise ValueError("No valid car images could be generated")

        # Stack all car images vertically
        final_composite = car_images[0]
        for car_img in car_images[1:]:
            # Ensure all images have the same width
            if final_composite.shape[1] != car_img.shape[1]:
                target_width = final_composite.shape[1]
                aspect_ratio = car_img.shape[0] / car_img.shape[1]
                target_height = int(target_width * aspect_ratio)
                car_img = cv2.resize(car_img, (target_width, target_height))

            final_composite = cv2.vconcat([final_composite, car_img])

        # Save image
        output_file = Path(output_path)
        success = cv2.imwrite(str(output_file), final_composite)

        if not success:
            raise IOError(f"Failed to save image to {output_path}")

        return str(output_file)

