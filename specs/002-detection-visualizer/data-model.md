# Data Model: Car Detection Process Visualizer

**Feature**: Car Detection Process Visualizer  
**Date**: 2025-01-27

## Entities

### GUI State Entities

#### VideoDisplayState

Represents the current state of video display in the GUI.

**Attributes**:
- `current_frame_number` (int): Current frame being displayed (1-indexed)
- `total_frames` (int): Total number of frames in the video
- `video_width` (int): Video frame width in pixels
- `video_height` (int): Video frame height in pixels
- `current_frame_image` (QPixmap): Current frame as QPixmap for display
- `is_loaded` (bool): Whether a video is currently loaded

**Relationships**:
- Uses: VideoMetadata from Feature 001
- Updated by: Video frame navigation, frame number input

#### CoordinateOverlayState

Represents the state of coordinate overlay rendering.

**Attributes**:
- `left_coordinate` (int): X-coordinate in pixels for left measurement line (scaled if downsize_video used)
- `right_coordinate` (int): X-coordinate in pixels for right measurement line (scaled if downsize_video used)
- `left_coordinate_original` (int): Original left coordinate from config (before scaling)
- `right_coordinate_original` (int): Original right coordinate from config (before scaling)
- `scale_factor` (float): Scale factor applied if downsize_video is used (1.0 if not used)
- `is_visible` (bool): Whether coordinate overlays are visible
- `left_label` (str): Label text for left coordinate (e.g., "Left")
- `right_label` (str): Label text for right coordinate (e.g., "Right")

**Relationships**:
- Uses: Configuration from Feature 001
- Updated by: Configuration loading, video resizing

#### DetectionVisualizationState

Represents the state of detection visualization on the current frame.

