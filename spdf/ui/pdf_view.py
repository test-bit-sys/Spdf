"""
Interactive PDF Canvas (QGraphicsView and QGraphicsScene) for Spdf.
Supports continuous page layout, smooth high-DPI rendering, hand panning,
tool overlays (Highlight, Text, Note, Ink, Redaction), search match highlighting,
live annotation syncing, undo/redo, night reading mode, and text selection copying.
"""

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPathItem,
    QApplication, QMenu, QInputDialog, QMessageBox, QGraphicsItem
)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QPainterPath,
    QCursor, QWheelEvent, QMouseEvent, QKeyEvent, QContextMenuEvent, QKeySequence
)
from PySide6.QtCore import (
    Qt, QRectF, QPointF, Signal, QTimer, QSize
)
from spdf.config import (
    Colors, ToolMode, PAGE_SPACING, PAGE_MARGIN,
    DEFAULT_ZOOM, MIN_ZOOM, MAX_ZOOM
)
from spdf.models.document import PDFDocument
from spdf.models.render_worker import AsyncRenderManager
from spdf.ui.page_item import PageGraphicsItem
from spdf.ui.annotation_items import (
    HighlightItem, UnderlineItem, StrikethroughItem,
    InkItem, DraggableTextItem, StickyNoteItem,
    RedactionItem, StampImageItem, SearchHighlightItem
)
from spdf.icons import get_icon
import fitz


