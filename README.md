# Car Speed Detection from Video

A CLI application that processes MP4 video files to detect cars moving left-to-right, tracks when they cross predefined measurement coordinates, and calculates speed in km/h based on frame count and known distance.

## Features

- **Car Detection**: Uses YOLO (You Only Look Once) for accurate car detection
- **Speed Calculation**: Calculates car speed based on frame count and real-world distance
- **CLI Interface**: Fully command-line based with multiple output formats (text, JSON, CSV)
- **Modular Architecture**: Separated concerns for video processing, detection, tracking, and calculation
- **Accurate Measurements**: Validated against ground truth data with ±5% accuracy target

## Requirements

- Python 3.11 or higher
- OpenCV 4.8+
- YOLO (ultralytics)
- See `requirements.txt` for complete dependency list

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

1. Create a configuration file (`config.yaml`):
```yaml
left_coordinate: 100   # X coordinate in pixels for left measurement line
right_coordinate: 500  # X coordinate in pixels for right measurement line
distance: 200         # Real-world distance in centimeters between coordinates
fps: 30               # Frames per second of the video
```

2. Run the detection:
```bash
car-speed-detection video.mp4 config.yaml
```

## Usage

```bash
car-speed-detection <video-file> <config-file> [OPTIONS]
```

### Options

- `--output-format` / `-f`: Output format (text, json, csv) - default: text
- `--verbose` / `-v`: Enable verbose logging
- `--log-file` / `-l`: Path to write structured log file
- `--confidence-threshold` / `-c`: Minimum confidence for detection (0.0-1.0) - default: 0.5

### Examples

```bash
# Basic usage
car-speed-detection video.mp4 config.yaml

# JSON output
car-speed-detection video.mp4 config.yaml --output-format json

# Verbose with log file
car-speed-detection video.mp4 config.yaml --verbose --log-file processing.log
```

## Project Structure

```
src/
├── models/          # Data models (Configuration, DetectionResult, etc.)
├── services/        # Business logic (video processing, detection, tracking)
├── cli/             # CLI interface
└── lib/             # Shared utilities (logging, exceptions)

tests/
├── contract/        # CLI contract tests
├── integration/     # End-to-end tests
└── unit/            # Unit tests
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

This project follows TDD (Test-Driven Development) principles. All features must have tests written first.

## License

[Add license information]

## Contributing

[Add contributing guidelines]

