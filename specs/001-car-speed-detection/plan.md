# Implementation Plan: Car Speed Detection from Video

**Branch**: `001-car-speed-detection` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-car-speed-detection/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a CLI application that processes MP4 video files to detect cars moving left-to-right, tracks when they cross predefined left and right measurement coordinates, and calculates speed in km/h based on frame count and known distance. The system uses YOLO for car detection and OpenCV for video processing, with a modular architecture that separates video ingestion, detection, tracking, and speed calculation.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: 
- OpenCV (cv2) for video processing and frame extraction
- YOLO model (ultralytics or similar) for car detection
- Click or argparse for CLI interface
- PyYAML or configparser for configuration file parsing
- NumPy for numerical operations

**Storage**: File-based (video files, configuration files, optional result logs)  
**Testing**: pytest with synthetic test videos and labeled ground truth data  
**Target Platform**: Cross-platform (Linux, macOS) CLI application  
**Project Type**: Single CLI application  
**Performance Goals**: Process videos up to 10 minutes in duration;   
**Constraints**: 
- Must handle videos without loading entire video into memory
- Must support MP4 format
- Must operate entirely via CLI
- Must maintain ±5% accuracy against ground truth
- Memory-efficient frame-by-frame processing

**Scale/Scope**: 
- Single video processing at a time
- Support for videos up to 10 minutes duration
- Handle standard video resolutions (720p, 1080p)
- The video will have multiple cars passing by, never more than once in the frame for each transit.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Accuracy-First (NON-NEGOTIABLE)
✅ **PASS**: 
- Speed calculation will use validated formula with ground truth testing
- Detection parameters (confidence thresholds, model selection) will be configurable and versioned
- Measurement errors will be logged with confidence intervals
- False positives/negatives will be tracked in logs

### II. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS**: 
- TDD will be enforced: tests written first, then implementation
- Computer vision tests will use synthetic or labeled test videos
- Speed calculation tests will use known ground truth data
- Integration tests will validate end-to-end pipeline

### III. Observability & Metrics
✅ **PASS**: 
- All detections will be logged with timestamps, confidence scores, frame numbers
- Performance metrics will track processing time per frame and per video
- Detection accuracy metrics will be collected
- Structured logging will be implemented

### IV. Modular Video Processing
✅ **PASS**: 
- Architecture will separate: video ingestion, detection logic, tracking, speed calculation, output formatting
- Detection algorithms will be pluggable (YOLO as initial implementation)
- Each module will be independently testable

### V. Data Management
✅ **PASS**: 
- Configuration used for each run will be logged
- Failed processing attempts will be logged with error context
- Results will be linked to source video metadata
- Video file paths and processing parameters will be traceable

**Gate Status**: ✅ **ALL GATES PASS** - Proceed to Phase 0 research

### Post-Design Constitution Check

*Re-evaluated after Phase 1 design completion*

#### I. Accuracy-First (NON-NEGOTIABLE)
✅ **PASS**: 
- Speed calculation uses validated formula: `speed (km/h) = (distance_meters / time_seconds) × 3.6`
- Detection parameters (confidence threshold) are configurable via CLI
- Measurement includes confidence scores from detection
- Frame counting is precise (no skipping during measurement period)
- Ground truth testing will be implemented in integration tests

#### II. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS**: 
- Test structure defined: unit, integration, contract tests
- Integration tests will use labeled test videos with known speeds
- Speed calculation tests will use synthetic data with known ground truth
- TDD workflow will be enforced during implementation

#### III. Observability & Metrics
✅ **PASS**: 
- Structured logging implemented (JSON format)
- Logs include: timestamps, frame numbers, detection confidence, speed calculations
- Performance metrics tracked: processing time per frame and per video
- CLI options for verbose logging and log file output
- All detections and coordinate crossings logged

#### IV. Modular Video Processing
✅ **PASS**: 
- Clear module separation: video_processor, car_detector, car_tracker, coordinate_crossing_detector, speed_calculator
- Detection algorithm (YOLO) is pluggable - can swap models
- Each module independently testable
- CLI interface separated from processing logic

#### V. Data Management
✅ **PASS**: 
- Configuration file path and parameters logged in results
- Video metadata (path, dimensions, fps) included in results
- Failed processing attempts logged with error context
- Results traceable to source video and configuration

**Post-Design Gate Status**: ✅ **ALL GATES PASS** - Design aligns with constitution principles

## Project Structure

### Documentation (this feature)

```text
specs/001-car-speed-detection/
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
├── models/
│   ├── __init__.py
│   ├── config.py           # Configuration model/parser
│   └── detection_result.py  # Detection and speed measurement models
├── services/
│   ├── __init__.py
│   ├── video_processor.py  # Video ingestion and frame extraction
│   ├── car_detector.py     # YOLO-based car detection
│   ├── car_tracker.py       # Car tracking across frames
│   ├── coordinate_crossing_detector.py  # Detect when car crosses left/right coordinates
│   └── speed_calculator.py  # Speed calculation logic
├── cli/
│   ├── __init__.py
│   └── main.py              # CLI entry point and command handling
└── lib/
    ├── __init__.py
    └── logging_config.py    # Structured logging setup

tests/
├── contract/
│   └── test_cli_interface.py  # CLI contract tests
├── integration/
│   ├── test_end_to_end.py     # Full pipeline integration tests
│   └── test_video_processing.py  # Video processing integration
└── unit/
    ├── test_config.py
    ├── test_detector.py
    ├── test_tracker.py
    ├── test_speed_calculator.py
    └── test_coordinate_crossing.py
```

**Structure Decision**: Single project structure chosen as this is a CLI application. Modules are organized by responsibility: models for data structures, services for business logic, cli for user interface, and lib for shared utilities. This aligns with Constitution Principle IV (Modular Video Processing) by clearly separating concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all constitution gates pass.
