"""Car detection service using YOLO."""

from typing import List
import numpy as np
from ultralytics import YOLO

from src.models import DetectionResult, BoundingBox
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class CarDetector:
    """Detects cars in video frames using YOLO."""

    # YOLO class ID for "car" (COCO dataset)
    CAR_CLASS_ID = 2

    def __init__(self, confidence_threshold: float = 0.5, model_name: str = "yolov8n.pt"):
        """
        Initialize car detector.

        Args:
            confidence_threshold: Minimum confidence score for detections (0.0 to 1.0)
            model_name: YOLO model name (default: yolov8n.pt for nano model)
        """
        self.confidence_threshold = confidence_threshold
        self.model = YOLO(model_name)

    def detect(self, frame: np.ndarray, frame_number: int) -> List[DetectionResult]:
        """
        Detect cars in a frame.

        Args:
            frame: Video frame as numpy array
            frame_number: Current frame number

        Returns:
            List of DetectionResult objects for detected cars
        """
        # Run YOLO detection
        results = self.model(frame, verbose=False)

        detections = []

        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes

            for i in range(len(boxes)):
                # Extract box coordinates (x1, y1, x2, y2)
                box = boxes.xyxy[i].cpu().numpy()
                confidence = float(boxes.conf[i].cpu().numpy())
                class_id = int(boxes.cls[i].cpu().numpy())

                # Filter by confidence threshold
                if confidence < self.confidence_threshold:
                    continue

                # Filter by class (only cars)
                if class_id != self.CAR_CLASS_ID:
                    continue

                # Create bounding box
                bbox = BoundingBox(
                    x1=int(box[0]),
                    y1=int(box[1]),
                    x2=int(box[2]),
                    y2=int(box[3])
                )

                # Create detection result
                detection = DetectionResult(
                    frame_number=frame_number,
                    bounding_box=bbox,
                    confidence=confidence,
                    class_id=class_id,
                    class_name="car"
                )

                detections.append(detection)

                # Log detection
                logger.info(
                    "Car detected",
                    extra={
                        "frame_number": frame_number,
                        "confidence": confidence,
                        "bbox": {
                            "x1": bbox.x1,
                            "y1": bbox.y1,
                            "x2": bbox.x2,
                            "y2": bbox.y2,
                            "center_x": bbox.center_x,
                            "center_y": bbox.center_y
                        },
                        "event_type": "detection"
                    }
                )

        return detections

