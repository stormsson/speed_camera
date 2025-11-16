# Quickstart Guide: Car Speed Detection

**Feature**: Car Speed Detection from Video  
**Date**: 2025-01-27

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- MP4 video file with cars moving left to right
- Configuration file with measurement parameters

## Installation

### 1. Install Dependencies

```bash
pip install opencv-python>=4.8.0
pip install ultralytics>=8.0.0
pip install numpy>=1.24.0
pip install PyYAML>=6.0
pip install click>=8.1.0
```

Or install from requirements file (if provided):
```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python -c "import cv2; import ultralytics; print('Dependencies installed successfully')"
```

## Configuration File Setup

Create a YAML configuration file (e.g., `config.yaml`):

```yaml
left_coordinate: 100   # X coordinate in pixels for left measurement line
right_coordinate: 500   # X coordinate in pixels for right measurement line
distance: 200          # Real-world distance in centimeters between coordinates
fps: 30                # Frames per second of the video
```

### Configuration Parameters Explained

- **left_coordinate**: The X pixel coordinate where the left measurement line is drawn. This is where the car's speed measurement starts.
- **right_coordinate**: The X pixel coordinate where the right measurement line is drawn. This is where the car's speed measurement ends.
- **distance**: The real-world horizontal distance between the left and right coordinates in centimeters. This is used to calculate speed.
- **fps**: The frame rate of the video (frames per second). Used to convert frame count to time.

### Finding Coordinate Values

1. Open your video in a video player or image editor
2. Identify where you want the left and right measurement lines
3. Note the X pixel coordinates (horizontal position)
4. Ensure `right_coordinate > left_coordinate`

### Measuring Real-World Distance

1. Measure the horizontal distance between the two coordinate points in the real world
2. Convert to centimeters
3. Enter this value as `distance` in the configuration

## Basic Usage

### Simple Command

```bash
car-speed-detection video.mp4 config.yaml
```

This will:
1. Load the video file
2. Load the configuration
3. Process frames to detect cars
4. Track cars and detect coordinate crossings
5. Calculate speed
6. Output result to stdout

### Example Output

```
Car Speed Detection Result
==========================
Video: video.mp4
Configuration: config.yaml

Speed: 45.2 km/h
Frame Count: 30
Time: 1.0 seconds
Distance: 2.0 meters

Left Crossing: Frame 100
Right Crossing: Frame 130
```

## Advanced Usage

### JSON Output

Get structured JSON output:

```bash
car-speed-detection video.mp4 config.yaml --output-format json
```

Output:
```json
{
  "success": true,
  "video_path": "video.mp4",
  "config_path": "config.yaml",
  "speed_kmh": 45.2,
  "frame_count": 30,
  "time_seconds": 1.0,
  "distance_meters": 2.0,
  "left_crossing_frame": 100,
  "right_crossing_frame": 130,
  "track_id": 1,
  "confidence": 0.85,
  "processing_time_seconds": 12.5
}
```

### Verbose Logging

See detailed processing information:

```bash
car-speed-detection video.mp4 config.yaml --verbose
```

This prints to stderr:
- Frame processing progress
- Detection events
- Tracking updates
- Coordinate crossings

### Save Logs to File

```bash
car-speed-detection video.mp4 config.yaml --log-file processing.log
```

Creates a JSON log file with structured event data.

### Adjust Detection Sensitivity

Use a higher confidence threshold for more reliable detections:

```bash
car-speed-detection video.mp4 config.yaml --confidence-threshold 0.7
```

Default is 0.5. Higher values (0.7-0.9) reduce false positives but may miss some cars.

## Troubleshooting

### "No car detected in video"

**Possible causes**:
- No cars in the video
- Cars not clearly visible
- Confidence threshold too high
- Video quality too low

**Solutions**:
- Lower confidence threshold: `--confidence-threshold 0.3`
- Check video quality and lighting
- Ensure cars are clearly visible and moving left to right

### "Car detected but did not cross both measurement coordinates"

**Possible causes**:
- Car doesn't cross both left and right coordinates
- Car moves in wrong direction (right to left)
- Coordinates set incorrectly

**Solutions**:
- Verify coordinates are correct for your video
- Ensure car moves from left to right
- Check that coordinates are within video frame bounds

### "Invalid configuration: Missing required field"

**Possible causes**:
- Configuration file missing required fields
- YAML syntax error

**Solutions**:
- Check all required fields are present: `left_coordinate`, `right_coordinate`, `distance`, `fps`
- Validate YAML syntax
- Ensure numeric values are correct

### "Failed to load video file"

**Possible causes**:
- Video file doesn't exist
- Video file is corrupted
- Unsupported video format

**Solutions**:
- Verify file path is correct
- Ensure file is MP4 format
- Try re-encoding the video

### Slow Processing

**Possible causes**:
- Large video file
- High resolution video
- CPU-only processing (no GPU)

**Solutions**:
- Processing is frame-by-frame and may take time for long videos
- Consider using GPU if available (automatic if CUDA available)
- Expected: ~10-60 seconds for 10-minute videos

## Testing with Sample Data

### Create Test Configuration

Create `test_config.yaml`:
```yaml
left_coordinate: 100
right_coordinate: 500
distance: 200
fps: 30
```

### Test with Your Video

```bash
car-speed-detection your_video.mp4 test_config.yaml --verbose
```

## Next Steps

- Review the [data model documentation](./data-model.md) for entity details
- Check [research documentation](./research.md) for technology choices
- See [implementation plan](./plan.md) for architecture details

## Getting Help

```bash
car-speed-detection --help
```

Shows all available options and usage information.

