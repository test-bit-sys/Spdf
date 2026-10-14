"""
PDF Merge Dialog for Spdf.
Allows selecting multiple PDF files, reordering the sequence, and combining them into a single PDF.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
import fitz
from spdf.config import Colors
from spdf.icons import get_icon


class MergeDialog(QDialog):
    """Multi-file PDF merger interface."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge PDF Files")
        self.setFixedSize(500, 380)
        self.setStyleSheet(f"background-color: {Colors.BG_PANEL};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QLabel("Add and arrange PDF files in the order you wish to merge them:", self)
        header.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
        layout.addWidget(header)

        # File list
        self.file_list = QListWidget(self)
        layout.addWidget(self.file_list)

        # Row of manipulation buttons
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("Add Files...", self)
        self.btn_add.setIcon(get_icon("add", size=16))
        self.btn_add.clicked.connect(self._add_files)
        btn_row.addWidget(self.btn_add)

        self.btn_remove = QPushButton("Remove", self)
        self.btn_remove.setIcon(get_icon("delete", color=Colors.ACCENT_CRIMSON, size=16))
        self.btn_remove.clicked.connect(self._remove_selected)
        btn_row.addWidget(self.btn_remove)

        self.btn_up = QPushButton("Move Up", self)
        self.btn_up.clicked.connect(self._move_up)
        btn_row.addWidget(self.btn_up)

        self.btn_down = QPushButton("Move Down", self)
        self.btn_down.clicked.connect(self._move_down)
        btn_row.addWidget(self.btn_down)

        layout.addLayout(btn_row)

        # Bottom actions
        action_row = QHBoxLayout()
        action_row.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        action_row.addWidget(self.btn_cancel)

        self.btn_merge = QPushButton("Merge Documents", self)
        self.btn_merge.setObjectName("PrimaryButton")
        self.btn_merge.setIcon(get_icon("merge", color="#121212", size=16))
        self.btn_merge.clicked.connect(self._execute_merge)
        action_row.addWidget(self.btn_merge)

        layout.addLayout(action_row)

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files to Merge", "", "PDF Files (*.pdf)"
        )
        for p in paths:
            self.file_list.addItem(QListWidgetItem(p))

    def _remove_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def _move_up(self):
        row = self.file_list.currentRow()
        if row > 0:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row - 1, item)
            self.file_list.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.file_list.currentRow()
        if row < self.file_list.count() - 1:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row + 1, item)
            self.file_list.setCurrentRow(row + 1)

    def _execute_merge(self):
        if self.file_list.count() < 2:
            QMessageBox.warning(self, "Merge Warning", "Please add at least 2 PDF files to merge.")
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "Merged.pdf", "PDF Files (*.pdf)"
        )
        if not out_path:
            return

        try:
            merged_doc = fitz.open()
            for i in range(self.file_list.count()):
                file_path = self.file_list.item(i).text()
                src_doc = fitz.open(file_path)
                merged_doc.insert_pdf(src_doc)
                src_doc.close()
            merged_doc.save(out_path)
            merged_doc.close()
            QMessageBox.information(self, "Success", f"Merged PDF created successfully at:\n{out_path}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Merge Error", f"Failed to merge PDFs: {str(e)}")
