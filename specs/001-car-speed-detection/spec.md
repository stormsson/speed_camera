# Feature Specification: Car Speed Detection from Video

**Feature Branch**: `001-car-speed-detection`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "Build an application that is able to elaborate mp4 video files. it will need to recognize a car passing by, from left to right, and identify its speed. The car will move horizontally and will first intercept a "left" coordinate that will be the starting measurement point, and then the "right" coordinate. left and right coordinates will be provided in the configuration file. in the configuration there will be a fixed horizontal distance that is the space between the left and right coordinate, so for example the configuration could be something like left_coordinate: 100 (meaning 100px) right_coordinate: 500 ( meaning 500px) distance: 200 (meaning 200 cms) The configuration will also have a fps parameter to identify the camera speed. The software needs to calculate in how many frames the car moves from left_coordinate to right_coordinate and identify the car speed, and provide in output the speed in km/h. this must work all from CLI."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Detect Car Speed from Video (Priority: P1)

A user provides an MP4 video file and a configuration file containing measurement parameters. The system processes the video to detect a car moving from left to right, tracks when it crosses the left and right measurement coordinates, calculates the speed based on the frame count and known distance, and outputs the speed in km/h via the command line.

**Why this priority**: This is the core functionality that delivers the primary value - measuring car speed from video. Without this, the application has no purpose.

**Independent Test**: Can be fully tested by providing a test video with a known car speed (validated with ground truth) and verifying the output matches expected speed within acceptable tolerance. Delivers immediate value as a standalone speed measurement tool.

**Acceptance Scenarios**:

1. **Given** a valid MP4 video file containing a car moving left to right, **When** the user runs the CLI command with video and config file, **Then** the system outputs the detected car speed in km/h
1a. **Given** a video with multiple cars passing sequentially, **When** the system processes the video, **Then** it outputs speed measurements for each car that completes the crossing, continuing to process subsequent cars after each completion
2. **Given** a video where a car crosses both left and right coordinates, **When** the system processes the video, **Then** it correctly identifies the frame when the car's rightmost bounding box edge first crosses the left coordinate and the frame when it crosses the right coordinate
3. **Given** a configuration file with left_coordinate, right_coordinate, distance, and fps parameters, **When** the system calculates speed, **Then** it uses the formula: speed = (distance / time) where time = (frame_count / fps) and outputs in km/h
4. **Given** a video with no car or a car that doesn't cross both coordinates, **When** the system processes the video, **Then** it reports that no valid speed measurement could be determined
5. **Given** a successful speed measurement, **When** the user runs the CLI command with `--show` parameter, **Then** the system generates a composite image showing the car at left and right coordinate crossings side-by-side, with each frame displaying both left_coordinate and right_coordinate vertical bars
6. **Given** multiple cars in a video, **When** the user runs the CLI command with `--show` parameter, **Then** the system generates a composite image with each car's crossing frames displayed one after the other (vertically stacked), showing all cars that completed the crossing

---

### User Story 2 - Configuration File Management (Priority: P2)

A user provides a configuration file that defines the measurement parameters (left coordinate, right coordinate, distance, fps, and optionally downsize_video). The system validates the configuration, loads the parameters, and uses them for speed calculation. If downsize_video is specified, the system resizes the video before processing to optimize performance.

**Why this priority**: Configuration is required for P1 to work, but can be developed and tested independently. This enables flexibility in measurement setup and supports different camera configurations.

**Independent Test**: Can be tested independently by providing various configuration files (valid, invalid, missing fields) and verifying the system correctly parses, validates, and reports errors appropriately.

**Acceptance Scenarios**:

1. **Given** a valid configuration file with all required parameters, **When** the system loads the configuration, **Then** it successfully parses and uses the values for speed calculation
2. **Given** a configuration file with missing required parameters, **When** the system attempts to load it, **Then** it reports a clear error message indicating which parameters are missing
3. **Given** a configuration file with invalid parameter values (e.g., negative coordinates, zero fps), **When** the system validates the configuration, **Then** it reports validation errors with specific parameter names
4. **Given** a configuration file with `downsize_video` parameter, **When** the system processes the video, **Then** it resizes the video width to the specified value before processing, maintaining aspect ratio by scaling height proportionally

---

### Edge Cases

