"""
Interactive Digital Signature Drawing Pad Dialog for Spdf.
Allows users to smoothly draw signatures with mouse or stylus,
clear canvas, adjust stroke thickness, import images, and insert into PDF.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QFileDialog, QWidget
)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QPainterPath, QPixmap, QImage
)
import io
from PySide6.QtCore import Qt, QPointF, QSize, QByteArray, QBuffer
from spdf.config import Colors
from spdf.icons import get_icon


class SignatureCanvas(QWidget):
    """Drawing area for digital signature capture."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(480, 220)
        self.setStyleSheet("background-color: #FFFFFF; border: 2px dashed #444444; border-radius: 6px;")
        self.points = []
        self.paths: list[tuple[QPainterPath, QColor, float]] = []
        self.current_path = None
        self.pen_color = QColor("#111111")
        self.stroke_width = 3.0

    def clear(self):
        self.paths.clear()
        self.current_path = None
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.current_path = QPainterPath(event.pos())
            self.paths.append((self.current_path, self.pen_color, self.stroke_width))
            self.update()

    def mouseMoveEvent(self, event):
        if self.current_path and event.buttons() & Qt.LeftButton:
            self.current_path.lineTo(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        self.current_path = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor("#FFFFFF"))

        # Baseline watermark guide
        painter.setPen(QPen(QColor("#E0E0E0"), 1.0, Qt.DashLine))
        painter.drawLine(30, 160, 450, 160)
        painter.setPen(QColor("#AAAAAA"))
        painter.drawText(35, 155, "Sign above this line")

        # Render paths
        for path, color, width in self.paths:
            pen = QPen(color, width)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)

    def export_pixmap(self) -> QPixmap:
        """Render signature on transparent background cropped cleanly to content."""
        if not self.paths:
            return QPixmap()

        total_rect = None
        for path, color, width in self.paths:
            r = path.boundingRect().adjusted(-width - 6, -width - 6, width + 6, width + 6)
            if total_rect is None:
                total_rect = r
            else:
                total_rect = total_rect.united(r)

        if total_rect is None or total_rect.isEmpty():
            total_rect = QRectF(0, 0, 100, 50)

        full_pixmap = QPixmap(self.size())
        full_pixmap.fill(Qt.transparent)
        painter = QPainter(full_pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        for path, color, width in self.paths:
            pen = QPen(color, width)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)
        painter.end()

        crop_rect = total_rect.toRect().intersected(self.rect())
        if crop_rect.isValid() and not crop_rect.isEmpty():
            return full_pixmap.copy(crop_rect)
        return full_pixmap

    def has_signature(self) -> bool:
        return len(self.paths) > 0


class SignatureDialog(QDialog):
    """Modal dialog for creating, loading, and placing digital signatures."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Signature")
        self.setFixedSize(540, 380)
        self.setStyleSheet(f"background-color: {Colors.BG_PANEL};")

        self.signature_pixmap = None
        self.signature_bytes = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header info
        title_label = QLabel("Draw your digital signature or import an image:", self)
        title_label.setStyleSheet(f"font-weight: bold; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(title_label)

        # Signature Canvas
        self.canvas = SignatureCanvas(self)
        layout.addWidget(self.canvas, alignment=Qt.AlignCenter)

        # Controls row
        ctrl_row = QHBoxLayout()
        
        lbl_thick = QLabel("Thickness:", self)
        ctrl_row.addWidget(lbl_thick)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(1, 8)
        self.slider.setValue(3)
        self.slider.valueChanged.connect(self._on_thickness_changed)
        ctrl_row.addWidget(self.slider)

        # Color choices (Black, Blue, Red)
        lbl_col = QLabel("Ink:", self)
        ctrl_row.addWidget(lbl_col)
        for c_hex in ["#111111", "#0D47A1", "#B71C1C"]:
            c_btn = QPushButton(self)
            c_btn.setFixedSize(20, 20)
            c_btn.setStyleSheet(f"background-color: {c_hex}; border: 1px solid #555555; border-radius: 4px;")
            c_btn.clicked.connect(lambda ch=False, c=c_hex: self._set_pen_color(c))
            ctrl_row.addWidget(c_btn)

        self.btn_clear = QPushButton("Clear", self)
        self.btn_clear.setIcon(get_icon("clear", size=16))
        self.btn_clear.clicked.connect(self.canvas.clear)
        ctrl_row.addWidget(self.btn_clear)

        self.btn_import = QPushButton("Import Image...", self)
        self.btn_import.setIcon(get_icon("open", size=16))
        self.btn_import.clicked.connect(self._import_image)
        ctrl_row.addWidget(self.btn_import)

        layout.addLayout(ctrl_row)

        # Action buttons row
        action_row = QHBoxLayout()
        action_row.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        action_row.addWidget(self.btn_cancel)

        self.btn_apply = QPushButton("Apply Signature", self)
        self.btn_apply.setObjectName("PrimaryButton")
        self.btn_apply.setIcon(get_icon("check", color="#121212", size=16))
        self.btn_apply.clicked.connect(self._apply)
        action_row.addWidget(self.btn_apply)

        layout.addLayout(action_row)

    def _set_pen_color(self, color_hex: str):
        self.canvas.pen_color = QColor(color_hex)

    def _on_thickness_changed(self, val):
        self.canvas.stroke_width = float(val)

    def _import_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Signature Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            pix = QPixmap(path)
            if not pix.isNull():
                self.signature_pixmap = pix.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                with open(path, "rb") as f:
                    self.signature_bytes = f.read()
                self.accept()

    def _apply(self):
        if not self.canvas.has_signature() and not self.signature_pixmap:
            return

        if not self.signature_pixmap:
            self.signature_pixmap = self.canvas.export_pixmap().scaled(
                220, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            ba = QByteArray()
            buf = QBuffer(ba)
            buf.open(QBuffer.WriteOnly)
            self.signature_pixmap.save(buf, "PNG")
            self.signature_bytes = ba.data()

        self.accept()
