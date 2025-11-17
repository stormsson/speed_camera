"""Navigation controls widget for frame-by-frame navigation."""

from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLineEdit,
    QLabel,
    QHBoxLayout,
    QVBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator


class NavigationControlsWidget(QWidget):
    """Widget for frame navigation controls."""

    # Signals
    previous_frame_requested = Signal()
    next_frame_requested = Signal()
    frame_number_changed = Signal(int)  # Emitted when frame number is changed via input

    def __init__(self, parent: QWidget = None):
        """Initialize navigation controls widget."""
        super().__init__(parent)

        self._current_frame_number: int = 1
        self._total_frames: int = 0

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Previous Frame button
        self.prev_button = QPushButton("Previous Frame")
        self.prev_button.clicked.connect(self._on_previous_clicked)
        self.prev_button.setEnabled(False)
        layout.addWidget(self.prev_button)

        # Frame number input
        self.frame_input = QLineEdit()
        self.frame_input.setValidator(QIntValidator(1, 999999, self))
        self.frame_input.setMaximumWidth(80)
        self.frame_input.setText("1")
        self.frame_input.returnPressed.connect(self._on_frame_input_entered)
        self.frame_input.editingFinished.connect(self._on_frame_input_entered)
        layout.addWidget(self.frame_input)

        # Frame counter display
        self.frame_counter = QLabel("Frame 1 of 0")
        layout.addWidget(self.frame_counter)

        # Next Frame button
        self.next_button = QPushButton("Next Frame")
        self.next_button.clicked.connect(self._on_next_clicked)
        self.next_button.setEnabled(False)
        layout.addWidget(self.next_button)

        layout.addStretch()

    def _on_previous_clicked(self) -> None:
        """Handle Previous Frame button click."""
        self.previous_frame_requested.emit()

    def _on_next_clicked(self) -> None:
        """Handle Next Frame button click."""
        self.next_frame_requested.emit()

    def _on_frame_input_entered(self) -> None:
        """Handle frame number input."""
        text = self.frame_input.text().strip()
        if not text:
            self.frame_input.setText(str(self._current_frame_number))
            return

        try:
            frame_number = int(text)
            if 1 <= frame_number <= self._total_frames:
                self.frame_number_changed.emit(frame_number)
            else:
                # Invalid frame number - show error and restore
                self._show_input_error(
                    f"Frame number must be between 1 and {self._total_frames}"
                )
                self.frame_input.setText(str(self._current_frame_number))
        except ValueError:
            # Invalid input - restore
            self._show_input_error("Invalid frame number")
            self.frame_input.setText(str(self._current_frame_number))

    def _show_input_error(self, message: str) -> None:
        """Show error message for invalid input."""
        # Highlight input field with red background
        self.frame_input.setStyleSheet("background-color: #ffcccc;")
        # Reset after a short delay (in a real app, you might use a timer)
        # For now, just set it back on next update

    def set_frame_info(self, current_frame: int, total_frames: int) -> None:
        """
        Update frame information.

        Args:
            current_frame: Current frame number (1-indexed)
            total_frames: Total number of frames
        """
        self._current_frame_number = current_frame
        self._total_frames = total_frames

        # Update frame counter
        self.frame_counter.setText(f"Frame {current_frame} of {total_frames}")

        # Update frame input
        self.frame_input.setText(str(current_frame))
        self.frame_input.setStyleSheet("")  # Clear error styling

        # Update button states
        self.prev_button.setEnabled(current_frame > 1)
        self.next_button.setEnabled(current_frame < total_frames)

        # Update validator range
        validator = QIntValidator(1, total_frames, self)
        self.frame_input.setValidator(validator)

    def set_controls_enabled(self, enabled: bool) -> None:
        """
        Enable or disable all navigation controls.

        Args:
            enabled: Whether controls should be enabled
        """
        if hasattr(self, 'prev_button') and self.prev_button:
            self.prev_button.setEnabled(enabled)
        if hasattr(self, 'next_button') and self.next_button:
            self.next_button.setEnabled(enabled)
        if hasattr(self, 'frame_input') and self.frame_input:
            self.frame_input.setEnabled(enabled)

