# Implementation Plan: Car Detection Process Visualizer

**Branch**: `002-detection-visualizer` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-detection-visualizer/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a PySide6 GUI application that visualizes the car detection process from Feature 001. The application accepts JSON result files from Feature 001 CLI, automatically loads video and configuration files, and provides frame-by-frame navigation with live detection visualization. Users can see coordinate overlays, bounding boxes, tracking information, and crossing events both from live detection and expected results from JSON. The visualizer integrates directly with Feature 001's services (CarDetector, CarTracker, CoordinateCrossingDetector) and maintains tracking state across forward/backward navigation.

## Technical Context

**Language/Version**: Python 3.11+ (matches Feature 001)  
**Primary Dependencies**: PySide6 (GUI framework), opencv-python (video processing), ultralytics (YOLO detection - via Feature 001), numpy (image processing), PyYAML (config parsing)  
**Storage**: File-based (JSON input files, video files, config files) - no database required  
**Testing**: pytest, pytest-qt (for PySide6 widget testing), pytest-cov (coverage)  
**Target Platform**: Desktop (Linux, macOS, Windows) - PySide6 is cross-platform  
**Project Type**: Single desktop application (GUI module added to existing project)  
**Performance Goals**: Frame display within 0.5s of navigation click (SC-002), detection may take 1-3s per frame depending on hardware, support videos up to 5 minutes without performance degradation (SC-004)  
**Constraints**: GUI must remain responsive during detection processing (use QThread for async), memory efficient (no full video loading), frame-by-frame navigation must be smooth  
**Scale/Scope**: Single-user desktop application, one video at a time, debugging/visualization tool

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Accuracy-First (NON-NEGOTIABLE)
✅ **PASS**: Visualizer displays detection results from Feature 001's validated services. Live detection uses same CarDetector service as Feature 001, ensuring consistency. JSON input contains validated speed measurements from Feature 001 CLI.

### II. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS**: GUI components will be tested using pytest-qt. Frame navigation, coordinate overlay rendering, and detection visualization will have unit tests. Integration tests will validate end-to-end visualization workflow with test videos.

### III. Observability & Metrics
⚠️ **PARTIAL**: GUI application focuses on visualization, not production metrics. However, detection confidence scores and processing times are displayed to users. Logging can be added for debugging purposes. **Justification**: This is a debugging/visualization tool, not a production system. User-visible metrics (confidence, frame numbers) are sufficient.

### IV. Modular Video Processing
✅ **PASS**: Visualizer reuses Feature 001's modular services (VideoProcessor, CarDetector, CarTracker, CoordinateCrossingDetector). GUI layer is separate from detection logic. Detection services are pluggable and independently testable.

### V. Data Management
✅ **PASS**: JSON input files link results to source video metadata (video_path, config_path). Configuration used is stored in JSON. Failed processing attempts will show user-friendly error messages.

**Gate Status**: ✅ **PASS** (with justified partial on Observability - acceptable for visualization tool)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/              # Shared models (from Feature 001)
├── services/            # Shared services (from Feature 001)
├── cli/                 # CLI application (Feature 001)
├── gui/                 # NEW: GUI application (Feature 002)
│   ├── __init__.py
│   ├── main.py          # GUI entry point
│   ├── widgets/         # PySide6 widgets
│   │   ├── __init__.py
│   │   ├── video_display.py      # Video frame display widget
│   │   ├── coordinate_overlay.py # Coordinate overlay widget
│   │   └── detection_overlay.py  # Detection visualization widget
│   ├── windows/         # Main window
│   │   ├── __init__.py
│   │   └── main_window.py        # Main application window
│   └── controllers/     # Business logic controllers
│       ├── __init__.py
│       ├── video_controller.py    # Video loading/navigation
│       ├── detection_controller.py # Detection coordination
│       └── json_loader.py          # JSON file loading
└── lib/                 # Shared utilities

tests/
├── contract/
├── integration/
└── unit/
    └── gui/             # NEW: GUI unit tests
        ├── __init__.py
        ├── test_video_display.py
        ├── test_coordinate_overlay.py
        └── test_detection_overlay.py
```

**Structure Decision**: Single project structure with new `src/gui/` module. GUI follows MVC-like pattern with widgets (view), controllers (logic), and windows (main UI). Reuses existing `src/models/` and `src/services/` from Feature 001. Tests organized under `tests/unit/gui/` for GUI-specific tests.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
