# Implementation Plan: Car Detection Process Visualizer

**Branch**: `002-detection-visualizer` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)  
**Updated**: 2025-01-27 (Added debugging requirements FR-020 through FR-026)  
**Input**: Feature specification from `/specs/002-detection-visualizer/spec.md`

## Summary

Build a PySide6 GUI application that visualizes the car detection process from Feature 001, allowing users to:
- View video frames with coordinate overlays
- Navigate frame-by-frame through videos
- See live detection results (bounding boxes, tracking, crossing events)
- Compare live detection with expected results from JSON
- **Debug unexpected detection events** with detailed information panel showing why detection events occurred or did not occur

Technical approach: Direct integration with Feature 001's services (CarDetector, CarTracker, CoordinateCrossingDetector), using QLabel/QPixmap for frame display and QPainter for overlays. Frame-by-frame navigation using OpenCV VideoCapture with frame seeking.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: PySide6, OpenCV (cv2), numpy, Feature 001 services (CarDetector, CarTracker, CoordinateCrossingDetector)  
**Storage**: N/A (in-memory state, file-based JSON input)  
**Testing**: pytest, pytest-qt for GUI testing  
**Target Platform**: Desktop (Windows, macOS, Linux)  
**Project Type**: Single desktop application  
**Performance Goals**: Frame display within 0.5 seconds, first frame within 3 seconds, detection processing 1-3 seconds per frame  
**Constraints**: Must handle videos up to 5 minutes without performance degradation, maintain tracking state across forward/backward navigation  
**Scale/Scope**: Single-user desktop application, frame-by-frame video analysis

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Accuracy-First (NON-NEGOTIABLE)
✅ **PASS**: Debug panel (FR-020 through FR-026) provides detailed detection analysis to validate accuracy. Shows exact comparison values (car_rightmost_x vs coordinate_value) and crossing logic, enabling users to verify detection correctness.

### II. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS**: GUI components testable with pytest-qt. Debug panel data display can be unit tested. Detection analysis logic can be tested independently.

### III. Observability & Metrics
✅ **PASS**: Debug panel provides detailed logging of detection state per frame. Shows confidence scores, bounding box positions, and crossing analysis. Enables debugging and validation of detection accuracy.

### IV. Modular Video Processing
✅ **PASS**: Reuses Feature 001's modular services (CarDetector, CarTracker, CoordinateCrossingDetector). Debug panel is separate component that analyzes detection results.

### V. Data Management
✅ **PASS**: JSON input file provides traceability. Debug panel shows detection state linked to frame numbers and configuration.

**All gates pass. Ready for implementation.**

## Project Structure

### Documentation (this feature)

```text
specs/002-detection-visualizer/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── gui-interface.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/              # Feature 001 models (reused)
├── services/            # Feature 001 services (reused)
├── cli/                 # Feature 001 CLI (separate)
├── lib/                 # Shared utilities
└── gui/                 # GUI application (NEW)
    ├── __init__.py
    ├── main.py          # Application entry point
    ├── models.py        # GUI state models
    ├── windows/
    │   └── main_window.py
    ├── widgets/
    │   ├── video_display.py
    │   ├── coordinate_overlay.py
    │   ├── detection_overlay.py
    │   ├── navigation_controls.py
    │   └── debug_panel.py          # NEW: Debug information panel
    └── controllers/
        ├── detection_controller.py
        ├── detection_worker.py
        ├── json_loader.py
        └── video_controller.py

tests/
├── contract/
├── integration/
└── unit/
    └── gui/             # NEW: GUI unit tests
        ├── test_main_window.py
        ├── test_debug_panel.py     # NEW: Debug panel tests
        └── test_detection_overlay.py
```

**Structure Decision**: Single project structure. GUI application in `src/gui/` directory. Reuses Feature 001's models and services from `src/models/` and `src/services/`. New debug panel widget in `src/gui/widgets/debug_panel.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All complexity is justified by feature requirements.

