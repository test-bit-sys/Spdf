"""
Export Pages Dialog for Spdf.
Allows rendering and saving PDF pages as high-resolution images (PNG, JPG, TIFF).
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QRadioButton, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from spdf.config import Colors
from spdf.models.document import PDFDocument
from spdf.utils.helpers import parse_page_ranges
from spdf.icons import get_icon


class ExportDialog(QDialog):
    """Interface for exporting PDF pages to image files."""
    def __init__(self, doc: PDFDocument, current_page: int = 0, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.current_page = current_page
        self.setWindowTitle("Export PDF Pages as Images")
        self.setFixedSize(440, 320)
        self.setStyleSheet(f"background-color: {Colors.BG_PANEL};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Image Format row
        fmt_row = QHBoxLayout()
        fmt_label = QLabel("Image Format:", self)
        fmt_row.addWidget(fmt_label)
        self.combo_fmt = QComboBox(self)
        self.combo_fmt.addItems(["PNG (Lossless, Transparent)", "JPEG (Standard)", "TIFF (Archive)"])
        fmt_row.addWidget(self.combo_fmt)
        layout.addLayout(fmt_row)

        # Resolution / DPI row
        dpi_row = QHBoxLayout()
        dpi_label = QLabel("Resolution (DPI):", self)
        dpi_row.addWidget(dpi_label)
        self.combo_dpi = QComboBox(self)
        self.combo_dpi.addItems(["150 DPI (Balanced)", "300 DPI (High Resolution)", "72 DPI (Web Screen)"])
        dpi_row.addWidget(self.combo_dpi)
        layout.addLayout(dpi_row)

        # Page range selection
        lbl_pages = QLabel("Pages to Export:", self)
        lbl_pages.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
        layout.addWidget(lbl_pages)

        self.radio_all = QRadioButton(f"All Pages (1 to {self.doc.page_count})", self)
        self.radio_all.setChecked(True)
        layout.addWidget(self.radio_all)

        self.radio_current = QRadioButton(f"Current Page Only (Page {self.current_page + 1})", self)
        layout.addWidget(self.radio_current)

        self.radio_custom = QRadioButton("Custom Page Range (e.g. 1-3, 5):", self)
        layout.addWidget(self.radio_custom)

        self.custom_edit = QLineEdit(self)
        self.custom_edit.setPlaceholderText("1-3, 5")
        layout.addWidget(self.custom_edit)

        # Bottom buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        self.btn_export = QPushButton("Export Images", self)
        self.btn_export.setObjectName("PrimaryButton")
        self.btn_export.setIcon(get_icon("export_image", color="#121212", size=16))
        self.btn_export.clicked.connect(self._execute_export)
        btn_row.addWidget(self.btn_export)

        layout.addLayout(btn_row)

    def _execute_export(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if not folder:
            return

        fmt_map = {"PNG": "png", "JPEG": "jpg", "TIFF": "tiff"}
        fmt_text = self.combo_fmt.currentText().split()[0]
        fmt_ext = fmt_map.get(fmt_text, "png")

        dpi_map = {"150": 150, "300": 300, "72": 72}
        dpi_val = dpi_map.get(self.combo_dpi.currentText().split()[0], 150)

        # Determine target page indices
        if self.radio_all.isChecked():
            target_indices = list(range(self.doc.page_count))
        elif self.radio_current.isChecked():
            target_indices = [self.current_page]
        else:
            target_indices = parse_page_ranges(self.custom_edit.text(), self.doc.page_count)

        if not target_indices:
            QMessageBox.warning(self, "Invalid Pages", "No valid pages selected for export.")
            return

        base_name = os.path.splitext(self.doc.file_name)[0]
        try:
            for idx in target_indices:
                out_file = os.path.join(folder, f"{base_name}_page_{idx + 1}.{fmt_ext}")
                self.doc.export_page_image(idx, out_file, dpi=dpi_val, fmt=fmt_ext)
            QMessageBox.information(
                self, "Export Complete",
                f"Exported {len(target_indices)} page images successfully to:\n{folder}"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export pages: {str(e)}")
