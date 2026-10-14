"""
PDF Split Dialog for Spdf.
Supports splitting PDF documents by page ranges (e.g. 1-3, 4-8) or bursting into single-page files.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QRadioButton,
    QLineEdit, QSpinBox, QPushButton, QLabel, QFileDialog, QMessageBox
)
from spdf.config import Colors
from spdf.models.document import PDFDocument
from spdf.utils.helpers import parse_page_ranges
import fitz


class SplitDialog(QDialog):
    """Interface for splitting PDF documents."""
    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.setWindowTitle("Split PDF Document")
        self.setFixedSize(460, 280)
        self.setStyleSheet(f"background-color: {Colors.BG_PANEL};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        info = QLabel(f"Document contains {self.doc.page_count} total pages.", self)
        info.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
        layout.addWidget(info)

        # Radio 1: By Range
        self.radio_range = QRadioButton("Split by page ranges (e.g., '1-3, 4-8, 9'):", self)
        self.radio_range.setChecked(True)
        layout.addWidget(self.radio_range)

        self.range_edit = QLineEdit(self)
        self.range_edit.setPlaceholderText("1-3, 4-6, 7")
        layout.addWidget(self.range_edit)

        # Radio 2: Burst
        self.radio_burst = QRadioButton("Burst into individual single-page PDF files", self)
        layout.addWidget(self.radio_burst)

        # Bottom buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        self.btn_split = QPushButton("Split Document", self)
        self.btn_split.setObjectName("PrimaryButton")
        self.btn_split.clicked.connect(self._execute_split)
        btn_row.addWidget(self.btn_split)

        layout.addLayout(btn_row)

    def _execute_split(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not folder:
            return

        base_name = os.path.splitext(self.doc.file_name)[0]
        try:
            if self.radio_burst.isChecked():
                for idx in range(self.doc.page_count):
                    out_path = os.path.join(folder, f"{base_name}_Page_{idx + 1}.pdf")
                    single_doc = fitz.open()
                    single_doc.insert_pdf(self.doc.doc, from_page=idx, to_page=idx)
                    single_doc.save(out_path)
                    single_doc.close()
                QMessageBox.information(self, "Success", f"Split {self.doc.page_count} pages successfully.")
                self.accept()

            else:
                range_text = self.range_edit.text().strip()
                if not range_text:
                    QMessageBox.warning(self, "Input Error", "Please provide page ranges.")
                    return

                parts = [p.strip() for p in range_text.split(",") if p.strip()]
                for i, part in enumerate(parts):
                    indices = parse_page_ranges(part, self.doc.page_count)
                    if indices:
                        out_path = os.path.join(folder, f"{base_name}_Part_{i + 1}.pdf")
                        part_doc = fitz.open()
                        for p_idx in indices:
                            part_doc.insert_pdf(self.doc.doc, from_page=p_idx, to_page=p_idx)
                        part_doc.save(out_path)
                        part_doc.close()
                QMessageBox.information(self, "Success", f"Split into {len(parts)} files successfully.")
                self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Split Error", f"Failed to split PDF: {str(e)}")
