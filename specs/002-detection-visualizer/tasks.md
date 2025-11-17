# Tasks: Car Detection Process Visualizer

**Feature**: Car Detection Process Visualizer  
**Branch**: `002-detection-visualizer`  
**Date**: 2025-01-27  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Summary

This document contains actionable, dependency-ordered tasks for implementing the Car Detection Process Visualizer GUI application. Tasks are organized by phase, with each user story implemented as an independently testable increment.

**Total Tasks**: 45  
**User Story 1 (P1)**: 12 tasks  
**User Story 2 (P2)**: 8 tasks  
**User Story 3 (P3)**: 15 tasks  
**Setup & Foundational**: 7 tasks  
**Polish**: 3 tasks

## Implementation Strategy

**MVP Scope**: User Story 1 (P1) - Visualize Video Frames with Coordinate Overlays. This delivers immediate value as a coordinate validation tool and enables independent testing.

**Incremental Delivery**:
1. Phase 1-2: Setup and foundational infrastructure
2. Phase 3: User Story 1 (MVP) - Coordinate visualization
3. Phase 4: User Story 2 - Frame navigation
4. Phase 5: User Story 3 - Detection visualization
5. Final Phase: Polish and cross-cutting concerns

**Parallel Opportunities**: Tasks marked with [P] can be executed in parallel as they work on different files with no dependencies on incomplete tasks.

## Dependencies

### User Story Completion Order

```
Phase 1: Setup
  ↓
Phase 2: Foundational (blocks all user stories)
  ↓
Phase 3: User Story 1 (P1) - Coordinate Overlays [MVP]
  ↓
Phase 4: User Story 2 (P2) - Frame Navigation (depends on US1)
  ↓
Phase 5: User Story 3 (P3) - Detection Visualization (depends on US1, US2)
  ↓
Final Phase: Polish
```

**Story Dependencies**:
- User Story 2 depends on User Story 1 (needs coordinate overlay display)
- User Story 3 depends on User Story 1 and User Story 2 (needs frame navigation and coordinate display)

## Phase 1: Setup

**Goal**: Initialize project structure and install dependencies for GUI application.

### Setup Tasks

- [X] T001 Create GUI module structure: src/gui/ directory with __init__.py
- [X] T002 Create GUI widgets subdirectory: src/gui/widgets/ with __init__.py
- [X] T003 Create GUI windows subdirectory: src/gui/windows/ with __init__.py
- [X] T004 Create GUI controllers subdirectory: src/gui/controllers/ with __init__.py
- [X] T005 Update requirements.txt to include PySide6>=6.5.0 and pytest-qt>=4.2.0
- [X] T006 Create GUI test directory structure: tests/unit/gui/ with __init__.py

## Phase 2: Foundational

**Goal**: Implement core infrastructure that blocks all user stories. These components are prerequisites for video loading, JSON parsing, and service integration.

### Foundational Tasks

- [X] T007 [P] Create JSON loader controller in src/gui/controllers/json_loader.py to parse Feature 001 JSON result files and extract video_path, config_path, speed_measurements
- [X] T008 [P] Create video controller in src/gui/controllers/video_controller.py to handle video loading, frame extraction, and metadata management using Feature 001's VideoProcessor
- [X] T009 [P] Create detection controller in src/gui/controllers/detection_controller.py to coordinate Feature 001's services (CarDetector, CarTracker, CoordinateCrossingDetector) for live detection
- [X] T010 Create GUI state models in src/gui/models.py for VideoDisplayState, CoordinateOverlayState, DetectionVisualizationState, FrameNavigationState per data-model.md

## Phase 3: User Story 1 - Visualize Video Frames with Coordinate Overlays (P1) [MVP]

**Goal**: Users can open a JSON result file, automatically load video and configuration, and see coordinate overlays on video frames.

**Independent Test Criteria**: Load a video and configuration file, verify coordinate lines appear at correct pixel positions on the video frame. Testable without frame navigation or detection.

**Acceptance**: JSON file opens → video and config auto-load → first frame displays → coordinate lines visible at correct positions.

### User Story 1 Tasks

