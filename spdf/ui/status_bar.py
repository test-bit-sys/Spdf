"""
Status Bar Component for Spdf.
Displays document dimensions, current zoom level, file size, and page counts.
"""

from PySide6.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from spdf.config import Colors
from spdf.utils.helpers import format_page_dimensions


class SpdfStatusBar(QStatusBar):
    """High-density bottom status bar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizeGripEnabled(False)
        self.setStyleSheet(f"background-color: #141414; border-top: 1px solid {Colors.BORDER_SUBTLE};")

        # Left status / action message
        self.lbl_status = QLabel("Ready", self)
        self.lbl_status.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding-left: 6px;")
        self.addWidget(self.lbl_status, 1)

        # Right permanent metrics container
        self.right_container = QWidget(self)
        right_layout = QHBoxLayout(self.right_container)
        right_layout.setContentsMargins(0, 0, 6, 0)
        right_layout.setSpacing(16)

        # Page Dimensions
        self.lbl_dimensions = QLabel("0.0 × 0.0 in", self)
        self.lbl_dimensions.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        right_layout.addWidget(self.lbl_dimensions)

        # File Size
        self.lbl_filesize = QLabel("0 B", self)
        self.lbl_filesize.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        right_layout.addWidget(self.lbl_filesize)

        # Zoom level
        self.lbl_zoom = QLabel("100%", self)
        self.lbl_zoom.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: bold;")
        right_layout.addWidget(self.lbl_zoom)

        # Page counter
        self.lbl_pages = QLabel("Page 1 of 1", self)
        self.lbl_pages.setStyleSheet(f"color: {Colors.ACCENT_GOLD}; font-weight: bold;")
        right_layout.addWidget(self.lbl_pages)

        self.addPermanentWidget(self.right_container)

    def set_status_message(self, text: str):
        self.lbl_status.setText(text)

    def update_metrics(self, current_page: int, total_pages: int, width_pt: float, height_pt: float,
                       file_size_str: str, zoom_factor: float):
        self.lbl_pages.setText(f"Page {current_page + 1} of {max(1, total_pages)}")
        self.lbl_dimensions.setText(format_page_dimensions(width_pt, height_pt))
        self.lbl_filesize.setText(file_size_str)
        self.lbl_zoom.setText(f"{int(round(zoom_factor * 100))}%")
