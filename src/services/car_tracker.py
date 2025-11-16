"""Car tracking service using IoU (Intersection over Union) matching."""

from typing import List, Dict
import numpy as np

from src.models import DetectionResult, TrackedCar


def calculate_iou(box1: DetectionResult, box2: DetectionResult) -> float:
    """
    Calculate Intersection over Union (IoU) between two detections.

    Args:
        box1: First detection
        box2: Second detection

    Returns:
        IoU value between 0.0 and 1.0
    """
    bbox1 = box1.bounding_box
    bbox2 = box2.bounding_box

    # Calculate intersection area
    x1 = max(bbox1.x1, bbox2.x1)
    y1 = max(bbox1.y1, bbox2.y1)
    x2 = min(bbox1.x2, bbox2.x2)
    y2 = min(bbox1.y2, bbox2.y2)

    if x2 <= x1 or y2 <= y1:
        return 0.0

    intersection = (x2 - x1) * (y2 - y1)

    # Calculate union area
    area1 = bbox1.width * bbox1.height
    area2 = bbox2.width * bbox2.height
    union = area1 + area2 - intersection

    if union == 0:
        return 0.0

    return intersection / union


class CarTracker:
    """Tracks cars across frames using IoU matching."""

    def __init__(self, iou_threshold: float = 0.3):
        """
        Initialize car tracker.

        Args:
            iou_threshold: Minimum IoU for matching detections to existing tracks
        """
        self.iou_threshold = iou_threshold
        self.tracked_cars: Dict[int, TrackedCar] = {}
        self.next_track_id = 1

    def update(self, detections: List[DetectionResult], frame_number: int) -> List[TrackedCar]:
        """
        Update tracks with new detections.

        Args:
            detections: List of detections in current frame
            frame_number: Current frame number

        Returns:
            List of currently tracked cars
        """
        if not detections:
            # No detections, return existing tracks
            return list(self.tracked_cars.values())

        # Match detections to existing tracks
        matched_tracks = set()
        matched_detections = set()

        # Try to match each detection to existing tracks
        for detection in detections:
            best_iou = 0.0
            best_track_id = None

            for track_id, tracked_car in self.tracked_cars.items():
                if track_id in matched_tracks:
                    continue

                # Calculate IoU with last detection in track
                if tracked_car.detections:
                    last_detection = tracked_car.detections[-1]
                    iou = calculate_iou(detection, last_detection)

                    if iou > best_iou and iou >= self.iou_threshold:
                        best_iou = iou
                        best_track_id = track_id

            # Match detection to best track
            if best_track_id is not None:
                self.tracked_cars[best_track_id].add_detection(detection)
                matched_tracks.add(best_track_id)
                matched_detections.add(id(detection))

        # Create new tracks for unmatched detections
        for detection in detections:
            if id(detection) not in matched_detections:
                new_track = TrackedCar(track_id=self.next_track_id)
                new_track.add_detection(detection)
                self.tracked_cars[self.next_track_id] = new_track
                self.next_track_id += 1

        return list(self.tracked_cars.values())

    def get_tracked_car(self, track_id: int) -> TrackedCar:
        """
        Get a tracked car by ID.

        Args:
            track_id: Track ID

        Returns:
            TrackedCar object
        """
        return self.tracked_cars[track_id]

