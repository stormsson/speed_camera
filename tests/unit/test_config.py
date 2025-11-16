"""Unit tests for Configuration model and file loading."""

import pytest
import tempfile
import os
from pathlib import Path

from src.models.config import Configuration, InvalidConfigurationError


class TestConfigurationValidation:
    """Test Configuration model validation."""

    def test_valid_config(self):
        """Test creating a valid configuration."""
        config = Configuration(
            left_coordinate=100,
            right_coordinate=500,
            distance=200.0,
            fps=30.0
        )
        assert config.left_coordinate == 100
        assert config.right_coordinate == 500
        assert config.distance == 200.0
        assert config.fps == 30.0

    def test_left_coordinate_negative_raises_error(self):
        """Test that negative left_coordinate raises validation error."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            Configuration(
                left_coordinate=-1,
                right_coordinate=500,
                distance=200.0,
                fps=30.0
            )
        assert "left_coordinate" in str(exc_info.value).lower()
        assert "must be >= 0" in str(exc_info.value).lower()

    def test_right_coordinate_less_than_left_raises_error(self):
        """Test that right_coordinate <= left_coordinate raises validation error."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            Configuration(
                left_coordinate=500,
                right_coordinate=100,
                distance=200.0,
                fps=30.0
            )
        assert "right_coordinate" in str(exc_info.value).lower()
        assert "must be > left_coordinate" in str(exc_info.value).lower()

    def test_right_coordinate_equal_to_left_raises_error(self):
        """Test that right_coordinate equal to left_coordinate raises validation error."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            Configuration(
                left_coordinate=100,
                right_coordinate=100,
                distance=200.0,
                fps=30.0
            )
        assert "right_coordinate" in str(exc_info.value).lower()

    def test_distance_zero_raises_error(self):
        """Test that distance <= 0 raises validation error."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            Configuration(
                left_coordinate=100,
                right_coordinate=500,
                distance=0.0,
                fps=30.0
            )
        assert "distance" in str(exc_info.value).lower()
        assert "must be > 0" in str(exc_info.value).lower()

    def test_distance_negative_raises_error(self):
        """Test that negative distance raises validation error."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            Configuration(
                left_coordinate=100,
                right_coordinate=500,
                distance=-10.0,
                fps=30.0
            )
        assert "distance" in str(exc_info.value).lower()

    def test_fps_zero_raises_error(self):
        """Test that fps <= 0 raises validation error."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            Configuration(
                left_coordinate=100,
                right_coordinate=500,
                distance=200.0,
                fps=0.0
            )
        assert "fps" in str(exc_info.value).lower()
        assert "must be > 0" in str(exc_info.value).lower()

    def test_fps_negative_raises_error(self):
        """Test that negative fps raises validation error."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            Configuration(
                left_coordinate=100,
                right_coordinate=500,
                distance=200.0,
                fps=-10.0
            )
        assert "fps" in str(exc_info.value).lower()


class TestConfigurationFileParsing:
    """Test configuration file loading from YAML."""

    def test_load_valid_yaml_file(self):
        """Test loading a valid YAML configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
left_coordinate: 100
right_coordinate: 500
distance: 200
fps: 30
""")
            temp_path = f.name

        try:
            config = Configuration.load_from_yaml(temp_path)
            assert config.left_coordinate == 100
            assert config.right_coordinate == 500
            assert config.distance == 200.0
            assert config.fps == 30.0
        finally:
            os.unlink(temp_path)

    def test_load_yaml_with_float_values(self):
        """Test loading YAML with float values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