- [X] T011 [US1] Create main window class in src/gui/windows/main_window.py with menu bar (File menu with "Open JSON Result File..." and "Exit" actions), central widget area, and status bar
- [X] T012 [US1] Create video display widget in src/gui/widgets/video_display.py as QLabel subclass to display video frames as QPixmap with aspect ratio preservation
- [X] T013 [US1] Create coordinate overlay widget in src/gui/widgets/coordinate_overlay.py to render vertical lines at left_coordinate and right_coordinate positions using QPainter, with labels "Left" and "Right"
- [X] T014 [US1] Integrate JSON loader in main window: connect "Open JSON Result File..." action to file dialog, load JSON, extract video_path and config_path, handle errors with user-friendly dialogs
- [X] T015 [US1] Integrate video controller in main window: auto-load video from JSON video_path, extract metadata (frame_count, width, height, fps), display first frame in video display widget
- [X] T016 [US1] Load configuration from JSON config_path using Feature 001's Configuration model in src/models/config.py, handle InvalidConfigurationError with error dialog
- [X] T017 [US1] Integrate coordinate overlay in video display widget: pass Configuration to overlay widget, render coordinate lines scaled correctly if downsize_video is used, validate coordinates are within frame bounds
- [X] T018 [US1] Create GUI entry point in src/gui/main.py with QApplication initialization, MainWindow instantiation, and application execution
- [X] T019 [US1] Update window title in main window to display current video file name when loaded, or "Car Detection Visualizer" when no video loaded
- [X] T020 [US1] Handle empty state in video display widget: show placeholder message "No video loaded" when no video is available
- [X] T021 [US1] Implement coordinate scaling logic in coordinate overlay widget: calculate scale_factor when downsize_video is used, scale coordinates proportionally to match Feature 001's behavior
- [X] T022 [US1] Add error handling for out-of-bounds coordinates: display warning message when coordinates are outside video frame dimensions (0 to video_width)

## Phase 4: User Story 2 - Frame-by-Frame Navigation (P2)

**Goal**: Users can navigate through video one frame at a time using forward/backward controls and frame number input.

**Independent Test Criteria**: Load a video, use navigation controls to move forward and backward through frames, verify each frame displays correctly and frame numbers update appropriately. Testable independently after US1.

**Acceptance**: Navigation buttons work → frame updates → frame counter updates → frame number input works → boundaries handled correctly.

### User Story 2 Tasks

- [X] T023 [US2] Create navigation controls widget in src/gui/widgets/navigation_controls.py with "Previous Frame" button, "Next Frame" button, frame number input (QLineEdit with QIntValidator), and frame counter display (QLabel)
- [X] T024 [US2] Implement frame navigation logic in video controller: add methods to navigate to next frame, previous frame, and specific frame number using OpenCV VideoCapture frame seeking (cap.set(cv2.CAP_PROP_POS_FRAMES))
- [X] T025 [US2] Integrate navigation controls in main window: connect button signals to video controller navigation methods, update video display widget on frame change
- [X] T026 [US2] Implement frame number input validation in navigation controls widget: validate integer input, check bounds (1 <= value <= total_frames), show error message and highlight input on invalid input, update display on valid input
- [X] T027 [US2] Update frame counter display in navigation controls widget: show format "Frame X of Y", update immediately when frame changes via buttons or input
- [X] T028 [US2] Implement button state management in navigation controls widget: disable "Previous Frame" when current_frame_number = 1, disable "Next Frame" when current_frame_number = total_frames
- [X] T029 [US2] Update status bar in main window to show current frame number and total frames (format: "Frame X of Y")
- [X] T030 [US2] Implement frame cache in video controller: cache recently viewed frames (e.g., last 10 frames) for quick back navigation, keyed by frame_number

## Phase 5: User Story 3 - Visualize Detection Process (P3)

**Goal**: Users see visual indicators of the car detection process including bounding boxes, tracking information, and coordinate crossing events, both from live detection and expected results from JSON.

**Independent Test Criteria**: Load a video with JSON speed_measurements, navigate to frames, verify live detection runs, bounding boxes appear, tracking IDs are consistent across frames, crossing events are highlighted, and expected results from JSON are displayed alongside live detection. Testable after US1 and US2.

**Acceptance**: Live detection runs on frame navigation → bounding boxes displayed → tracking state maintained → crossing events highlighted → JSON expected results shown → visual distinction between live and expected.

### User Story 3 Tasks

