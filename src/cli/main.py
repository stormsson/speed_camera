"""CLI interface for car speed detection."""

import sys
import time
import json
import csv
import logging
from io import StringIO
from typing import Optional, Tuple, List

import click

from src.models import Configuration, ProcessingResult, VideoMetadata, TrackedCar
from src.services.video_processor import VideoProcessor
from src.services.vehicle_detector import VehicleDetector
from src.services.car_tracker import CarTracker
from src.services.coordinate_crossing_detector import CoordinateCrossingDetector
from src.services.speed_calculator import SpeedCalculator
from src.services.image_generator import ImageGenerator
from src.lib.exceptions import (
    VideoLoadError,
    InvalidConfigurationError,
    NoCarDetectedError,
    CarNotCrossingBothCoordinatesError,
)
from src.lib.logging_config import setup_logging, get_logger


def process_video(
    video_path: str,
    config_path: str,
    config: Configuration,
    confidence_threshold: float = 0.5,
    return_tracked_cars: bool = False,
    debug: bool = False
) -> Tuple[ProcessingResult, Optional[List[TrackedCar]]]:
    """
    Process video to detect car speed.

    Args:
        video_path: Path to video file
        config_path: Path to configuration file
        config: Configuration object
        confidence_threshold: Detection confidence threshold
        return_tracked_cars: If True, return list of tracked cars for visualization
        debug: If True, generate debug images for each crossing event

    Returns:
        Tuple of (ProcessingResult with speed measurements, optional list of tracked cars)

    Raises:
        VideoLoadError: If video cannot be loaded
        NoCarDetectedError: If no car is detected
        CarNotCrossingBothCoordinatesError: If car doesn't cross both coordinates
    """
    logger = get_logger(__name__)
    start_time = time.time()
    frames_processed = 0
    detections_count = 0
    logs = []

    try:
        # Initialize components
        # Pass config to VideoProcessor for potential resizing
        video_processor = VideoProcessor(video_path, config=config)
        video_metadata = video_processor.get_metadata()
        
        # Get scaled coordinates if video was resized
        scaled_coords = video_processor.get_scaled_coordinates()
        scaled_config = None
        if scaled_coords:
            # Create a temporary config with scaled coordinates for crossing detection
            from src.models.config import Configuration
            scaled_config = Configuration(
                left_coordinate=scaled_coords[0],
                right_coordinate=scaled_coords[1],
                distance=config.distance,  # Distance doesn't change
                fps=config.fps,
                downsize_video=config.downsize_video,
                yolo_model=config.yolo_model,
                yolo_confidence_threshold=config.yolo_confidence_threshold,
            )
            crossing_detector = CoordinateCrossingDetector(scaled_config)
        else:
            crossing_detector = CoordinateCrossingDetector(config)
        
        vehicle_detector = VehicleDetector(confidence_threshold=confidence_threshold)
        car_tracker = CarTracker()
        speed_calculator = SpeedCalculator(config)
        
        # Initialize debug image generator if debug mode is enabled
        debug_image_generator = None
        if debug:
            from src.services.debug_image_generator import DebugImageGenerator
            # Use scaled config if video was resized, otherwise use original config
            debug_config = scaled_config if scaled_config else config
            debug_image_generator = DebugImageGenerator(debug_config)

        # Process frames
        tracked_cars_with_crossings = []
        
        for frame_number, frame in video_processor.iter_frames():
            frames_processed += 1
            frame_one_based = frame_number + 1

            # Detect cars
            detections = vehicle_detector.detect(frame, frame_one_based)
            detections_count += len(detections)

            # Update tracking
            tracked_cars = car_tracker.update(detections, frame_one_based)

            # Check for coordinate crossings
            for tracked_car in tracked_cars:
                crossing_events = crossing_detector.detect_crossings(
                    tracked_car, 
                    frame_one_based,
                    debug=debug,
                    video_processor=video_processor if debug else None,
                    debug_image_generator=debug_image_generator
                )
                
                # If car has crossed both coordinates, mark for speed calculation
                if tracked_car.is_complete() and tracked_car not in tracked_cars_with_crossings:
                    tracked_cars_with_crossings.append(tracked_car)

        video_processor.close()

        # Calculate speeds for all cars that crossed both coordinates
        if not tracked_cars_with_crossings:
            # Check if any cars were detected at all
            if detections_count == 0:
                raise NoCarDetectedError(video_path=video_path)
            else:
                raise CarNotCrossingBothCoordinatesError(video_path=video_path)

        # Calculate speed for each completed car
        speed_measurements = []
        for completed_car in tracked_cars_with_crossings:
            try:
                speed_measurement = speed_calculator.calculate_from_tracked_car(completed_car)
            except ValueError as e:
                logger.error(f"Error calculating speed for car {completed_car.track_id}: {str(e)}", exc_info=True)
                continue
            except Exception as e:
                logger.error(f"Unknown Error calculating speed for car {completed_car.track_id}: {str(e)}", exc_info=True)
                continue
            speed_measurements.append(speed_measurement)

        processing_time = time.time() - start_time

        result = ProcessingResult(
            video_path=video_path,
            config_path=config_path,
            video_metadata=video_metadata,
            config=config,
            speed_measurements=speed_measurements,
            processing_time_seconds=processing_time,
            frames_processed=frames_processed,
            detections_count=detections_count,
            error_message=None,
            logs=logs
        )

        if return_tracked_cars:
            return result, tracked_cars_with_crossings if tracked_cars_with_crossings else None
        return result, None

    except (VideoLoadError, NoCarDetectedError, CarNotCrossingBothCoordinatesError):
        # Re-raise these exceptions
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Processing failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Try to get metadata even on error
        try:
            video_processor = VideoProcessor(video_path, config=config)
            video_metadata = video_processor.get_metadata()
            video_processor.close()
        except Exception:
            video_metadata = VideoMetadata(
                file_path=video_path,
                frame_count=0,
                fps=0.0,
                width=0,
                height=0,
                duration_seconds=0.0
            )

        result = ProcessingResult(
            video_path=video_path,
            config_path=config_path,
            video_metadata=video_metadata,
            config=config,
            speed_measurements=[],
            processing_time_seconds=processing_time,
            frames_processed=frames_processed,
            detections_count=detections_count,
            error_message=error_msg,
            logs=logs
        )
        
        return result, None


