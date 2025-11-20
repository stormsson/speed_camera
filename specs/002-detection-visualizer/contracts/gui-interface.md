# GUI Interface Contract: Car Detection Process Visualizer

**Feature**: Car Detection Process Visualizer  
**Date**: 2025-01-27

## Overview

This contract defines the GUI interface behavior and user interactions for the visualizer application. The contract ensures consistent behavior across implementations and provides testable specifications.

## GUI Components

### Main Window

**Component**: `MainWindow` (PySide6 QMainWindow)

**Required Elements**:
- Menu bar with "File" menu containing:
  - "Open JSON Result File..." action (primary input method)
  - "Exit" action
- Central widget area for video display
- Status bar showing current frame number and total frames (format: "Frame X of Y")
- Toolbar or button panel for navigation controls

**Behavior**:
- Window MUST be resizable
- Window title MUST display current video file name (if loaded) or "Car Detection Visualizer"
- Window MUST handle close event gracefully (cleanup resources)

### Video Display Widget

**Component**: `VideoWidget` (PySide6 QLabel or QWidget)

**Required Elements**:
- Display area for video frame
- Coordinate overlay lines (vertical lines at left_coordinate and right_coordinate)
- Detection visualization overlays (bounding boxes, tracking IDs, crossing markers)

**Behavior**:
- MUST display current video frame as QPixmap
- MUST maintain aspect ratio when resizing
- MUST update display within 0.5 seconds of frame change (SC-002)
- MUST show coordinate lines at correct pixel positions (SC-003)
- MUST handle empty state (no video loaded) with placeholder message

**Coordinate Overlay Contract**:
- Left coordinate line: Vertical line at x = left_coordinate (scaled if downsize_video used)
- Right coordinate line: Vertical line at x = right_coordinate (scaled if downsize_video used)
- Lines MUST be clearly visible (minimum 2px width, contrasting color)
- Lines MUST be labeled with text "Left" and "Right" near top of frame
- Lines MUST span full height of frame

**Detection Visualization Contract**:
- Live detection bounding boxes: Rectangles drawn using BoundingBox coordinates (x1, y1, x2, y2) from live detection
- Expected bounding boxes (from JSON): Highlighted differently (e.g., dashed outline) for known cars from JSON speed_measurements
- Tracking IDs: Text label displayed near bounding box showing track_id (live and expected)
- Confidence scores: Text label displayed on bounding box showing confidence (format: "XX%")
- Live crossing events: Special marker (circle or arrow) at crossing coordinate from live detection
- Expected crossing frames (from JSON): Highlighted differently (e.g., different color) at left_crossing_frame and right_crossing_frame from JSON
- Colors: Different color per track_id for visual distinction, distinct colors for live vs expected results

### Navigation Controls Widget

**Component**: `ControlsWidget` (PySide6 QWidget)

**Required Elements**:
- "Previous Frame" button (QPushButton)
- "Next Frame" button (QPushButton)
- Frame number input (QLineEdit with QIntValidator)
- Frame counter display (QLabel showing "Frame X of Y")

**Behavior**:
- "Previous Frame" button:
  - MUST be disabled when current_frame_number = 1
  - MUST be enabled when current_frame_number > 1
  - On click: Navigate to previous frame, update display
- "Next Frame" button:
  - MUST be disabled when current_frame_number = total_frames
  - MUST be enabled when current_frame_number < total_frames
  - On click: Navigate to next frame, update display
- Frame number input:
  - MUST accept integer input only
  - MUST validate input: 1 <= value <= total_frames
  - On valid input: Navigate to specified frame, update display
  - On invalid input: Show error message, highlight input, do not update display
  - MUST update value when frame changes via buttons
- Frame counter display:
  - MUST show format: "Frame [current] of [total]"
  - MUST update immediately when frame changes

### Detection Status Indicator

**Component**: Detection status display (QLabel in status bar or main window)

**Required Elements**:
- Detection status label showing current state:
  - "Ready" (no detection running)
  - "Detecting..." (detection running on current frame)
  - "Complete" (detection finished for current frame)

**Behavior**:
- MUST update when detection starts/completes on frame navigation
- MUST show processing indicator during live detection (1-3 seconds per frame)

### Debug Information Panel

**Component**: `DebugPanelWidget` (PySide6 QWidget or QDockWidget)

