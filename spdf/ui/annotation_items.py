"""
Interactive Graphics Items for Spdf Canvas Annotations.
Provides live interactive elements on the PDF canvas for text overlays,
freehand drawings, highlights, sticky notes, signatures, and redactions.
"""

from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsPathItem,
    QGraphicsPixmapItem, QGraphicsTextItem, QInputDialog, QMenu
)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPainterPath, QCursor
)
from PySide6.QtCore import Qt, QRectF, QPointF
from spdf.config import Colors
from spdf.icons import get_pixmap
import io


class AnnotationBase:
    """Base mixin for annotation serialization."""
    page_idx: int = 0
    kind: str = "base"

    def to_dict(self) -> dict:
        raise NotImplementedError


class HighlightItem(QGraphicsRectItem, AnnotationBase):
    """Semi-transparent highlighter box."""
    def __init__(self, rect: QRectF, color_hex: str = Colors.ANNOT_HIGHLIGHT, page_idx: int = 0, parent=None):
        super().__init__(rect, parent)
        self.page_idx = page_idx
        self.kind = "highlight"
        self.color_hex = color_hex
        
        c = QColor(color_hex)
        c.setAlpha(95)  # semi-transparent highlight
        self.setBrush(QBrush(c))
        self.setPen(QPen(Qt.NoPen))
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

    def to_dict(self) -> dict:
        r = self.rect()
        p = self.pos()
        return {
            "kind": "highlight",
            "x": r.x() + p.x(),
            "y": r.y() + p.y(),
            "w": r.width(),
            "h": r.height(),
            "color": self.color_hex
        }


class UnderlineItem(QGraphicsRectItem, AnnotationBase):
    """Underline stroke annotation."""
    def __init__(self, rect: QRectF, color_hex: str = Colors.ANNOT_UNDERLINE, page_idx: int = 0, parent=None):
        super().__init__(rect, parent)
        self.page_idx = page_idx
        self.kind = "underline"
        self.color_hex = color_hex
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(QColor(self.color_hex), 2.0)
        painter.setPen(pen)
        r = self.rect()
        painter.drawLine(int(r.left()), int(r.bottom()), int(r.right()), int(r.bottom()))

    def to_dict(self) -> dict:
        r = self.rect()
        p = self.pos()
        return {
            "kind": "underline",
            "x": r.x() + p.x(),
            "y": r.y() + p.y(),
            "w": r.width(),
            "h": r.height(),
            "color": self.color_hex
        }


class StrikethroughItem(QGraphicsRectItem, AnnotationBase):
    """Strikethrough stroke annotation."""
    def __init__(self, rect: QRectF, color_hex: str = Colors.ANNOT_STRIKETHROUGH, page_idx: int = 0, parent=None):
        super().__init__(rect, parent)
        self.page_idx = page_idx
        self.kind = "strikethrough"
        self.color_hex = color_hex
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(QColor(self.color_hex), 2.0)
        painter.setPen(pen)
        r = self.rect()
        mid_y = int(r.top() + r.height() / 2.0)
        painter.drawLine(int(r.left()), mid_y, int(r.right()), mid_y)

    def to_dict(self) -> dict:
        r = self.rect()
        p = self.pos()
        return {
            "kind": "strikethrough",
            "x": r.x() + p.x(),
            "y": r.y() + p.y(),
            "w": r.width(),
            "h": r.height(),
            "color": self.color_hex
        }


class InkItem(QGraphicsPathItem, AnnotationBase):
    """Freehand pen/pencil drawing path."""
    def __init__(self, path: QPainterPath, raw_points: list, color_hex: str = Colors.ANNOT_INK,
                 stroke_width: float = 2.5, page_idx: int = 0, parent=None):
        super().__init__(path, parent)
        self.page_idx = page_idx
        self.kind = "ink"
        self.raw_points = raw_points
        self.color_hex = color_hex
        self.stroke_width = stroke_width

        pen = QPen(QColor(color_hex), stroke_width)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)
        self.setFlags(QGraphicsItem.ItemIsSelectable)

    def to_dict(self) -> dict:
        return {
            "kind": "ink",
            "points": self.raw_points,
            "width": self.stroke_width,
            "color": self.color_hex
        }


