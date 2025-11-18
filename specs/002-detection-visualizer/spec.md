# Feature Specification: Car Detection Process Visualizer

**Feature Branch**: `002-detection-visualizer`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "create a GUI application using pyside6 that allows the user to see the vertical coordinates of the frame, and operate the video frame by frame showing the process that the main application does"

## Clarifications

### Session 2025-01-27

- Q: What is the primary input method for the GUI application? → A: JSON file is the primary input method (user opens JSON result file from Feature 001 CLI, system auto-loads video and config from JSON paths)
- Q: When should car detection run to identify bounding boxes? → A: Run live detection on-demand when user navigates to a frame (detect cars in current frame using Feature 001's CarDetector service)
- Q: How should car tracking state be managed during frame navigation? → A: Maintain tracking state across navigation (tracking state persists, allowing forward/backward navigation while preserving track IDs)
- Q: How should speed_measurements from JSON be used? → A: Use JSON speed_measurements to highlight known cars (track_id, crossing frames) and show expected results alongside live detection
- Q: How should coordinate crossing detection work? → A: Run live crossing detection on each frame AND highlight expected crossings from JSON (show both live detected crossings and expected crossing frames from speed_measurements)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualize Video Frames with Coordinate Overlays (Priority: P1)

A user opens a JSON result file (from Feature 001 CLI output) in the visualization application. The system automatically loads the video file and configuration file referenced in the JSON (via `video_path` and `config_path` fields). The system displays the current video frame with visual overlays showing the left and right measurement coordinates as vertical lines on the frame. The user can see exactly where the measurement points are located relative to the video content.

**Why this priority**: This is the core visualization capability that enables users to understand the measurement setup and verify coordinate positions. Without this, users cannot validate that coordinates are correctly positioned.

**Independent Test**: Can be fully tested by loading a video and configuration file, and verifying that the coordinate lines appear at the correct pixel positions on the video frame. Delivers immediate value as a coordinate validation tool.

**Acceptance Scenarios**:

1. **Given** a JSON result file (from Feature 001 CLI) containing `video_path` and `config_path` fields, **When** the user opens the JSON file in the application, **Then** the system automatically loads the video and configuration files and displays the current frame with vertical lines overlaid at the specified coordinate positions
2. **Given** a video frame is displayed, **When** the user views the frame, **Then** the coordinate lines are clearly visible and labeled (e.g., "Left" and "Right") so users can distinguish them
3. **Given** coordinate values that are outside the video frame dimensions, **When** the system displays the frame, **Then** it indicates that coordinates are out of bounds or handles the error appropriately

---

### User Story 2 - Frame-by-Frame Navigation (Priority: P2)

A user navigates through the video one frame at a time using forward and backward controls. The system displays each frame sequentially, allowing the user to examine the video frame-by-frame to understand the detection process.

**Why this priority**: Frame-by-frame navigation is essential for debugging and understanding exactly when events occur. This enables users to see the precise moment when a car crosses each coordinate.

**Independent Test**: Can be tested independently by loading a video and using navigation controls to move forward and backward through frames, verifying that each frame displays correctly and frame numbers update appropriately.

**Acceptance Scenarios**:

1. **Given** a video is loaded, **When** the user clicks the "Next Frame" button, **Then** the system advances to the next frame and updates the display
2. **Given** a video is loaded, **When** the user clicks the "Previous Frame" button, **Then** the system moves to the previous frame and updates the display
3. **Given** the user is at the first frame, **When** the user attempts to go to the previous frame, **Then** the system either disables the button or indicates that no previous frame exists
4. **Given** the user is at the last frame, **When** the user attempts to go to the next frame, **Then** the system either disables the button or indicates that no next frame exists
5. **Given** the user navigates through frames, **When** frames change, **Then** the system displays the current frame number and total frame count

---

### User Story 3 - Visualize Detection Process (Priority: P3)

A user views the video frames and sees visual indicators showing the car detection process that the main application performs. This includes displaying detected car bounding boxes, tracking information, and highlighting when cars cross the measurement coordinates.

**Why this priority**: This enables users to understand and debug how the main detection application works. Users can verify that detection is working correctly and see why certain measurements succeed or fail.

**Independent Test**: Can be tested independently by loading a video and running the detection process, then verifying that car bounding boxes, tracking information, and coordinate crossing events are visually displayed on the frames.

**Acceptance Scenarios**:

1. **Given** a video is loaded and user navigates to a frame, **When** the system runs live detection on the current frame (using Feature 001's CarDetector service), **Then** the system displays a bounding box around each detected car (using Feature 001's BoundingBox from DetectionResult)
2. **Given** a car is being tracked across frames (using Feature 001's CarTracker service), **When** the user navigates forward or backward through frames, **Then** the system maintains tracking state and visual indicators showing the same car's identity across frames (using Feature 001's TrackedCar model with track_id), preserving track IDs regardless of navigation direction
3. **Given** a car crosses the left coordinate (detected live by Feature 001's CoordinateCrossingDetector), **When** the crossing occurs, **Then** the system highlights or marks this event visually (using Feature 001's CoordinateCrossingEvent model)
4. **Given** a car crosses the right coordinate (detected live by Feature 001's CoordinateCrossingDetector), **When** the crossing occurs, **Then** the system highlights or marks this event visually (using Feature 001's CoordinateCrossingEvent model)
5. **Given** JSON speed_measurements contain left_crossing_frame and right_crossing_frame data, **When** the user navigates to those frames, **Then** the system highlights expected crossing frames from JSON alongside any live detected crossings, visually distinguishing between expected and live crossing events
6. **Given** detection information is available (from Feature 001's DetectionResult and TrackedCar models), **When** the user views a frame, **Then** the system displays relevant detection metadata (e.g., confidence scores from DetectionResult, tracking ID from TrackedCar) if available
7. **Given** a JSON file contains `speed_measurements` with track_id and crossing frame information, **When** the user navigates to frames containing known cars from JSON, **Then** the system highlights these known cars (e.g., by track_id) and displays expected speed results alongside live detection results

---

### Edge Cases

- What happens when the video file cannot be loaded or is corrupted?
- How does the system handle configuration files with invalid coordinate values?
- What happens when the user navigates frames while detection is still processing?
- How does the system handle videos with no detected cars?
- What happens when multiple cars are detected simultaneously? Answer: only one car is considered at the time
- How does the system display coordinates when video resolution changes between frames?
- What happens when the user closes the video file or switches to a different video?
- How does the system handle very long videos that may cause performance issues?
- What happens when detection processing fails or encounters errors?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a graphical user interface for video visualization
- **FR-002**: System MUST allow users to open JSON result files (from Feature 001 CLI output format) containing `video_path`, `config_path`, and `speed_measurements` fields
- **FR-003**: System MUST automatically load the video file and configuration file referenced in the JSON file (extracting paths from `video_path` and `config_path` JSON fields). The configuration file MUST use Feature 001's Configuration model from `src/models/config.py` with attributes: left_coordinate, right_coordinate, distance, fps, downsize_video
- **FR-004**: System MUST display video frames in the graphical interface
- **FR-005**: System MUST overlay vertical lines on video frames indicating the left_coordinate and right_coordinate positions from the configuration
- **FR-006**: System MUST label coordinate lines clearly (e.g., "Left" and "Right") so users can distinguish them
- **FR-007**: System MUST provide controls to navigate to the next frame
- **FR-008**: System MUST provide controls to navigate to the previous frame
- **FR-009**: System MUST display the current frame number and total frame count
- **FR-010**: System MUST show the current frame number as a small editable textbox. When the user writes a different frame number in the textbox, the system MUST change the frame shown in the GUI to that frame number
- **FR-011**: System MUST handle navigation at video boundaries (first/last frame) appropriately
- **FR-012**: System MUST run live car detection on-demand when user navigates to a frame (using Feature 001's CarDetector service) and visualize bounding boxes on the current frame (using Feature 001's BoundingBox from DetectionResult model)
- **FR-013**: System MUST maintain tracking state across frame navigation (forward and backward) using Feature 001's CarTracker service and visualize car tracking information (using Feature 001's TrackedCar model with track_id attribute), preserving consistent track IDs as user navigates
- **FR-014**: System MUST run live crossing detection on each frame (using Feature 001's CoordinateCrossingDetector) AND highlight expected crossing frames from JSON speed_measurements (left_crossing_frame, right_crossing_frame), showing both live detected crossings and expected crossings visually
- **FR-015**: System MUST visually distinguish between live detected crossing events (from CoordinateCrossingDetector) and expected crossing frames (from JSON speed_measurements) when displaying crossing highlights
- **FR-016**: System MUST display detection metadata (e.g., confidence scores from Feature 001's DetectionResult, tracking IDs from Feature 001's TrackedCar) when available
- **FR-018**: System MUST extract and use `speed_measurements` data from JSON file to highlight known cars (using track_id, left_crossing_frame, right_crossing_frame) and display expected speed results alongside live detection results
- **FR-019**: System MUST visually distinguish between expected results from JSON (e.g., known track_ids, crossing frames) and live detection results (e.g., current bounding boxes, live tracking)
- **FR-017**: System MUST handle errors gracefully and display user-friendly error messages for invalid files or configurations

### Key Entities *(include if feature involves data)*

- **Video Display**: Represents the visual rendering of video frames in the interface. Key attributes: current frame, frame number, video dimensions, display area

- **Coordinate Overlay**: Represents the visual indicators for measurement coordinates. Key attributes: left coordinate position, right coordinate position, line visibility, labels. Uses Feature 001's Configuration model for coordinate values.

- **Detection Visualization**: Represents the visual indicators of the detection process. Key attributes: 
  - Bounding boxes (from Feature 001's BoundingBox model)
  - Tracking information (from Feature 001's TrackedCar model with track_id)
  - Crossing events (from Feature 001's CoordinateCrossingEvent model)
  - Detection metadata (from Feature 001's DetectionResult model: confidence, class_name)
  - Speed measurements (from Feature 001's SpeedMeasurement model, when available)

- **Frame Navigation State**: Represents the current position in video playback. Key attributes: current frame number, total frames, navigation controls state

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully open a video file and see the first frame displayed within 3 seconds of file selection
- **SC-002**: Users can navigate between frames and see frame updates (including live detection results) displayed within reasonable time (detection may take 1-3 seconds per frame depending on hardware, but frame display should be responsive)
- **SC-003**: Coordinate overlay lines appear at the correct pixel positions matching configuration values with 100% accuracy
- **SC-004**: Users can successfully view and navigate through videos up to 5 minutes in duration without performance degradation or interface freezing
- **SC-005**: Detection visualization elements (bounding boxes, tracking, crossing events) are clearly visible and distinguishable from the video content for at least 90% of users
- **SC-006**: Users can complete the workflow of opening a video, viewing coordinate overlays, and navigating frames without requiring external documentation or training

## Integration with Feature 001 (Car Speed Detection)

This visualizer application integrates with and visualizes the detection process implemented in Feature 001 (`001-car-speed-detection`). The following components from Feature 001 are referenced:

### Data Models (from Feature 001)

The visualizer MUST use or display data from the following Feature 001 data models:

- **BoundingBox** (`src/models/detection_result.py`): Represents detected car bounding boxes with attributes (x1, y1, x2, y2, width, height, center_x, center_y). The visualizer displays these bounding boxes on video frames.

- **DetectionResult** (`src/models/detection_result.py`): Represents a single car detection with attributes (frame_number, bounding_box, confidence, class_id, class_name). The visualizer displays detection metadata including confidence scores.

- **TrackedCar** (`src/models/detection_result.py`): Represents a car tracked across frames with attributes (track_id, detections, first_detection_frame, last_detection_frame, left_crossing_frame, right_crossing_frame). The visualizer maintains and displays tracking information to show car identity across frames.

- **SpeedMeasurement** (`src/models/detection_result.py`): Represents calculated speed results with attributes (speed_kmh, frame_count, track_id, left_crossing_frame, right_crossing_frame, confidence). The visualizer MUST extract speed_measurements from JSON input file and use them to highlight known cars and display expected results alongside live detection.

- **CoordinateCrossingEvent** (`src/models/detection_result.py`): Represents coordinate crossing events with attributes (track_id, frame_number, coordinate_type, coordinate_value, car_rightmost_x, confidence). The visualizer highlights these crossing events on frames.

### Services (from Feature 001)

The visualizer MUST integrate with or reuse the following Feature 001 services:

- **CarDetector** (`src/services/car_detector.py`): YOLO-based car detection service that produces DetectionResult objects. The visualizer uses this service to detect cars in frames or displays results from this service.

- **CarTracker** (`src/services/car_tracker.py`): Car tracking service using IoU matching that maintains TrackedCar objects across frames. The visualizer uses this service to track cars and maintain consistent track IDs. Tracking state MUST persist across forward and backward frame navigation to preserve track identity.

- **CoordinateCrossingDetector** (`src/services/coordinate_crossing_detector.py`): Service that detects when cars cross left and right coordinates, producing CoordinateCrossingEvent objects. The visualizer MUST run this service live on each frame to detect crossings, AND also highlight expected crossing frames from JSON speed_measurements data, visually distinguishing between live detected and expected crossings.

- **SpeedCalculator** (`src/services/speed_calculator.py`): Service that calculates speed from crossing events and configuration, producing SpeedMeasurement objects. The visualizer may display speed calculations when available.

### Configuration Model (from Feature 001)

The visualizer MUST use the same Configuration model from Feature 001 (`src/models/config.py`) which includes:

- `left_coordinate` (int): X-coordinate in pixels for left measurement line
- `right_coordinate` (int): X-coordinate in pixels for right measurement line
- `distance` (float): Real-world distance between coordinates in centimeters
- `fps` (float): Frames per second
- `downsize_video` (Optional[int]): Optional target width in pixels for video resizing (for performance optimization)

The visualizer MUST handle the `downsize_video` parameter correctly, scaling coordinates proportionally when videos are resized, matching Feature 001's behavior.

## Assumptions

- The application integrates with or uses the same detection logic as the main car speed detection application (Feature 001)
- Video files are in MP4 format (matching Feature 001's input format)
- Configuration files use the same format as Feature 001's Configuration model (left_coordinate, right_coordinate, distance, fps, downsize_video)
- The GUI application is intended for debugging, visualization, and validation purposes
- Users have access to both video files and configuration files that they want to visualize
- The application runs detection processing on-demand when user navigates to frames using Feature 001's CarDetector service (live detection, not pre-computed)
- Coordinate values are provided in pixels relative to the video frame width (matching Feature 001's coordinate system)
- The application is used on desktop platforms with sufficient screen resolution to display video frames clearly
- The user has specified a preference for a specific GUI framework implementation, but the specification remains technology-agnostic to allow for implementation flexibility