**Required Elements**:
- Section header showing current frame number
- Per-tracked-car analysis sections (one section per car detected in current frame)
- For each car section:
  - YOLO detection results display:
    - Bounding box coordinates (x1, y1, x2, y2 from Feature 001's BoundingBox)
    - Confidence score (from Feature 001's DetectionResult)
    - Class name (from Feature 001's DetectionResult)
    - Car rightmost X coordinate (BoundingBox.x2)
  - Tracked car information display:
    - Track ID (from Feature 001's TrackedCar)
    - Left crossing frame (left_crossing_frame from Feature 001's TrackedCar)
    - Right crossing frame (right_crossing_frame from Feature 001's TrackedCar)
  - Coordinate crossing analysis display:
    - When crossing detected: vehicle_rightmost_x value, coordinate_value, comparison logic (e.g., "vehicle_rightmost_x >= coordinate_value"), condition met status
    - When crossing NOT detected: vehicle_rightmost_x value, coordinate_value, comparison result (e.g., "vehicle_rightmost_x < coordinate_value"), crossing state explanation (e.g., "left_crossing_frame is None" or "left already crossed, waiting for right")
- Comparison section showing live detection results vs expected JSON results (when JSON speed_measurements available)
- Empty state message when no cars detected in current frame

**Behavior**:
- MUST update automatically when user navigates to different frame (FR-024)
- MUST display detection information separately for each tracked car (FR-025)
- MUST show both live detection results and expected JSON results when available (FR-026)
- MUST display accurate detection analysis data matching actual detection state (SC-008)
- MUST handle empty state (no cars detected) gracefully with informative message
- Panel can be dockable (QDockWidget) or fixed (QWidget) - implementation choice

**Data Sources**:
- Receives detection data from DetectionController (detections, tracked_cars, crossing_events)
- Receives configuration from MainWindow (left_coordinate, right_coordinate)
- Receives JSON speed_measurements from JsonLoader (expected results)
- Updates triggered by frame navigation events from MainWindow

**Display Format Contract**:
- MUST show frame number prominently at top
- MUST organize information by tracked car (one section per track_id)
- MUST clearly label each data field (e.g., "Bounding Box:", "Confidence:", "Track ID:")
- MUST format comparison logic clearly (e.g., "250 >= 200" with explanation)
- MUST distinguish between live detection results and expected JSON results visually (e.g., labels "Live:" vs "Expected:")
- MUST show crossing state explanation in human-readable format

## User Interaction Contracts

### File Opening

**Action**: User selects "Open JSON Result File..." from File menu

**Contract**:
1. System MUST display file dialog (QFileDialog)
2. File dialog MUST filter for JSON files (*.json)
3. On file selection:
   - System MUST load and parse JSON file
   - System MUST extract video_path, config_path, and speed_measurements from JSON
   - System MUST automatically load video file from video_path
   - System MUST automatically load configuration file from config_path
   - System MUST extract speed_measurements (track_id, left_crossing_frame, right_crossing_frame, speed_kmh) from JSON
   - System MUST validate JSON structure (must contain video_path, config_path, speed_measurements)
   - System MUST extract video metadata (frame_count, width, height, fps)
   - System MUST display first frame
   - System MUST update frame counter display
   - System MUST enable navigation controls (if video has >1 frame)
   - System MUST load coordinate overlays from configuration
   - System MUST store JSON speed_measurements for highlighting known cars
   - System MUST complete within 3 seconds (SC-001)
4. On JSON load error:
   - System MUST display error message dialog: "Failed to load JSON file: [error details]"
   - System MUST not update display
   - System MUST log error with context
5. On video load error (from video_path in JSON):
   - System MUST display error message dialog: "Failed to load video file from JSON: [error details]"
   - System MUST not update display
   - System MUST log error with context
6. On configuration load error (from config_path in JSON):
   - System MUST display error message dialog (using Feature 001's InvalidConfigurationError)
   - System MUST not update coordinate overlays
   - System MUST log error with context

### Frame Navigation

**Action**: User clicks "Next Frame" button

**Contract**:
1. System MUST increment current_frame_number by 1
2. System MUST validate: current_frame_number <= total_frames
3. System MUST load and display frame at current_frame_number
4. System MUST update frame counter display
5. System MUST update frame number input value
6. System MUST run live detection on new frame (using Feature 001's VehicleDetector)
7. System MUST update tracking state (using Feature 001's CarTracker, maintaining state across navigation)
8. System MUST run crossing detection on new frame (using Feature 001's CoordinateCrossingDetector)
9. System MUST update detection visualization (live results + expected from JSON)
10. System MUST highlight expected crossing frames from JSON if current frame matches left_crossing_frame or right_crossing_frame
11. System MUST complete frame display within 0.5 seconds (SC-002), detection may take 1-3 seconds
12. System MUST disable "Next Frame" button if current_frame_number = total_frames

**Action**: User clicks "Previous Frame" button

**Contract**:
1. System MUST decrement current_frame_number by 1
2. System MUST validate: current_frame_number >= 1
3. System MUST load and display frame at current_frame_number
4. System MUST update frame counter display
5. System MUST update frame number input value
6. System MUST run live detection on new frame (using Feature 001's VehicleDetector)
7. System MUST update tracking state (using Feature 001's CarTracker, maintaining state across backward navigation)
8. System MUST run crossing detection on new frame (using Feature 001's CoordinateCrossingDetector)
9. System MUST update detection visualization (live results + expected from JSON)
10. System MUST highlight expected crossing frames from JSON if current frame matches left_crossing_frame or right_crossing_frame
11. System MUST complete frame display within 0.5 seconds (SC-002), detection may take 1-3 seconds
12. System MUST disable "Previous Frame" button if current_frame_number = 1

**Action**: User enters frame number in text input and presses Enter or loses focus

**Contract**:
1. System MUST validate input:
   - MUST be integer
   - MUST be >= 1
   - MUST be <= total_frames
2. If valid:
   - System MUST set current_frame_number to input value
   - System MUST load and display frame at current_frame_number
   - System MUST update frame counter display
   - System MUST update detection visualization for new frame (if available)
   - System MUST complete within 0.5 seconds (SC-002)
3. If invalid:
   - System MUST display error message: "Frame number must be between 1 and [total_frames]"
   - System MUST highlight input field (red border or background)
   - System MUST not update display
   - System MUST restore previous valid frame number in input

### Detection Visualization

**Action**: Detection results available for current frame

**Contract**:
1. System MUST display live detection bounding boxes for all detections in current frame (from Feature 001's VehicleDetector)
2. System MUST highlight expected cars from JSON speed_measurements (by track_id) with distinct visual style (e.g., dashed outline, different color)
3. System MUST display tracking ID for each tracked car (both live and expected from JSON)
4. System MUST display confidence score for each live detection
5. System MUST highlight live crossing events (if any) for current frame (from Feature 001's CoordinateCrossingDetector)
6. System MUST highlight expected crossing frames from JSON (left_crossing_frame, right_crossing_frame) with distinct visual style
7. System MUST use consistent colors for same track_id across frames (maintained by Feature 001's CarTracker)
8. System MUST visually distinguish between live detection results and expected results from JSON
9. System MUST update visualization immediately when frame changes and detection completes

## Error Handling Contracts

### Video Load Error

**Condition**: Video file cannot be loaded

**Contract**:
- System MUST display error dialog with message: "Failed to load video file: [error details]"
- System MUST log error with structured format (timestamp, file path, error type)
- System MUST not update video display
- System MUST reset GUI to "no video loaded" state

### Configuration Load Error

**Condition**: Configuration file is invalid or missing

**Contract**:
- System MUST display error dialog with message from Feature 001's InvalidConfigurationError
- System MUST log error with structured format
- System MUST not update coordinate overlays
- System MUST maintain previous configuration state (if any)

### Frame Out of Bounds Error

**Condition**: User enters invalid frame number

**Contract**:
- System MUST display inline error message (tooltip or label near input)
- System MUST highlight input field
- System MUST not navigate to invalid frame
- System MUST restore previous valid frame number in input

### Detection Processing Error

**Condition**: Detection service fails

**Contract**:
- System MUST display error message in status bar or dialog
- System MUST log error with structured format
- System MUST stop detection processing
- System MUST update detection status indicator to "Error"

## Performance Contracts

### Frame Display Performance

**Requirement**: SC-002 - Frame updates within 0.5 seconds

**Contract**:
- Frame navigation (next/previous/input) MUST complete display update within 0.5 seconds
- Measurement: Time from user action to frame displayed
- Includes: Frame loading, overlay rendering, detection visualization update

### Video Load Performance

**Requirement**: SC-001 - First frame displayed within 3 seconds

**Contract**:
- Video file opening MUST display first frame within 3 seconds of file selection
- Measurement: Time from file dialog "OK" to first frame displayed
- Includes: File loading, metadata extraction, first frame extraction, display update

### Coordinate Overlay Accuracy

**Requirement**: SC-003 - Coordinate lines at correct positions with 100% accuracy

**Contract**:
- Coordinate overlay lines MUST appear at exact pixel positions matching configuration values
- Scaled coordinates MUST match Feature 001's scaling calculation exactly
- Validation: Compare displayed line position to expected position (must match exactly)

## Testing Contracts

### GUI Component Testing

**Contract**: All GUI components MUST be testable using pytest-qt

**Requirements**:
- Components MUST expose testable methods for state inspection
- Signal emissions MUST be testable
- Widget interactions (button clicks, input changes) MUST be testable via qtbot
- Visual rendering MUST be testable via widget screenshot or pixel comparison

### Integration Testing

**Contract**: GUI integration with Feature 001 services MUST be testable

**Requirements**:
- Feature 001 services MUST be mockable for GUI testing
- GUI MUST handle service errors gracefully (testable)
- GUI MUST display Feature 001's data models correctly (testable)