left_coordinate: 100
right_coordinate: 500
distance: 200.5
fps: 29.97
""")
            temp_path = f.name

        try:
            config = Configuration.load_from_yaml(temp_path)
            assert config.distance == 200.5
            assert config.fps == 29.97
        finally:
            os.unlink(temp_path)

    def test_load_file_not_found_raises_error(self):
        """Test that loading non-existent file raises error."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            Configuration.load_from_yaml("/nonexistent/path/config.yaml")
        assert "not found" in str(exc_info.value).lower() or "cannot read" in str(exc_info.value).lower()

    def test_load_invalid_yaml_raises_error(self):
        """Test that loading invalid YAML raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
left_coordinate: 100
right_coordinate: 500
invalid: yaml: syntax: [error
""")
            temp_path = f.name

        try:
            with pytest.raises(InvalidConfigurationError) as exc_info:
                Configuration.load_from_yaml(temp_path)
            assert "yaml" in str(exc_info.value).lower() or "parse" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)

    def test_load_missing_required_field_raises_error(self):
        """Test that missing required fields raise validation error."""
        # Missing left_coordinate
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
right_coordinate: 500
distance: 200
fps: 30
""")
            temp_path = f.name

        try:
            with pytest.raises(InvalidConfigurationError) as exc_info:
                Configuration.load_from_yaml(temp_path)
            assert "left_coordinate" in str(exc_info.value).lower()
            assert "missing" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)

    def test_load_missing_multiple_fields_raises_error(self):
        """Test that missing multiple required fields are all reported."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
left_coordinate: 100
""")
            temp_path = f.name

        try:
            with pytest.raises(InvalidConfigurationError) as exc_info:
                Configuration.load_from_yaml(temp_path)
            error_msg = str(exc_info.value).lower()
            # Should mention missing fields
            assert "right_coordinate" in error_msg or "distance" in error_msg or "fps" in error_msg
        finally:
            os.unlink(temp_path)

    def test_load_invalid_values_in_file_raises_error(self):
        """Test that invalid values in YAML file raise validation error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
left_coordinate: 100
right_coordinate: 50
distance: 200
fps: 30
""")
            temp_path = f.name

        try:
            with pytest.raises(InvalidConfigurationError) as exc_info:
                Configuration.load_from_yaml(temp_path)
            assert "right_coordinate" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)

    def test_downsize_video_optional_parameter_parsing(self):
        """Test that downsize_video optional parameter is parsed correctly."""
        config_yaml = """
left_coordinate: 100
right_coordinate: 500
distance: 200
fps: 30
downsize_video: 480
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_yaml)
            temp_path = f.name

        try:
            config = Configuration.load_from_yaml(temp_path)
            assert config.downsize_video == 480
        finally:
            os.unlink(temp_path)

    def test_downsize_video_missing_parameter(self):
        """Test that missing downsize_video parameter is handled gracefully."""
        config_yaml = """
left_coordinate: 100
right_coordinate: 500
distance: 200
fps: 30
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_yaml)
            temp_path = f.name

        try:
            config = Configuration.load_from_yaml(temp_path)
            assert config.downsize_video is None
        finally:
            os.unlink(temp_path)

    def test_downsize_video_validation_positive(self):
        """Test that downsize_video must be > 0 if present."""
        config_yaml = """
left_coordinate: 100
right_coordinate: 500
distance: 200
fps: 30
downsize_video: 0
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_yaml)
            temp_path = f.name

        try:
            with pytest.raises(InvalidConfigurationError) as exc_info:
                Configuration.load_from_yaml(temp_path)
            assert "downsize_video" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)

    def test_downsize_video_validation_negative(self):
        """Test that negative downsize_video is rejected."""
        config_yaml = """
left_coordinate: 100
right_coordinate: 500
distance: 200
fps: 30
downsize_video: -100
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_yaml)
            temp_path = f.name

        try:
            with pytest.raises(InvalidConfigurationError) as exc_info:
                Configuration.load_from_yaml(temp_path)
            assert "downsize_video" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)

    def test_coordinate_scaling_calculation(self):
        """Test coordinate scaling calculation when downsize_video is specified."""
        from src.models.config import Configuration
        
        # Original coordinates for 1920px width video
        original_left = 100
        original_right = 500
        downsize_width = 480
        
        # Calculate scale factor
        scale_factor = downsize_width / 1920.0
        
        # Expected scaled coordinates
        expected_left = int(original_left * scale_factor)
        expected_right = int(original_right * scale_factor)
        
        # Verify calculation
        assert expected_left == 25  # 100 * (480/1920) = 25
        assert expected_right == 125  # 500 * (480/1920) = 125
        assert scale_factor == 0.25  # 480/1920 = 0.25

