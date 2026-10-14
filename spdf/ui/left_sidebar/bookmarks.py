"""
Bookmarks / Table of Contents Component for Spdf.
Parses and displays the hierarchical TOC tree from PDF metadata with click-to-jump navigation.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
)
from PySide6.QtCore import Qt, Signal
from spdf.models.document import PDFDocument
from spdf.icons import get_icon
from spdf.config import Colors


class BookmarksWidget(QWidget):
    """Hierarchical Bookmarks / Table of Contents tree."""
    pageJumpRequested = Signal(int)

    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)

        self.empty_label = QLabel("No bookmarks in this document", self)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; padding: 20px;")
        layout.addWidget(self.empty_label)

        self.refresh_bookmarks()

    def refresh_bookmarks(self):
        """Parse doc.get_toc() and populate the tree hierarchy."""
        self.tree.clear()
        if not self.doc or self.doc.is_locked():
            self.empty_label.show()
            self.tree.hide()
            return

        toc = self.doc.get_toc()
        if not toc:
            self.empty_label.show()
            self.tree.hide()
            return

        self.empty_label.hide()
        self.tree.show()

        # Stack to manage hierarchy: [(level, QTreeWidgetItem)]
        stack = []
        for entry in toc:
            # entry: [level, title, page_number]
            level = entry[0]
            title = entry[1]
            page_num = entry[2]

            item = QTreeWidgetItem([title])
            item.setIcon(0, get_icon("bookmarks", color=Colors.ACCENT_GOLD, size=16))
            item.setData(0, Qt.UserRole, max(0, page_num - 1))

            # Find parent item based on level
            while stack and stack[-1][0] >= level:
                stack.pop()

            if stack:
                parent_item = stack[-1][1]
                parent_item.addChild(item)
            else:
                self.tree.addTopLevelItem(item)

            stack.append((level, item))

        self.tree.expandAll()

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        page_idx = item.data(0, Qt.UserRole)
        if page_idx is not None:
            self.pageJumpRequested.emit(page_idx)
