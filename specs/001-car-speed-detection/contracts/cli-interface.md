# CLI Interface Contract

**Feature**: Car Speed Detection from Video  
**Date**: 2025-01-27  
**Interface Type**: Command-Line Interface

## Command Structure

### Primary Command

```bash
car-speed-detection <video-file> <config-file> [OPTIONS]
```

### Arguments

#### Required Arguments

- `<video-file>` (positional)
  - **Type**: File path (string)
  - **Description**: Path to MP4 video file to process
  - **Validation**: File must exist and be readable
  - **Error**: "Video file not found: {path}" or "Cannot read video file: {path}"

- `<config-file>` (positional)
  - **Type**: File path (string)
  - **Description**: Path to YAML configuration file
  - **Validation**: File must exist, be readable, and contain valid YAML with required fields
  - **Error**: "Configuration file not found: {path}" or "Invalid configuration: {error details}"

#### Optional Arguments

- `--output-format` / `-f`
  - **Type**: Choice (json, text, csv)
  - **Default**: `text`
  - **Description**: Output format for results
  - **Values**:
    - `text`: Human-readable text output (default)
    - `json`: JSON structured output
    - `csv`: CSV format output

- `--verbose` / `-v`
  - **Type**: Flag (boolean)
  - **Default**: `false`
  - **Description**: Enable verbose logging output
  - **Effect**: Prints detailed processing information to stderr

- `--log-file` / `-l`
  - **Type**: File path (string)
  - **Default**: None (no file logging)
  - **Description**: Path to write structured log file
  - **Format**: JSON lines (one JSON object per line)

- `--confidence-threshold` / `-c`
  - **Type**: Float (0.0 to 1.0)
  - **Default**: `0.5`
  - **Description**: Minimum confidence score for car detection
  - **Validation**: Must be between 0.0 and 1.0

- `--show` / `-s`
  - **Type**: Flag (boolean)
  - **Default**: `false`
  - **Description**: Generate and save a composite image showing the car crossing both boundaries
  - **Effect**: Creates a side-by-side image with left crossing frame and right crossing frame, including vertical bars indicating the measurement coordinates and car bounding boxes
  - **Output**: Saves image file (PNG format) in current directory with auto-generated filename (e.g., `{video_name}_speed_result.png`)

- `--help` / `-h`
  - **Type**: Flag
  - **Description**: Show help message and exit

## Output Formats

### Text Output (Default)

**Success Case**:
```
Car Speed Detection Result
==========================
Video: /path/to/video.mp4
Configuration: /path/to/config.yaml

Speed: 45.2 km/h
Frame Count: 30
Time: 1.0 seconds
Distance: 2.0 meters

Left Crossing: Frame 100
Right Crossing: Frame 130
```

**Error Case**:
```
Error: No car detected in video
Video: /path/to/video.mp4
```

**Exit Code**: 0 (success) or 1 (error)

### JSON Output

**Success Case**:
```json
{
  "success": true,
  "video_path": "/path/to/video.mp4",
  "config_path": "/path/to/config.yaml",
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

**Error Case**:
```json
{
  "success": false,
  "error": "No car detected in video",
  "video_path": "/path/to/video.mp4",
  "config_path": "/path/to/config.yaml",
  "processing_time_seconds": 10.2
}
```

**Exit Code**: 0 (success) or 1 (error)

### CSV Output

**Success Case**:
```csv
video_path,config_path,speed_kmh,frame_count,time_seconds,distance_meters,left_crossing_frame,right_crossing_frame,track_id,confidence,processing_time_seconds
/path/to/video.mp4,/path/to/config.yaml,45.2,30,1.0,2.0,100,130,1,0.85,12.5
```

**Error Case**:
```csv
video_path,config_path,error,processing_time_seconds
/path/to/video.mp4,/path/to/config.yaml,"No car detected in video",10.2
```

**Exit Code**: 0 (success) or 1 (error)

## Error Handling

### Error Categories

1. **File Not Found**
   - Video file: `"Video file not found: {path}"`
   - Config file: `"Configuration file not found: {path}"`
   - Exit code: 1

2. **Invalid Configuration**
   - Missing field: `"Invalid configuration: Missing required field '{field}'"`
   - Invalid value: `"Invalid configuration: '{field}' must be {requirement}"`
   - Exit code: 1

3. **Video Processing Error**
   - Cannot open: `"Failed to load video file: {error}"`
   - Corrupted: `"Video file appears to be corrupted: {error}"`
   - Exit code: 1

4. **Detection Error**
   - No car detected: `"No car detected in video"`
   - Car not crossing: `"Car detected but did not cross both measurement coordinates"`
   - Exit code: 1

5. **Processing Error**
   - General: `"Processing failed: {error}"`
   - Exit code: 1

### Error Output

Errors are always written to **stderr**, regardless of output format.

**Text format**: Error message to stderr
**JSON format**: Error object to stdout (with `"success": false`)
**CSV format**: Error in CSV row to stdout

## Logging

### Verbose Mode (`--verbose`)

When enabled, prints to stderr:
- Frame processing progress
- Detection events
- Tracking updates
- Coordinate crossing events
- Performance metrics

### Log File (`--log-file`)

When specified, writes structured JSON logs:
- One JSON object per line
- Includes: timestamp, frame_number, event_type, details
- Example:
```json
{"timestamp": "2025-01-27T10:30:45.123Z", "frame": 100, "event": "detection", "confidence": 0.85, "bbox": {"x1": 50, "y1": 100, "x2": 200, "y2": 250}}
{"timestamp": "2025-01-27T10:30:45.234Z", "frame": 100, "event": "left_crossing", "track_id": 1, "coordinate": 100}
```

## Examples

### Basic Usage

```bash
car-speed-detection video.mp4 config.yaml
```

### Generate Visualization Image

```bash
car-speed-detection video.mp4 config.yaml --show
```

This creates a composite image file (e.g., `video_speed_result.png`) showing the car at both crossing points side-by-side with vertical boundary lines.

### JSON Output

```bash
car-speed-detection video.mp4 config.yaml --output-format json
```

### Verbose with Log File

```bash
car-speed-detection video.mp4 config.yaml --verbose --log-file processing.log
```

### Custom Confidence Threshold

```bash
car-speed-detection video.mp4 config.yaml --confidence-threshold 0.7
```

### Combined Options

```bash
car-speed-detection video.mp4 config.yaml --show --output-format json --verbose
```

## Configuration File Format

The configuration file must be valid YAML with the following structure:

```yaml
left_coordinate: 100  # pixels, X coordinate of left measurement line
right_coordinate: 500  # pixels, X coordinate of right measurement line
distance: 200         # centimeters, real-world distance between coordinates
fps: 30               # frames per second
```

### Required Fields

- `left_coordinate`: Integer >= 0
- `right_coordinate`: Integer > left_coordinate
- `distance`: Float > 0 (in centimeters)
- `fps`: Float > 0 (frames per second)

## Exit Codes

- `0`: Success - speed calculated and output
- `1`: Error - processing failed (see error message)
- `2`: Usage error - invalid arguments or help requested

## Performance Expectations

- Processing time: Should complete within 60 seconds for 10-minute videos
- Memory usage: Should not exceed reasonable limits (processes frame-by-frame)
- Output: Should be immediate after processing completes

## Versioning

This contract applies to version 1.0.0 of the CLI interface. Future versions will maintain backward compatibility for core functionality while potentially adding new options.

