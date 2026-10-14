"""
Page Thumbnails Sidebar Component for Spdf.
Displays live miniature previews of all PDF pages with click-to-jump,
drag-and-drop page reordering, and a comprehensive right-click context menu.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QMenu, QFileDialog, QMessageBox, QAbstractItemView
)
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtCore import Qt, Signal, QSize
from spdf.models.document import PDFDocument
from spdf.models.render_worker import AsyncRenderManager
from spdf.icons import get_icon
from spdf.config import Colors


class ThumbnailListWidget(QListWidget):
    """Subclassed QListWidget supporting internal drag-and-drop reordering."""
    orderChanged = Signal(int, int)  # from_index, to_index

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ThumbnailListWidget")
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Snap)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setIconSize(QSize(120, 160))
        self.setGridSize(QSize(160, 205))
        self.setSpacing(8)
        self.setWordWrap(True)
        self._drag_start_row = -1

    def startDrag(self, supportedActions):
        self._drag_start_row = self.currentRow()
        super().startDrag(supportedActions)

    def dropEvent(self, event):
        dest_item = self.itemAt(event.pos())
        dest_row = self.row(dest_item) if dest_item else self.count() - 1
        super().dropEvent(event)
        if self._drag_start_row >= 0 and dest_row >= 0 and self._drag_start_row != dest_row:
            self.orderChanged.emit(self._drag_start_row, dest_row)
        self._drag_start_row = -1


class ThumbnailsWidget(QWidget):
    """Thumbnails container handling rendering, context menus, and page actions."""
    pageJumpRequested = Signal(int)
    documentModified = Signal()

    def __init__(self, doc: PDFDocument, render_mgr: AsyncRenderManager, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.render_mgr = render_mgr

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.list_widget = ThumbnailListWidget(self)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.orderChanged.connect(self._on_order_changed)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)

        if self.render_mgr:
            self.render_mgr.thumbnailReady.connect(self._on_thumbnail_ready)

        self.refresh_thumbnails()

    def set_document(self, doc: PDFDocument, render_mgr: AsyncRenderManager = None):
        """Update active document and render manager."""
        if self.render_mgr:
            try:
                self.render_mgr.thumbnailReady.disconnect(self._on_thumbnail_ready)
            except Exception:
                pass
        self.doc = doc
        self.render_mgr = render_mgr
        if self.render_mgr:
            self.render_mgr.thumbnailReady.connect(self._on_thumbnail_ready)
        self.refresh_thumbnails()

    def refresh_thumbnails(self):
        """Reload thumbnail items for all document pages."""
        self.list_widget.clear()
        if not self.doc or self.doc.is_locked() or not self.render_mgr:
            return

        for idx in range(self.doc.page_count):
            item = QListWidgetItem(f"Page {idx + 1}")
            item.setData(Qt.UserRole, idx)
            item.setSizeHint(QSize(150, 195))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignBottom)
            # Default placeholder pixmap
            pix = self.render_mgr.get_cached_thumbnail(idx)
            if pix:
                item.setIcon(QIcon(pix))
            else:
                blank_pix = QPixmap(120, 160)
                blank_pix.fill(QColor("#252525"))
                item.setIcon(QIcon(blank_pix))
                self.render_mgr.request_thumbnail(idx, target_width=120)
            self.list_widget.addItem(item)

    def _on_thumbnail_ready(self, page_idx: int, pixmap: QPixmap):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == page_idx:
                item.setIcon(QIcon(pixmap))
                break

    def _on_item_clicked(self, item: QListWidgetItem):
        page_idx = item.data(Qt.UserRole)
        self.pageJumpRequested.emit(page_idx)

    def select_page(self, page_idx: int):
        """Highlight active page thumbnail without firing jump signal."""
        self.list_widget.blockSignals(True)
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == page_idx:
                self.list_widget.setCurrentItem(item)
                break
        self.list_widget.blockSignals(False)

    def _on_order_changed(self, from_idx: int, to_idx: int):
        self.doc.move_page(from_idx, to_idx)
        self.documentModified.emit()
        self.refresh_thumbnails()

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        page_idx = item.data(Qt.UserRole)

        menu = QMenu(self)
        
        act_cw = menu.addAction(get_icon("rotate_cw"), "Rotate Clockwise 90°")
        act_ccw = menu.addAction(get_icon("rotate_ccw"), "Rotate Counter-Clockwise 90°")
        menu.addSeparator()
        act_insert = menu.addAction(get_icon("insert"), "Insert Blank Page After")
        act_extract = menu.addAction(get_icon("extract"), "Extract Page to New PDF...")
        menu.addSeparator()
        act_del = menu.addAction(get_icon("delete", color=Colors.ACCENT_CRIMSON), "Delete Page")

        action = menu.exec_(self.list_widget.mapToGlobal(pos))
        if action == act_cw:
            self.doc.rotate_page(page_idx, 90)
            self.documentModified.emit()
            self.refresh_thumbnails()
        elif action == act_ccw:
            self.doc.rotate_page(page_idx, -90)
            self.documentModified.emit()
            self.refresh_thumbnails()
        elif action == act_insert:
            self.doc.insert_blank_page(page_idx + 1)
            self.documentModified.emit()
            self.refresh_thumbnails()
        elif action == act_extract:
            path, _ = QFileDialog.getSaveFileName(self, "Extract Page", f"Page_{page_idx + 1}.pdf", "PDF Files (*.pdf)")
            if path:
                self.doc.extract_pages([page_idx], path)
                QMessageBox.information(self, "Extracted", f"Page {page_idx + 1} extracted successfully.")
        elif action == act_del:
            if self.doc.page_count <= 1:
                QMessageBox.warning(self, "Delete Page", "Cannot delete the only page in the document.")
                return
            confirm = QMessageBox.question(
                self, "Confirm Delete", f"Delete Page {page_idx + 1} permanently?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.doc.delete_page(page_idx)
                self.documentModified.emit()
                self.refresh_thumbnails()
