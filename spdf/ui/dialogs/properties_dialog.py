"""
Document Properties Dialog for Spdf.
Displays metadata, security status, page count, and physical page dimensions.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QFormLayout, QPushButton, QTabWidget, QWidget
)
from PySide6.QtCore import Qt
from spdf.config import Colors
from spdf.models.document import PDFDocument
from spdf.utils.helpers import format_page_dimensions


class PropertiesDialog(QDialog):
    """Document properties and metadata inspector dialog."""
    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.setWindowTitle("Document Properties")
        self.setFixedSize(480, 420)
        self.setStyleSheet(f"background-color: {Colors.BG_PANEL};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        meta = self.doc.doc.metadata if self.doc.doc else {}

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setVerticalSpacing(8)

        def add_row(lbl, val):
            l = QLabel(f"<b>{lbl}:</b>")
            l.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            v = QLabel(str(val or "None"))
            v.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
            v.setTextInteractionFlags(Qt.TextSelectableByMouse)
            form.addRow(l, v)

        add_row("File Name", self.doc.file_name)
        add_row("Location", self.doc.file_path or "In Memory")
        add_row("File Size", self.doc.file_size_str)
        add_row("Total Pages", self.doc.page_count)
        
        if self.doc.page_count > 0:
            w, h = self.doc.get_page_size(0)
            add_row("Page 1 Size", format_page_dimensions(w, h))

        add_row("Title", meta.get("title"))
        add_row("Author", meta.get("author"))
        add_row("Subject", meta.get("subject"))
        add_row("Keywords", meta.get("keywords"))
        add_row("Creator", meta.get("creator"))
        add_row("Producer", meta.get("producer"))
        add_row("Created", meta.get("creationDate"))
        add_row("Modified", meta.get("modDate"))
        add_row("Encrypted", "Yes (Password Protected)" if self.doc._is_encrypted else "No")

        layout.addLayout(form)
        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close", self)
        btn_close.setObjectName("PrimaryButton")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)