class PDFGraphicsView(QGraphicsView):
    """Interactive high-resolution viewport for PDF pages and annotations."""
    pageChanged = Signal(int)       # 0-indexed current visible page
    zoomChanged = Signal(float)     # current zoom factor (e.g. 1.25)
    annotationAdded = Signal(dict)  # emitted when an annotation is added
    statusMessageRequested = Signal(str)

    def __init__(self, doc: PDFDocument, render_mgr: AsyncRenderManager, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.render_mgr = render_mgr
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Configuration & Flags
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, False)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setBackgroundBrush(QBrush(QColor(Colors.BG_WORKSPACE)))

        # Tool & State tracking
        self.tool_mode: ToolMode = ToolMode.HAND
        self.zoom_factor: float = DEFAULT_ZOOM
        self.active_color: str = Colors.ANNOT_HIGHLIGHT
        self.active_stroke_width: float = 2.5
        self.active_font_size: int = 14
        self.active_stamp_pixmap = None
        self.active_stamp_bytes = None

        # Modes & Undo/Redo
        self.invert_colors: bool = False
        self.continuous_mode: bool = True
        self.current_single_page: int = 0
        self.selected_text: str = ""
        self._undo_stack: list = []  # ('ADD' | 'DEL', page_idx, item)
        self._redo_stack: list = []

        # Dragging / Interaction state
        self._is_panning = False
        self._pan_start_pos = QPointF()
        self._drag_start_item_pos = None
        self._active_page_item: PageGraphicsItem = None
        self._temp_rect_item: QGraphicsRectItem = None
        self._ink_points = []
        self._ink_path = QPainterPath()
        self._temp_ink_item = None

        # Items in scene
        self.page_items: list[PageGraphicsItem] = []
        self.search_highlight_items: list[SearchHighlightItem] = []

        # Connect render manager signals
        self.render_mgr.pageReady.connect(self._on_page_pixmap_ready)

        # Connect scroll event throttle
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)

        # Build page scene
        self.rebuild_pages()

    def set_tool_mode(self, mode: ToolMode):
        """Switch active tool mode."""
        self.tool_mode = mode
        if mode == ToolMode.HAND:
            self.setCursor(QCursor(Qt.OpenHandCursor))
            self.setDragMode(QGraphicsView.NoDrag)
        elif mode == ToolMode.SELECT:
            self.setCursor(QCursor(Qt.CrossCursor))
            self.setDragMode(QGraphicsView.NoDrag)
        elif mode in (ToolMode.HIGHLIGHT, ToolMode.UNDERLINE, ToolMode.STRIKETHROUGH, ToolMode.REDACT):
            self.setCursor(QCursor(Qt.CrossCursor))
            self.setDragMode(QGraphicsView.NoDrag)
        elif mode == ToolMode.INK:
            self.setCursor(QCursor(Qt.CrossCursor))
            self.setDragMode(QGraphicsView.NoDrag)
        elif mode == ToolMode.TEXT:
            self.setCursor(QCursor(Qt.IBeamCursor))
            self.setDragMode(QGraphicsView.NoDrag)
        elif mode in (ToolMode.STICKY_NOTE, ToolMode.SIGNATURE, ToolMode.STAMP):
            self.setCursor(QCursor(Qt.PointingHandCursor))
            self.setDragMode(QGraphicsView.NoDrag)

    def toggle_invert_colors(self) -> bool:
        """Toggle night reading / dark document mode."""
        self.invert_colors = not self.invert_colors
        for p in self.page_items:
            p.set_invert_colors(self.invert_colors)
        bg = "#111111" if self.invert_colors else Colors.BG_WORKSPACE
        self.setBackgroundBrush(QBrush(QColor(bg)))
        msg = "Night Reading Mode (Colors Inverted)" if self.invert_colors else "Standard Reading Mode"
        self.statusMessageRequested.emit(msg)
        return self.invert_colors

    def set_continuous_mode(self, continuous: bool):
        """Switch between Continuous Vertical Scroll and Single Page View."""
        if self.continuous_mode != continuous:
            self.continuous_mode = continuous
            cur_p = self.get_most_visible_page()
            self.rebuild_pages()
            self.jump_to_page(cur_p)

    def sync_annotations_to_document(self):
        """Extract all live annotation items from all pages and store in doc.pending_annotations."""
        if not self.doc:
            return
        self.doc.pending_annotations.clear()
        for p in self.page_items:
            annots = p.collect_pending_annotations()
            if annots:
                self.doc.pending_annotations[p.page_idx] = annots

    def delete_selected_annotations(self):
        """Remove any currently selected annotation items from their pages."""
        deleted_count = 0
        for item in list(self.scene.selectedItems()):
            for p in self.page_items:
                if item in p.annotation_items:
                    self._undo_stack.append(("DEL", p.page_idx, item))
                    p.remove_annotation_item(item)
                    deleted_count += 1
                    break
        if deleted_count > 0:
            self._redo_stack.clear()
            self.sync_annotations_to_document()
            self.doc.is_modified = True
            self.statusMessageRequested.emit(f"Deleted {deleted_count} annotation(s)")

    def undo(self):
        """Undo last annotation change."""
        if not self._undo_stack:
            self.statusMessageRequested.emit("Nothing to undo")
            return
        action_type, page_idx, item = self._undo_stack.pop()
        if action_type == "ADD":
            if 0 <= page_idx < len(self.page_items):
                p = self.page_items[page_idx]
                p.remove_annotation_item(item)
                self._redo_stack.append(("ADD", page_idx, item))
                self.sync_annotations_to_document()
                self.doc.is_modified = True
                self.statusMessageRequested.emit("Annotation undone")
        elif action_type == "DEL":
            if 0 <= page_idx < len(self.page_items):
                p = self.page_items[page_idx]
                p.add_annotation_item(item)
                self._redo_stack.append(("DEL", page_idx, item))
                self.sync_annotations_to_document()
                self.doc.is_modified = True
                self.statusMessageRequested.emit("Annotation restored")

    def redo(self):
        """Redo last undone annotation change."""
        if not self._redo_stack:
            self.statusMessageRequested.emit("Nothing to redo")
            return
        action_type, page_idx, item = self._redo_stack.pop()
        if action_type == "ADD":
            if 0 <= page_idx < len(self.page_items):
                p = self.page_items[page_idx]
                p.add_annotation_item(item)
                self._undo_stack.append(("ADD", page_idx, item))
                self.sync_annotations_to_document()
                self.doc.is_modified = True
                self.statusMessageRequested.emit("Annotation redone")
        elif action_type == "DEL":
            if 0 <= page_idx < len(self.page_items):
                p = self.page_items[page_idx]
                p.remove_annotation_item(item)
                self._undo_stack.append(("DEL", page_idx, item))
                self.sync_annotations_to_document()
                self.doc.is_modified = True
                self.statusMessageRequested.emit("Annotation removed")

    def copy_selected_text(self) -> bool:
        """Copy selected text or selected annotation text to clipboard."""
        for item in self.scene.selectedItems():
            if isinstance(item, DraggableTextItem):
                text = item.toPlainText()
                if text:
                    QApplication.clipboard().setText(text)
                    self.statusMessageRequested.emit(f"Copied text to clipboard")
                    return True
            elif isinstance(item, StickyNoteItem):
                text = item.comment_text
                if text:
                    QApplication.clipboard().setText(text)
                    self.statusMessageRequested.emit(f"Copied note to clipboard")
                    return True

        if self.selected_text:
            QApplication.clipboard().setText(self.selected_text)
            self.statusMessageRequested.emit(f"Copied {len(self.selected_text)} characters to clipboard")
            return True

        return False

    def rebuild_pages(self):
        """Reconstruct page items in vertical column centered in scene."""
        self.scene.clear()
        self.page_items.clear()
        self.search_highlight_items.clear()

        if not self.doc or self.doc.is_locked() or self.doc.page_count == 0:
            return

        # Update render manager with latest bytes
        self.render_mgr.set_document_bytes(self.doc.to_bytes())

        max_width = 0.0
        for i in range(self.doc.page_count):
            w, _ = self.doc.get_page_size(i)
            max_width = max(max_width, w)

        y_offset = PAGE_SPACING
        for i in range(self.doc.page_count):
            w, h = self.doc.get_page_size(i)
            x_offset = PAGE_MARGIN + (max_width - w) / 2.0

            p_item = PageGraphicsItem(i, w, h)
            p_item.setPos(x_offset, y_offset)
            p_item.set_invert_colors(self.invert_colors)
            self.scene.addItem(p_item)
            self.page_items.append(p_item)

            y_offset += h + PAGE_SPACING

        scene_w = max_width + (PAGE_MARGIN * 2)
        scene_h = y_offset + PAGE_SPACING
        self.scene.setSceneRect(0, 0, scene_w, scene_h)

        # Trigger rendering of visible pages
        self.update_visible_pages()

    def update_visible_pages(self):
        """Request high-DPI rendering for pages in or near the viewport."""
        if not self.page_items:
            return

        viewport_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        for p_item in self.page_items:
            item_scene_rect = p_item.sceneBoundingRect()
            buffer_rect = viewport_rect.adjusted(0, -300, 0, 300)
            if item_scene_rect.intersects(buffer_rect):
                cached = self.render_mgr.get_cached_pixmap(p_item.page_idx, self.zoom_factor)
                if cached:
                    p_item.set_pixmap(cached)
                else:
                    self.render_mgr.request_page(p_item.page_idx, self.zoom_factor)

    def _on_page_pixmap_ready(self, page_idx: int, zoom: float, pixmap):
        if round(zoom, 2) == round(self.zoom_factor, 2):
            if 0 <= page_idx < len(self.page_items):
                self.page_items[page_idx].set_pixmap(pixmap)

    def _on_scroll(self):
        """Update current page index and load freshly visible pages."""
        self.update_visible_pages()
        current = self.get_most_visible_page()
        if current >= 0:
            self.pageChanged.emit(current)

    def get_most_visible_page(self) -> int:
        """Find which page occupies the most vertical space in viewport."""
        if not self.page_items:
            return 0
        viewport_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        best_page = 0
        max_intersection = -1.0
        for p in self.page_items:
            r = p.sceneBoundingRect()
            inter = r.intersected(viewport_rect)
            area = inter.width() * inter.height()
            if area > max_intersection:
                max_intersection = area
                best_page = p.page_idx
        return best_page

    def jump_to_page(self, page_idx: int):
        """Scroll smoothly to the top of the given page."""
        if 0 <= page_idx < len(self.page_items):
            p_item = self.page_items[page_idx]
            self.centerOn(p_item.pos().x() + p_item.page_width / 2.0, p_item.pos().y() + 20)
            self.pageChanged.emit(page_idx)

    # ==================== ZOOM CONTROLS ====================

    def set_zoom(self, factor: float):
        factor = max(MIN_ZOOM, min(MAX_ZOOM, factor))
        if round(self.zoom_factor, 2) == round(factor, 2):
            return

        self.zoom_factor = factor
        self.resetTransform()
        self.scale(factor, factor)
        self.zoomChanged.emit(factor)
        self.update_visible_pages()

    def zoom_in(self):
        self.set_zoom(self.zoom_factor * 1.25)

    def zoom_out(self):
        self.set_zoom(self.zoom_factor / 1.25)

    def fit_width(self):
        if not self.page_items:
            return
        view_w = self.viewport().width() - (PAGE_MARGIN * 2) - 30
        max_page_w = max(p.page_width for p in self.page_items)
        if max_page_w > 0:
            factor = max(MIN_ZOOM, min(MAX_ZOOM, view_w / max_page_w))
            self.set_zoom(factor)

    def fit_page(self):
        if not self.page_items:
            return
        cur_idx = self.get_most_visible_page()
        p = self.page_items[cur_idx]
        view_w = self.viewport().width() - 40
        view_h = self.viewport().height() - 40
        factor = min(view_w / p.page_width, view_h / p.page_height)
        self.set_zoom(factor)
        self.jump_to_page(cur_idx)

    # ==================== MOUSE & KEY EVENTS ====================

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        scene_pos = self.mapToScene(event.pos())
        target_page = self._find_page_at(scene_pos)

        # Middle mouse button or Hand tool panning
        if event.button() == Qt.MiddleButton or (self.tool_mode == ToolMode.HAND and event.button() == Qt.LeftButton):
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            event.accept()
            return

        if event.button() == Qt.LeftButton and target_page:
            self._active_page_item = target_page
            item_pos = target_page.mapFromScene(scene_pos)
            self._drag_start_item_pos = item_pos

            if self.tool_mode in (ToolMode.HIGHLIGHT, ToolMode.UNDERLINE, ToolMode.STRIKETHROUGH, ToolMode.REDACT, ToolMode.SELECT):
                # Start drawing temporary drag rectangle
                self._temp_rect_item = QGraphicsRectItem(QRectF(item_pos, item_pos), target_page)
                if self.tool_mode == ToolMode.SELECT:
                    pen_color = QColor(Colors.ACCENT_BLUE)
                elif self.tool_mode == ToolMode.REDACT:
                    pen_color = QColor(Colors.ACCENT_CRIMSON)
                else:
                    pen_color = QColor(self.active_color)

                self._temp_rect_item.setPen(QPen(pen_color, 1.5, Qt.DashLine))
                self._temp_rect_item.setBrush(QBrush(QColor(pen_color.red(), pen_color.green(), pen_color.blue(), 50)))

            elif self.tool_mode == ToolMode.INK:
                self._ink_points = [(item_pos.x(), item_pos.y())]
                self._ink_path = QPainterPath(item_pos)
                self._temp_ink_item = QGraphicsPathItem(self._ink_path, target_page)
                pen = QPen(QColor(self.active_color), self.active_stroke_width)
                pen.setCapStyle(Qt.RoundCap)
                self._temp_ink_item.setPen(pen)

            elif self.tool_mode == ToolMode.TEXT:
                text_item = DraggableTextItem("Enter text here", item_pos, self.active_font_size, self.active_color, target_page.page_idx)
                target_page.add_annotation_item(text_item)
                self._undo_stack.append(("ADD", target_page.page_idx, text_item))
                self._redo_stack.clear()
                self.sync_annotations_to_document()
                self.annotationAdded.emit(text_item.to_dict())

            elif self.tool_mode == ToolMode.STICKY_NOTE:
                comment, ok = QInputDialog.getMultiLineText(self, "Add Sticky Note", "Enter note comment:")
                if ok and comment:
                    note_item = StickyNoteItem(item_pos, comment, Colors.ANNOT_NOTE, target_page.page_idx)
                    target_page.add_annotation_item(note_item)
                    self._undo_stack.append(("ADD", target_page.page_idx, note_item))
                    self._redo_stack.clear()
                    self.sync_annotations_to_document()
                    self.annotationAdded.emit(note_item.to_dict())

            elif self.tool_mode in (ToolMode.SIGNATURE, ToolMode.STAMP):
                if self.active_stamp_pixmap and self.active_stamp_bytes:
                    stamp_item = StampImageItem(self.active_stamp_pixmap, self.active_stamp_bytes, item_pos, target_page.page_idx)
                    target_page.add_annotation_item(stamp_item)
                    self._undo_stack.append(("ADD", target_page.page_idx, stamp_item))
                    self._redo_stack.clear()
                    self.sync_annotations_to_document()
                    self.annotationAdded.emit(stamp_item.to_dict())

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            delta = event.pos() - self._pan_start_pos
            self._pan_start_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        scene_pos = self.mapToScene(event.pos())
        if self._active_page_item:
            item_pos = self._active_page_item.mapFromScene(scene_pos)

            if self._temp_rect_item and self._drag_start_item_pos:
                rect = QRectF(self._drag_start_item_pos, item_pos).normalized()
                self._temp_rect_item.setRect(rect)

            elif self._temp_ink_item and self.tool_mode == ToolMode.INK:
                self._ink_points.append((item_pos.x(), item_pos.y()))
                self._ink_path.lineTo(item_pos)
                self._temp_ink_item.setPath(self._ink_path)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_panning:
            self._is_panning = False
            self.setCursor(QCursor(Qt.OpenHandCursor if self.tool_mode == ToolMode.HAND else Qt.ArrowCursor))
            event.accept()
            return

        if self._active_page_item and self._drag_start_item_pos:
            scene_pos = self.mapToScene(event.pos())
            end_item_pos = self._active_page_item.mapFromScene(scene_pos)
            drag_rect = QRectF(self._drag_start_item_pos, end_item_pos).normalized()

            if self._temp_rect_item:
                self.scene.removeItem(self._temp_rect_item)
                self._temp_rect_item = None

                if drag_rect.width() > 5 and drag_rect.height() > 5:
                    page_idx = self._active_page_item.page_idx

                    if self.tool_mode == ToolMode.SELECT:
                        # Extract text from the selected rectangle
                        page = self.doc.get_page(page_idx)
                        if page:
                            clip_r = fitz.Rect(drag_rect.x(), drag_rect.y(), drag_rect.right(), drag_rect.bottom())
                            txt = page.get_text("text", clip=clip_r).strip()
                            self.selected_text = txt
                            if txt:
                                snippet = txt[:40].replace("\n", " ")
                                self.statusMessageRequested.emit(f'Selected: "{snippet}..." (Ctrl+C to copy)')
                    else:
                        if self.tool_mode == ToolMode.HIGHLIGHT:
                            item = HighlightItem(drag_rect, self.active_color, page_idx)
                        elif self.tool_mode == ToolMode.UNDERLINE:
                            item = UnderlineItem(drag_rect, self.active_color, page_idx)
                        elif self.tool_mode == ToolMode.STRIKETHROUGH:
                            item = StrikethroughItem(drag_rect, self.active_color, page_idx)
                        elif self.tool_mode == ToolMode.REDACT:
                            item = RedactionItem(drag_rect, page_idx)
                        else:
                            item = None

                        if item:
                            self._active_page_item.add_annotation_item(item)
                            self._undo_stack.append(("ADD", page_idx, item))
                            self._redo_stack.clear()
                            self.sync_annotations_to_document()
                            self.annotationAdded.emit(item.to_dict())

            elif self._temp_ink_item:
                self.scene.removeItem(self._temp_ink_item)
                self._temp_ink_item = None
                if len(self._ink_points) >= 2:
                    page_idx = self._active_page_item.page_idx
                    ink_item = InkItem(
                        self._ink_path, self._ink_points, self.active_color,
                        self.active_stroke_width, page_idx
                    )
                    self._active_page_item.add_annotation_item(ink_item)
                    self._undo_stack.append(("ADD", page_idx, ink_item))
                    self._redo_stack.clear()
                    self.sync_annotations_to_document()
                    self.annotationAdded.emit(ink_item.to_dict())

        self._active_page_item = None
        self._drag_start_item_pos = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.delete_selected_annotations()
            event.accept()
            return
        elif event.key() == Qt.Key_Escape:
            self.scene.clearSelection()
            self.set_tool_mode(ToolMode.HAND)
            event.accept()
            return
        elif event.matches(QKeySequence.Copy) or (event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier):
            if self.copy_selected_text():
                event.accept()
                return
        elif event.matches(QKeySequence.Undo) or (event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier):
            self.undo()
            event.accept()
            return
        elif event.matches(QKeySequence.Redo) or (event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier):
            self.redo()
            event.accept()
            return
        elif event.key() == Qt.Key_PageDown:
            cur = self.get_most_visible_page()
            if cur < len(self.page_items) - 1:
                self.jump_to_page(cur + 1)
            event.accept()
            return
        elif event.key() == Qt.Key_PageUp:
            cur = self.get_most_visible_page()
            if cur > 0:
                self.jump_to_page(cur - 1)
            event.accept()
            return
        super().keyPressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        item = self.itemAt(event.pos())
        menu = QMenu(self)

        # Check if right-clicked on an annotation item
        target_annot = None
        curr = item
        while curr:
            for p in self.page_items:
                if curr in p.annotation_items:
                    target_annot = curr
                    break
            if target_annot:
                break
            curr = curr.parentItem()

        if target_annot:
            target_annot.setSelected(True)
            act_del = menu.addAction(get_icon("delete", color=Colors.ACCENT_CRIMSON), "Delete Annotation")
            act_copy = menu.addAction(get_icon("copy"), "Copy Content")
            menu.addSeparator()
            act_front = menu.addAction("Bring to Front")
            act_back = menu.addAction("Send to Back")

            action = menu.exec_(event.globalPos())
            if action == act_del:
                self.delete_selected_annotations()
            elif action == act_copy:
                self.copy_selected_text()
            elif action == act_front:
                target_annot.setZValue(target_annot.zValue() + 1)
            elif action == act_back:
                target_annot.setZValue(max(1, target_annot.zValue() - 1))
            event.accept()
            return

        # General Canvas context menu
        act_hand = menu.addAction(get_icon("hand"), "Hand Tool (Pan)")
        act_select = menu.addAction(get_icon("select"), "Select Tool")
        menu.addSeparator()
        act_zin = menu.addAction(get_icon("zoom_in"), "Zoom In")
        act_zout = menu.addAction(get_icon("zoom_out"), "Zoom Out")
        act_fit_w = menu.addAction(get_icon("fit_width"), "Fit to Width")
        act_fit_p = menu.addAction(get_icon("fit_page"), "Fit to Page")
        menu.addSeparator()
        night_title = "Normal Reading Mode (Day)" if self.invert_colors else "Invert Colors (Night Reading)"
        act_invert = menu.addAction(get_icon("night_mode"), night_title)

        action = menu.exec_(event.globalPos())
        if action == act_hand:
            self.set_tool_mode(ToolMode.HAND)
        elif action == act_select:
            self.set_tool_mode(ToolMode.SELECT)
        elif action == act_zin:
            self.zoom_in()
        elif action == act_zout:
            self.zoom_out()
        elif action == act_fit_w:
            self.fit_width()
        elif action == act_fit_p:
            self.fit_page()
        elif action == act_invert:
            self.toggle_invert_colors()

        event.accept()

    def _find_page_at(self, scene_pos: QPointF) -> PageGraphicsItem:
        for p in self.page_items:
            if p.sceneBoundingRect().contains(scene_pos):
                return p
        return None

    # ==================== SEARCH HIGHLIGHTING ====================

    def display_search_matches(self, matches: list, active_idx: int = 0):
        """Clear previous search highlights and place yellow glowing markers."""
        for h in self.search_highlight_items:
            if h.scene():
                self.scene.removeItem(h)
        self.search_highlight_items.clear()

        for idx, match in enumerate(matches):
            p_idx = match["page"]
            if 0 <= p_idx < len(self.page_items):
                p_item = self.page_items[p_idx]
                r: fitz.Rect = match["rect"]
                qrect = QRectF(r.x0, r.y0, r.width, r.height)
                is_curr = (idx == active_idx)
                high_item = SearchHighlightItem(qrect, is_current=is_curr, parent=p_item)
                self.search_highlight_items.append(high_item)

                if is_curr:
                    self.jump_to_page(p_idx)
                    match_scene_pos = p_item.mapToScene(qrect.center())
                    self.centerOn(match_scene_pos)