- What happens when multiple cars appear in the video simultaneously?
- How does the system handle a car that moves right to left instead of left to right?
- What happens when a car partially crosses the left coordinate but never reaches the right coordinate?
- How does the system handle videos with poor lighting or low visibility?
- What happens when the video file is corrupted or in an unsupported format?
- How does the system handle a car that stops or reverses direction between coordinates?
- What happens when the fps in the configuration doesn't match the actual video fps?
- How does the system handle videos where the car is partially occluded or not fully visible?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept MP4 video files as input via CLI
- **FR-002**: System MUST accept a configuration file containing left_coordinate (pixels), right_coordinate (pixels), distance (centimeters), and fps (frames per second) parameters
- **FR-003**: System MUST detect cars moving horizontally from left to right in the video
- **FR-004**: System MUST identify the frame when a car first crosses the left_coordinate (crossing occurs when the rightmost edge of the car's bounding box intersects the left_coordinate)
- **FR-005**: System MUST identify the frame when the same car crosses the right_coordinate (crossing occurs when the rightmost edge of the car's bounding box intersects the right_coordinate)
- **FR-006**: System MUST calculate the number of frames between left_coordinate and right_coordinate crossings
- **FR-007**: System MUST calculate car speed using the formula: speed (km/h) = (distance in meters / time in seconds) × 3.6, where time = frame_count / fps
- **FR-008**: System MUST output the calculated speed in km/h via CLI for each car that completes the crossing (output format must support multiple cars: JSON array, CSV multiple rows, text numbered list)
- **FR-009**: System MUST validate configuration file parameters and report errors for invalid or missing values
- **FR-010**: System MUST handle cases where no car is detected or a car doesn't cross both coordinates and report appropriate messages
- **FR-011**: System MUST operate entirely via command-line interface with no GUI dependencies
- **FR-012**: System MUST support an optional `--show` parameter that generates a composite image showing all cars crossing both left and right boundaries. For each car, the image MUST display left and right crossing frames side-by-side with vertical bars indicating the measurement coordinates. Multiple cars MUST be displayed one after the other (vertically stacked) in the composite image
- **FR-013**: System MUST support an optional `downsize_video` configuration parameter (integer, e.g., 480 or 360) that resizes the video width to the specified value before processing, maintaining aspect ratio by scaling height proportionally, to optimize visual recognition performance
- **FR-014**: System MUST process multiple cars sequentially in the video. When a car completes crossing both coordinates and speed is calculated, the system MUST continue processing to detect and measure the next car. Each completed car measurement MUST be included in the output

### Key Entities *(include if feature involves data)*

- **Video File**: Represents an MP4 video file containing footage of cars. Key attributes: file path, format, frame rate, resolution, duration
- **Configuration**: Represents measurement parameters. Key attributes: left_coordinate (pixels), right_coordinate (pixels), distance (centimeters), fps (frames per second), downsize_video (optional integer for target width in pixels)
- **Car Detection**: Represents a detected vehicle in the video. Key attributes: bounding box coordinates, frame number, tracking ID
- **Speed Measurement**: Represents a calculated speed result. Key attributes: speed value (km/h), frame count, time duration, confidence/validity status
- **Processing Result**: Represents the complete processing outcome. Key attributes: list of speed measurements (one per car), video metadata, processing statistics

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully measure car speed from a video file in under 60 seconds from command execution to result output
- **SC-002**: System correctly identifies car speed within ±5% accuracy when tested against videos with known ground truth speeds
- **SC-003**: System successfully processes at least 90% of valid MP4 video files containing clearly visible cars moving left to right
- **SC-004**: System provides clear error messages for 100% of invalid configuration files, specifying which parameters are missing or invalid
- **SC-005**: System handles video files up to 10 minutes in duration without memory exhaustion or performance degradation
- **SC-006**: Users can complete the speed measurement workflow (provide video + config, get result) without requiring any GUI or interactive prompts

## Assumptions

- Video files contain footage from a camera placed perpendicular to the road
- Cars move in a generally horizontal path from left to right
- The left and right coordinates are provided in pixels relative to the video frame dimensions
- The distance parameter represents the real-world horizontal distance between the left and right measurement points in centimeters
- The fps parameter in the configuration matches or represents the actual frame rate of the video
- Multiple cars may appear sequentially in the video, and the system should process all cars that complete the crossing
- The camera position and angle remain constant throughout the video
- Video quality is sufficient for car detection algorithms to identify vehicles

## Clarifications

### Session 2025-01-27

- Q: What should the `--show` parameter image display and where should it be saved? → A: Composite image showing both crossing frames (left and right) side-by-side with vertical bars indicating the boundaries in each frame
- Q: How is a car considered to have crossed a coordinate threshold? → A: The car is considered crossing the threshold from left to right when the rightmost part of the bounding box (x2 coordinate) intersects the coordinate, not the center of the bounding box
- Q: What vertical bars should be displayed in each frame of the --show composite image? → A: Each frame in the composite image must show both vertical bars (left_coordinate and right_coordinate), not just the relevant one for that frame
- Q: Should video resizing maintain aspect ratio when downsize_video is specified? → A: Yes, maintain aspect ratio (scale height proportionally) to avoid distortion
- Q: What is the purpose and format of the downsize_video configuration option? → A: Optional integer parameter (e.g., 480 or 360) that resizes video width to the specified value before processing, maintaining aspect ratio, to optimize visual recognition performance
- Q: How should the system handle multiple cars in a video and what should the output format be? → A: System must process multiple cars sequentially. When a car completes crossing both coordinates, calculate speed and continue processing the next car. Output must be a list/array of speed measurements (one per car). For --show parameter, generate composite image with each car's crossing frames displayed one after the other (vertically stacked)
