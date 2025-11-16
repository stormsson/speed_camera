"""Integration tests for multi-car output formats."""

import pytest
import json
import csv
from io import StringIO

from src.models import (
    ProcessingResult, SpeedMeasurement, VideoMetadata, Configuration
)


class TestMultiCarOutputFormats:
    """Test output formats with multiple cars."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration."""
        return Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0
        )

    @pytest.fixture
    def sample_metadata(self):
        """Create sample video metadata."""
        return VideoMetadata(
            file_path="test_video.mp4",
            frame_count=200,
            fps=30.0,
            width=640,
            height=480,
            duration_seconds=6.67
        )

    @pytest.fixture
    def multi_car_result(self, sample_config, sample_metadata):
        """Create ProcessingResult with multiple speed measurements."""
        measurement1 = SpeedMeasurement(
            speed_kmh=60.0,
            speed_ms=16.67,
            frame_count=30,
            time_seconds=1.0,
            distance_meters=2.0,
            left_crossing_frame=10,
            right_crossing_frame=40,
            track_id=1,
            confidence=0.85,
            is_valid=True
        )
        
        measurement2 = SpeedMeasurement(
            speed_kmh=80.0,
            speed_ms=22.22,
            frame_count=20,
            time_seconds=0.67,
            distance_meters=2.0,
            left_crossing_frame=70,
            right_crossing_frame=90,
            track_id=2,
            confidence=0.80,
            is_valid=True
        )
        
        return ProcessingResult(
            video_path="test_video.mp4",
            config_path="config.yaml",
            video_metadata=sample_metadata,
            config=sample_config,
            speed_measurements=[measurement1, measurement2],
            processing_time_seconds=2.0,
            frames_processed=200,
            detections_count=100
        )

    def test_text_output_with_multiple_cars(self, multi_car_result):
        """Test text output format with multiple cars."""
        from src.cli.main import format_text_output
        
        output = format_text_output(multi_car_result)
        
        # Should contain "Car 1" and "Car 2"
        assert "Car 1" in output or "Car" in output
        assert "60.00" in output or "60.0" in output  # First car speed
        assert "80.00" in output or "80.0" in output  # Second car speed
        assert "test_video.mp4" in output

    def test_json_output_with_multiple_cars(self, multi_car_result):
        """Test JSON output format with multiple cars."""
        from src.cli.main import format_json_output
        
        output = format_json_output(multi_car_result)
        data = json.loads(output)
        
        # Should have speed_measurements as array
        assert "speed_measurements" in data
        assert isinstance(data["speed_measurements"], list)
        assert len(data["speed_measurements"]) == 2
        
        # Check first car
        assert data["speed_measurements"][0]["speed_kmh"] == 60.0
        assert data["speed_measurements"][0]["track_id"] == 1
        
        # Check second car
        assert data["speed_measurements"][1]["speed_kmh"] == 80.0
        assert data["speed_measurements"][1]["track_id"] == 2

    def test_csv_output_with_multiple_cars(self, multi_car_result):
        """Test CSV output format with multiple cars."""
        from src.cli.main import format_csv_output
        
        output = format_csv_output(multi_car_result)
        
        # Parse CSV
        reader = csv.DictReader(StringIO(output))
        rows = list(reader)
        
        # Should have multiple rows, one per car
        assert len(rows) == 2
        
        # Check first car
        assert rows[0]["speed_kmh"] == "60.0"
        assert rows[0]["track_id"] == "1"
        
        # Check second car
        assert rows[1]["speed_kmh"] == "80.0"
        assert rows[1]["track_id"] == "2"
        
        # Both should have same video path
        assert rows[0]["video_path"] == "test_video.mp4"
        assert rows[1]["video_path"] == "test_video.mp4"

    def test_text_output_with_no_cars(self, sample_config, sample_metadata):
        """Test text output when no cars are detected."""
        from src.cli.main import format_text_output
        
        result = ProcessingResult(
            video_path="test_video.mp4",
            config_path="config.yaml",
            video_metadata=sample_metadata,
            config=sample_config,
            speed_measurements=[],
            processing_time_seconds=1.5,
            frames_processed=200,
            detections_count=0,
            error_message="No car detected"
        )
        
        output = format_text_output(result)
        assert "Error" in output or "No" in output

    def test_json_output_with_no_cars(self, sample_config, sample_metadata):
        """Test JSON output when no cars are detected."""
        from src.cli.main import format_json_output
        
        result = ProcessingResult(
            video_path="test_video.mp4",
            config_path="config.yaml",
            video_metadata=sample_metadata,
            config=sample_config,
            speed_measurements=[],
            processing_time_seconds=1.5,
            frames_processed=200,
            detections_count=0,
            error_message="No car detected"
        )
        
        output = format_json_output(result)
        data = json.loads(output)
        
        assert data["success"] is False
        assert "error" in data
        assert "speed_measurements" in data
        assert data["speed_measurements"] == []

