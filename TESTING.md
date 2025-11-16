# Testing Guide: Car Speed Detection

## Quick Start Testing

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- opencv-python (video processing)
- ultralytics (YOLO car detection)
- numpy, PyYAML, click (core dependencies)
- pytest (for running tests)

**Note**: YOLO will download model weights on first use (~6MB for yolov8n.pt).

### 2. Create a Configuration File

Create a file named `config.yaml`:

```yaml
left_coordinate: 100   # X pixel coordinate for left measurement line
right_coordinate: 500  # X pixel coordinate for right measurement line
distance: 200         # Real-world distance in centimeters between coordinates
fps: 30               # Video frame rate (frames per second)
```

**How to find coordinates:**
- Open your video in a video player
- Note the X pixel position where you want the left measurement line
- Note the X pixel position where you want the right measurement line
- Ensure right_coordinate > left_coordinate

**How to measure distance:**
- Measure the horizontal distance between the two coordinate points in real life
- Convert to centimeters
- Enter in the config file

### 3. Run the Application

#### Option A: Run as Python module

```bash
python -m src.cli.main video.mp4 config.yaml
```

#### Option B: Install and run as command

First, create a simple entry point or run directly:

```bash
python src/cli/main.py video.mp4 config.yaml
```

### 4. Example Output

**Text format (default):**
```
Car Speed Detection Result
==================================================
Video: video.mp4
Configuration: config.yaml

Speed: 45.20 km/h
Frame Count: 30
Time: 1.00 seconds
Distance: 2.00 meters

Left Crossing: Frame 100
Right Crossing: Frame 130
```

**JSON format:**
```bash
python -m src.cli.main video.mp4 config.yaml --output-format json
```

**CSV format:**
```bash
python -m src.cli.main video.mp4 config.yaml --output-format csv
```

### 5. Advanced Options

**Verbose logging:**
```bash
python -m src.cli.main video.mp4 config.yaml --verbose
```

**Save logs to file:**
```bash
python -m src.cli.main video.mp4 config.yaml --log-file processing.log
```

**Adjust detection sensitivity:**
```bash
python -m src.cli.main video.mp4 config.yaml --confidence-threshold 0.7
```

### 6. Troubleshooting

**"No module named 'cv2'" or "No module named 'ultralytics'":**
```bash
pip install -r requirements.txt
```

**"No car detected in video":**
- Check that cars are clearly visible
- Lower confidence threshold: `--confidence-threshold 0.3`
- Verify video quality and lighting

**"Car detected but did not cross both measurement coordinates":**
- Check that coordinates are correct for your video
- Ensure car moves from left to right
- Verify coordinates are within video frame bounds

**"Invalid configuration":**
- Check all required fields are present
- Ensure right_coordinate > left_coordinate
- Verify distance > 0 and fps > 0

### 7. Testing with Sample Data

If you don't have a video yet, you can:

1. **Record a test video:**
   - Use your phone to record a car passing by
   - Ensure camera is perpendicular to the road
   - Car should move horizontally from left to right

2. **Create test config:**
   - Use the sample config.yaml above
   - Adjust coordinates based on your video dimensions
   - Measure real-world distance between coordinates

### 8. Expected Performance

- Processing time: ~10-60 seconds for 10-minute videos
- First run: May take longer as YOLO downloads model weights
- Memory: Processes frame-by-frame (memory efficient)

