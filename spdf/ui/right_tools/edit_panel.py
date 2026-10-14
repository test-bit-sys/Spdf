"""
Edit PDF Panel for Spdf.
Provides tools for adding text overlays, image/stamp overlays, and permanent redactions.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QSpinBox, QFileDialog, QMessageBox
)
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap
from PySide6.QtCore import Qt, Signal, QByteArray, QBuffer
from spdf.models.document import PDFDocument
from spdf.config import Colors, ToolMode
from spdf.icons import get_icon


def create_stamp_pixmap(text: str, color_hex: str = "#E53935") -> tuple:
    """Generate a high-res rubber stamp image."""
    pix = QPixmap(240, 80)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing, True)
    
    # Outer double border
    pen = QPen(QColor(color_hex), 3.0)
    painter.setPen(pen)
    painter.drawRoundedRect(4, 4, 232, 72, 8, 8)
    
    pen_inner = QPen(QColor(color_hex), 1.0)
    painter.setPen(pen_inner)
    painter.drawRoundedRect(8, 8, 224, 64, 6, 6)

    # Stamp text
    font = QFont("Helvetica", 18, QFont.Bold)
    font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
    painter.setFont(font)
    painter.drawText(pix.rect(), Qt.AlignCenter, text)
    painter.end()

    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QBuffer.WriteOnly)
    pix.save(buf, "PNG")
    return pix, ba.data()


class EditPanel(QWidget):
    """PDF editing tools (Text, Stamps, Redactions)."""
    toolRequested = Signal(object)       # ToolMode
    stampSelected = Signal(object, bytes)# pixmap, raw_bytes
    redactionsApplied = Signal()

    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)

        lbl_title = QLabel("Edit PDF", self)
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {Colors.ACCENT_GOLD}; margin-bottom: 4px;")
        layout.addWidget(lbl_title)

        # 1. Add Text
        self.btn_text = QPushButton("Add Text Overlay", self)
        self.btn_text.setIcon(get_icon("text", size=18))
        self.btn_text.setCheckable(True)
        self.btn_text.clicked.connect(self._on_add_text)
        layout.addWidget(self.btn_text)

        # 2. Add Stamp / Image section
        lbl_stamp = QLabel("Stamps & Images:", self)
        lbl_stamp.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin-top: 6px;")
        layout.addWidget(lbl_stamp)

        self.combo_stamps = QComboBox(self)
        self.combo_stamps.addItems(["APPROVED", "CONFIDENTIAL", "DRAFT", "VOID"])
        layout.addWidget(self.combo_stamps)

        self.btn_apply_stamp = QPushButton("Place Selected Stamp", self)
        self.btn_apply_stamp.setIcon(get_icon("stamp", size=18))
        self.btn_apply_stamp.clicked.connect(self._on_place_stamp)
        layout.addWidget(self.btn_apply_stamp)

        self.btn_import_img = QPushButton("Insert Image from File...", self)
        self.btn_import_img.setIcon(get_icon("export_image", size=18))
        self.btn_import_img.clicked.connect(self._on_insert_image)
        layout.addWidget(self.btn_import_img)

        # 3. Redactions section
        lbl_redact = QLabel("Sanitization & Redaction:", self)
        lbl_redact.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin-top: 8px;")
        layout.addWidget(lbl_redact)

        self.btn_redact = QPushButton("Mark Area for Redaction", self)
        self.btn_redact.setIcon(get_icon("redact", color=Colors.ACCENT_CRIMSON, size=18))
        self.btn_redact.setCheckable(True)
        self.btn_redact.clicked.connect(self._on_mark_redact)
        layout.addWidget(self.btn_redact)

        self.btn_apply_redact = QPushButton("Apply Redactions Permanently", self)
        self.btn_apply_redact.setObjectName("DangerButton")
        self.btn_apply_redact.setIcon(get_icon("check", color="#FFFFFF", size=16))
        self.btn_apply_redact.clicked.connect(self._on_apply_redactions)
        layout.addWidget(self.btn_apply_redact)

        layout.addStretch()

    def set_document(self, doc: PDFDocument):
        self.doc = doc

    def _on_add_text(self):
        self.toolRequested.emit(ToolMode.TEXT)

    def _on_place_stamp(self):
        stamp_name = self.combo_stamps.currentText()
        color = "#43A047" if stamp_name == "APPROVED" else "#E53935"
        pix, b = create_stamp_pixmap(stamp_name, color)
        self.stampSelected.emit(pix, b)
        self.toolRequested.emit(ToolMode.STAMP)

    def _on_insert_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image to Insert", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            pix = QPixmap(path)
            if not pix.isNull():
                with open(path, "rb") as f:
                    data = f.read()
                scaled = pix.scaled(200, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.stampSelected.emit(scaled, data)
                self.toolRequested.emit(ToolMode.STAMP)

    def _on_mark_redact(self):
        self.toolRequested.emit(ToolMode.REDACT)

    def _on_apply_redactions(self):
        if not self.doc:
            return
        confirm = QMessageBox.warning(
            self, "Apply Redactions",
            "Permanently blackout and erase all marked redactions in the document?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.doc.bake_annotations()
            self.redactionsApplied.emit()
            QMessageBox.information(self, "Redactions Applied", "Document redacted and sanitized successfully.")
