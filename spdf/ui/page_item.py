"""
PageGraphicsItem for rendering individual PDF pages in QGraphicsScene.
Renders white paper surface, subtle drop shadow, high-DPI rasterized content,
and hosts child interactive annotation items.
"""

from PySide6.QtWidgets import QGraphicsItem, QGraphicsDropShadowEffect
from PySide6.QtGui import QPainter, QBrush, QPen, QColor, QPixmap
from PySide6.QtCore import Qt, QRectF, QPointF
from spdf.config import Colors
from spdf.ui.annotation_items import AnnotationBase


class PageGraphicsItem(QGraphicsItem):
    """Represents a single PDF page with drop shadow and rasterized content."""
    def __init__(self, page_idx: int, width: float, height: float, parent=None):
        super().__init__(parent)
        self.page_idx = page_idx
        self.page_width = width
        self.page_height = height
        self._pixmap: QPixmap = QPixmap()
        self._inverted_pixmap: QPixmap = QPixmap()
        self.annotation_items = []
        self.invert_colors: bool = False

        # Optimization flags
        self.setAcceptHoverEvents(True)
        self.setZValue(1)

    def set_invert_colors(self, invert: bool):
        if self.invert_colors != invert:
            self.invert_colors = invert
            self._inverted_pixmap = QPixmap()
            self.update()

    def boundingRect(self) -> QRectF:
        # Include room for drop shadow (8px around)
        return QRectF(-4, -4, self.page_width + 12, self.page_height + 12)

    def page_rect(self) -> QRectF:
        """Exact PDF page bounds."""
        return QRectF(0, 0, self.page_width, self.page_height)

    def set_pixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        self._inverted_pixmap = QPixmap()
        self.update()

    def set_page_size(self, width: float, height: float):
        self.prepareGeometryChange()
        self.page_width = width
        self.page_height = height
        self.update()

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # 1. Subtle drop shadow
        shadow_rect = QRectF(3, 3, self.page_width + 4, self.page_height + 4)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 90))

        # 2. Paper canvas background
        canvas_rect = self.page_rect()
        bg_col = QColor("#1C1C1C") if self.invert_colors else QColor(Colors.PAGE_BG)
        painter.fillRect(canvas_rect, QBrush(bg_col))

        # 3. High-resolution rasterized PDF page image
        if not self._pixmap.isNull():
            if self.invert_colors:
                if self._inverted_pixmap.isNull():
                    img = self._pixmap.toImage()
                    img.invertPixels()
                    self._inverted_pixmap = QPixmap.fromImage(img)
                painter.drawPixmap(canvas_rect.toRect(), self._inverted_pixmap)
            else:
                painter.drawPixmap(canvas_rect.toRect(), self._pixmap)
        else:
            # Placeholder loading shimmer/text
            painter.setPen(QColor("#777777" if self.invert_colors else "#9E9E9E"))
            painter.drawText(canvas_rect, Qt.AlignCenter, f"Loading Page {self.page_idx + 1}...")

        # 4. Subtle 1px border
        border_col = QColor("#444444") if self.invert_colors else QColor(Colors.PAGE_BORDER)
        painter.setPen(QPen(border_col, 1.0))
        painter.drawRect(canvas_rect)

    def add_annotation_item(self, item: QGraphicsItem):
        item.setParentItem(self)
        self.annotation_items.append(item)

    def remove_annotation_item(self, item: QGraphicsItem):
        if item in self.annotation_items:
            self.annotation_items.remove(item)
            if self.scene():
                self.scene().removeItem(item)

    def collect_pending_annotations(self) -> list:
        """Extract serialized annotation data from active items."""
        data = []
        for it in self.annotation_items:
            if isinstance(it, AnnotationBase):
                d = it.to_dict()
                d["page_idx"] = self.page_idx
                data.append(d)
        return data

    def clear_annotations(self):
        for it in list(self.annotation_items):
            if self.scene():
                self.scene().removeItem(it)
        self.annotation_items.clear()