## Phase 0: Research & Design Decisions

**Status**: ✅ Complete (see [research.md](./research.md))

Key decisions:
- PySide6 with QLabel/QPixmap for frame display, QPainter for overlays
- Direct import of Feature 001 services (no API layer needed)
- OpenCV VideoCapture with frame seeking for navigation
- Hybrid approach: JSON input + live detection on-demand
- pytest-qt for GUI testing

**New Research for Debug Panel** (FR-020 through FR-026):
- **Decision**: Use QDockWidget or QWidget panel for debug information display
- **Rationale**: QDockWidget allows dockable/undockable panel, QWidget provides simpler fixed panel. For debugging use case, fixed panel or dockable panel both acceptable.
- **Implementation**: Display structured text (QTextEdit or QTreeWidget) showing detection analysis per tracked car
- **Data Source**: Current frame's DetectionResult, TrackedCar, CoordinateCrossingEvent, Configuration
- **Update Strategy**: Auto-update on frame navigation, show per-car analysis

## Phase 1: Design & Contracts

**Status**: ✅ Complete (see [data-model.md](./data-model.md), [contracts/gui-interface.md](./contracts/gui-interface.md))

### Data Model Updates

**New Entity**: `DebugInformationState` (added to data-model.md)

Represents detailed detection analysis data displayed in the debug panel.

**Attributes**:
- `current_frame_number` (int): Frame being analyzed
- `detection_results` (List[DetectionResult]): Live YOLO detection results for current frame
- `tracked_cars_analysis` (Dict[int, TrackedCarAnalysis]): Per-tracked-car analysis
- `coordinate_crossing_analysis` (Dict[int, CrossingAnalysis]): Per-car crossing detection analysis
- `configuration_values` (Configuration): Current configuration (left_coordinate, right_coordinate)
- `json_expected_results` (List[SpeedMeasurement]): Expected results from JSON for comparison

**TrackedCarAnalysis** (nested):
- `track_id` (int)
- `bounding_box` (BoundingBox): Current frame bounding box
- `confidence` (float): Detection confidence
- `class_name` (str): Detected class
- `left_crossing_frame` (Optional[int]): Frame when left was crossed (if any)
- `right_crossing_frame` (Optional[int]): Frame when right was crossed (if any)
- `car_rightmost_x` (int): Computed rightmost X coordinate (BoundingBox.x2)

**CrossingAnalysis** (nested):
- `track_id` (int)
- `coordinate_type` (str): "left" or "right"
- `coordinate_value` (int): Coordinate being checked
- `car_rightmost_x` (int): Car's rightmost X position
- `comparison_result` (str): "car_rightmost_x >= coordinate_value" or "car_rightmost_x < coordinate_value"
- `condition_met` (bool): Whether crossing condition was met
- `crossing_state` (str): Explanation of current crossing state (e.g., "left_crossing_frame is None", "left already crossed, waiting for right")
- `crossing_detected` (bool): Whether crossing event was detected this frame

### Contract Updates

**New Component**: `DebugPanelWidget` (added to contracts/gui-interface.md)

**Component**: `DebugPanelWidget` (PySide6 QWidget or QDockWidget)

**Required Elements**:
- Section for each tracked car in current frame
- Display of YOLO detection results (bounding box coordinates, confidence, class_name)
- Display of tracked car information (track_id, left_crossing_frame, right_crossing_frame)
- Display of coordinate crossing analysis:
  - When crossing detected: car_rightmost_x, coordinate_value, comparison logic, condition met status
  - When crossing NOT detected: car_rightmost_x, coordinate_value, comparison result, crossing state explanation
- Comparison section showing live detection vs expected JSON results
- Auto-update on frame navigation

