# Research: Car Speed Detection Technology Choices

**Feature**: Car Speed Detection from Video  
**Date**: 2025-01-27  
**Purpose**: Document technology decisions and rationale for implementation

## Technology Decisions

### 1. Python Language and Version

**Decision**: Python 3.11+

**Rationale**: 
- Python has excellent ecosystem for computer vision and video processing
- Strong library support for OpenCV, YOLO, and scientific computing
- CLI development is straightforward with libraries like Click or argparse
- Cross-platform compatibility
- Python 3.11+ provides good performance improvements and modern features

**Alternatives Considered**:
- Python 3.9/3.10: Older versions, less performance optimizations
- Other languages (C++, Rust): More complex development, less ecosystem support for rapid prototyping

### 2. Video Processing Library

**Decision**: OpenCV (cv2) version 4.8+

**Rationale**:
- Industry standard for video processing in Python
- Excellent MP4 support and frame-by-frame extraction
- Efficient memory usage with VideoCapture for streaming frames
- Well-documented and widely used
- Supports various video formats and codecs
- Good performance for frame extraction and basic image operations

**Alternatives Considered**:
- FFmpeg-python: Lower-level, more complex API
- MoviePy: Higher-level but heavier, more suited for video editing
- PyAV: More complex, less commonly used

### 3. Car Detection Model

**Decision**: YOLO (You Only Look Once) - ultralytics YOLOv8 or similar

**Rationale**:
- State-of-the-art object detection with excellent accuracy
- Fast inference speed suitable for video processing
- Pre-trained models available for vehicle detection
- Good balance between accuracy and performance
- Active development and community support
- Can be fine-tuned if needed for specific use cases

**Alternatives Considered**:
- YOLOv5: Older version, less accurate than v8
- Faster R-CNN: More accurate but slower inference
- SSD (Single Shot Detector): Good speed but lower accuracy than YOLO
- Custom trained models: Would require training data and longer development time

**Implementation Notes**:
- Use ultralytics library for easy YOLO integration
- Consider YOLOv8n (nano) for speed or YOLOv8s (small) for better accuracy
- Filter detections to "car" class only
- Set appropriate confidence threshold (e.g., 0.5) configurable via config

### 4. Object Tracking

**Decision**: Simple Intersection over Union (IoU) tracking or DeepSORT

**Rationale**:
- Need to track the same car across frames to identify left/right coordinate crossings
- IoU tracking is simple and effective for single car scenarios
- DeepSORT provides more robust tracking if multiple cars need to be handled
- Start with IoU-based tracking, can upgrade to DeepSORT if needed

**Alternatives Considered**:
- No tracking: Would not work - need to identify same car across frames
- Complex tracking (SORT, ByteTrack): May be overkill for single car scenario

**Implementation Notes**:
- Track cars by matching bounding boxes across frames using IoU
- Maintain tracking ID for each detected car
- Handle tracking loss and re-identification if needed

### 5. Configuration File Format

**Decision**: YAML format

**Rationale**:
- Human-readable and easy to edit
- Supports comments for documentation
- Standard format for configuration files
- Good Python library support (PyYAML)
- Can be validated easily

**Alternatives Considered**:
- JSON: Less readable, no comments
- INI/configparser: Less structured, limited data types
- TOML: Good alternative but less commonly used

**Configuration Structure**:
```yaml
left_coordinate: 100  # pixels
right_coordinate: 500  # pixels
distance: 200         # centimeters
fps: 30               # frames per second
```

### 6. CLI Framework

**Decision**: Click library

**Rationale**:
- Clean, declarative API for CLI commands
- Good argument parsing and validation
- Built-in help generation
- Easy to extend with subcommands if needed
- Better than argparse for complex CLIs

**Alternatives Considered**:
- argparse: Standard library but more verbose
- Typer: Modern alternative, but Click is more established

### 7. Testing Framework

**Decision**: pytest

**Rationale**:
- Industry standard for Python testing
- Excellent fixtures and parametrization support
- Good integration with coverage tools
- Supports test discovery and organization
- Rich assertion introspection

**Alternatives Considered**:
- unittest: Standard library but less features
- nose2: Less actively maintained

### 8. Logging Framework

**Decision**: Python logging module with structured JSON output

**Rationale**:
- Standard library, no dependencies
- Can output structured JSON for observability (Constitution Principle III)
- Configurable log levels
- Can integrate with external log aggregation if needed

**Implementation Notes**:
- Use structured logging format (JSON) for machine parsing
- Include: timestamps, frame numbers, detection confidence, speed calculations
- Log all detections, coordinate crossings, and speed measurements

## Architecture Patterns

### Modular Design (Constitution Principle IV)

**Decision**: Separate modules for:
1. Video ingestion (video_processor.py)
2. Car detection (car_detector.py)
3. Car tracking (car_tracker.py)
4. Coordinate crossing detection (coordinate_crossing_detector.py)
5. Speed calculation (speed_calculator.py)
6. CLI interface (cli/main.py)

**Rationale**: 
- Each module independently testable
- Easy to swap detection algorithms (e.g., different YOLO versions)
- Clear separation of concerns
- Aligns with Constitution Principle IV

### Frame-by-Frame Processing

**Decision**: Process video frame-by-frame without loading entire video into memory

**Rationale**:
- Memory efficient (handles long videos)
- Can process videos larger than available RAM
- Aligns with performance constraints
- Standard approach for video processing

## Performance Considerations

### Frame Processing Speed

**Target**: Process 10-minute video (30 fps = 18,000 frames) in under 60 seconds
**Implies**: ~300 frames/second processing rate

**Optimization Strategies**:
- Use YOLO nano model for faster inference
- Skip frames if needed (process every Nth frame, interpolate)
- Optimize OpenCV operations
- Consider GPU acceleration if available (optional)

### Memory Management

**Strategy**:
- Use OpenCV VideoCapture for streaming (doesn't load entire video)
- Process and discard frames after detection
- Only keep necessary state (tracking information, crossing events)
- Avoid storing all frames in memory

## Accuracy Considerations

### Detection Accuracy

**Strategy**:
- Use pre-trained YOLO model with good vehicle detection accuracy
- Set appropriate confidence threshold (configurable)
- Filter to "car" class only (exclude trucks, buses if needed)
- Handle false positives through tracking consistency

### Speed Calculation Accuracy

**Strategy**:
- Precise frame counting (no frame skipping during measurement period)
- Accurate FPS from configuration (or detect from video metadata)
- Use floating-point precision for time calculations
- Validate against ground truth test videos

## Dependencies Summary

**Core Dependencies**:
- opencv-python >= 4.8.0
- ultralytics (YOLO) >= 8.0.0
- numpy >= 1.24.0
- PyYAML >= 6.0
- click >= 8.1.0

**Development Dependencies**:
- pytest >= 7.4.0
- pytest-cov >= 4.1.0

**Optional**:
- torch (if using GPU acceleration with YOLO)

## Open Questions Resolved

1. **Q**: Which YOLO version to use?
   **A**: YOLOv8 (ultralytics) - best balance of accuracy and speed

2. **Q**: How to handle multiple cars?
   **A**: Track first detected car that crosses both coordinates (per spec assumption)

3. **Q**: Configuration file format?
   **A**: YAML - human-readable, supports comments

4. **Q**: Frame skipping for performance?
   **A**: Not during measurement period (left to right crossing), but can skip frames before detection starts

5. **Q**: GPU acceleration?
   **A**: Optional - will work on CPU, GPU can be used if available for faster processing