def format_text_output(result: ProcessingResult) -> str:
    """Format result as human-readable text."""
    output = []
    output.append("Car Speed Detection Result")
    output.append("=" * 50)
    output.append(f"Video: {result.video_path}")
    output.append(f"Configuration: {result.config_path}")
    output.append("")

    if result.speed_measurements:
        for idx, sm in enumerate(result.speed_measurements, 1):
            if sm.is_valid:
                output.append(f"Car {idx}:")
                output.append(f"  Speed: {sm.speed_kmh:.2f} km/h")
                output.append(f"  Frame Count: {sm.frame_count}")
                output.append(f"  Time: {sm.time_seconds:.2f} seconds")
                output.append(f"  Distance: {sm.distance_meters:.2f} meters")
                output.append(f"  Left Crossing: Frame {sm.left_crossing_frame}")
                output.append(f"  Right Crossing: Frame {sm.right_crossing_frame}")
                output.append("")
    elif result.error_message:
        output.append(f"Error: {result.error_message}")
    else:
        output.append("Error: No valid speed measurement")

    return "\n".join(output)


def format_json_output(result: ProcessingResult) -> str:
    """Format result as JSON."""
    valid_measurements = [sm for sm in result.speed_measurements if sm.is_valid]
    data = {
        "success": len(valid_measurements) > 0,
        "video_path": result.video_path,
        "config_path": result.config_path,
        "processing_time_seconds": result.processing_time_seconds,
        "frames_processed": result.frames_processed,
        "detections_count": result.detections_count,
        "speed_measurements": [
            {
                "speed_kmh": sm.speed_kmh,
                "frame_count": sm.frame_count,
                "time_seconds": sm.time_seconds,
                "distance_meters": sm.distance_meters,
                "left_crossing_frame": sm.left_crossing_frame,
                "right_crossing_frame": sm.right_crossing_frame,
                "track_id": sm.track_id,
                "confidence": sm.confidence,
            }
            for sm in valid_measurements
        ],
    }

    if not valid_measurements:
        data["error"] = result.error_message or "No valid speed measurement"

    return json.dumps(data, indent=2)


