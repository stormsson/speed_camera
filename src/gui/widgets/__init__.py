"""GUI widgets module."""

from src.gui.widgets.video_display import VideoDisplayWidget
from src.gui.widgets.coordinate_overlay import CoordinateOverlayWidget
from src.gui.widgets.navigation_controls import NavigationControlsWidget
from src.gui.widgets.detection_overlay import DetectionOverlayWidget
from src.gui.widgets.debug_panel import DebugPanelWidget

__all__ = [
    "VideoDisplayWidget",
    "CoordinateOverlayWidget",
    "NavigationControlsWidget",
    "DetectionOverlayWidget",
    "DebugPanelWidget",
]
