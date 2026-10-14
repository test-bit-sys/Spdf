"""
Left Collapsible Sidebar for Spdf.
Houses Page Thumbnails, Bookmarks (Table of Contents), and Document Search tabs.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Signal
from spdf.models.document import PDFDocument
from spdf.models.render_worker import AsyncRenderManager
from spdf.ui.left_sidebar.thumbnails import ThumbnailsWidget
from spdf.ui.left_sidebar.bookmarks import BookmarksWidget
from spdf.ui.left_sidebar.search_panel import SearchPanel
from spdf.icons import get_icon


class LeftSidebar(QWidget):
    """Container tab widget for left panel features."""
    pageJumpRequested = Signal(int)
    documentModified = Signal()
    matchesUpdated = Signal(list, int)

    def __init__(self, doc: PDFDocument, render_mgr: AsyncRenderManager, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.render_mgr = render_mgr

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget(self)
        self.tabs.setObjectName("SidebarTabs")

        # 1. Thumbnails
        self.thumbnails_tab = ThumbnailsWidget(self.doc, self.render_mgr, self)
        self.thumbnails_tab.pageJumpRequested.connect(self.pageJumpRequested.emit)
        self.thumbnails_tab.documentModified.connect(self.documentModified.emit)
        self.tabs.addTab(self.thumbnails_tab, get_icon("thumbnails", size=16), "Pages")

        # 2. Bookmarks
        self.bookmarks_tab = BookmarksWidget(self.doc, self)
        self.bookmarks_tab.pageJumpRequested.connect(self.pageJumpRequested.emit)
        self.tabs.addTab(self.bookmarks_tab, get_icon("bookmarks", size=16), "Bookmarks")

        # 3. Search
        self.search_tab = SearchPanel(self.doc, self)
        self.search_tab.matchesUpdated.connect(self.matchesUpdated.emit)
        self.tabs.addTab(self.search_tab, get_icon("search", size=16), "Search")

        layout.addWidget(self.tabs)

    def set_document(self, doc: PDFDocument, render_mgr: AsyncRenderManager = None):
        self.doc = doc
        self.render_mgr = render_mgr
        self.thumbnails_tab.set_document(doc, render_mgr)
        self.bookmarks_tab.doc = doc
        self.bookmarks_tab.refresh_bookmarks()
        self.search_tab.set_document(doc)

    def refresh(self):
        self.thumbnails_tab.refresh_thumbnails()
        self.bookmarks_tab.refresh_bookmarks()

    def select_page(self, page_idx: int):
        self.thumbnails_tab.select_page(page_idx)
