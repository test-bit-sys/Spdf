"""
Comment & Annotate Panel for Spdf.
Provides controls for Highlights, Underlines, Strikethroughs, Sticky Notes,
Freehand Ink drawing, color palette selections, and stroke thicknesses.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QButtonGroup, QMessageBox
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal
from spdf.models.document import PDFDocument
from spdf.config import Colors, ToolMode
from spdf.icons import get_icon


class CommentPanel(QWidget):
    """Annotation tools and property adjustments panel."""
    toolRequested = Signal(object)      # ToolMode
    colorChanged = Signal(str)          # hex color
    strokeWidthChanged = Signal(float)  # stroke width
    fontSizeChanged = Signal(int)       # font size
    annotationsBaked = Signal()

    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)

        lbl_title = QLabel("Comment & Annotate", self)
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {Colors.ACCENT_GOLD}; margin-bottom: 4px;")
        layout.addWidget(lbl_title)

        # Tool group buttons
        self.btn_highlight = QPushButton("Highlight Text / Area", self)
        self.btn_highlight.setIcon(get_icon("highlight", color=Colors.ANNOT_HIGHLIGHT, size=18))
        self.btn_highlight.setCheckable(True)
        self.btn_highlight.clicked.connect(lambda: self.toolRequested.emit(ToolMode.HIGHLIGHT))
        layout.addWidget(self.btn_highlight)

        self.btn_underline = QPushButton("Underline", self)
        self.btn_underline.setIcon(get_icon("underline", color=Colors.ANNOT_UNDERLINE, size=18))
        self.btn_underline.setCheckable(True)
        self.btn_underline.clicked.connect(lambda: self.toolRequested.emit(ToolMode.UNDERLINE))
        layout.addWidget(self.btn_underline)

        self.btn_strike = QPushButton("Strikethrough", self)
        self.btn_strike.setIcon(get_icon("strikethrough", color=Colors.ANNOT_STRIKETHROUGH, size=18))
        self.btn_strike.setCheckable(True)
        self.btn_strike.clicked.connect(lambda: self.toolRequested.emit(ToolMode.STRIKETHROUGH))
        layout.addWidget(self.btn_strike)

        self.btn_ink = QPushButton("Freehand Pen (Draw)", self)
        self.btn_ink.setIcon(get_icon("ink", color=Colors.ANNOT_INK, size=18))
        self.btn_ink.setCheckable(True)
        self.btn_ink.clicked.connect(lambda: self.toolRequested.emit(ToolMode.INK))
        layout.addWidget(self.btn_ink)

        self.btn_note = QPushButton("Add Sticky Note", self)
        self.btn_note.setIcon(get_icon("note", color=Colors.ANNOT_NOTE, size=18))
        self.btn_note.setCheckable(True)
        self.btn_note.clicked.connect(lambda: self.toolRequested.emit(ToolMode.STICKY_NOTE))
        layout.addWidget(self.btn_note)

        # Color palette swatches
        lbl_colors = QLabel("Annotation Color:", self)
        lbl_colors.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin-top: 8px;")
        layout.addWidget(lbl_colors)

        swatch_layout = QHBoxLayout()
        swatch_layout.setSpacing(6)
        colors = ["#FFE600", "#E53935", "#1E88E5", "#43A047", "#8E24AA", "#000000"]
        for c_hex in colors:
            btn = QPushButton(self)
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(f"background-color: {c_hex}; border: 1px solid #444444; border-radius: 4px;")
            btn.clicked.connect(lambda checked=False, ch=c_hex: self.colorChanged.emit(ch))
            swatch_layout.addWidget(btn)
        layout.addLayout(swatch_layout)

        # Stroke width slider
        lbl_stroke = QLabel("Stroke Thickness:", self)
        lbl_stroke.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin-top: 6px;")
        layout.addWidget(lbl_stroke)

        self.slider_stroke = QSlider(Qt.Horizontal, self)
        self.slider_stroke.setRange(1, 12)
        self.slider_stroke.setValue(3)
        self.slider_stroke.valueChanged.connect(lambda val: self.strokeWidthChanged.emit(float(val)))
        layout.addWidget(self.slider_stroke)

        # Font size slider
        lbl_font = QLabel("Text Font Size:", self)
        lbl_font.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin-top: 6px;")
        layout.addWidget(lbl_font)

        self.slider_font = QSlider(Qt.Horizontal, self)
        self.slider_font.setRange(8, 48)
        self.slider_font.setValue(14)
        self.slider_font.valueChanged.connect(lambda val: self.fontSizeChanged.emit(val))
        layout.addWidget(self.slider_font)

        # Bake button
        self.btn_bake = QPushButton("Save Annotations to PDF", self)
        self.btn_bake.setObjectName("PrimaryButton")
        self.btn_bake.setIcon(get_icon("save", color="#121212", size=16))
        self.btn_bake.clicked.connect(self._on_bake)
        layout.addWidget(self.btn_bake)

        layout.addStretch()

    def set_document(self, doc: PDFDocument):
        self.doc = doc

    def _on_bake(self):
        if self.doc:
            self.doc.bake_annotations()
            self.annotationsBaked.emit()
            QMessageBox.information(self, "Annotations Saved", "All annotations have been baked into the PDF.")
