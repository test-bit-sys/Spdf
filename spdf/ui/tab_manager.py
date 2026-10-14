"""
Multi-Document Tab Manager for Spdf.
Manages simultaneous open PDF documents in modern multi-document tabs, with modified indicators,
tab closures, and an elegant Home / Empty State screen when no files are open.
"""

from PySide6.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from spdf.models.document import PDFDocument
from spdf.models.render_worker import AsyncRenderManager
from spdf.ui.pdf_view import PDFGraphicsView
from spdf.config import Colors
from spdf.icons import get_icon


class DocumentTab(QWidget):
    """Container for a single open PDF document and its view."""
    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.render_mgr = AsyncRenderManager(self)
        self.view = PDFGraphicsView(self.doc, self.render_mgr, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)


import os
from spdf.utils.helpers import RecentFilesManager, format_file_size


class HomeScreenWidget(QWidget):
    """Welcoming home screen when no PDF is active."""
    openRequested = Signal()
    blankRequested = Signal()
    mergeRequested = Signal()
    fileSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(16)

        # App branding header
        lbl_logo = QLabel("Spdf", self)
        lbl_logo.setStyleSheet(f"font-size: 38px; font-weight: 800; color: {Colors.ACCENT_GOLD}; letter-spacing: 2px;")
        lbl_logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_logo)

        lbl_sub = QLabel("Professional PDF Reader, Editor, and Document Management", self)
        lbl_sub.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; margin-bottom: 10px;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_sub)

        # Action Cards row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        btn_row.setAlignment(Qt.AlignCenter)

        # Card 1: Open PDF
        btn_open = QPushButton("Open File...\n(Ctrl+O)", self)
        btn_open.setObjectName("PrimaryButton")
        btn_open.setIcon(get_icon("open", color="#121212", size=22))
        btn_open.setFixedSize(160, 64)
        btn_open.clicked.connect(self.openRequested.emit)
        btn_row.addWidget(btn_open)

        # Card 2: Create Blank
        btn_new = QPushButton("New Blank PDF\n(Ctrl+N)", self)
        btn_new.setIcon(get_icon("insert", size=22))
        btn_new.setFixedSize(160, 64)
        btn_new.clicked.connect(self.blankRequested.emit)
        btn_row.addWidget(btn_new)

        # Card 3: Merge PDFs
        btn_merge = QPushButton("Merge PDFs...\nCombine Files", self)
        btn_merge.setIcon(get_icon("merge", size=22))
        btn_merge.setFixedSize(160, 64)
        btn_merge.clicked.connect(self.mergeRequested.emit)
        btn_row.addWidget(btn_merge)

        layout.addLayout(btn_row)

        # Recent Files Container
        self.recent_container = QWidget(self)
        self.recent_container.setMaximumWidth(680)
        recent_layout = QVBoxLayout(self.recent_container)
        recent_layout.setContentsMargins(0, 16, 0, 0)
        recent_layout.setSpacing(8)

        recent_header = QHBoxLayout()
        lbl_recent = QLabel("Recent Documents", self)
        lbl_recent.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {Colors.TEXT_PRIMARY};")
        recent_header.addWidget(lbl_recent)
        recent_header.addStretch()

        self.btn_clear_recent = QPushButton("Clear History", self)
        self.btn_clear_recent.setStyleSheet(f"font-size: 11px; padding: 2px 8px; color: {Colors.TEXT_MUTED}; background: transparent; border: none;")
        self.btn_clear_recent.clicked.connect(self._clear_recent)
        recent_header.addWidget(self.btn_clear_recent)
        recent_layout.addLayout(recent_header)

        from PySide6.QtWidgets import QListWidget, QListWidgetItem
        self.recent_list = QListWidget(self)
        self.recent_list.setMaximumHeight(200)
        self.recent_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {Colors.BG_PANEL};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 10px;
                border-radius: 4px;
                border-bottom: 1px solid {Colors.BORDER_SUBTLE};
            }}
            QListWidget::item:hover {{
                background-color: {Colors.BG_HOVER};
            }}
        """)
        self.recent_list.itemClicked.connect(self._on_recent_item_clicked)
        recent_layout.addWidget(self.recent_list)

        self.lbl_no_recent = QLabel("Drag and drop PDF files here, or choose an action above.", self)
        self.lbl_no_recent.setAlignment(Qt.AlignCenter)
        self.lbl_no_recent.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px; padding: 20px;")
        recent_layout.addWidget(self.lbl_no_recent)

        layout.addWidget(self.recent_container, alignment=Qt.AlignCenter)
        self.refresh_recent_files()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_recent_files()

    def refresh_recent_files(self):
        recent = RecentFilesManager.get_recent_files()
        self.recent_list.clear()
        if recent:
            self.recent_list.show()
            self.lbl_no_recent.hide()
            self.btn_clear_recent.show()
            from PySide6.QtWidgets import QListWidgetItem
            for path in recent:
                fname = os.path.basename(path)
                try:
                    fsize = format_file_size(os.path.getsize(path))
                except Exception:
                    fsize = ""
                item = QListWidgetItem(f"  {fname}    ({fsize})\n  {path}")
                item.setIcon(get_icon("properties", color=Colors.ACCENT_GOLD, size=18))
                item.setData(Qt.UserRole, path)
                self.recent_list.addItem(item)
        else:
            self.recent_list.hide()
            self.lbl_no_recent.show()
            self.btn_clear_recent.hide()

    def _on_recent_item_clicked(self, item):
        path = item.data(Qt.UserRole)
        if path and os.path.exists(path):
            self.fileSelected.emit(path)

    def _clear_recent(self):
        RecentFilesManager.clear_recent_files()
        self.refresh_recent_files()


class TabManager(QWidget):
    """Manages document tabs and home screen state."""
    currentDocumentChanged = Signal(object, object)  # doc, view
    allTabsClosed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setObjectName("DocumentTabs")
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tab_widget)

        # Home screen when no tabs open
        self.home_screen = HomeScreenWidget(self)
        layout.addWidget(self.home_screen)
        self.home_screen.hide()

    def count(self) -> int:
        return self.tab_widget.count()

    def current_tab(self) -> DocumentTab:
        return self.tab_widget.currentWidget()

    def current_doc(self) -> PDFDocument:
        tab = self.current_tab()
        return tab.doc if tab else None

    def current_view(self) -> PDFGraphicsView:
        tab = self.current_tab()
        return tab.view if tab else None

    def add_document(self, doc: PDFDocument) -> DocumentTab:
        tab = DocumentTab(doc, self)
        idx = self.tab_widget.addTab(tab, get_icon("properties", size=14), doc.file_name)
        self.tab_widget.setTabToolTip(idx, doc.file_path or doc.file_name)
        self.tab_widget.setCurrentIndex(idx)

        # Hook modified state to tab title indicator
        doc.modifiedChanged.connect(lambda mod, t=tab: self._update_tab_title(t))

        self._check_empty_state()
        return tab

    def _update_tab_title(self, tab: DocumentTab):
        idx = self.tab_widget.indexOf(tab)
        if idx >= 0:
            prefix = "* " if tab.doc.is_modified else ""
            self.tab_widget.setTabText(idx, f"{prefix}{tab.doc.file_name}")

    def close_tab(self, index: int) -> bool:
        tab = self.tab_widget.widget(index)
        if not tab:
            return True

        if tab.doc.is_modified:
            ans = QMessageBox.question(
                self, "Save Changes?",
                f'Document "{tab.doc.file_name}" has unsaved changes.\nDo you want to save before closing?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if ans == QMessageBox.Save:
                if tab.doc.file_path:
                    tab.doc.save()
                else:
                    path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "Document.pdf", "PDF Files (*.pdf)")
                    if path:
                        tab.doc.save(path)
                    else:
                        return False
            elif ans == QMessageBox.Cancel:
                return False

        tab.doc.close()
        self.tab_widget.removeTab(index)
        tab.deleteLater()
        self._check_empty_state()
        return True

    def close_current_tab(self) -> bool:
        cur_idx = self.tab_widget.currentIndex()
        if cur_idx >= 0:
            return self.close_tab(cur_idx)
        return False

    def _check_empty_state(self):
        if self.tab_widget.count() == 0:
            self.tab_widget.hide()
            self.home_screen.show()
            self.currentDocumentChanged.emit(None, None)
            self.allTabsClosed.emit()
        else:
            self.home_screen.hide()
            self.tab_widget.show()
            cur = self.current_tab()
            if cur:
                self.currentDocumentChanged.emit(cur.doc, cur.view)

    def _on_tab_changed(self, index: int):
        self._check_empty_state()
        cur = self.current_tab()
        if cur:
            self.currentDocumentChanged.emit(cur.doc, cur.view)
