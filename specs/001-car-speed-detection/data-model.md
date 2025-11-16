# Data Model: Car Speed Detection

**Feature**: Car Speed Detection from Video  
**Date**: 2025-01-27

## Entities

### Configuration

Represents the measurement parameters loaded from the configuration file.

**Attributes**:
- `left_coordinate` (int): X-coordinate in pixels where left measurement line is drawn
- `right_coordinate` (int): X-coordinate in pixels where right measurement line is drawn
- `distance` (float): Real-world distance between left and right coordinates in centimeters
- `fps` (float): Frames per second of the video/camera

**Validation Rules**:
- `left_coordinate` MUST be >= 0
- `right_coordinate` MUST be > `left_coordinate`
- `distance` MUST be > 0
- `fps` MUST be > 0

**Relationships**:
- Used by: SpeedCalculator, CoordinateCrossingDetector
- Loaded from: Configuration file (YAML)

### VideoMetadata

Represents metadata about the video file being processed.

**Attributes**:
- `file_path` (str): Path to the video file
- `frame_count` (int): Total number of frames in video
- `fps` (float): Actual frame rate of video (may differ from config fps)
- `width` (int): Video frame width in pixels
- `height` (int): Video frame height in pixels
- `duration_seconds` (float): Total video duration

**Relationships**:
- Extracted from: Video file via OpenCV
- Used by: VideoProcessor, SpeedCalculator

### DetectionResult

Represents a single car detection in a video frame.

**Attributes**:
- `frame_number` (int): Frame index where detection occurred
- `bounding_box` (BoundingBox): Coordinates of detected car
- `confidence` (float): Detection confidence score (0.0 to 1.0)
- `class_id` (int): YOLO class ID (should be "car" class)
- `class_name` (str): Detected class name (e.g., "car")

**Relationships**:
- Created by: CarDetector
- Used by: CarTracker, CoordinateCrossingDetector

### BoundingBox

Represents the bounding box coordinates of a detected object.

**Attributes**:
- `x1` (int): Left X coordinate
- `y1` (int): Top Y coordinate
- `x2` (int): Right X coordinate
- `y2` (int): Bottom Y coordinate
- `width` (int): Computed width (x2 - x1)
- `height` (int): Computed height (y2 - y1)
- `center_x` (int): Computed center X coordinate
- `center_y` (int): Computed center Y coordinate

**Methods**:
- `intersects_x(x: int) -> bool`: Check if bounding box intersects with vertical line at x
- `center_x_coordinate() -> int`: Get center X coordinate for crossing detection

### TrackedCar

Represents a car being tracked across multiple frames.

**Attributes**:
- `track_id` (int): Unique identifier for this tracked car
- `detections` (List[DetectionResult]): List of detections for this car, ordered by frame
- `first_detection_frame` (int): Frame number of first detection
- `last_detection_frame` (int): Frame number of most recent detection
- `left_crossing_frame` (Optional[int]): Frame when car crossed left coordinate (None if not crossed)
- `right_crossing_frame` (Optional[int]): Frame when car crossed right coordinate (None if not crossed)

**State Transitions**:
1. **Initial**: `left_crossing_frame = None`, `right_crossing_frame = None`
2. **Left Crossed**: `left_crossing_frame` set to frame number
3. **Right Crossed**: `right_crossing_frame` set to frame number
4. **Complete**: Both coordinates crossed, ready for speed calculation

**Relationships**:
- Created by: CarTracker
- Used by: CoordinateCrossingDetector, SpeedCalculator

### CoordinateCrossingEvent

Represents an event when a car crosses a measurement coordinate.

**Attributes**:
- `track_id` (int): ID of the tracked car that crossed
- `frame_number` (int): Frame when crossing occurred
- `coordinate_type` (str): "left" or "right"
- `coordinate_value` (int): X-coordinate value that was crossed
- `car_center_x` (int): X-coordinate of car center when crossing occurred
- `confidence` (float): Detection confidence at crossing frame

