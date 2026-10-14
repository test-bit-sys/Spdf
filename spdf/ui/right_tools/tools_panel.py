"""
Right Collapsible Tools Panel for Spdf (Adobe Acrobat Pro DC Style).
Houses the quick tools switcher and dedicated sub-panels for Organize Pages,
Edit PDF, Comment & Annotate, Protect & Sign, and Export / Convert.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from spdf.models.document import PDFDocument
from spdf.ui.right_tools.organize_panel import OrganizePanel
from spdf.ui.right_tools.edit_panel import EditPanel
from spdf.ui.right_tools.comment_panel import CommentPanel
from spdf.ui.right_tools.protect_panel import ProtectPanel
from spdf.ui.right_tools.export_panel import ExportPanel
from spdf.config import Colors
from spdf.icons import get_icon


class CategoryCard(QFrame):
    """Clickable card for each Acrobat Pro DC tool category."""
    clicked = Signal()

    def __init__(self, title: str, icon_name: str, desc: str, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("CategoryCard")
        self.setStyleSheet(f"""
            QFrame#CategoryCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: 6px;
            }}
            QFrame#CategoryCard:hover {{
                background-color: {Colors.BG_HOVER};
                border: 1px solid {Colors.ACCENT_GOLD};
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(12)

        icon_lbl = QLabel(self)
        icon_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        icon_lbl.setStyleSheet("background: transparent; border: none;")
        icon_lbl.setPixmap(get_icon(icon_name, color=Colors.ACCENT_GOLD, size=24).pixmap(24, 24))
        lay.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        lbl_t = QLabel(title, self)
        lbl_t.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        lbl_t.setStyleSheet(f"font-weight: 600; font-size: 12px; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
        lbl_d = QLabel(desc, self)
        lbl_d.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        lbl_d.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_MUTED}; background: transparent; border: none;")
        text_col.addWidget(lbl_t)
        text_col.addWidget(lbl_d)
        lay.addLayout(text_col)
        lay.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ToolsHubView(QWidget):
    """Initial tools menu showing the 5 Acrobat Pro categories."""
    categorySelected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 14, 10, 14)
        layout.setSpacing(8)

        header = QLabel("Tools", self)
        header.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Colors.TEXT_PRIMARY}; padding: 0 4px;")
        layout.addWidget(header)

        categories = [
            ("Organize Pages", "merge", 1, "Merge, split, extract, and rotate"),
            ("Edit PDF", "text", 2, "Add text, stamps, and redactions"),
            ("Comment", "note", 3, "Highlight, draw, and sticky notes"),
            ("Protect & Sign", "lock", 4, "Digital signatures and encryption"),
            ("Export PDF", "export_image", 5, "Convert to images and text"),
        ]

        for title, icon_name, page_idx, desc in categories:
            card = CategoryCard(title, icon_name, desc, self)
            card.clicked.connect(lambda idx=page_idx: self.categorySelected.emit(idx))
            layout.addWidget(card)

        layout.addStretch()


class RightToolsPanel(QWidget):
    """Main container hosting the stacked tools panels with back navigation."""
    toolRequested = Signal(object)        # ToolMode
    colorChanged = Signal(str)            # hex color
    strokeWidthChanged = Signal(float)    # stroke width
    fontSizeChanged = Signal(int)         # font size
    stampSelected = Signal(object, bytes) # pixmap, raw_bytes
    documentModified = Signal()
    pagesRebuilt = Signal()

    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc

        self.setMinimumWidth(260)
        self.setMaximumWidth(320)
        self.setStyleSheet(f"background-color: {Colors.BG_PANEL}; border-left: 1px solid {Colors.BORDER_SUBTLE};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top navigation header for sub-panels
        self.nav_bar = QWidget(self)
        self.nav_bar.setStyleSheet(f"background-color: {Colors.BG_TOOLBAR}; border-bottom: 1px solid {Colors.BORDER_SUBTLE};")
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(8, 6, 8, 6)

        self.btn_back = QPushButton(" All Tools", self.nav_bar)
        self.btn_back.setIcon(get_icon("prev_page", size=14))
        self.btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        nav_layout.addWidget(self.btn_back)
        nav_layout.addStretch()
        layout.addWidget(self.nav_bar)
        self.nav_bar.hide()

        # Stacked pages
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack)

        # 0. Tools Hub
        self.hub = ToolsHubView(self)
        self.hub.categorySelected.connect(self._switch_to_category)
        self.stack.addWidget(self.hub)

        # 1. Organize
        self.organize_panel = OrganizePanel(self.doc, self)
        self.organize_panel.documentModified.connect(self.documentModified.emit)
        self.organize_panel.pagesRebuilt.connect(self.pagesRebuilt.emit)
        self.stack.addWidget(self.organize_panel)

        # 2. Edit
        self.edit_panel = EditPanel(self.doc, self)
        self.edit_panel.toolRequested.connect(self.toolRequested.emit)
        self.edit_panel.stampSelected.connect(self.stampSelected.emit)
        self.edit_panel.redactionsApplied.connect(self.pagesRebuilt.emit)
        self.stack.addWidget(self.edit_panel)

        # 3. Comment
        self.comment_panel = CommentPanel(self.doc, self)
        self.comment_panel.toolRequested.connect(self.toolRequested.emit)
        self.comment_panel.colorChanged.connect(self.colorChanged.emit)
        self.comment_panel.strokeWidthChanged.connect(self.strokeWidthChanged.emit)
        self.comment_panel.fontSizeChanged.connect(self.fontSizeChanged.emit)
        self.comment_panel.annotationsBaked.connect(self.pagesRebuilt.emit)
        self.stack.addWidget(self.comment_panel)

        # 4. Protect
        self.protect_panel = ProtectPanel(self.doc, self)
        self.protect_panel.toolRequested.connect(self.toolRequested.emit)
        self.protect_panel.signatureReady.connect(self.stampSelected.emit)
        self.protect_panel.documentSaved.connect(self.documentModified.emit)
        self.stack.addWidget(self.protect_panel)

        # 5. Export
        self.export_panel = ExportPanel(self.doc, self)
        self.stack.addWidget(self.export_panel)

        self.stack.currentChanged.connect(self._on_stack_changed)

    def set_document(self, doc: PDFDocument):
        self.doc = doc
        self.organize_panel.set_document(doc)
        self.edit_panel.set_document(doc)
        self.comment_panel.set_document(doc)
        self.protect_panel.set_document(doc)
        self.export_panel.set_document(doc)

    def _switch_to_category(self, index: int):
        self.stack.setCurrentIndex(index)

    def _on_stack_changed(self, index: int):
        if index == 0:
            self.nav_bar.hide()
        else:
            self.nav_bar.show()

    def show_category(self, name: str):
        mapping = {
            "organize": 1,
            "edit": 2,
            "comment": 3,
            "protect": 4,
            "export": 5
        }
        idx = mapping.get(name.lower(), 0)
        self.stack.setCurrentIndex(idx)
