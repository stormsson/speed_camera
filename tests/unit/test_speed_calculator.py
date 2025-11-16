"""Unit tests for speed calculator."""

import pytest
from src.models import (
    SpeedMeasurement,
    Configuration,
    TrackedCar,
    DetectionResult,
    BoundingBox,
)


class TestSpeedCalculator:
    """Test speed calculation functionality."""

    def test_calculate_speed_basic(self):
        """Test basic speed calculation."""
        from src.services.speed_calculator import SpeedCalculator
        
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,  # 200 cm = 2 meters
            fps=30.0
        )
        calculator = SpeedCalculator(config)
        
        # Car crosses left at frame 0, right at frame 30
        # Time = 30 frames / 30 fps = 1 second
        # Speed = 2 meters / 1 second = 2 m/s = 7.2 km/h
        measurement = calculator.calculate(
            left_crossing_frame=0,
            right_crossing_frame=30,
            track_id=1,
            confidence=0.85
        )
        
        assert measurement.frame_count == 30
        assert measurement.time_seconds == pytest.approx(1.0, rel=0.01)
        assert measurement.distance_meters == pytest.approx(2.0, rel=0.01)
        assert measurement.speed_ms == pytest.approx(2.0, rel=0.01)
        assert measurement.speed_kmh == pytest.approx(7.2, rel=0.01)
        assert measurement.is_valid is True

    def test_speed_formula_verification(self):
        """Test speed formula: speed_kmh = (distance_meters / time_seconds) × 3.6."""
        from src.services.speed_calculator import SpeedCalculator
        
        config = Configuration(100, 500, 100.0, 10.0)  # 1 meter, 10 fps
        
        calculator = SpeedCalculator(config)
        
        # 10 frames at 10 fps = 1 second
        # Speed = 1 m / 1 s = 1 m/s = 3.6 km/h
        measurement = calculator.calculate(0, 10, 1, 0.85)
        
        assert measurement.speed_ms == pytest.approx(1.0, rel=0.01)
        assert measurement.speed_kmh == pytest.approx(3.6, rel=0.01)

    def test_unit_conversion_centimeters_to_meters(self):
        """Test conversion from centimeters to meters."""
        from src.services.speed_calculator import SpeedCalculator
        
        config = Configuration(100, 500, 500.0, 30.0)  # 500 cm = 5 meters
        
        calculator = SpeedCalculator(config)
        measurement = calculator.calculate(0, 30, 1, 0.85)
        
        assert measurement.distance_meters == pytest.approx(5.0, rel=0.01)

    def test_speed_calculation_with_different_fps(self):
        """Test speed calculation with different frame rates."""
        from src.services.speed_calculator import SpeedCalculator
        
        # 60 fps: faster frame rate means less time
        config = Configuration(100, 500, 200.0, 60.0)
        calculator = SpeedCalculator(config)
        
        # 60 frames at 60 fps = 1 second
        measurement = calculator.calculate(0, 60, 1, 0.85)
        assert measurement.time_seconds == pytest.approx(1.0, rel=0.01)
        assert measurement.speed_kmh == pytest.approx(7.2, rel=0.01)

    def test_validation_frame_count_positive(self):
        """Test that frame_count must be positive."""
        from src.services.speed_calculator import SpeedCalculator
        
        config = Configuration(100, 500, 200.0, 30.0)
        calculator = SpeedCalculator(config)
        
        # Same frame for left and right (invalid)
        with pytest.raises(ValueError):
            calculator.calculate(10, 10, 1, 0.85)

    def test_validation_time_positive(self):
        """Test that time must be positive."""
        from src.services.speed_calculator import SpeedCalculator
        
        config = Configuration(100, 500, 200.0, 30.0)
        calculator = SpeedCalculator(config)
        
        # Right before left (invalid order)
        with pytest.raises(ValueError):
            calculator.calculate(30, 0, 1, 0.85)

    def test_speed_measurement_attributes(self):
        """Test that speed measurement has all required attributes."""
        from src.services.speed_calculator import SpeedCalculator
        
        config = Configuration(100, 500, 200.0, 30.0)
        calculator = SpeedCalculator(config)
        
        measurement = calculator.calculate(0, 30, 1, 0.85)
        
        assert measurement.left_crossing_frame == 0
        assert measurement.right_crossing_frame == 30
        assert measurement.track_id == 1
        assert measurement.confidence == 0.85
        assert measurement.is_valid is True

    def test_realistic_speed_calculation(self):
        """Test realistic speed calculation scenario."""
        from src.services.speed_calculator import SpeedCalculator
        
        # Realistic scenario: 10 meters distance, 30 fps, car takes 60 frames
        config = Configuration(100, 500, 1000.0, 30.0)  # 10 meters
        calculator = SpeedCalculator(config)
        
        measurement = calculator.calculate(0, 60, 1, 0.90)
        
        # Time = 60 / 30 = 2 seconds
        # Speed = 10 m / 2 s = 5 m/s = 18 km/h
        assert measurement.time_seconds == pytest.approx(2.0, rel=0.01)
        assert measurement.speed_ms == pytest.approx(5.0, rel=0.01)
        assert measurement.speed_kmh == pytest.approx(18.0, rel=0.01)

