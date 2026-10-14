"""
Password and Encryption Dialogs for Spdf.
Handles decryption password prompt for protected PDFs and AES-256 encryption setup.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from spdf.config import Colors
from spdf.icons import get_icon


class PasswordPromptDialog(QDialog):
    """Prompt user for password to unlock an encrypted PDF document."""
    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Required")
        self.setFixedSize(380, 190)
        self.setStyleSheet(f"background-color: {Colors.BG_PANEL};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel(f'The document "{filename}" is protected with a password.', self)
        header.setWordWrap(True)
        header.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(header)

        self.pw_edit = QLineEdit(self)
        self.pw_edit.setEchoMode(QLineEdit.Password)
        self.pw_edit.setPlaceholderText("Enter document password")
        self.pw_edit.returnPressed.connect(self.accept)
        layout.addWidget(self.pw_edit)

        self.show_cb = QCheckBox("Show password", self)
        self.show_cb.stateChanged.connect(self._toggle_show_pw)
        layout.addWidget(self.show_cb)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        self.btn_unlock = QPushButton("Unlock", self)
        self.btn_unlock.setObjectName("PrimaryButton")
        self.btn_unlock.setIcon(get_icon("lock", color="#121212", size=16))
        self.btn_unlock.clicked.connect(self.accept)
        btn_row.addWidget(self.btn_unlock)

        layout.addLayout(btn_row)

    def _toggle_show_pw(self, state):
        self.pw_edit.setEchoMode(QLineEdit.Normal if state == Qt.Checked.value else QLineEdit.Password)

    def get_password(self) -> str:
        return self.pw_edit.text()


class EncryptPDFDialog(QDialog):
    """Setup AES-256 encryption with user and owner passwords."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Encrypt Document with Password")
        self.setFixedSize(420, 260)
        self.setStyleSheet(f"background-color: {Colors.BG_PANEL};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        info = QLabel("Set a password to restrict opening and viewing this document.", self)
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(info)

        lbl_pw = QLabel("Document Password:", self)
        layout.addWidget(lbl_pw)
        self.user_pw = QLineEdit(self)
        self.user_pw.setEchoMode(QLineEdit.Password)
        self.user_pw.setPlaceholderText("User password (required to view)")
        layout.addWidget(self.user_pw)

        lbl_confirm = QLabel("Confirm Password:", self)
        layout.addWidget(lbl_confirm)
        self.confirm_pw = QLineEdit(self)
        self.confirm_pw.setEchoMode(QLineEdit.Password)
        self.confirm_pw.setPlaceholderText("Confirm password")
        layout.addWidget(self.confirm_pw)

        lbl_owner = QLabel("Owner / Permissions Password (Optional):", self)
        layout.addWidget(lbl_owner)
        self.owner_pw = QLineEdit(self)
        self.owner_pw.setEchoMode(QLineEdit.Password)
        self.owner_pw.setPlaceholderText("Owner password (required to modify permissions)")
        layout.addWidget(self.owner_pw)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        self.btn_encrypt = QPushButton("Encrypt & Save", self)
        self.btn_encrypt.setObjectName("PrimaryButton")
        self.btn_encrypt.setIcon(get_icon("lock", color="#121212", size=16))
        self.btn_encrypt.clicked.connect(self._validate)
        btn_row.addWidget(self.btn_encrypt)

        layout.addLayout(btn_row)

    def _validate(self):
        pw = self.user_pw.text()
        conf = self.confirm_pw.text()
        if not pw:
            QMessageBox.warning(self, "Invalid Password", "Password cannot be empty.")
            return
        if pw != conf:
            QMessageBox.warning(self, "Mismatch", "Passwords do not match.")
            return
        self.accept()

    def get_passwords(self) -> tuple:
        return self.user_pw.text(), self.owner_pw.text() or self.user_pw.text()
