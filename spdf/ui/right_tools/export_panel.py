"""
Export & Convert Panel for Spdf.
Supports exporting PDF pages to high-resolution images and extracting document text.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox
)
from spdf.models.document import PDFDocument
from spdf.config import Colors
from spdf.ui.dialogs.export_dialog import ExportDialog
from spdf.icons import get_icon


class ExportPanel(QWidget):
    """Export and conversion tools panel."""
    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)

        lbl_title = QLabel("Export & Convert", self)
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {Colors.ACCENT_GOLD}; margin-bottom: 4px;")
        layout.addWidget(lbl_title)

        # 1. Export to Images
        self.btn_export_img = QPushButton("Export Pages as Images...", self)
        self.btn_export_img.setIcon(get_icon("export_image", size=18))
        self.btn_export_img.clicked.connect(self._on_export_images)
        layout.addWidget(self.btn_export_img)

        # 2. Extract Text
        self.btn_extract_txt = QPushButton("Extract All Text (.txt / .md)...", self)
        self.btn_extract_txt.setIcon(get_icon("export_text", size=18))
        self.btn_extract_txt.clicked.connect(self._on_extract_text)
        layout.addWidget(self.btn_extract_txt)

        layout.addStretch()

    def set_document(self, doc: PDFDocument):
        self.doc = doc

    def _on_export_images(self):
        if not self.doc or self.doc.page_count == 0:
            return
        dlg = ExportDialog(self.doc, current_page=0, parent=self)
        dlg.exec_()

    def _on_extract_text(self):
        if not self.doc or self.doc.page_count == 0:
            return
        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Extracted Text", "ExtractedText.txt", "Text Files (*.txt);;Markdown Files (*.md)"
        )
        if out_path:
            try:
                full_text = self.doc.extract_all_text()
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(full_text)
                QMessageBox.information(self, "Success", f"Extracted text saved to:\n{out_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to extract text: {str(e)}")