def format_csv_output(result: ProcessingResult) -> str:
    """Format result as CSV."""
    output = StringIO()
    fieldnames = [
        "video_path", "config_path", "speed_kmh", "frame_count", "time_seconds",
        "distance_meters", "left_crossing_frame", "right_crossing_frame",
        "track_id", "confidence", "processing_time_seconds", "error"
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    valid_measurements = [sm for sm in result.speed_measurements if sm.is_valid]
    
    if valid_measurements:
        # Write one row per car
        for sm in valid_measurements:
            row = {
                "video_path": result.video_path,
                "config_path": result.config_path,
                "speed_kmh": sm.speed_kmh,
                "frame_count": sm.frame_count,
                "time_seconds": sm.time_seconds,
                "distance_meters": sm.distance_meters,
                "left_crossing_frame": sm.left_crossing_frame,
                "right_crossing_frame": sm.right_crossing_frame,
                "track_id": sm.track_id,
                "confidence": sm.confidence,
                "processing_time_seconds": result.processing_time_seconds,
                "error": "",
            }
            writer.writerow(row)
    else:
        # Write error row if no valid measurements
        row = {
            "video_path": result.video_path,
            "config_path": result.config_path,
            "speed_kmh": "",
            "frame_count": "",
            "time_seconds": "",
            "distance_meters": "",
            "left_crossing_frame": "",
            "right_crossing_frame": "",
            "track_id": "",
            "confidence": "",
            "processing_time_seconds": result.processing_time_seconds,
            "error": result.error_message or "No valid speed measurement",
        }
        writer.writerow(row)
    
    return output.getvalue()


@click.command()
@click.argument("video_file", type=click.Path(exists=True, readable=True))
@click.argument("config_file", type=click.Path(exists=True, readable=True))
@click.option(
    "--output-format", "-f",
    type=click.Choice(["text", "json", "csv"], case_sensitive=False),
    default="text",
    help="Output format (text, json, csv)"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose logging"
)
@click.option(
    "--log-file", "-l",
    type=click.Path(),
    default=None,
    help="Path to log file"
)
@click.option(
    "--confidence-threshold", "-c",
    type=float,
    default=0.5,
    help="Minimum confidence for detection (0.0 to 1.0)"
)
@click.option(
    "--show", "-s",
    is_flag=True,
    default=False,
    help="Generate and save composite image showing car crossing boundaries"
)
@click.option(
    "--debug", "-d",
    is_flag=True,
    default=False,
    help="Generate debug images for each crossing event (saved as crossing_[frame_number].png)"
)
def cli(
    video_file: str,
    config_file: str,
    output_format: str,
    verbose: bool,
    log_file: Optional[str],
    confidence_threshold: float,
    show: bool,
    debug: bool
):
    """
    Detect car speed from video file.

    VIDEO_FILE: Path to MP4 video file
    CONFIG_FILE: Path to YAML configuration file
    """
    # Setup logging
    # Without -v: WARNING and above only. With -v: DEBUG and above
    setup_logging(level=logging.DEBUG if verbose else logging.WARNING, log_file=log_file, verbose=verbose)

    try:
        # Load configuration
        config = Configuration.load_from_yaml(config_file)

        # Validate confidence threshold
        if not 0.0 <= confidence_threshold <= 1.0:
            click.echo(f"Error: confidence-threshold must be between 0.0 and 1.0", err=True)
            sys.exit(1)

        # Process video
        result, tracked_cars = process_video(
            video_file, 
            config_file, 
            config, 
            confidence_threshold,
            return_tracked_cars=show,
            debug=debug
        )

        # Get video path object for output file naming
        from pathlib import Path
        video_path_obj = Path(video_file)
        
        # Generate image if --show flag is set
        if show and result.speed_measurements and tracked_cars:
            try:
                output_image_path = f"{video_path_obj.stem}_speed_result.png"
                
                # Reopen video processor for image generation (with config for resizing if needed)
                video_processor = VideoProcessor(video_file, config=config)
                image_generator = ImageGenerator(config)
                
                image_path = image_generator.generate_multi_car_composite_image(
                    video_processor,
                    tracked_cars,
                    output_image_path
                )
                logger = get_logger(__name__)
                logger.info(f"Image saved to: {image_path}")
                if output_format.lower() == "text":
                    click.echo(f"\nImage saved to: {image_path}")
                
                video_processor.close()
            except Exception as e:
                logger = get_logger(__name__)
                logger.error(f"Failed to generate image: {str(e)}", exc_info=True)
                if verbose:
                    click.echo(f"Warning: Could not generate image: {str(e)}", err=True)

        # Format and output result
        if output_format.lower() == "json":
            output = format_json_output(result)
            click.echo(output)
            # file output to file
            with open(f"{video_path_obj.stem}_output.json", "w") as f:
                f.write(output)
        elif output_format.lower() == "csv":
            output = format_csv_output(result)
            click.echo(output)
            # file output to file
            with open(f"{video_path_obj.stem}_output.csv", "w") as f:
                f.write(output)
        else:  # text
            output = format_text_output(result)
            click.echo(output)

        # Exit code based on success
        valid_measurements = [sm for sm in result.speed_measurements if sm.is_valid]
        if valid_measurements:
            sys.exit(0)
        else:
            sys.exit(1)

    except InvalidConfigurationError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
    except VideoLoadError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
    except NoCarDetectedError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
    except CarNotCrossingBothCoordinatesError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: Processing failed: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()

