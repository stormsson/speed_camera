# Research: Car Detection Process Visualizer

**Feature**: Car Detection Process Visualizer  
**Date**: 2025-01-27

## Research Questions & Findings

### 1. PySide6 GUI Framework for Video Visualization

**Question**: What is the best approach for displaying video frames and overlays in PySide6?

**Decision**: Use QLabel with QPixmap for frame display, QPainter for overlays, and QGraphicsView/QGraphicsScene for advanced rendering if needed.

**Rationale**: 
- QLabel with QPixmap is the simplest approach for displaying video frames
- QPainter allows drawing overlays (lines, bounding boxes) directly on the frame
- QGraphicsView provides more advanced features if needed (zooming, panning) but adds complexity
- OpenCV frames (numpy arrays) can be converted to QPixmap using QImage

**Alternatives Considered**:
- QGraphicsView/QGraphicsScene: More powerful but overkill for simple frame display
- OpenCV's built-in display (cv2.imshow): Not suitable for integrated GUI application
- Matplotlib: Better for static plots, not ideal for interactive video display

**Implementation Notes**:
- Convert OpenCV BGR frames to RGB before displaying (cv2.cvtColor)
- Use QPixmap.fromImage() to convert numpy array to QPixmap
- Overlay drawing can be done by creating a QPixmap copy, drawing on it with QPainter, then displaying

### 2. Integration with Feature 001 Services

**Question**: How should the visualizer integrate with Feature 001's services?

**Decision**: Import and directly use Feature 001's services and models from `src/services/` and `src/models/`.

**Rationale**:
- Feature 001 services are already modular and independently testable
- Direct import maintains consistency and avoids duplication
- Services can be used synchronously for real-time visualization or asynchronously for background processing
- Models are already defined and validated in Feature 001

**Alternatives Considered**:
- API layer: Unnecessary complexity for same-process integration
- Service duplication: Violates DRY principle and creates maintenance burden
- Event-driven architecture: Overkill for GUI application with direct service calls

**Implementation Notes**:
- Import services: `from src.services.car_detector import CarDetector`
- Import models: `from src.models.detection_result import DetectionResult, TrackedCar`
- Services can be instantiated in the GUI application and called from GUI thread or worker thread
- For async processing, use QThread to run detection in background

### 3. Frame-by-Frame Navigation Performance

**Question**: How to efficiently navigate frames without loading entire video into memory?

**Decision**: Use OpenCV's VideoCapture with frame seeking (cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)).

**Rationale**:
- OpenCV VideoCapture supports frame seeking without loading entire video
- Feature 001 already uses VideoCapture, so same approach maintains consistency
- Frame seeking is fast enough for interactive navigation (<0.5s requirement)
- Caching recently viewed frames can improve performance for back/forward navigation

**Alternatives Considered**:
- Load all frames into memory: Not feasible for long videos, violates memory constraints
- Pre-extract all frames to disk: Requires significant disk space and preprocessing time
- Streaming approach: More complex, not needed for frame-by-frame navigation

**Implementation Notes**:
- Use VideoProcessor from Feature 001 for video access
- Implement frame cache (e.g., last 10 frames) for quick back navigation
- Validate frame number before seeking (ensure within video bounds)

### 4. JSON Input and Live Detection Integration

**Question**: How should JSON input and live detection work together?

**Decision**: JSON file is the primary input method. System automatically loads video and config from JSON paths. Live detection runs on-demand when user navigates to frames. JSON speed_measurements are used to highlight known cars and show expected results alongside live detection.

**Rationale**:
- JSON input simplifies workflow (single file to open)
- Live detection on-demand allows users to see the actual detection process
- JSON speed_measurements provide expected results for comparison
- Both live and expected results shown together enable debugging and validation
- Feature 001's services support synchronous execution for frame-by-frame detection

**Alternatives Considered**:
- Pre-computed only: Less flexible, doesn't show live detection process
- Real-time only: Doesn't leverage JSON data for comparison
- Hybrid approach: Best of both worlds - shows live process AND expected results