**Relationships**:
- Created by: CoordinateCrossingDetector
- Used by: SpeedCalculator

### SpeedMeasurement

Represents the final calculated speed result.

**Attributes**:
- `speed_kmh` (float): Calculated speed in kilometers per hour
- `speed_ms` (float): Calculated speed in meters per second (for internal use)
- `frame_count` (int): Number of frames between left and right crossings
- `time_seconds` (float): Time duration in seconds (frame_count / fps)
- `distance_meters` (float): Distance in meters (converted from config distance in cm)
- `left_crossing_frame` (int): Frame when left coordinate was crossed
- `right_crossing_frame` (int): Frame when right coordinate was crossed
- `track_id` (int): ID of the tracked car measured
- `confidence` (float): Average confidence across detection frames
- `is_valid` (bool): Whether measurement is valid (both coordinates crossed)

**Validation Rules**:
- `is_valid` MUST be True for measurement to be reported
- `frame_count` MUST be > 0
- `time_seconds` MUST be > 0
- `speed_kmh` MUST be >= 0

**Relationships**:
- Created by: SpeedCalculator
- Output by: CLI interface

### ProcessingResult

Represents the overall result of processing a video file.

**Attributes**:
- `video_path` (str): Path to processed video file
- `config_path` (str): Path to configuration file used
- `video_metadata` (VideoMetadata): Metadata about the video
- `config` (Configuration): Configuration used for processing
- `speed_measurement` (Optional[SpeedMeasurement]): Calculated speed (None if no valid measurement)
- `processing_time_seconds` (float): Total time taken to process video
- `frames_processed` (int): Total number of frames processed
- `detections_count` (int): Total number of car detections made
- `error_message` (Optional[str]): Error message if processing failed (None if successful)
- `logs` (List[Dict]): Structured log entries from processing

**Relationships**:
- Created by: Main processing pipeline
- Output by: CLI interface

## Data Flow

1. **Configuration Loading**: YAML file → Configuration entity
2. **Video Loading**: MP4 file → VideoMetadata + frame stream
3. **Frame Processing**: Frame → DetectionResult (via CarDetector)
4. **Tracking**: DetectionResult → TrackedCar (via CarTracker)
5. **Crossing Detection**: TrackedCar + Configuration → CoordinateCrossingEvent (via CoordinateCrossingDetector)
6. **Speed Calculation**: CoordinateCrossingEvent(s) + Configuration → SpeedMeasurement (via SpeedCalculator)
7. **Result Assembly**: All entities → ProcessingResult → CLI output

## State Management

### TrackedCar State Machine

```
[Initial] 
  → (car detected) 
[Tracking] 
  → (crosses left coordinate) 
[Left Crossed] 
  → (crosses right coordinate) 
[Complete] 
  → (speed calculated)
[Measured]
```

### Processing Pipeline State

```
[Idle]
  → (video + config loaded)
[Initialized]
  → (processing frames)
[Processing]
  → (car detected and tracked)
[Tracking]
  → (both coordinates crossed)
[Complete]
  → (speed calculated)
[Finished]
```

## Validation Rules Summary

### Configuration Validation
- All required fields present
- Numeric values within valid ranges
- right_coordinate > left_coordinate

### Detection Validation
- Confidence >= threshold (configurable, default 0.5)
- Class is "car"
- Bounding box within frame bounds

### Speed Calculation Validation
- Both coordinates crossed
- Frame count > 0
- Time > 0
- Resulting speed >= 0

## Error States

### NoCarDetected
- No car detected in entire video
- Error message: "No car detected in video"

### CarNotCrossingBothCoordinates
- Car detected but doesn't cross both left and right coordinates
- Error message: "Car detected but did not cross both measurement coordinates"

### InvalidConfiguration
- Missing required fields or invalid values
- Error message: "Invalid configuration: [specific issue]"

### VideoLoadError
- Video file cannot be opened or is corrupted
- Error message: "Failed to load video file: [error details]"

