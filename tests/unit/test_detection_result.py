"""Unit tests for ProcessingResult with multiple speed measurements."""

import pytest
from src.models import (
    ProcessingResult, SpeedMeasurement, VideoMetadata, Configuration
)


class TestProcessingResultMultipleMeasurements:
    """Test ProcessingResult model with multiple speed measurements."""

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

    def test_processing_result_with_empty_measurements_list(self, sample_config, sample_metadata):
        """Test ProcessingResult with empty speed_measurements list."""
        result = ProcessingResult(
            video_path="test_video.mp4",
            config_path="config.yaml",
            video_metadata=sample_metadata,
            config=sample_config,
            speed_measurements=[],  # Empty list
            processing_time_seconds=1.5,
            frames_processed=200,
            detections_count=50
        )
        
        assert result.speed_measurements == []
        assert len(result.speed_measurements) == 0

    def test_processing_result_with_single_measurement(self, sample_config, sample_metadata):
        """Test ProcessingResult with single speed measurement (backward compatibility)."""
        measurement = SpeedMeasurement(
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
        
        result = ProcessingResult(
            video_path="test_video.mp4",
            config_path="config.yaml",
            video_metadata=sample_metadata,
            config=sample_config,
            speed_measurements=[measurement],
            processing_time_seconds=1.5,
            frames_processed=200,
            detections_count=50
        )
        
        assert len(result.speed_measurements) == 1
        assert result.speed_measurements[0].speed_kmh == 60.0
        assert result.speed_measurements[0].track_id == 1

    def test_processing_result_with_multiple_measurements(self, sample_config, sample_metadata):
        """Test ProcessingResult with multiple speed measurements."""
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
        
        result = ProcessingResult(
            video_path="test_video.mp4",
            config_path="config.yaml",
            video_metadata=sample_metadata,
            config=sample_config,
            speed_measurements=[measurement1, measurement2],
            processing_time_seconds=2.0,
            frames_processed=200,
            detections_count=100
        )
        
        assert len(result.speed_measurements) == 2
        assert result.speed_measurements[0].track_id == 1
        assert result.speed_measurements[1].track_id == 2
        assert result.speed_measurements[0].speed_kmh == 60.0
        assert result.speed_measurements[1].speed_kmh == 80.0

    def test_processing_result_backward_compatibility(self, sample_config, sample_metadata):
        """Test that ProcessingResult maintains backward compatibility with speed_measurement property."""
        measurement = SpeedMeasurement(
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
        
        result = ProcessingResult(
            video_path="test_video.mp4",
            config_path="config.yaml",
            video_metadata=sample_metadata,
            config=sample_config,
            speed_measurements=[measurement],
            processing_time_seconds=1.5,
            frames_processed=200,
            detections_count=50
        )
        
        # Test backward compatibility property
        assert result.speed_measurement is not None
        assert result.speed_measurement.track_id == 1
        assert result.speed_measurement.speed_kmh == 60.0