**Behavior**:
- MUST update automatically when user navigates to different frame (FR-024)
- MUST display detection information separately for each tracked car (FR-025)
- MUST show both live detection results and expected JSON results when available (FR-026)
- MUST display accurate detection analysis data matching actual detection state (SC-008)
- MUST handle empty state (no cars detected) gracefully

**Integration Points**:
- Receives detection data from DetectionController
- Receives configuration from MainWindow
- Receives JSON speed_measurements from JsonLoader
- Updates triggered by frame navigation events

## Implementation Notes

### Debug Panel Implementation

**Location**: `src/gui/widgets/debug_panel.py`

**Key Methods**:
- `update_debug_info(frame_number, detections, tracked_cars, crossing_events, config, json_measurements)`: Update panel with current frame data
- `_format_car_analysis(tracked_car, detection, crossing_analysis)`: Format per-car analysis display
- `_format_crossing_explanation(crossing_analysis)`: Format crossing detection explanation
- `_format_comparison(live_results, json_results)`: Format live vs expected comparison

**Data Flow**:
1. User navigates to frame → MainWindow triggers detection
2. DetectionController processes frame → returns detections, tracked_cars, crossing_events
3. MainWindow calls `debug_panel.update_debug_info()` with all data
4. DebugPanel formats and displays analysis

**Display Format** (example):
```
Frame 42 - Debug Information
============================

Track ID: 1
-----------
Detection:
  Bounding Box: (x1=100, y1=50, x2=250, y2=200)
  Confidence: 0.95
  Class: car
  Car Rightmost X: 250

Tracking:
  Track ID: 1
  Left Crossing Frame: 40
  Right Crossing Frame: None

Crossing Analysis (Left):
  Coordinate Value: 200
  Car Rightmost X: 250
  Comparison: 250 >= 200
  Condition Met: Yes
  Crossing Detected: Yes (Frame 40)

Crossing Analysis (Right):
  Coordinate Value: 400
  Car Rightmost X: 250
  Comparison: 250 < 400
  Condition Met: No
  Crossing State: Left already crossed, waiting for right

JSON Expected:
  Left Crossing Frame: 40 (matches)
  Right Crossing Frame: 45 (expected)
```

### Integration with Existing GUI

**MainWindow Updates**:
- Add DebugPanelWidget to layout (dockable or fixed panel)
- Connect frame navigation signals to debug panel update
- Pass detection results, configuration, JSON measurements to debug panel

**DetectionController Integration**:
- No changes needed (already provides all required data)
- Debug panel consumes existing DetectionController output

## Testing Strategy

### Debug Panel Testing

**Unit Tests** (`tests/unit/gui/test_debug_panel.py`):
- Test debug info formatting for crossing detected case
- Test debug info formatting for crossing NOT detected case
- Test per-car analysis display
- Test live vs JSON comparison display
- Test empty state (no cars detected)
- Test auto-update on frame change

**Integration Tests**:
- Test debug panel updates when navigating frames
- Test debug panel shows accurate data matching DetectionController output
- Test debug panel handles multiple tracked cars correctly

## Next Steps

1. ✅ Phase 0: Research complete
2. ✅ Phase 1: Design & Contracts complete (updated with debug panel)
3. ⏭️ Phase 2: Task breakdown (`/speckit.tasks` command)
4. ⏭️ Implementation: Create debug panel widget and integrate with MainWindow

## Updated Requirements Summary

**New Functional Requirements Added**:
- FR-020: Debug information panel/window
- FR-021: Display YOLO detection results, tracked car info, coordinate crossing analysis
- FR-022: Display crossing detection explanation (when detected)
- FR-023: Display crossing non-detection explanation (when not detected)
- FR-024: Auto-update debug panel on frame navigation
- FR-025: Separate display per tracked car
- FR-026: Compare live detection vs expected JSON results

**New Success Criteria Added**:
- SC-007: Users can identify why detection events occurred in 95% of unexpected cases
- SC-008: Debug panel displays accurate detection analysis with 100% accuracy
