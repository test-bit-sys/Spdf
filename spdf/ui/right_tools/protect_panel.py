"""
Protect & Sign Panel for Spdf.
Supports digital signature drawing, signature image imports, and document encryption.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal
from spdf.models.document import PDFDocument
from spdf.config import Colors, ToolMode
from spdf.ui.dialogs.signature_dialog import SignatureDialog
from spdf.ui.dialogs.password_dialog import EncryptPDFDialog
from spdf.icons import get_icon


class ProtectPanel(QWidget):
    """Document security and digital signature tools."""
    toolRequested = Signal(object)        # ToolMode
    signatureReady = Signal(object, bytes)# pixmap, raw_bytes
    documentSaved = Signal()

    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)

        lbl_title = QLabel("Protect & Sign", self)
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {Colors.ACCENT_GOLD}; margin-bottom: 4px;")
        layout.addWidget(lbl_title)

        # 1. Digital Signature
        lbl_sig = QLabel("Signatures:", self)
        lbl_sig.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin-top: 4px;")
        layout.addWidget(lbl_sig)

        self.btn_draw_sig = QPushButton("Draw Digital Signature...", self)
        self.btn_draw_sig.setIcon(get_icon("signature", size=18))
        self.btn_draw_sig.clicked.connect(self._on_draw_sig)
        layout.addWidget(self.btn_draw_sig)

        # 2. Security & Encryption
        lbl_sec = QLabel("Security & Encryption:", self)
        lbl_sec.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin-top: 10px;")
        layout.addWidget(lbl_sec)

        self.btn_encrypt = QPushButton("Encrypt with Password...", self)
        self.btn_encrypt.setIcon(get_icon("lock", size=18))
        self.btn_encrypt.clicked.connect(self._on_encrypt)
        layout.addWidget(self.btn_encrypt)

        layout.addStretch()

    def set_document(self, doc: PDFDocument):
        self.doc = doc

    def _on_draw_sig(self):
        dlg = SignatureDialog(self)
        if dlg.exec_():
            if dlg.signature_pixmap and dlg.signature_bytes:
                self.signatureReady.emit(dlg.signature_pixmap, dlg.signature_bytes)
                self.toolRequested.emit(ToolMode.SIGNATURE)

    def _on_encrypt(self):
        if not self.doc or self.doc.page_count == 0:
            return
        dlg = EncryptPDFDialog(self)
        if dlg.exec_():
            user_pw, owner_pw = dlg.get_passwords()
            out_path, _ = QFileDialog.getSaveFileName(
                self, "Save Encrypted PDF", "Protected.pdf", "PDF Files (*.pdf)"
            )
            if out_path:
                try:
                    self.doc.save_encrypted(out_path, user_pw, owner_pw)
                    QMessageBox.information(
                        self, "Encryption Complete",
                        f"Document encrypted with AES-256 and saved successfully to:\n{out_path}"
                    )
                    self.documentSaved.emit()
                except Exception as e:
                    QMessageBox.critical(self, "Encryption Error", f"Failed to encrypt document: {str(e)}")
