"""JSON loader controller for parsing Feature 001 JSON result files."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.models import SpeedMeasurement
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class JsonLoader:
    """Controller for loading and parsing JSON result files from Feature 001."""

    def __init__(self):
        """Initialize JSON loader."""
        pass

    def load_json_file(self, json_path: str) -> Dict[str, Any]:
        """
        Load and parse JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            Parsed JSON data as dictionary

        Raises:
            FileNotFoundError: If JSON file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValueError: If JSON structure is invalid
        """
        path = Path(json_path)

        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON syntax: {str(e)}",
                e.doc,
                e.pos
            ) from e

        # Validate required fields
        if not isinstance(data, dict):
            raise ValueError("JSON file must contain a dictionary/object")

        required_fields = ['video_path', 'config_path']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(
                f"Missing required fields in JSON: {', '.join(missing_fields)}"
            )

        logger.info(
            "JSON file loaded",
            extra={
                "json_path": json_path,
                "video_path": data.get('video_path'),
                "config_path": data.get('config_path'),
                "has_speed_measurements": 'speed_measurements' in data
            }
        )

        return data

    def extract_video_path(self, json_data: Dict[str, Any]) -> str:
        """
        Extract video path from JSON data.

        Args:
            json_data: Parsed JSON data

        Returns:
            Video file path
        """
        return str(json_data['video_path'])

    def extract_config_path(self, json_data: Dict[str, Any]) -> str:
        """
        Extract configuration path from JSON data.

        Args:
            json_data: Parsed JSON data

        Returns:
            Configuration file path
        """
        return str(json_data['config_path'])

    def extract_speed_measurements(
        self,
        json_data: Dict[str, Any]
    ) -> List[SpeedMeasurement]:
        """
        Extract speed measurements from JSON data.

        Args:
            json_data: Parsed JSON data

        Returns:
            List of SpeedMeasurement objects
        """
        if 'speed_measurements' not in json_data:
            return []

        measurements = []
        speed_data_list = json_data['speed_measurements']

        if not isinstance(speed_data_list, list):
            logger.warning(
                "speed_measurements is not a list, skipping",
                extra={"json_data": json_data}
            )
            return []

        for sm_data in speed_data_list:
            try:
                # Calculate speed_ms from speed_kmh if not present
                speed_kmh = float(sm_data.get('speed_kmh', 0.0))
                speed_ms = sm_data.get('speed_ms')
                if speed_ms is None:
                    speed_ms = speed_kmh / 3.6  # Convert km/h to m/s

                measurement = SpeedMeasurement(
                    speed_kmh=speed_kmh,
                    speed_ms=float(speed_ms),
                    frame_count=int(sm_data.get('frame_count', 0)),
                    time_seconds=float(sm_data.get('time_seconds', 0.0)),
                    distance_meters=float(sm_data.get('distance_meters', 0.0)),
                    left_crossing_frame=int(sm_data.get('left_crossing_frame', 0)),
                    right_crossing_frame=int(sm_data.get('right_crossing_frame', 0)),
                    track_id=int(sm_data.get('track_id', 0)),
                    confidence=float(sm_data.get('confidence', 0.0)),
                    is_valid=bool(sm_data.get('is_valid', True))
                )
                measurements.append(measurement)
            except (ValueError, TypeError, KeyError) as e:
                logger.warning(
                    "Failed to parse speed measurement from JSON",
                    extra={"error": str(e), "data": sm_data}
                )
                continue

        logger.info(
            "Extracted speed measurements from JSON",
            extra={"count": len(measurements)}
        )

        return measurements

