"""
Organize Pages Panel for Spdf.
Provides actions for Merging, Splitting, Extracting, Deleting, and Rotating PDF pages.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QInputDialog, QMessageBox, QFileDialog
)
from PySide6.QtCore import Signal
from spdf.models.document import PDFDocument
from spdf.ui.dialogs.merge_dialog import MergeDialog
from spdf.ui.dialogs.split_dialog import SplitDialog
from spdf.icons import get_icon
from spdf.config import Colors
from spdf.utils.helpers import parse_page_ranges


class OrganizePanel(QWidget):
    """Page organization tools panel."""
    documentModified = Signal()
    pagesRebuilt = Signal()

    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)

        lbl_title = QLabel("Organize Pages", self)
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {Colors.ACCENT_GOLD}; margin-bottom: 4px;")
        layout.addWidget(lbl_title)

        # Merge
        self.btn_merge = QPushButton("Merge PDF Files...", self)
        self.btn_merge.setIcon(get_icon("merge", size=18))
        self.btn_merge.clicked.connect(self._on_merge)
        layout.addWidget(self.btn_merge)

        # Split
        self.btn_split = QPushButton("Split Document...", self)
        self.btn_split.setIcon(get_icon("split", size=18))
        self.btn_split.clicked.connect(self._on_split)
        layout.addWidget(self.btn_split)

        # Extract
        self.btn_extract = QPushButton("Extract Pages...", self)
        self.btn_extract.setIcon(get_icon("extract", size=18))
        self.btn_extract.clicked.connect(self._on_extract)
        layout.addWidget(self.btn_extract)

        # Rotate All CW
        self.btn_rot_cw = QPushButton("Rotate All Pages (90° CW)", self)
        self.btn_rot_cw.setIcon(get_icon("rotate_cw", size=18))
        self.btn_rot_cw.clicked.connect(self._on_rotate_cw)
        layout.addWidget(self.btn_rot_cw)

        # Rotate All CCW
        self.btn_rot_ccw = QPushButton("Rotate All Pages (90° CCW)", self)
        self.btn_rot_ccw.setIcon(get_icon("rotate_ccw", size=18))
        self.btn_rot_ccw.clicked.connect(self._on_rotate_ccw)
        layout.addWidget(self.btn_rot_ccw)

        # Insert Blank Page
        self.btn_insert = QPushButton("Insert Blank Page", self)
        self.btn_insert.setIcon(get_icon("insert", size=18))
        self.btn_insert.clicked.connect(self._on_insert_blank)
        layout.addWidget(self.btn_insert)

        # Delete Pages
        self.btn_delete = QPushButton("Delete Pages...", self)
        self.btn_delete.setObjectName("DangerButton")
        self.btn_delete.setIcon(get_icon("delete", color="#FFFFFF", size=18))
        self.btn_delete.clicked.connect(self._on_delete_pages)
        layout.addWidget(self.btn_delete)

        layout.addStretch()

    def set_document(self, doc: PDFDocument):
        self.doc = doc

    def _on_merge(self):
        dlg = MergeDialog(self)
        if dlg.exec_():
            self.pagesRebuilt.emit()

    def _on_split(self):
        if not self.doc or self.doc.page_count == 0:
            return
        dlg = SplitDialog(self.doc, self)
        dlg.exec_()

    def _on_extract(self):
        if not self.doc or self.doc.page_count == 0:
            return
        range_str, ok = QInputDialog.getText(
            self, "Extract Pages",
            f"Enter page range to extract (1-{self.doc.page_count}, e.g., '1-3, 5'):"
        )
        if ok and range_str:
            indices = parse_page_ranges(range_str, self.doc.page_count)
            if not indices:
                QMessageBox.warning(self, "Extract", "No valid pages specified.")
                return
            out_path, _ = QFileDialog.getSaveFileName(
                self, "Save Extracted PDF", "Extracted.pdf", "PDF Files (*.pdf)"
            )
            if out_path:
                self.doc.extract_pages(indices, out_path)
                QMessageBox.information(self, "Success", f"Extracted {len(indices)} pages successfully.")

    def _on_rotate_cw(self):
        if self.doc:
            self.doc.rotate_all_pages(90)
            self.documentModified.emit()
            self.pagesRebuilt.emit()

    def _on_rotate_ccw(self):
        if self.doc:
            self.doc.rotate_all_pages(-90)
            self.documentModified.emit()
            self.pagesRebuilt.emit()

    def _on_insert_blank(self):
        if self.doc:
            self.doc.insert_blank_page()
            self.documentModified.emit()
            self.pagesRebuilt.emit()

    def _on_delete_pages(self):
        if not self.doc or self.doc.page_count <= 1:
            QMessageBox.warning(self, "Delete Pages", "Cannot delete pages from a single-page document.")
            return
        range_str, ok = QInputDialog.getText(
            self, "Delete Pages",
            f"Enter page numbers/ranges to delete (1-{self.doc.page_count}, e.g., '2, 4-5'):"
        )
        if ok and range_str:
            indices = parse_page_ranges(range_str, self.doc.page_count)
            if not indices:
                return
            if len(indices) >= self.doc.page_count:
                QMessageBox.warning(self, "Delete Error", "Cannot delete all pages in the document.")
                return
            confirm = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete {len(indices)} page(s)?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.doc.delete_pages(indices)
                self.documentModified.emit()
                self.pagesRebuilt.emit()