class DraggableTextItem(QGraphicsTextItem, AnnotationBase):
    """Movable and in-place editable text overlay."""
    def __init__(self, text: str, pos: QPointF, font_size: int = 14,
                 color_hex: str = Colors.ANNOT_TEXT, page_idx: int = 0, parent=None):
        super().__init__(text, parent)
        self.page_idx = page_idx
        self.kind = "text"
        self.font_size = font_size
        self.color_hex = color_hex
        
        self.setPos(pos)
        self.setFont(QFont("Helvetica", font_size))
        self.setDefaultTextColor(QColor(color_hex))
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def to_dict(self) -> dict:
        p = self.pos()
        rect = self.boundingRect()
        return {
            "kind": "text",
            "x": p.x(),
            "y": p.y(),
            "w": max(60.0, rect.width()),
            "h": max(24.0, rect.height()),
            "text": self.toPlainText(),
            "font_size": self.font_size,
            "color": self.color_hex
        }


class StickyNoteItem(QGraphicsItem, AnnotationBase):
    """Interactive Sticky Note icon with click-to-edit comment."""
    def __init__(self, pos: QPointF, text: str = "Sticky Note",
                 color_hex: str = Colors.ANNOT_NOTE, page_idx: int = 0, parent=None):
        super().__init__(parent)
        self.page_idx = page_idx
        self.kind = "note"
        self.comment_text = text
        self.color_hex = color_hex
        self.setPos(pos)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.icon_pixmap = get_pixmap("note", color=color_hex, size=24)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip(f"Sticky Note: {text}\n(Double click to edit)")

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 24, 24)

    def paint(self, painter: QPainter, option, widget=None):
        painter.drawPixmap(0, 0, self.icon_pixmap)

    def mouseDoubleClickEvent(self, event):
        text, ok = QInputDialog.getMultiLineText(
            None, "Sticky Note Comment", "Edit comment text:", self.comment_text
        )
        if ok and text:
            self.comment_text = text
            self.setToolTip(f"Sticky Note: {text}\n(Double click to edit)")
        super().mouseDoubleClickEvent(event)

    def to_dict(self) -> dict:
        p = self.pos()
        return {
            "kind": "note",
            "x": p.x(),
            "y": p.y(),
            "text": self.comment_text,
            "color": self.color_hex
        }


class RedactionItem(QGraphicsRectItem, AnnotationBase):
    """Blackout redaction area with [REDACTED] label and hash preview."""
    def __init__(self, rect: QRectF, page_idx: int = 0, parent=None):
        super().__init__(rect, parent)
        self.page_idx = page_idx
        self.kind = "redact"
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setPen(QPen(QColor(Colors.ACCENT_CRIMSON), 1.5, Qt.DashLine))
        self.setBrush(QBrush(QColor(20, 20, 20, 220)))

    def paint(self, painter: QPainter, option, widget=None):
        super().paint(painter, option, widget)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Helvetica", 9, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "[REDACTED]")

    def to_dict(self) -> dict:
        r = self.rect()
        p = self.pos()
        return {
            "kind": "redact",
            "x": r.x() + p.x(),
            "y": r.y() + p.y(),
            "w": r.width(),
            "h": r.height()
        }


class StampImageItem(QGraphicsPixmapItem, AnnotationBase):
    """Movable stamp or signature image item."""
    def __init__(self, pixmap, img_bytes: bytes, pos: QPointF, page_idx: int = 0, parent=None):
        super().__init__(pixmap, parent)
        self.page_idx = page_idx
        self.kind = "image"
        self.img_bytes = img_bytes
        self.setPos(pos)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def to_dict(self) -> dict:
        p = self.pos()
        r = self.boundingRect()
        return {
            "kind": "image",
            "x": p.x(),
            "y": p.y(),
            "w": r.width(),
            "h": r.height(),
            "image_bytes": self.img_bytes
        }


class SearchHighlightItem(QGraphicsRectItem):
    """Glow highlight for active search matches."""
    def __init__(self, rect: QRectF, is_current: bool = False, parent=None):
        super().__init__(rect, parent)
        fill_color = QColor(Colors.ACCENT_GOLD)
        fill_color.setAlpha(160 if is_current else 80)
        self.setBrush(QBrush(fill_color))
        border_pen = QPen(QColor(Colors.ACCENT_GOLD), 2.0 if is_current else 1.0)
        self.setPen(border_pen)
        self.setZValue(100)
