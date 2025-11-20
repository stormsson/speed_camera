# Tasks: Car Speed Detection from Video

**Input**: Design documents from `/specs/001-car-speed-detection/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per Constitution Principle II (TDD is NON-NEGOTIABLE). Tests MUST be written first and fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan (src/, tests/, src/models/, src/services/, src/cli/, src/lib/)
- [x] T002 Initialize Python project with dependencies (requirements.txt with opencv-python>=4.8.0, ultralytics>=8.0.0, numpy>=1.24.0, PyYAML>=6.0, click>=8.1.0, pytest>=7.4.0)
- [x] T003 [P] Configure pytest in pytest.ini or pyproject.toml
- [x] T004 [P] Create .gitignore for Python project
- [x] T005 [P] Create README.md with project overview

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create base data models in src/models/__init__.py (export all models)
- [x] T007 [P] Create BoundingBox model in src/models/detection_result.py with attributes (x1, y1, x2, y2, width, height, center_x, center_y) and methods (intersects_x, center_x_coordinate)
- [x] T008 [P] Create DetectionResult model in src/models/detection_result.py with attributes (frame_number, bounding_box, confidence, class_id, class_name)
- [x] T009 [P] Create VideoMetadata model in src/models/detection_result.py with attributes (file_path, frame_count, fps, width, height, duration_seconds)
- [x] T010 [P] Create TrackedCar model in src/models/detection_result.py with attributes (track_id, detections, first_detection_frame, last_detection_frame, left_crossing_frame, right_crossing_frame)
- [x] T011 [P] Create SpeedMeasurement model in src/models/detection_result.py with attributes (speed_kmh, speed_ms, frame_count, time_seconds, distance_meters, left_crossing_frame, right_crossing_frame, track_id, confidence, is_valid)
- [x] T012 [P] Create CoordinateCrossingEvent model in src/models/detection_result.py with attributes (track_id, frame_number, coordinate_type, coordinate_value, vehicle_rightmost_x, confidence)
- [x] T013 [P] Create ProcessingResult model in src/models/detection_result.py with attributes (video_path, config_path, video_metadata, config, speed_measurement, processing_time_seconds, frames_processed, detections_count, error_message, logs)
- [x] T014 Configure structured logging in src/lib/logging_config.py with JSON format output
- [x] T015 Create base error handling classes in src/lib/exceptions.py (VideoLoadError, InvalidConfigurationError, NoCarDetectedError, CarNotCrossingBothCoordinatesError)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 2 - Configuration File Management (Priority: P2)

**Goal**: Load and validate configuration file containing measurement parameters (left_coordinate, right_coordinate, distance, fps)

**Independent Test**: Can be tested independently by providing various configuration files (valid, invalid, missing fields) and verifying the system correctly parses, validates, and reports errors appropriately.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [P] [US2] Unit test for Configuration model validation in tests/unit/test_config.py (test valid config, test missing fields, test invalid values)
- [x] T017 [P] [US2] Unit test for configuration file parsing in tests/unit/test_config.py (test YAML parsing, test file not found, test invalid YAML)

### Implementation for User Story 2

- [x] T018 [US2] Create Configuration model in src/models/config.py with attributes (left_coordinate, right_coordinate, distance, fps) and validation rules
- [x] T019 [US2] Implement configuration file loader in src/models/config.py (load_from_yaml method with file path validation)
- [x] T020 [US2] Implement configuration validation in src/models/config.py (validate all required fields, validate numeric ranges, validate right_coordinate > left_coordinate)
- [x] T021 [US2] Add error handling for invalid configuration in src/models/config.py (raise InvalidConfigurationError with specific error messages)

**Checkpoint**: At this point, User Story 2 should be fully functional and testable independently

---

## Phase 4: User Story 1 - Detect Car Speed from Video (Priority: P1) 🎯 MVP

**Goal**: Process MP4 video file to detect cars, track coordinate crossings, calculate speed, and output result via CLI

**Independent Test**: Can be fully tested by providing a test video with a known car speed (validated with ground truth) and verifying the output matches expected speed within acceptable tolerance.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T022 [P] [US1] Unit test for video processor in tests/unit/test_video_processor.py (test video loading, test frame extraction, test metadata extraction)
- [x] T023 [P] [US1] Unit test for car detector in tests/unit/test_detector.py (test YOLO detection, test confidence filtering, test car class filtering)
- [x] T024 [P] [US1] Unit test for car tracker in tests/unit/test_tracker.py (test IoU tracking, test track ID assignment, test tracking across frames)
- [x] T025 [P] [US1] Unit test for coordinate crossing detector in tests/unit/test_coordinate_crossing.py (test left crossing detection, test right crossing detection, test crossing frame identification)
- [x] T026 [P] [US1] Unit test for speed calculator in tests/unit/test_speed_calculator.py (test speed formula, test unit conversion, test validation)
- [x] T027 [P] [US1] Integration test for end-to-end pipeline in tests/integration/test_end_to_end.py (test full video processing with known ground truth speed)
- [x] T028 [P] [US1] Contract test for CLI interface in tests/contract/test_cli_interface.py (test command arguments, test output formats, test error messages)

### Implementation for User Story 1

- [x] T029 [P] [US1] Implement video processor in src/services/video_processor.py (load video with OpenCV, extract frames, extract metadata)
- [x] T030 [P] [US1] Implement car detector in src/services/car_detector.py (initialize YOLO model, detect cars in frame, filter by class and confidence)
- [x] T031 [US1] Implement car tracker in src/services/car_tracker.py (track cars using IoU matching, assign track IDs, maintain tracking state)
- [x] T032 [US1] Implement coordinate crossing detector in src/services/coordinate_crossing_detector.py (detect when car center crosses left coordinate, detect when car center crosses right coordinate, record crossing frames)
- [x] T033 [US1] Implement speed calculator in src/services/speed_calculator.py (calculate time from frame count and fps, convert distance from cm to meters, calculate speed in km/h using formula: speed_kmh = (distance_meters / time_seconds) × 3.6)
- [x] T034 [US1] Implement main processing pipeline in src/cli/main.py (orchestrate video processing, detection, tracking, crossing detection, speed calculation)
- [x] T035 [US1] Implement CLI interface in src/cli/main.py (Click command with video and config arguments, output format options, verbose and log file options, confidence threshold option)
- [x] T036 [US1] Implement output formatters in src/cli/main.py (text output, JSON output, CSV output)
- [x] T037 [US1] Add error handling for no car detected in src/cli/main.py (catch NoCarDetectedError, output appropriate error message)
- [x] T038 [US1] Add error handling for car not crossing both coordinates in src/cli/main.py (catch CarNotCrossingBothCoordinatesError, output appropriate error message)
- [x] T039 [US1] Add logging for all detections in src/services/car_detector.py (log detection events with timestamp, frame number, confidence)
- [x] T040 [US1] Add logging for coordinate crossings in src/services/coordinate_crossing_detector.py (log crossing events with timestamp, frame number, coordinate type)
- [x] T041 [US1] Add logging for speed calculations in src/services/speed_calculator.py (log speed calculation with all parameters and result)
- [x] T042 [US1] Add performance metrics tracking in src/cli/main.py (track processing time per frame, total processing time, frame count)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. This is the MVP!

---

## Phase 4.5: Visualization Feature (FR-012) - Show Crossing Boundaries

**Goal**: Generate composite image showing car crossing both left and right boundaries side-by-side with vertical bars indicating measurement coordinates

**Independent Test**: Can be tested independently by running the CLI with `--show` parameter on a video with successful speed measurement and verifying the composite image is generated with correct annotations.

### Tests for Visualization Feature ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T051 [P] [US1] Unit test for image generator in tests/unit/test_image_generator.py (test composite image creation, test vertical bar drawing, test bounding box annotation)
- [x] T052 [P] [US1] Contract test for --show parameter in tests/contract/test_cli_interface.py (test --show flag, test image file creation, test image content validation)

### Implementation for Visualization Feature

- [x] T053 [US1] Create image generator service in src/services/image_generator.py (create composite side-by-side image, draw vertical boundary lines, annotate car bounding boxes)
- [x] T054 [US1] Implement frame extraction for crossing events in src/services/image_generator.py (extract left crossing frame, extract right crossing frame from video)
- [x] T055 [US1] Implement annotation drawing in src/services/image_generator.py (draw vertical bars at left/right coordinates, draw car bounding boxes, add labels)
- [x] T056 [US1] Add --show parameter to CLI in src/cli/main.py (add Click option, generate image when flag is set, save image file with auto-generated name)
- [x] T057 [US1] Integrate image generation into processing pipeline in src/cli/main.py (call image generator after successful speed calculation, handle errors gracefully)

**Checkpoint**: At this point, the --show parameter should generate composite images showing car crossings with boundary annotations.

---

## Phase 4.6: Performance Optimization Feature (FR-013) - Video Downsizing

**Goal**: Add optional downsize_video configuration parameter to resize video width before processing, maintaining aspect ratio, to optimize visual recognition performance

**Independent Test**: Can be tested independently by providing a configuration file with downsize_video parameter and verifying the video is resized correctly and coordinates are scaled proportionally.

### Tests for Video Downsizing Feature ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T066 [P] [US2] Unit test for downsize_video configuration in tests/unit/test_config.py (test optional parameter parsing, test validation, test coordinate scaling calculation)
- [x] T067 [P] [US2] Unit test for video resizing in tests/unit/test_video_processor.py (test frame resizing with aspect ratio, test coordinate scaling, test metadata update)

### Implementation for Video Downsizing Feature

- [x] T068 [US2] Add downsize_video optional parameter to Configuration model in src/models/config.py (add Optional[int] field, update validation to require > 0 if present)
- [x] T069 [US2] Update configuration loading in src/models/config.py (parse optional downsize_video from YAML, handle missing parameter gracefully)
- [x] T070 [US2] Implement video resizing in VideoProcessor in src/services/video_processor.py (resize frames to target width maintaining aspect ratio, update metadata with new dimensions)
- [x] T071 [US2] Implement coordinate scaling calculation in src/services/video_processor.py (calculate scale factor, scale left_coordinate and right_coordinate proportionally)
- [x] T072 [US2] Integrate video resizing into processing pipeline in src/cli/main.py (apply resizing before detection if downsize_video is specified, use scaled coordinates)

**Checkpoint**: At this point, the downsize_video parameter should resize videos before processing and scale coordinates proportionally for performance optimization.

---

## Phase 4.7: Multi-Car Processing Feature (FR-014) - Sequential Car Detection

**Goal**: Process multiple cars sequentially in the video, continuing to detect and measure each car after the previous one completes crossing both coordinates

**Independent Test**: Can be tested independently by providing a video with multiple cars passing sequentially and verifying that speed measurements are output for each car that completes the crossing.

### Tests for Multi-Car Processing Feature ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T081 [P] [US1] Unit test for multi-car processing in tests/unit/test_multi_car_processing.py (test sequential car detection, test multiple speed measurements, test continuation after car completion)
- [x] T082 [P] [US1] Unit test for ProcessingResult with multiple measurements in tests/unit/test_detection_result.py (test speed_measurements list, test empty list handling, test single car compatibility)
- [x] T083 [P] [US1] Integration test for multi-car output formats in tests/integration/test_multi_car_output.py (test text output with multiple cars, test JSON array output, test CSV multiple rows)

### Implementation for Multi-Car Processing Feature

- [x] T084 [US1] Update ProcessingResult model in src/models/detection_result.py (change speed_measurement to speed_measurements list, maintain backward compatibility if possible)
- [x] T085 [US1] Update processing pipeline in src/cli/main.py (continue processing after each car completes, collect all completed cars, reset tracking state for next car)
- [x] T086 [US1] Update text output formatter in src/cli/main.py (format multiple speed measurements as numbered list: Car 1, Car 2, etc.)
- [x] T087 [US1] Update JSON output formatter in src/cli/main.py (output speed_measurements as array of objects)
- [x] T088 [US1] Update CSV output formatter in src/cli/main.py (output multiple rows, one per car)
- [x] T089 [US1] Update image generator for multi-car visualization in src/services/image_generator.py (stack car images vertically using cv2.vconcat, label each car section)
- [x] T090 [US1] Implement car completion tracking in src/cli/main.py (track completed cars, reset crossing detector state for next car, handle cars that don't complete)

**Checkpoint**: At this point, the system should process all cars sequentially, output measurements for each, and display them vertically stacked in the visualization image.

---

## Phase 4.8: Fix FR-004/FR-005 - Transition-Based Crossing Detection

**Goal**: Update coordinate crossing detection to use transition-based detection (detect crossing on first frame where rightmost edge transitions from < coordinate to >= coordinate) instead of simple threshold check

**Independent Test**: Can be tested independently by providing test cases with known frame transitions and verifying crossing is detected at the exact transition frame, not after the car has already passed the line.

### Tests for Transition-Based Crossing Detection ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T100 [P] [US1] Update unit test for transition-based left crossing detection in tests/unit/test_coordinate_crossing.py (test crossing detected on transition frame, test no crossing when already past coordinate, test crossing with previous frame state)
- [x] T101 [P] [US1] Update unit test for transition-based right crossing detection in tests/unit/test_coordinate_crossing.py (test crossing detected on transition frame, test no crossing when already past coordinate, test crossing only after left crossing)
- [x] T102 [P] [US1] Add integration test for transition-based crossing accuracy in tests/integration/test_end_to_end.py (test crossing frame accuracy against ground truth, verify transition detection improves timing accuracy)

### Implementation for Transition-Based Crossing Detection

- [x] T103 [US1] Update coordinate crossing detector in src/services/coordinate_crossing_detector.py (check previous frame's rightmost_x to detect transition from < coordinate to >= coordinate for left crossing, check previous frame's rightmost_x to detect transition from < coordinate to >= coordinate for right crossing, handle edge case when car first appears past coordinate)
- [x] T104 [US1] Update crossing detection logic to use previous frame state in src/services/coordinate_crossing_detector.py (access previous detection from tracked_car.detections list, compare previous frame's x2 with current frame's x2, only trigger crossing event on transition)
- [x] T105 [US1] Update logging in src/services/coordinate_crossing_detector.py (log previous frame x2 value, log transition detection criteria, log when crossing is skipped due to no transition)

**Checkpoint**: At this point, crossing detection should accurately identify the exact frame where the car transitions across coordinates, improving speed measurement accuracy.

---

## Phase 4.9: Debug Feature (FR-015) - Generate Debug Images on Crossing Events

**Goal**: Add `--debug` CLI parameter that generates PNG images named `crossing_[frame_number].png` in the project folder for each crossing event, showing bounding box, coordinate lines, and detection criteria text

**Independent Test**: Can be tested independently by running the CLI with `--debug` parameter on a video with crossing events and verifying PNG files are generated with correct annotations and criteria text.

### Tests for Debug Feature ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T110 [P] [US1] Unit test for debug image generator in tests/unit/test_debug_image_generator.py (test PNG file creation, test bounding box drawing, test coordinate line drawing, test criteria text rendering)
- [x] T111 [P] [US1] Contract test for --debug parameter in tests/contract/test_cli_interface.py (test --debug flag, test debug image file creation, test image content validation, test file naming convention)
- [x] T112 [P] [US1] Integration test for debug image generation in tests/integration/test_end_to_end.py (test debug images generated for both left and right crossings, test multiple cars generate separate debug images)

### Implementation for Debug Feature

- [x] T113 [US1] Create debug image generator service in src/services/debug_image_generator.py (create debug image from frame, draw car bounding box with color, draw vertical lines for left_coordinate and right_coordinate, render detection criteria text string)
- [x] T114 [US1] Implement detection criteria text formatting in src/services/debug_image_generator.py (format text as "bounding box X: [coord] - left line coord: [coord]" for left crossing, format text as "bounding box X: [coord] - right line coord: [coord]" for right crossing, include frame number and track ID in text)
- [x] T115 [US1] Implement debug image file saving in src/services/debug_image_generator.py (save PNG file with naming convention `crossing_[frame_number].png`, save to project folder (current working directory), handle file write errors gracefully)
- [x] T116 [US1] Add --debug parameter to CLI in src/cli/main.py (add Click option flag, pass debug flag to processing pipeline, conditionally enable debug image generation)
- [x] T117 [US1] Integrate debug image generation into crossing detection in src/services/coordinate_crossing_detector.py (accept debug flag and video processor, generate debug image when crossing event detected, pass frame and detection data to debug image generator)
- [x] T118 [US1] Update processing pipeline in src/cli/main.py (pass debug flag to coordinate crossing detector, ensure video processor is available for frame extraction during crossing events, handle debug image generation errors without failing main processing)

**Checkpoint**: At this point, the --debug parameter should generate PNG images for each crossing event with bounding boxes, coordinate lines, and detection criteria text, enabling debugging of crossing detection accuracy.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T091 [P] Update README.md with installation instructions, usage examples, and troubleshooting
- [ ] T092 [P] Add docstrings to all modules and functions following Python conventions
- [ ] T093 Code cleanup and refactoring (remove unused imports, improve naming, optimize imports)
- [ ] T094 [P] Add type hints to all functions and classes
- [ ] T095 Performance optimization (profile video processing, optimize frame extraction, optimize detection if needed)
- [ ] T096 [P] Validate quickstart.md examples work correctly
- [ ] T097 Add comprehensive error messages with actionable guidance
- [ ] T098 Ensure all logs follow structured JSON format consistently

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 2 (Phase 3)**: Depends on Foundational completion - Can be developed independently
- **User Story 1 (Phase 4)**: Depends on Foundational completion - Uses Configuration from US2 but can work with minimal config implementation
- **Visualization Feature (Phase 4.5)**: Depends on Phase 4 completion - Extends User Story 1 with image generation
- **Video Downsizing Feature (Phase 4.6)**: Depends on Phase 3 completion - Extends User Story 2 with performance optimization
- **Multi-Car Processing Feature (Phase 4.7)**: Depends on Phase 4 completion - Extends User Story 1 with sequential multi-car processing
- **Transition-Based Crossing Detection (Phase 4.8)**: Depends on Phase 4 completion - Fixes FR-004/FR-005 to improve crossing detection accuracy
- **Debug Feature (Phase 4.9)**: Depends on Phase 4 completion - Implements FR-015 for debugging crossing events
- **Polish (Phase 5)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Ideally uses US2 Configuration model but can proceed with basic config if needed

**Note**: While US2 is P2 and US1 is P1, US2 (Configuration) is actually a prerequisite for US1. However, US2 can be developed and tested independently. For MVP, you can implement a minimal Configuration model in Foundational phase and enhance it in US2.

### Within Each User Story

- Tests (included per TDD requirement) MUST be written and FAIL before implementation
- Models before services
- Services before CLI integration
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational model tasks marked [P] can run in parallel (within Phase 2)
- All test tasks for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Video processor, car detector, and other service implementations marked [P] can be developed in parallel after models are complete

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for video processor in tests/unit/test_video_processor.py"
Task: "Unit test for car detector in tests/unit/test_detector.py"
Task: "Unit test for car tracker in tests/unit/test_tracker.py"
Task: "Unit test for coordinate crossing detector in tests/unit/test_coordinate_crossing.py"
Task: "Unit test for speed calculator in tests/unit/test_speed_calculator.py"

# Launch service implementations in parallel (after models complete):
Task: "Implement video processor in src/services/video_processor.py"
Task: "Implement car detector in src/services/car_detector.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
   - Include minimal Configuration model in Foundational phase
3. Complete Phase 4: User Story 1 (core functionality)
4. **STOP and VALIDATE**: Test User Story 1 independently with known ground truth video
5. Deploy/demo if ready

**Note**: For MVP, you can implement a basic Configuration model in Phase 2 and skip Phase 3 (US2) initially, then enhance configuration handling later.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 2 (Configuration) → Test independently → Validate config handling
3. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
4. Add Polish → Refine and optimize
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 2 (Configuration)
   - Developer B: User Story 1 models and tests
3. After US2 complete:
   - Developer A: User Story 1 services
   - Developer B: User Story 1 CLI integration
4. Stories complete and integrate

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD REQUIRED**: Verify tests fail before implementing (Constitution Principle II)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All detection parameters must be configurable (Constitution Principle I)
- All operations must be logged with structured JSON format (Constitution Principle III)
- Each module must be independently testable (Constitution Principle IV)

