# Quickstart: Car Detection Process Visualizer

**Feature**: Car Detection Process Visualizer  
**Date**: 2025-01-27

## Prerequisites

- Python 3.11+
- Feature 001 (Car Speed Detection) must be implemented and available
- JSON result file from Feature 001 CLI (contains video_path, config_path, speed_measurements)

## Installation

```bash
# Install dependencies
pip install PySide6 opencv-python numpy pytest pytest-qt

# Ensure Feature 001 dependencies are installed
pip install ultralytics PyYAML click
```

## Basic Usage

### 1. Launch the Application

```bash
python -m src.gui.main
```

### 2. Open a JSON Result File

1. Click "File" → "Open JSON Result File..."
2. Select a JSON file from Feature 001 CLI output (e.g., `moving_car_flipped_output.json`)
3. The system will automatically:
   - Load the video file from `video_path` in JSON
   - Load the configuration file from `config_path` in JSON
   - Extract speed measurements from `speed_measurements` in JSON
   - Display the first frame with coordinate overlays
   - Store expected results for highlighting known cars
4. The first frame will be displayed within 3 seconds

### 4. Navigate Frames

**Using Buttons**:
- Click "Previous Frame" to go back one frame
- Click "Next Frame" to advance one frame
- Buttons are disabled at video boundaries

**Using Frame Number Input**:
- Enter a frame number in the text input field
- Press Enter or click outside the field
- The display will jump to the specified frame
- Invalid frame numbers will show an error message

### 5. Visualize Detection Process

**Live Detection** (automatic on frame navigation):
1. Navigate to any frame (using buttons or frame number input)
2. Live detection automatically runs on the current frame (using Feature 001's VehicleDetector)
3. Bounding boxes, tracking IDs, and crossing events appear as detection completes (1-3 seconds)
4. Expected results from JSON are highlighted alongside live detection results
5. Known cars from JSON speed_measurements are highlighted with distinct visual style
6. Expected crossing frames from JSON (left_crossing_frame, right_crossing_frame) are highlighted when you navigate to those frames

## Example Workflow

### Validate Coordinate Positions

1. Open JSON result file: `moving_car_flipped_output.json`
2. System automatically loads video and config from JSON paths
3. Verify coordinate lines appear at correct positions
4. Navigate frames to see coordinates relative to video content

### Debug Detection Issues

1. Open JSON result file from Feature 001 CLI
2. Navigate frame-by-frame to observe:
   - Live detection running on each frame (bounding boxes appear after 1-3 seconds)
   - How cars are tracked (track IDs remain consistent across forward/backward navigation)
   - When cars cross coordinates (live crossing markers appear)
   - Expected results from JSON highlighted alongside live detection
3. Compare live detection results with expected results from JSON
4. Identify frames where detection fails or tracking differs from expected

### Verify Speed Calculation

1. Open JSON result file containing speed_measurements
2. Navigate to frames where cars cross left and right coordinates (from JSON: left_crossing_frame, right_crossing_frame)
3. Verify live crossing detection matches expected crossing frames from JSON
4. Check speed measurements displayed from JSON (speed_kmh, track_id, frame_count)
5. Compare live detection tracking with expected track_ids from JSON

## JSON Input File Format

The JSON file must be from Feature 001 CLI output and contain:

```json
{
  "success": true,
  "video_path": "/path/to/video.mp4",
  "config_path": "config.yml",
  "speed_measurements": [
    {
      "speed_kmh": 32.4,
      "frame_count": 15,
      "time_seconds": 0.5,
      "distance_meters": 4.5,
      "left_crossing_frame": 5,
      "right_crossing_frame": 20,
      "track_id": 1,
      "confidence": 0.86
    }
  ]
}
```

**Required Fields**:
- `video_path`: Path to MP4 video file (absolute or relative)
- `config_path`: Path to YAML configuration file (absolute or relative)
- `speed_measurements`: Array of speed measurement objects (may be empty)

**Speed Measurement Fields** (used for highlighting):
- `track_id`: Car tracking ID
- `left_crossing_frame`: Frame number where car crossed left coordinate
- `right_crossing_frame`: Frame number where car crossed right coordinate
- `speed_kmh`: Calculated speed (displayed but not used for detection)

## Keyboard Shortcuts (If Implemented)

- `←` / `←`: Previous frame
- `→` / `→`: Next frame
- `Ctrl+O`: Open JSON result file
- `Esc`: Close application

## Troubleshooting

### JSON File Won't Load

**Error**: "Failed to load JSON file"

**Solutions**:
- Verify JSON file is valid JSON format
- Check JSON contains required fields: video_path, config_path, speed_measurements
- Verify file permissions (must be readable)
- Check JSON syntax is correct

### Video File Won't Load (from JSON)

**Error**: "Failed to load video file from JSON"

**Solutions**:
- Verify video_path in JSON points to valid MP4 file
- Check file permissions (must be readable)
- Ensure video file is not corrupted
- Verify path is correct (absolute or relative to JSON file location)

### Configuration File Invalid

**Error**: "Invalid configuration: [error details]"

**Solutions**:
- Verify all required parameters are present
- Check parameter values are valid (positive numbers, right_coordinate > left_coordinate)
- Verify YAML syntax is correct
- Check file encoding (must be UTF-8)

### Frame Navigation Slow

**Symptoms**: Frame updates take longer than 0.5 seconds

**Solutions**:
- Check video file is not corrupted
- Verify system has sufficient memory
- Try using downsize_video parameter to reduce video resolution
- Check for background processes consuming resources

### Detection Not Appearing

**Symptoms**: No bounding boxes or tracking information displayed

**Solutions**:
- Wait for detection to complete (1-3 seconds per frame)
- Check that cars are actually present in the current frame
- Verify Feature 001's VehicleDetector service is working correctly
- Check detection confidence threshold (may be too high)
- Navigate to frames where cars are expected (from JSON speed_measurements)
- Verify tracking state is maintained across navigation (should persist forward/backward)

### Coordinate Lines Not Visible

**Symptoms**: Coordinate overlay lines don't appear

**Solutions**:
- Verify configuration file has been loaded
- Check that coordinates are within video frame bounds
- Verify coordinates are scaled correctly if downsize_video is used
- Check coordinate line color/width settings

## Next Steps

- See [spec.md](./spec.md) for complete feature specification
- See [plan.md](./plan.md) for implementation details
- See [data-model.md](./data-model.md) for data model documentation
- See [contracts/gui-interface.md](./contracts/gui-interface.md) for GUI interface contracts