**Attributes**:
- `detections` (List[DetectionResult]): List of live detections for current frame (from Feature 001's CarDetector)
- `tracked_cars` (Dict[int, TrackedCar]): Dictionary mapping track_id to TrackedCar, maintained across navigation (from Feature 001's CarTracker)
- `crossing_events` (List[CoordinateCrossingEvent]): List of live crossing events for current frame (from Feature 001's CoordinateCrossingDetector)
- `json_speed_measurements` (List[SpeedMeasurement]): List of speed measurements from JSON input file (expected results)
- `is_detection_running` (bool): Whether detection is currently processing on current frame
- `tracking_state` (CarTracker): Persistent tracking state maintained across forward/backward navigation

**Relationships**:
- Uses: DetectionResult, TrackedCar, CoordinateCrossingEvent, SpeedMeasurement from Feature 001
- Updated by: Live detection processing on frame navigation, JSON file loading

#### FrameNavigationState

Represents the current position and navigation state in video playback.

**Attributes**:
- `current_frame_number` (int): Current frame number (1-indexed)
- `total_frames` (int): Total number of frames
- `can_go_previous` (bool): Whether previous frame navigation is possible
- `can_go_next` (bool): Whether next frame navigation is possible
- `frame_cache` (Dict[int, QPixmap]): Cache of recently viewed frames (key: frame_number, value: frame image)
- `frame_cache_size` (int): Maximum number of frames to cache (e.g., 10)

**Relationships**:
- Uses: VideoMetadata from Feature 001
- Updated by: Frame navigation controls, frame number input

### Feature 001 Data Models (Reused)

The visualizer uses the following data models from Feature 001. See `/specs/001-car-speed-detection/data-model.md` for complete documentation:

- **Configuration** (`src/models/config.py`): Measurement parameters including left_coordinate, right_coordinate, distance, fps, downsize_video
- **VideoMetadata** (`src/models/detection_result.py`): Video file metadata including frame_count, fps, width, height
- **BoundingBox** (`src/models/detection_result.py`): Bounding box coordinates (x1, y1, x2, y2, center_x, center_y)
- **DetectionResult** (`src/models/detection_result.py`): Single car detection with frame_number, bounding_box, confidence, class_id, class_name
- **TrackedCar** (`src/models/detection_result.py`): Car tracked across frames with track_id, detections, left_crossing_frame, right_crossing_frame
- **CoordinateCrossingEvent** (`src/models/detection_result.py`): Crossing event with track_id, frame_number, coordinate_type, coordinate_value
- **SpeedMeasurement** (`src/models/detection_result.py`): Speed calculation result with speed_kmh, track_id, frame_count, left_crossing_frame, right_crossing_frame

## Data Flow

1. **JSON Input Loading**: JSON file (from Feature 001 CLI) → Extract video_path, config_path, speed_measurements
2. **Configuration Loading**: config_path (YAML file) → Feature 001's Configuration entity → CoordinateOverlayState
3. **Video Loading**: video_path (MP4 file) → Feature 001's VideoMetadata + VideoDisplayState
4. **JSON Speed Measurements Loading**: speed_measurements from JSON → DetectionVisualizationState.json_speed_measurements
5. **Frame Navigation**: User input → FrameNavigationState → Video frame extraction → VideoDisplayState update
6. **Live Detection Processing** (On-demand per frame):
   - Current frame → Feature 001's CarDetector → DetectionResult
   - DetectionResult → Feature 001's CarTracker (maintains state) → TrackedCar
   - TrackedCar → Feature 001's CoordinateCrossingDetector → CoordinateCrossingEvent
   - All live results → DetectionVisualizationState
7. **Visualization Rendering**:
   - VideoDisplayState + CoordinateOverlayState + DetectionVisualizationState (live + JSON) → Rendered frame with overlays
   - Visual distinction: Live detection results vs expected results from JSON

## State Management

### VideoDisplayState Lifecycle

```
[No Video Loaded]
  → (user opens video file)
[Video Loaded]
  → (frame navigation)
[Frame Displayed]
  → (user closes video)
[No Video Loaded]
```

### DetectionVisualizationState Lifecycle

```
[No Detection]
  → (user opens JSON file)
[JSON Speed Measurements Loaded]
  → (user navigates to frame)
[Live Detection Running on Current Frame]
  → (detection completes)
[Live Detection Results Available + JSON Expected Results]
  → (user navigates to next/previous frame)
[Tracking State Maintained, New Frame Detection Running]
  → (detection completes)
[Updated Detection Results per Frame]
```

### FrameNavigationState Updates

- `current_frame_number` updated on: next frame, previous frame, frame number input
- `can_go_previous` = `current_frame_number > 1`
- `can_go_next` = `current_frame_number < total_frames`
- `frame_cache` updated: add current frame, remove oldest if cache full

## Validation Rules

### Frame Number Input Validation

- MUST be integer
- MUST be >= 1
- MUST be <= total_frames
- Invalid input: show error, do not update display

### Coordinate Overlay Validation

- Coordinates MUST be within video frame bounds (0 to video_width)
- If coordinates are out of bounds: show warning or error message
- Scale factor MUST be calculated correctly when downsize_video is used

### Detection Visualization Validation

- Bounding boxes MUST be within frame bounds
- Track IDs MUST be consistent across frames (from Feature 001's CarTracker)
- Crossing events MUST match Feature 001's CoordinateCrossingDetector logic

## Error States

### VideoLoadError
- Video file cannot be opened or is corrupted
- Error message: "Failed to load video file: [error details]"
- State: VideoDisplayState.is_loaded = False

### InvalidConfigurationError
- Configuration file missing or invalid
- Error message: "Invalid configuration: [specific issue]" (from Feature 001)
- State: CoordinateOverlayState not initialized

### FrameOutOfBoundsError
- Frame number input is outside valid range
- Error message: "Frame number must be between 1 and [total_frames]"
- State: FrameNavigationState not updated

### DetectionProcessingError
- Detection service fails or encounters error
- Error message: "Detection processing failed: [error details]"
- State: DetectionVisualizationState.is_detection_running = False, error logged

#### DebugInformationState

Represents detailed detection analysis data displayed in the debug panel.

**Attributes**:
- `current_frame_number` (int): Frame number being analyzed
- `detection_results` (List[DetectionResult]): Live YOLO detection results for current frame (from Feature 001's CarDetector)
- `tracked_cars_analysis` (Dict[int, TrackedCarAnalysis]): Dictionary mapping track_id to per-car analysis
- `coordinate_crossing_analysis` (Dict[int, CrossingAnalysis]): Dictionary mapping track_id to crossing detection analysis
- `configuration_values` (Configuration): Current configuration (left_coordinate, right_coordinate) from Feature 001
- `json_expected_results` (List[SpeedMeasurement]): Expected results from JSON speed_measurements for comparison

**Relationships**:
- Uses: DetectionResult, TrackedCar, CoordinateCrossingEvent, SpeedMeasurement, Configuration from Feature 001
- Updated by: Frame navigation, live detection processing

**TrackedCarAnalysis** (nested data structure):
- `track_id` (int): Track ID from Feature 001's TrackedCar
- `bounding_box` (BoundingBox): Current frame bounding box from Feature 001's DetectionResult
- `confidence` (float): Detection confidence from Feature 001's DetectionResult
- `class_name` (str): Detected class name from Feature 001's DetectionResult
- `left_crossing_frame` (Optional[int]): Frame when left was crossed (from Feature 001's TrackedCar)
- `right_crossing_frame` (Optional[int]): Frame when right was crossed (from Feature 001's TrackedCar)
- `car_rightmost_x` (int): Computed rightmost X coordinate (BoundingBox.x2 from Feature 001)

**CrossingAnalysis** (nested data structure):
- `track_id` (int): Track ID of car being analyzed
- `coordinate_type` (str): "left" or "right" coordinate being checked
- `coordinate_value` (int): Coordinate value from Feature 001's Configuration
- `car_rightmost_x` (int): Car's rightmost X position (BoundingBox.x2)
- `comparison_result` (str): Formatted comparison string (e.g., "car_rightmost_x >= coordinate_value" or "car_rightmost_x < coordinate_value")
- `condition_met` (bool): Whether crossing condition was met (car_rightmost_x >= coordinate_value)
- `crossing_state` (str): Explanation of current crossing state (e.g., "left_crossing_frame is None", "left already crossed, waiting for right")
- `crossing_detected` (bool): Whether crossing event was detected this frame (from Feature 001's CoordinateCrossingDetector)

