"""
Spdf - Professional PDF Reader, Editor, and Management Application.
Replicating the layout, workflow, and feature set of Adobe Acrobat Pro DC.

Entry point for launching the desktop application.
"""

import sys
import os
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

# Ensure local package import
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from spdf.config import APP_NAME, APP_TITLE, Colors
from spdf.style import DARK_THEME_QSS
from spdf.icons import get_icon
from spdf.ui.main_window import MainWindow


def main():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} - Professional PDF Editor")
    parser.add_argument("pdf_file", nargs="?", default=None, help="Path to initial PDF file to open")
    args = parser.parse_args()

    # High-DPI attributes for Qt5 compatibility; Qt6 enables HighDPI automatically
    from PySide6.QtCore import qVersion
    if qVersion().startswith("5"):
        try:
            if hasattr(Qt, "AA_EnableHighDpiScaling"):
                QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            if hasattr(Qt, "AA_UseHighDpiPixmaps"):
                QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_TITLE)
    app.setOrganizationName("Spdf")

    # Establish clean default typography with positive point size to avoid DPI scaling warnings
    from PySide6.QtGui import QFont
    app_font = QFont("Segoe UI", 9)
    app_font.setStyleHint(QFont.SansSerif)
    app.setFont(app_font)

    # Set dark theme stylesheet
    app.setStyleSheet(DARK_THEME_QSS)

    # Windows taskbar icon grouping support
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Spdf.PDFEditor.Pro.1.0")
        except Exception:
            pass

    # Set application brand icon
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "app_icon.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        app.setWindowIcon(get_icon("properties", color=Colors.ACCENT_GOLD, size=64))

    window = MainWindow(initial_pdf=args.pdf_file)
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
