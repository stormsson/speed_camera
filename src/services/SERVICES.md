# Services Documentation

This document provides detailed documentation for all service classes in the `src/services` module. These services form the core processing pipeline for car speed detection from video.

## Table of Contents

1. [CarDetector](#cardetector)
2. [CarTracker](#cartracker)
3. [CoordinateCrossingDetector](#coordinatecrossingdetector)
4. [SpeedCalculator](#speedcalculator)
5. [VideoProcessor](#videoprocessor)
6. [ImageGenerator](#imagegenerator)
7. [DebugImageGenerator](#debugimagegenerator)
8. [Support Classes](#support-classes)
9. [Current Pipeline](#current-pipeline)

---

## CarDetector

**File:** `car_detector.py`

**Purpose:** Detects cars in video frames using YOLO object detection model.

### Overview

The `CarDetector` class uses the Ultralytics YOLO model to detect cars in individual video frames. It filters detections by confidence threshold and class ID (only cars from the COCO dataset).

### Key Features

- Uses YOLOv8 model (default: `yolov8n.pt`)
- Filters detections by confidence threshold
- Only returns detections for the "car" class (COCO class ID 2)
- Logs all detections with structured logging

### Class Attributes

- `CAR_CLASS_ID` (int): COCO dataset class ID for cars (value: 2)

### Methods

#### `__init__(confidence_threshold: float = 0.7, model_name: str = "yolov8s.pt")`

Initializes the car detector with a YOLO model.

**Parameters:**
- `confidence_threshold` (float): Minimum confidence score (0.0 to 1.0) for accepting detections
- `model_name` (str): YOLO model file name (default: `yolov8s.pt`)

**Behavior:**
- Loads the YOLO model from the specified model file
- Sets the confidence threshold for filtering detections

#### `detect(frame: np.ndarray, frame_number: int) -> List[DetectionResult]`

Detects cars in a single video frame.

**Parameters:**
- `frame` (np.ndarray): Video frame as a numpy array (BGR format)
- `frame_number` (int): Current frame number for tracking

**Returns:**
- `List[[DetectionResult](#detectionresult)]`: List of detection results. See [DetectionResult](#detectionresult) for structure details.

**Behavior:**
1. Runs YOLO inference on the frame
2. Filters detections by confidence threshold
3. Filters detections by class ID (only cars)
4. Creates `DetectionResult` objects with bounding boxes
5. Logs each detection with structured logging

**Logging:**
- Logs INFO level messages for each detected car with:
  - Frame number
  - Confidence score
  - Bounding box coordinates
  - Event type: "detection"

**See Also:**
- [DetectionResult](#detectionresult) - Structure of detection results
- [BoundingBox](#boundingbox) - Bounding box coordinate structure

---

## CarTracker

**File:** `car_tracker.py`

**Purpose:** Tracks cars across multiple video frames using IoU (Intersection over Union) matching.

### Overview

The `CarTracker` class maintains tracks of cars across frames by matching new detections to existing tracks based on bounding box overlap. It uses a simple IoU-based matching algorithm to associate detections with tracks.

### Key Features

- IoU-based matching algorithm
- Automatic track ID assignment
- Maintains detection history for each tracked car
- Handles new tracks for unmatched detections

### Helper Function

#### `calculate_iou(box1: DetectionResult, box2: DetectionResult) -> float`

Calculates the Intersection over Union (IoU) between two detection bounding boxes.

**Parameters:**
- `box1` ([DetectionResult](#detectionresult)): First detection
- `box2` ([DetectionResult](#detectionresult)): Second detection

**Returns:**
- `float`: IoU value between 0.0 and 1.0 (1.0 = perfect overlap, 0.0 = no overlap)

**Algorithm:**
1. Calculates intersection area of the two bounding boxes
2. Calculates union area (area1 + area2 - intersection)
3. Returns intersection / union

### Methods

#### `__init__(iou_threshold: float = 0.3)`

Initializes the car tracker.

**Parameters:**
- `iou_threshold` (float): Minimum IoU value required to match a detection to an existing track (default: 0.3)

**Behavior:**
- Initializes empty dictionary for tracked cars
- Sets initial track ID counter to 1

#### `update(detections: List[DetectionResult], frame_number: int) -> List[TrackedCar]`

Updates tracks with new detections from the current frame.

**Parameters:**
- `detections` (List[[DetectionResult](#detectionresult)]): List of detections in the current frame
- `frame_number` (int): Current frame number

**Returns:**
- `List[[TrackedCar](#trackedcar)]`: List of all currently tracked cars

**Algorithm:**
1. If no detections, returns existing tracks
2. For each detection:
   - Calculates IoU with the last detection of each existing track
   - Matches to the track with highest IoU above threshold
   - Prevents double-matching (each track/detection matched only once)
3. Creates new tracks for unmatched detections
4. Returns all tracked cars

**Behavior:**
- Maintains detection history for each track
- Automatically assigns new track IDs for new cars
- Handles cases where cars disappear (tracks remain but aren't updated)

#### `get_tracked_car(track_id: int) -> TrackedCar`

Retrieves a tracked car by its track ID.

**Parameters:**
- `track_id` (int): Track ID

**Returns:**
- `[TrackedCar](#trackedcar)`: The tracked car object

---

## CoordinateCrossingDetector

**File:** `coordinate_crossing_detector.py`

**Purpose:** Detects when tracked cars cross measurement coordinates (left and right boundaries).

### Overview

The `CoordinateCrossingDetector` monitors tracked cars and detects when they cross predefined coordinate lines. It uses a transition-based detection algorithm that identifies crossings when a car's rightmost edge transitions from being less than a coordinate to being greater than or equal to it.

### Key Features

- Transition-based crossing detection (prevents duplicate detections)
- Detects left coordinate crossing first, then right
- Only detects right crossing after left has been crossed
- Optional debug image generation for crossing events
- Comprehensive logging of crossing events and skipped detections

### Methods

#### `__init__(config: Configuration)`

Initializes the coordinate crossing detector.

**Parameters:**
- `config` (Configuration): Configuration object containing:
  - `left_coordinate` (int): X coordinate of the left measurement line
  - `right_coordinate` (int): X coordinate of the right measurement line

**Behavior:**
- Extracts left and right coordinates from configuration
- Stores coordinates for crossing detection

#### `detect_crossings(tracked_car: TrackedCar, frame_number: int, debug: bool = False, video_processor: Optional[VideoProcessor] = None, debug_image_generator: Optional[DebugImageGenerator] = None) -> List[CoordinateCrossingEvent]`

Detects coordinate crossings for a tracked car.

**Parameters:**
- `tracked_car` ([TrackedCar](#trackedcar)): The tracked car to check for crossings
- `frame_number` (int): Current frame number
- `debug` (bool): If True, generate debug images for crossing events
- `video_processor` (Optional[VideoProcessor]): Required if debug=True, for extracting frames
- `debug_image_generator` (Optional[DebugImageGenerator]): Required if debug=True, for generating debug images

**Returns:**
- `List[[CoordinateCrossingEvent](#coordinatecrossingevent)]`: List of crossing events detected in this frame (typically 0 or 1)

**Detection Algorithm:**

1. **Left Coordinate Crossing:**
   - Only checked if `tracked_car.left_crossing_frame` is None
   - Requires transition: `previous_rightmost_x < left_coordinate AND current_rightmost_x >= left_coordinate`
   - Sets `tracked_car.left_crossing_frame` when detected
   - Creates [CoordinateCrossingEvent](#coordinatecrossingevent) for left crossing

2. **Right Coordinate Crossing:**
   - Only checked if left coordinate has been crossed AND right hasn't
   - Requires transition: `previous_rightmost_x < right_coordinate AND current_rightmost_x >= right_coordinate`
   - Sets `tracked_car.right_crossing_frame` when detected
   - Creates [CoordinateCrossingEvent](#coordinatecrossingevent) for right crossing

**Edge Cases Handled:**
- First detection: If car is already past coordinate on first detection, no transition can be detected (logged as debug)
- No previous frame: Skips transition detection if only one detection exists

**Logging:**
- **INFO level:** When crossing is detected, logs:
  - Frame number, track ID, coordinate type
  - Coordinate value, car rightmost X position
  - Previous rightmost X position
  - Confidence score
  - Event type ("left_crossing" or "right_crossing")
  - Transition detected flag

- **DEBUG level:** When crossing is skipped, logs:
  - Why crossing was skipped
  - Current and previous positions
  - Transition condition that wasn't met

**Debug Image Generation:**
- If `debug=True` and required components are provided:
  - Extracts frame from video processor
  - Generates debug image showing:
    - Car bounding box
    - Coordinate lines
    - Detection criteria text
  - Saves to `output/crossing_{frame_number}.png`

---

## SpeedCalculator

**File:** `speed_calculator.py`

**Purpose:** Calculates car speed from coordinate crossing events.

### Overview

The `SpeedCalculator` computes vehicle speed based on the time and distance between crossing two coordinate lines. It converts the distance (in centimeters) and frame-based time into speed in both m/s and km/h.

### Key Features

- Calculates speed from frame differences
- Converts distance from cm to meters
- Provides speed in both m/s and km/h
- Validates input parameters
- Calculates average confidence from all detections

### Methods

#### `__init__(config: Configuration)`

Initializes the speed calculator.

**Parameters:**
- `config` (Configuration): Configuration object containing:
  - `distance` (int): Distance between coordinates in centimeters
  - `fps` (float): Video frames per second

**Behavior:**
- Converts distance from cm to meters (divides by 100)
- Stores FPS for time calculations

#### `calculate(left_crossing_frame: int, right_crossing_frame: int, track_id: int, confidence: float) -> SpeedMeasurement`

Calculates speed from crossing frame numbers.

**Parameters:**
- `left_crossing_frame` (int): Frame number when left coordinate was crossed
- `right_crossing_frame` (int): Frame number when right coordinate was crossed
- `track_id` (int): ID of the tracked car
- `confidence` (float): Average confidence score across detections

**Returns:**
- `[SpeedMeasurement](#speedmeasurement)`: See [SpeedMeasurement](#speedmeasurement) for complete structure.

**Calculation:**
1. `frame_count = right_crossing_frame - left_crossing_frame`
2. `time_seconds = frame_count / fps`
3. `speed_ms = distance_meters / time_seconds`
4. `speed_kmh = speed_ms * 3.6`

**Raises:**
- `ValueError`: If `frame_count <= 0` or `time_seconds <= 0`

**Logging:**
- Logs INFO level message with all calculation parameters and results

#### `calculate_from_tracked_car(tracked_car: TrackedCar) -> SpeedMeasurement`

Calculates speed from a tracked car that has completed crossing both coordinates.

**Parameters:**
- `tracked_car` ([TrackedCar](#trackedcar)): Tracked car with both coordinates crossed

**Returns:**
- `[SpeedMeasurement](#speedmeasurement)`: Speed measurement object

**Behavior:**
1. Validates that car has crossed both coordinates
2. Validates that right crossing frame > left crossing frame
3. Calculates average confidence from all detections
4. Calls `calculate()` with extracted parameters

**Raises:**
- `ValueError`: If car hasn't crossed both coordinates or frames are invalid

---

## VideoProcessor

**File:** `video_processor.py`

**Purpose:** Handles video file loading, frame extraction, and optional video resizing.

### Overview

The `VideoProcessor` class provides an interface for working with video files using OpenCV. It supports frame-by-frame iteration, random frame access, and optional video resizing for performance optimization.

### Key Features

- Loads video files using OpenCV
- Extracts individual frames by frame number
- Iterates through all frames
- Optional video resizing (maintains aspect ratio)
- Automatic coordinate scaling when video is resized
- Context manager support (can be used with `with` statement)
- Caches metadata and scale factors

### Methods

#### `__init__(video_path: str, config: Optional[Configuration] = None)`

Initializes the video processor.

**Parameters:**
- `video_path` (str): Path to the video file
- `config` (Optional[Configuration]): Optional configuration for video resizing

**Behavior:**
- Opens video file using `cv2.VideoCapture`
- Raises `VideoLoadError` if video cannot be opened
- Initializes caches for metadata and scale factors

**Raises:**
- `VideoLoadError`: If video file cannot be opened

#### `get_metadata() -> VideoMetadata`

Extracts and returns video metadata.

**Returns:**
- `[VideoMetadata](#videometadata)`: See [VideoMetadata](#videometadata) for complete structure.

**Behavior:**
- Caches metadata on first call
- If `config.downsize_video` is set:
  - Calculates scale factor based on target width
  - Calculates new height maintaining aspect ratio
  - Scales coordinates proportionally
- Returns cached metadata on subsequent calls

#### `get_scaled_coordinates() -> Optional[Tuple[int, int]]`

Gets scaled coordinates if video was resized.

**Returns:**
- `Optional[Tuple[int, int]]`: Tuple of `(scaled_left_coordinate, scaled_right_coordinate)` or `None` if not resized

**Behavior:**
- Ensures metadata is calculated first
- Returns `None` if video wasn't resized
- Returns scaled coordinates if resizing was applied

#### `get_frame(frame_number: int) -> Optional[np.ndarray]`

Gets a specific frame by frame number.

**Parameters:**
- `frame_number` (int): Frame index to retrieve (0-based)

**Returns:**
- `Optional[np.ndarray]`: Frame as numpy array (BGR format), or `None` if frame cannot be read

**Behavior:**
- Seeks to specified frame number
- Reads frame from video
- If `config.downsize_video` is set, resizes frame maintaining aspect ratio
- Returns `None` if frame cannot be read

#### `iter_frames() -> Iterator[Tuple[int, np.ndarray]]`

Iterates through all frames in the video.

**Yields:**
- `Tuple[int, np.ndarray]`: Tuple of `(frame_number, frame_array)` where frame is resized if `downsize_video` is set

**Behavior:**
- Resets video to beginning
- Yields each frame sequentially
- Automatically resizes frames if `downsize_video` is configured
- Stops when end of video is reached

#### `close() -> None`

Releases video capture resources.

**Behavior:**
- Releases the OpenCV `VideoCapture` object
- Should be called when done processing to free resources

#### Context Manager Support

The class supports Python's context manager protocol:

```python
with VideoProcessor(video_path, config) as processor:
    # Process video
    pass
# Automatically closes when exiting context
```

---

## ImageGenerator

**File:** `image_generator.py`

**Purpose:** Generates composite visualization images showing car crossings with annotations.

### Overview

The `ImageGenerator` class creates annotated composite images that visualize car crossings at measurement coordinates. It can generate single-car or multi-car composite images with bounding boxes, coordinate lines, and labels.

### Key Features

- Extracts frames at crossing points
- Draws bounding boxes, coordinate lines, and text labels
- Creates side-by-side composite images
- Supports single-car and multi-car visualizations
- Handles video resizing (uses scaled coordinates automatically)

### Methods

#### `__init__(config: Configuration)`

Initializes the image generator.

**Parameters:**
- `config` (Configuration): Configuration with left and right coordinates

**Behavior:**
- Stores configuration and coordinate values

#### `extract_crossing_frames(video_processor: VideoProcessor, tracked_car: TrackedCar) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]`

Extracts frames at left and right crossing points.

**Parameters:**
- `video_processor` (VideoProcessor): Video processor instance
- `tracked_car` ([TrackedCar](#trackedcar)): Tracked car with crossing frame numbers

**Returns:**
- `Tuple[Optional[np.ndarray], Optional[np.ndarray]]`: Tuple of `(left_frame, right_frame)` or `(None, None)` if frames cannot be extracted

#### `draw_vertical_bar(frame: np.ndarray, x_coordinate: int, color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray`

Draws a vertical line at the specified x coordinate.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `x_coordinate` (int): X coordinate for the vertical line
- `color` (Tuple[int, int, int]): RGB color tuple (default: green)
- `thickness` (int): Line thickness

**Returns:**
- `np.ndarray`: Annotated frame (copy of original)

#### `draw_bounding_box(frame: np.ndarray, bbox, color: Tuple[int, int, int] = (255, 0, 0), thickness: int = 2) -> np.ndarray`

Draws a bounding box on the frame.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `bbox` ([BoundingBox](#boundingbox)): BoundingBox object
- `color` (Tuple[int, int, int]): RGB color tuple (default: red)
- `thickness` (int): Line thickness

**Returns:**
- `np.ndarray`: Annotated frame (copy of original)

#### `add_label(frame: np.ndarray, text: str, position: Tuple[int, int], color: Tuple[int, int, int] = (255, 255, 255), font_scale: float = 0.7, thickness: int = 2) -> np.ndarray`

Adds text label to frame.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `text` (str): Label text
- `position` (Tuple[int, int]): (x, y) position for text
- `color` (Tuple[int, int, int]): RGB color tuple (default: white)
- `font_scale` (float): Font scale
- `thickness` (int): Text thickness

**Returns:**
- `np.ndarray`: Annotated frame (copy of original)

#### `create_composite_image(left_frame: np.ndarray, right_frame: np.ndarray) -> np.ndarray`

Creates a side-by-side composite image from two frames.

**Parameters:**
- `left_frame` (np.ndarray): Left frame
- `right_frame` (np.ndarray): Right frame

**Returns:**
- `np.ndarray`: Composite image with frames side-by-side

**Behavior:**
- Resizes frames to match height if different
- Concatenates frames horizontally

#### `annotate_frame(frame: np.ndarray, coordinate: int, bbox, label: str, coordinate_color: Tuple[int, int, int] = (0, 255, 0), bbox_color: Tuple[int, int, int] = (255, 0, 0)) -> np.ndarray`

Annotates a frame with vertical bar, bounding box, and label.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `coordinate` (int): X coordinate for vertical bar
- `bbox` ([BoundingBox](#boundingbox)): BoundingBox object for car
- `label` (str): Text label
- `coordinate_color` (Tuple[int, int, int]): Color for vertical bar
- `bbox_color` (Tuple[int, int, int]): Color for bounding box

**Returns:**
- `np.ndarray`: Fully annotated frame

#### `annotate_frame_with_both_bars(frame: np.ndarray, bbox, label: str, left_color: Tuple[int, int, int] = (0, 255, 0), right_color: Tuple[int, int, int] = (0, 255, 0), bbox_color: Tuple[int, int, int] = (255, 0, 0), left_coord: Optional[int] = None, right_coord: Optional[int] = None) -> np.ndarray`

Annotates a frame with both left and right coordinate vertical bars, bounding box, and label.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `bbox` ([BoundingBox](#boundingbox)): BoundingBox object for car
- `label` (str): Text label
- `left_color` (Tuple[int, int, int]): Color for left coordinate bar
- `right_color` (Tuple[int, int, int]): Color for right coordinate bar
- `bbox_color` (Tuple[int, int, int]): Color for bounding box
- `left_coord` (Optional[int]): Optional left coordinate (uses config if not provided)
- `right_coord` (Optional[int]): Optional right coordinate (uses config if not provided)

**Returns:**
- `np.ndarray`: Fully annotated frame with both coordinate bars

#### `generate_composite_image(video_processor: VideoProcessor, tracked_car: TrackedCar, output_path: str) -> str`

Generates and saves composite image showing car crossings for a single car.

**Parameters:**
- `video_processor` (VideoProcessor): Video processor instance
- `tracked_car` ([TrackedCar](#trackedcar)): Tracked car with crossing information
- `output_path` (str): Path to save the output image

**Returns:**
- `str`: Path to saved image file

**Behavior:**
1. Validates that car has crossed both coordinates
2. Gets scaled coordinates if video was resized
3. Extracts frames at crossing points
4. Finds detections at crossing frames
5. Annotates both frames with coordinate bars and bounding boxes
6. Creates side-by-side composite
7. Saves to file

**Raises:**
- `ValueError`: If tracked car doesn't have both crossing frames or frames cannot be extracted
- `IOError`: If image cannot be saved

#### `generate_multi_car_composite_image(video_processor: VideoProcessor, tracked_cars: list, output_path: str) -> str`

Generates and saves composite image showing multiple cars vertically stacked.

**Parameters:**
- `video_processor` (VideoProcessor): Video processor instance
- `tracked_cars` (list): List of [TrackedCar](#trackedcar) objects that completed crossing
- `output_path` (str): Path to save the output image

**Returns:**
- `str`: Path to saved image file

**Behavior:**
1. Validates that at least one tracked car is provided
2. Gets scaled coordinates if video was resized
3. For each car:
   - Extracts crossing frames
   - Annotates frames with coordinate bars and bounding boxes
   - Creates side-by-side composite for that car
4. Stacks all car composites vertically
5. Ensures all images have same width before stacking
6. Saves final composite to file

**Raises:**
- `ValueError`: If no tracked cars provided or no valid images could be generated
- `IOError`: If image cannot be saved

---

## DebugImageGenerator

**File:** `debug_image_generator.py`

**Purpose:** Generates debug images for coordinate crossing events with detailed annotations.

### Overview

The `DebugImageGenerator` creates annotated debug images that show crossing events with bounding boxes, coordinate lines, and detection criteria text. These images are useful for debugging and understanding why crossings were detected.

### Key Features

- Generates debug images for each crossing event
- Shows bounding boxes, coordinate lines, and criteria text
- Saves images to `output/` directory
- Automatically creates output directory if it doesn't exist
- Comprehensive error handling and logging

### Methods

#### `__init__(config: Configuration)`

Initializes the debug image generator.

**Parameters:**
- `config` (Configuration): Configuration with left and right coordinates

**Behavior:**
- Stores configuration and coordinate values

#### `generate_debug_image(frame: np.ndarray, detection: DetectionResult, event: CoordinateCrossingEvent, frame_number: int) -> Optional[str]`

Generates debug image for a crossing event.

**Parameters:**
- `frame` (np.ndarray): Video frame as numpy array (BGR format)
- `detection` ([DetectionResult](#detectionresult)): Detection result for the crossing
- `event` ([CoordinateCrossingEvent](#coordinatecrossingevent)): Crossing event information
- `frame_number` (int): Frame number for file naming

**Returns:**
- `Optional[str]`: Path to saved PNG file, or `None` if saving failed

**Behavior:**
1. Creates a copy of the frame
2. Draws bounding box in green
3. Draws both coordinate lines in red
4. Formats and draws criteria text in black
5. Creates output directory if it doesn't exist
6. Saves image as `output/crossing_{frame_number}.png`
7. Logs success or failure

**Image Annotations:**
- **Bounding box:** Green rectangle around detected car
- **Coordinate lines:** Red vertical lines at left and right coordinates
- **Criteria text:** Black text showing:
  - Frame number and track ID
  - Bounding box rightmost X coordinate
  - Coordinate line value

**Logging:**
- **INFO level:** When image is saved successfully, logs:
  - File path
  - Frame number
  - Coordinate type
  - Track ID

- **ERROR level:** When image saving fails, logs:
  - File path
  - Frame number
  - Error details

#### Helper Methods

##### `_format_criteria_text(event: CoordinateCrossingEvent, detection: DetectionResult) -> str`

**Parameters:**
- `event` ([CoordinateCrossingEvent](#coordinatecrossingevent)): Crossing event
- `detection` ([DetectionResult](#detectionresult)): Detection result

Formats the detection criteria text string displayed on debug images.

**Returns:**
- Multi-line string with frame number, track ID, bounding box X, and coordinate value

##### `_draw_bounding_box(img: np.ndarray, detection: DetectionResult, color: tuple = (0, 255, 0), thickness: int = 2) -> None`

**Parameters:**
- `detection` ([DetectionResult](#detectionresult)): Detection result with bounding box

Draws bounding box on image (modifies image in place).

##### `_draw_coordinate_lines(img: np.ndarray, color: tuple = (255, 0, 0), thickness: int = 2) -> None`

Draws vertical lines for both left and right coordinates (modifies image in place).

##### `_draw_text(img: np.ndarray, text: str, position: tuple = (10, 30), font_scale: float = 0.6, color: tuple = (255, 255, 255), thickness: int = 1) -> None`

Draws text on image, supporting multi-line text (modifies image in place).

---

## Support Classes

This section documents the data model classes used throughout the services. These classes represent the core data structures that flow through the processing pipeline.

### BoundingBox

**File:** `src/models/detection_result.py`

**Purpose:** Represents the bounding box coordinates of a detected object.

**Fields:**
- `x1` (int): Left X coordinate
- `y1` (int): Top Y coordinate
- `x2` (int): Right X coordinate
- `y2` (int): Bottom Y coordinate

**Properties:**
- `width` (int): Computed width of bounding box (`x2 - x1`)
- `height` (int): Computed height of bounding box (`y2 - y1`)
- `center_x` (int): Computed center X coordinate (`(x1 + x2) // 2`)
- `center_y` (int): Computed center Y coordinate (`(y1 + y2) // 2`)

**Methods:**
- `intersects_x(x: int) -> bool`: Checks if bounding box intersects with a vertical line at x coordinate
- `center_x_coordinate() -> int`: Returns center X coordinate (alias for `center_x`)

**Usage:**
Used by `DetectionResult` to represent the spatial location of detected cars. The rightmost edge (`x2`) is used by `CoordinateCrossingDetector` to determine when cars cross measurement coordinates.

---

### DetectionResult

**File:** `src/models/detection_result.py`

**Purpose:** Represents a single car detection in a video frame.

**Fields:**
- `frame_number` (int): Frame index where detection occurred (1-based)
- `bounding_box` ([BoundingBox](#boundingbox)): Coordinates of detected car
- `confidence` (float): Detection confidence score (0.0 to 1.0)
- `class_id` (int): YOLO class ID (2 for "car" in COCO dataset)
- `class_name` (str): Detected class name (e.g., "car")

**Usage:**
- Created by `CarDetector.detect()` for each detected car
- Collected into lists by `CarTracker` to maintain detection history
- Used by `CoordinateCrossingDetector` to determine crossing events
- Referenced by `DebugImageGenerator` for visualization

**Lifecycle:**
1. Created when `CarDetector` detects a car in a frame
2. Added to `TrackedCar.detections` list by `CarTracker`
3. Referenced during crossing detection to get car position
4. Used in speed calculation to compute average confidence

---

### TrackedCar

**File:** `src/models/detection_result.py`

**Purpose:** Represents a car being tracked across multiple frames.

**Fields:**
- `track_id` (int): Unique identifier for this tracked car
- `detections` (List[[DetectionResult](#detectionresult)]): List of detections for this car, ordered by frame number
- `first_detection_frame` (Optional[int]): Frame number of first detection
- `last_detection_frame` (Optional[int]): Frame number of most recent detection
- `left_crossing_frame` (Optional[int]): Frame when car crossed left coordinate (None if not crossed)
- `right_crossing_frame` (Optional[int]): Frame when car crossed right coordinate (None if not crossed)

**Methods:**
- `add_detection(detection: DetectionResult) -> None`: Adds a detection to this tracked car and updates frame tracking
- `is_complete() -> bool`: Returns True if car has crossed both coordinates

**Usage:**
- Created by `CarTracker` when a new car is detected
- Updated by `CarTracker.update()` with new detections
- Modified by `CoordinateCrossingDetector` when crossings are detected
- Used by `SpeedCalculator` to calculate speed
- Passed to `ImageGenerator` for visualization

**State Management:**
- `left_crossing_frame` and `right_crossing_frame` are set by `CoordinateCrossingDetector` when transitions are detected
- Once set, these values are never changed (prevents duplicate crossing detection)
- `is_complete()` returns True only when both coordinates have been crossed

---

### CoordinateCrossingEvent

**File:** `src/models/detection_result.py`

**Purpose:** Represents an event when a car crosses a measurement coordinate.

**Fields:**
- `track_id` (int): ID of the tracked car that crossed
- `frame_number` (int): Frame when crossing occurred
- `coordinate_type` (str): "left" or "right"
- `coordinate_value` (int): X-coordinate value that was crossed
- `car_rightmost_x` (int): X-coordinate of car rightmost edge when crossing occurred
- `confidence` (float): Detection confidence at crossing frame

**Usage:**
- Created by `CoordinateCrossingDetector.detect_crossings()` when a crossing is detected
- Returned as a list (typically 0 or 1 events per call)
- Used by `DebugImageGenerator` to annotate debug images
- Contains all information needed to understand why a crossing was detected

**Note:**
This is an event object, not a state object. The actual crossing state is stored in `TrackedCar.left_crossing_frame` and `TrackedCar.right_crossing_frame`.

---

### SpeedMeasurement

**File:** `src/models/detection_result.py`

**Purpose:** Represents the final calculated speed result.

**Fields:**
- `speed_kmh` (float): Calculated speed in kilometers per hour
- `speed_ms` (float): Calculated speed in meters per second (for internal use)
- `frame_count` (int): Number of frames between left and right crossings
- `time_seconds` (float): Time duration in seconds (`frame_count / fps`)
- `distance_meters` (float): Distance in meters (converted from config distance in cm)
- `left_crossing_frame` (int): Frame when left coordinate was crossed
- `right_crossing_frame` (int): Frame when right coordinate was crossed
- `track_id` (int): ID of the tracked car measured
- `confidence` (float): Average confidence across all detection frames
- `is_valid` (bool): Whether measurement is valid (both coordinates crossed)

**Validation:**
The `__post_init__` method validates that:
- `frame_count > 0` for valid measurements
- `time_seconds > 0` for valid measurements
- `speed_kmh >= 0`

**Usage:**
- Created by `SpeedCalculator.calculate()` or `SpeedCalculator.calculate_from_tracked_car()`
- Collected into `ProcessingResult.speed_measurements` list
- Used for output formatting (text, JSON, CSV)
- Contains all information needed to report speed measurement results

---

### VideoMetadata

**File:** `src/models/detection_result.py`

**Purpose:** Represents metadata about the video file being processed.

**Fields:**
- `file_path` (str): Path to the video file
- `frame_count` (int): Total number of frames in video
- `fps` (float): Actual frame rate of video (may differ from config fps)
- `width` (int): Video frame width in pixels (resized if `downsize_video` is set)
- `height` (int): Video frame height in pixels (resized if `downsize_video` is set)
- `duration_seconds` (float): Total video duration

**Usage:**
- Created by `VideoProcessor.get_metadata()`
- Included in `ProcessingResult` for reporting
- Used to understand video characteristics and processing context
- Width/height reflect resized dimensions if video was downscaled

**Note:**
If video resizing is enabled, `width` and `height` reflect the resized dimensions, not the original video dimensions.

---

### ProcessingResult

**File:** `src/models/detection_result.py`

**Purpose:** Represents the overall result of processing a video file.

**Fields:**
- `video_path` (str): Path to processed video file
- `config_path` (str): Path to configuration file used
- `video_metadata` ([VideoMetadata](#videometadata)): Metadata about the video
- `processing_time_seconds` (float): Total time taken to process video
- `frames_processed` (int): Total number of frames processed
- `detections_count` (int): Total number of car detections made
- `speed_measurements` (List[[SpeedMeasurement](#speedmeasurement)]): List of calculated speeds
- `error_message` (Optional[str]): Error message if processing failed (None if successful)
- `logs` (List[dict]): Structured log entries from processing
- `config` (Optional[Configuration]): Configuration used for processing

**Properties:**
- `speed_measurement` (Optional[[SpeedMeasurement](#speedmeasurement)]): Backward compatibility property that returns the first measurement if available

**Usage:**
- Created by `process_video()` function in `src/cli/main.py`
- Used for output formatting (text, JSON, CSV)
- Contains all information about the processing run
- Includes error information if processing failed

**Success Criteria:**
- Processing is considered successful if `speed_measurements` contains at least one valid measurement
- If `error_message` is not None, processing encountered an error
- Multiple cars can result in multiple `SpeedMeasurement` objects

---

## Service Interaction Flow

The services work together in the following pipeline:

1. **VideoProcessor** loads video and provides frames
2. **CarDetector** detects cars in each frame
3. **CarTracker** tracks detected cars across frames
4. **CoordinateCrossingDetector** detects when cars cross coordinates
5. **SpeedCalculator** calculates speed from crossing events
6. **ImageGenerator** or **DebugImageGenerator** creates visualization images

This modular design allows each service to be tested independently and makes it easy to swap implementations (e.g., different detection models or tracking algorithms).

---

## Current Pipeline

This section describes how the services are orchestrated together in the CLI application (`src/cli/main.py`).

### Pipeline Overview

The processing pipeline follows a sequential frame-by-frame approach:

1. **Video Loading & Setup**
2. **Frame-by-Frame Processing**
3. **Speed Calculation**
4. **Result Generation**

### Detailed Pipeline Flow

#### 1. Initialization Phase

```python
# Load video and get metadata
video_processor = VideoProcessor(video_path, config=config)
video_metadata = video_processor.get_metadata()

# Handle video resizing if configured
scaled_coords = video_processor.get_scaled_coordinates()
if scaled_coords:
    # Create scaled config for crossing detection
    scaled_config = Configuration(...)
    crossing_detector = CoordinateCrossingDetector(scaled_config)
else:
    crossing_detector = CoordinateCrossingDetector(config)

# Initialize services
car_detector = CarDetector(confidence_threshold=confidence_threshold)
car_tracker = CarTracker()
speed_calculator = SpeedCalculator(config)

# Optional: Initialize debug image generator
if debug:
    debug_image_generator = DebugImageGenerator(debug_config)
```

**Key Points:**
- `VideoProcessor` handles video loading and optional resizing
- If video is resized, coordinates are automatically scaled
- All services are initialized before processing begins

#### 2. Frame-by-Frame Processing Loop

For each frame in the video:

```python
for frame_number, frame in video_processor.iter_frames():
    # Step 1: Detect cars in current frame
    detections = car_detector.detect(frame, frame_number)
    
    # Step 2: Update tracking with new detections
    tracked_cars = car_tracker.update(detections, frame_number)
    
    # Step 3: Check for coordinate crossings
    for tracked_car in tracked_cars:
        crossing_events = crossing_detector.detect_crossings(
            tracked_car,
            frame_number,
            debug=debug,
            video_processor=video_processor if debug else None,
            debug_image_generator=debug_image_generator
        )
        
        # Mark cars that have crossed both coordinates
        if tracked_car.is_complete():
            tracked_cars_with_crossings.append(tracked_car)
```

**Processing Steps:**

1. **Detection (`CarDetector.detect`)**:
   - Runs YOLO inference on the frame
   - Filters by confidence threshold and class ID
   - Returns list of [DetectionResult](#detectionresult) objects

2. **Tracking (`CarTracker.update`)**:
   - Matches new detections to existing tracks using IoU
   - Creates new tracks for unmatched detections
   - Maintains detection history for each tracked car
   - Returns all currently tracked cars

3. **Crossing Detection (`CoordinateCrossingDetector.detect_crossings`)**:
   - Checks each tracked car for coordinate crossings
   - Uses transition-based detection (prevents duplicates)
   - Updates `tracked_car.left_crossing_frame` and `tracked_car.right_crossing_frame`
   - Optionally generates debug images if `debug=True`

**Important Behaviors:**
- Frame numbers are 1-based (first frame is 1, not 0)
- Tracking maintains state across frames
- Crossing detection only triggers once per coordinate per car
- Debug images are generated on-the-fly during processing

#### 3. Speed Calculation Phase

After all frames are processed:

```python
# Calculate speed for each car that crossed both coordinates
for completed_car in tracked_cars_with_crossings:
    speed_measurement = speed_calculator.calculate_from_tracked_car(completed_car)
    speed_measurements.append(speed_measurement)
```

**Key Points:**
- Only cars that crossed both coordinates are processed
- Speed is calculated from frame differences and distance
- Average confidence is computed from all detections
- Results are collected into a list

#### 4. Result Generation

```python
result = [ProcessingResult](#processingresult)(
    video_path=video_path,
    config_path=config_path,
    video_metadata=video_metadata,
    config=config,
    speed_measurements=speed_measurements,
    processing_time_seconds=processing_time,
    frames_processed=frames_processed,
    detections_count=detections_count,
    error_message=None,
    logs=logs
)
```

**Optional: Image Generation**

If `--show` flag is used:

```python
if show and result.speed_measurements and tracked_cars:
    video_processor = VideoProcessor(video_file, config=config)
    image_generator = ImageGenerator(config)
    image_path = image_generator.generate_multi_car_composite_image(
        video_processor,
        tracked_cars,
        output_image_path
    )
```

### Error Handling

The pipeline handles several error conditions:

1. **VideoLoadError**: Video file cannot be opened
2. **NoCarDetectedError**: No cars detected in entire video
3. **CarNotCrossingBothCoordinatesError**: Cars detected but none crossed both coordinates
4. **ValueError**: Invalid speed calculation parameters

All errors are caught and included in the [ProcessingResult](#processingresult) with appropriate error messages.

### Performance Considerations

- **Video Resizing**: If `config.downsize_video` is set, frames are resized during iteration for faster processing
- **Coordinate Scaling**: Coordinates are automatically scaled when video is resized
- **Frame Caching**: `VideoProcessor` caches metadata and scale factors
- **Memory Management**: Frames are processed one at a time (not loaded entirely into memory)

### Debug Mode

When `--debug` flag is used:

- `DebugImageGenerator` is initialized
- Debug images are generated for each crossing event
- Images are saved to `output/crossing_{frame_number}.png`
- Shows bounding boxes, coordinate lines, and detection criteria

### Visualization Mode

When `--show` flag is used:

- Tracked cars are returned from `process_video()`
- `ImageGenerator` creates composite images showing:
  - Left and right crossing frames side-by-side
  - Both coordinate lines visible
  - Bounding boxes around detected cars
  - Multiple cars stacked vertically if multiple cars detected