**Implementation Notes**:
- JSON file contains: video_path, config_path, speed_measurements
- Auto-load video and config from JSON paths on file open
- Extract speed_measurements (track_id, left_crossing_frame, right_crossing_frame) from JSON
- Run live detection on current frame when user navigates (using Feature 001's CarDetector)
- Maintain tracking state across navigation (forward/backward) using Feature 001's CarTracker
- Highlight known cars from JSON (by track_id) alongside live detection results
- Visually distinguish between expected results (from JSON) and live detection results

### 5. Coordinate Overlay Rendering

**Question**: How to render coordinate lines that scale correctly with video resizing?

**Decision**: Render coordinate lines using QPainter on the frame display, scaling coordinates proportionally when downsize_video is used.

**Rationale**:
- QPainter provides precise pixel-level drawing
- Coordinate scaling must match Feature 001's behavior (proportional scaling with downsize_video)
- Overlay rendering should be separate from frame rendering for maintainability
- Lines should be clearly visible (thick, contrasting color) and labeled

**Alternatives Considered**:
- Separate overlay widget: More complex, potential synchronization issues
- Pre-rendered frames with overlays: Requires re-rendering on coordinate changes
- SVG overlays: Overkill for simple line drawing

**Implementation Notes**:
- Get coordinates from Feature 001's Configuration model
- Scale coordinates if downsize_video is set: `scaled_coord = coord * (video_width / original_width)`
- Draw vertical lines using QPainter.drawLine()
- Add text labels using QPainter.drawText()
- Use distinct colors for left (e.g., green) and right (e.g., red) coordinates

### 6. Detection Visualization (Bounding Boxes, Tracking, Crossings)

**Question**: How to visualize detection results (bounding boxes, tracking IDs, crossing events) on video frames?

**Decision**: Use QPainter to draw bounding boxes, tracking ID labels, and crossing event markers on the frame display.

**Rationale**:
- QPainter provides all necessary drawing primitives (rectangles, text, circles)
- Drawing directly on frame maintains pixel accuracy
- Can use different colors for different track IDs
- Crossing events can be marked with special indicators (e.g., circles, arrows)

**Alternatives Considered**:
- Separate overlay layer: More complex, potential performance issues
- Pre-annotated video: Not interactive, requires preprocessing
- HTML5 canvas approach: Not applicable for PySide6 desktop app

**Implementation Notes**:
- Bounding boxes: Draw rectangles using QPainter.drawRect() with coordinates from BoundingBox model
- Tracking IDs: Draw text label near bounding box using QPainter.drawText()
- Confidence scores: Display as text overlay on bounding box
- Crossing events: Draw circle or arrow marker at crossing coordinate
- Use color coding: Different colors for different track IDs, special color for crossing events
- Update visualization as user navigates frames

### 7. GUI Testing Framework for PySide6

**Question**: What testing framework should be used for PySide6 GUI components?

**Decision**: Use pytest-qt for PySide6 widget testing.

**Rationale**:
- pytest-qt is the standard testing framework for PySide6/PyQt applications
- Provides QApplication fixture and widget testing utilities
- Supports testing signal/slot connections
- Integrates well with existing pytest test structure from Feature 001

**Alternatives Considered**:
- Manual GUI testing only: Not sufficient for TDD and regression prevention
- Selenium-like approach: Not applicable for desktop applications
- Unit testing without GUI: Misses integration issues

**Implementation Notes**:
- Install pytest-qt: `pip install pytest-qt`
- Use qtbot fixture for widget interaction testing
- Test signal emissions and slot connections
- Test frame navigation, coordinate overlay rendering, detection visualization
- Mock Feature 001 services for isolated widget testing

### 8. Frame Number Input Validation

**Question**: How to handle frame number input validation in the editable textbox?

**Decision**: Validate input on change/enter: ensure integer, within bounds (1 to total_frames), update display immediately.

**Rationale**:
- Immediate validation provides better UX
- Integer validation prevents invalid input
- Bounds checking prevents seeking to non-existent frames
- Update display immediately on valid input (meets FR-010 requirement)

**Alternatives Considered**:
- Validate only on focus loss: Less responsive, user may not notice invalid input
- Allow out-of-bounds with warning: Confusing, better to prevent invalid input
- Separate validation dialog: Unnecessary complexity

**Implementation Notes**:
- Use QLineEdit with QIntValidator for integer input
- Connect textChanged or editingFinished signal to validation handler
- Show error message or highlight invalid input
- Update video frame display on valid input
- Disable/enable navigation buttons based on current frame position

## Summary

All technical decisions have been made. The visualizer will:
- Use PySide6 with QLabel/QPixmap for frame display and QPainter for overlays
- Directly import and use Feature 001's services and models
- Use OpenCV VideoCapture with frame seeking for navigation
- Support both real-time and pre-computed detection modes
- Render coordinate overlays and detection visualizations using QPainter
- Use pytest-qt for GUI testing
- Validate frame number input with immediate feedback

No blocking technical unknowns remain. Ready to proceed to Phase 1 design.