- [X] T031 [US3] Create detection overlay widget in src/gui/widgets/detection_overlay.py to render bounding boxes, tracking IDs, confidence scores, and crossing event markers using QPainter
- [X] T032 [US3] Integrate detection controller in main window: instantiate CarDetector, CarTracker, CoordinateCrossingDetector from Feature 001 services, maintain tracking state across frame navigation
- [X] T033 [US3] Implement live detection on frame navigation: call CarDetector.detect() on current frame when user navigates, update DetectionVisualizationState with DetectionResult objects
- [X] T034 [US3] Implement tracking state maintenance in detection controller: call CarTracker.update() with current frame detections, maintain TrackedCar dictionary across forward/backward navigation, preserve track IDs
- [X] T035 [US3] Implement live crossing detection in detection controller: call CoordinateCrossingDetector.detect_crossings() on current frame with tracked cars, update DetectionVisualizationState with CoordinateCrossingEvent objects
- [X] T036 [US3] Load JSON speed_measurements in JSON loader: extract speed_measurements array from JSON, parse SpeedMeasurement objects with track_id, left_crossing_frame, right_crossing_frame, store in DetectionVisualizationState
- [X] T037 [US3] Render live detection bounding boxes in detection overlay widget: draw rectangles using BoundingBox coordinates (x1, y1, x2, y2) from DetectionResult, use distinct colors per track_id
- [X] T038 [US3] Render tracking ID labels in detection overlay widget: display track_id text near bounding box for each TrackedCar, use consistent colors for same track_id across frames
- [X] T039 [US3] Render confidence scores in detection overlay widget: display confidence as text overlay on bounding box (format: "XX%") from DetectionResult
- [X] T040 [US3] Render live crossing event markers in detection overlay widget: draw circle or arrow marker at crossing coordinate for live CoordinateCrossingEvent objects
- [X] T041 [US3] Highlight expected cars from JSON in detection overlay widget: identify known cars by track_id from JSON speed_measurements, render with distinct visual style (e.g., dashed outline, different color) to distinguish from live detection
- [X] T042 [US3] Highlight expected crossing frames from JSON in detection overlay widget: when current frame matches left_crossing_frame or right_crossing_frame from JSON speed_measurements, highlight with distinct visual style (different color) to distinguish from live crossing events
- [X] T043 [US3] Integrate detection overlay in video display widget: overlay detection visualization on current frame, update on frame navigation and detection completion
- [X] T044 [US3] Create detection status indicator in main window: add QLabel to status bar showing "Ready", "Detecting...", or "Complete" based on detection processing state
- [X] T045 [US3] Implement async detection processing: use QThread to run detection in background, keep GUI responsive during detection (1-3 seconds per frame), update detection status indicator

## Final Phase: Polish & Cross-Cutting Concerns

**Goal**: Add error handling, performance optimizations, and user experience improvements.

### Polish Tasks

- [ ] T046 Add comprehensive error handling: handle VideoLoadError, InvalidConfigurationError, DetectionProcessingError with user-friendly error dialogs and logging per contracts/gui-interface.md
- [ ] T047 Implement performance optimizations: ensure frame display completes within 0.5 seconds (SC-002), optimize frame cache size, validate coordinate overlay accuracy (SC-003)
- [ ] T048 Add GUI component tests using pytest-qt: test video display widget, coordinate overlay widget, detection overlay widget, navigation controls widget per contracts/gui-interface.md testing requirements

## Parallel Execution Examples

### User Story 1 Parallel Opportunities

Tasks T012, T013, T014 can be worked on in parallel:
- T012: Create video display widget (different file)
- T013: Create coordinate overlay widget (different file)
- T014: Integrate JSON loader (different file, no dependencies on T012/T013 completion)

### User Story 3 Parallel Opportunities

Tasks T031, T033, T036 can be worked on in parallel:
- T031: Create detection overlay widget (different file)
- T033: Implement live detection (different file, uses existing services)
- T036: Load JSON speed_measurements (different file, uses existing JSON loader)

## Test Strategy

**Unit Tests**: GUI widgets tested independently using pytest-qt with mocked Feature 001 services.

**Integration Tests**: End-to-end workflow tested with test videos and JSON files from Feature 001 CLI output.

**Contract Tests**: GUI interface contracts validated per contracts/gui-interface.md specifications.

## Notes

- All tasks assume Feature 001 (Car Speed Detection) is fully implemented and available
- Tasks reference Feature 001's models and services directly (no API layer needed)
- GUI follows MVC-like pattern: widgets (view), controllers (logic), windows (main UI)
- Detection processing runs on-demand per frame (not pre-computed)
- Tracking state must persist across forward/backward navigation to maintain track IDs
- JSON speed_measurements provide expected results for comparison with live detection

