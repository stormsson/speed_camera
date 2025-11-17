"""GUI entry point for car detection visualizer."""

import sys
from PySide6.QtWidgets import QApplication

from src.gui.windows.main_window import MainWindow
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


def main() -> int:
    """
    Main entry point for GUI application.

    Returns:
        Exit code
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Car Detection Visualizer")

    # Create and show main window
    window = MainWindow()
    window.show()

    logger.info("GUI application started")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

