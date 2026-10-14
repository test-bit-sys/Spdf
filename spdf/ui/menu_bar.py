"""
Main Menu Bar for Spdf.
Implements the Adobe Acrobat Pro DC menu hierarchy: File, Edit, View, Tools, and Help.
"""

import os
from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal
from spdf.icons import get_icon
from spdf.config import APP_NAME, APP_VERSION, APP_TITLE
from spdf.utils.helpers import RecentFilesManager


class SpdfMenuBar(QMenuBar):
    """Application top menu bar."""
    newDocumentRequested = Signal()
    openDocumentRequested = Signal()
    openRecentRequested = Signal(str)
    saveDocumentRequested = Signal()
    saveAsDocumentRequested = Signal()
    closeTabRequested = Signal()
    propertiesRequested = Signal()
    printRequested = Signal()
    exitRequested = Signal()

    undoRequested = Signal()
    redoRequested = Signal()
    deleteAnnotationRequested = Signal()
    copyRequested = Signal()
    findRequested = Signal()

    zoomInRequested = Signal()
    zoomOutRequested = Signal()
    zoomActualRequested = Signal()
    fitWidthRequested = Signal()
    fitPageRequested = Signal()
    rotateCWRequested = Signal()
    rotateCCWRequested = Signal()
    toggleSidebarRequested = Signal()
    toggleToolsRequested = Signal()
    toggleNightModeRequested = Signal()
    fullscreenRequested = Signal()

    showToolCategory = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_file_menu()
        self._build_edit_menu()
        self._build_view_menu()
        self._build_tools_menu()
        self._build_help_menu()

    def _build_file_menu(self):
        file_menu = self.addMenu("&File")

        act_new = QAction(get_icon("insert"), "&New Blank Document", self)
        act_new.setShortcut(QKeySequence.New)
        act_new.triggered.connect(self.newDocumentRequested.emit)
        file_menu.addAction(act_new)

        act_open = QAction(get_icon("open"), "&Open...", self)
        act_open.setShortcut(QKeySequence.Open)
        act_open.triggered.connect(self.openDocumentRequested.emit)
        file_menu.addAction(act_open)

        # Recent files submenu
        self.recent_menu = file_menu.addMenu(get_icon("recent"), "Open &Recent")
        self.recent_menu.aboutToShow.connect(self._populate_recent_menu)

        file_menu.addSeparator()

        act_save = QAction(get_icon("save"), "&Save", self)
        act_save.setShortcut(QKeySequence.Save)
        act_save.triggered.connect(self.saveDocumentRequested.emit)
        file_menu.addAction(act_save)

        act_save_as = QAction(get_icon("save_as"), "Save &As...", self)
        act_save_as.setShortcut(QKeySequence.SaveAs)
        act_save_as.triggered.connect(self.saveAsDocumentRequested.emit)
        file_menu.addAction(act_save_as)

        file_menu.addSeparator()

        act_props = QAction(get_icon("properties"), "Document &Properties...", self)
        act_props.setShortcut(QKeySequence("Ctrl+D"))
        act_props.triggered.connect(self.propertiesRequested.emit)
        file_menu.addAction(act_props)

        act_print = QAction(get_icon("print"), "&Print...", self)
        act_print.setShortcut(QKeySequence.Print)
        act_print.triggered.connect(self.printRequested.emit)
        file_menu.addAction(act_print)

        file_menu.addSeparator()

        act_close = QAction(get_icon("close"), "&Close Document", self)
        act_close.setShortcut(QKeySequence.Close)
        act_close.triggered.connect(self.closeTabRequested.emit)
        file_menu.addAction(act_close)

        act_exit = QAction("E&xit", self)
        act_exit.setShortcut(QKeySequence.Quit)
        act_exit.triggered.connect(self.exitRequested.emit)
        file_menu.addAction(act_exit)

    def _populate_recent_menu(self):
        self.recent_menu.clear()
        recent = RecentFilesManager.get_recent_files()
        if not recent:
            act_none = QAction("No Recent Files", self)
            act_none.setEnabled(False)
            self.recent_menu.addAction(act_none)
            return

        for path in recent:
            fname = os.path.basename(path)
            act = QAction(f"{fname} ({path})", self)
            act.triggered.connect(lambda ch=False, p=path: self.openRecentRequested.emit(p))
            self.recent_menu.addAction(act)

        self.recent_menu.addSeparator()
        act_clear = QAction("Clear History", self)
        act_clear.triggered.connect(RecentFilesManager.clear_recent_files)
        self.recent_menu.addAction(act_clear)

    def _build_edit_menu(self):
        edit_menu = self.addMenu("&Edit")

        act_undo = QAction(get_icon("undo"), "&Undo", self)
        act_undo.setShortcut(QKeySequence.Undo)
        act_undo.triggered.connect(self.undoRequested.emit)
        edit_menu.addAction(act_undo)

        act_redo = QAction(get_icon("redo"), "&Redo", self)
        act_redo.setShortcut(QKeySequence.Redo)
        act_redo.triggered.connect(self.redoRequested.emit)
        edit_menu.addAction(act_redo)

        edit_menu.addSeparator()

        act_copy = QAction(get_icon("copy"), "&Copy Selected", self)
        act_copy.setShortcut(QKeySequence.Copy)
        act_copy.triggered.connect(self.copyRequested.emit)
        edit_menu.addAction(act_copy)

        act_del = QAction(get_icon("delete"), "&Delete Selected Annotation", self)
        act_del.setShortcut(QKeySequence.Delete)
        act_del.triggered.connect(self.deleteAnnotationRequested.emit)
        edit_menu.addAction(act_del)

        edit_menu.addSeparator()

        act_find = QAction(get_icon("search"), "&Find in Document...", self)
        act_find.setShortcut(QKeySequence.Find)
        act_find.triggered.connect(self.findRequested.emit)
        edit_menu.addAction(act_find)

    def _build_view_menu(self):
        view_menu = self.addMenu("&View")

        act_zin = QAction(get_icon("zoom_in"), "Zoom &In", self)
        act_zin.setShortcut(QKeySequence.ZoomIn)
        act_zin.triggered.connect(self.zoomInRequested.emit)
        view_menu.addAction(act_zin)

        act_zout = QAction(get_icon("zoom_out"), "Zoom &Out", self)
        act_zout.setShortcut(QKeySequence.ZoomOut)
        act_zout.triggered.connect(self.zoomOutRequested.emit)
        view_menu.addAction(act_zout)

        act_act = QAction(get_icon("actual_size"), "Actual Size (100%)", self)
        act_act.setShortcut(QKeySequence("Ctrl+0"))
        act_act.triggered.connect(self.zoomActualRequested.emit)
        view_menu.addAction(act_act)

        act_fit_w = QAction(get_icon("fit_width"), "Fit to &Width", self)
        act_fit_w.triggered.connect(self.fitWidthRequested.emit)
        view_menu.addAction(act_fit_w)

        act_fit_p = QAction(get_icon("fit_page"), "Fit to &Page", self)
        act_fit_p.triggered.connect(self.fitPageRequested.emit)
        view_menu.addAction(act_fit_p)

        view_menu.addSeparator()

        act_night = QAction(get_icon("night_mode"), "Invert Colors (Night Reading)", self)
        act_night.setShortcut(QKeySequence("Ctrl+I"))
        act_night.triggered.connect(self.toggleNightModeRequested.emit)
        view_menu.addAction(act_night)

        act_full = QAction(get_icon("fullscreen"), "Full &Screen", self)
        act_full.setShortcut(QKeySequence("F11"))
        act_full.triggered.connect(self.fullscreenRequested.emit)
        view_menu.addAction(act_full)

        view_menu.addSeparator()

        act_rcw = QAction(get_icon("rotate_cw"), "Rotate &Clockwise (90°)", self)
        act_rcw.setShortcut(QKeySequence("Ctrl+Shift+Plus"))
        act_rcw.triggered.connect(self.rotateCWRequested.emit)
        view_menu.addAction(act_rcw)

        act_rccw = QAction(get_icon("rotate_ccw"), "Rotate Counter-Clockwise (90°)", self)
        act_rccw.setShortcut(QKeySequence("Ctrl+Shift+Minus"))
        act_rccw.triggered.connect(self.rotateCCWRequested.emit)
        view_menu.addAction(act_rccw)

        view_menu.addSeparator()

        act_side = QAction(get_icon("sidebar_left"), "Toggle &Navigation Panel", self)
        act_side.setShortcut(QKeySequence("F4"))
        act_side.triggered.connect(self.toggleSidebarRequested.emit)
        view_menu.addAction(act_side)

        act_tools = QAction(get_icon("sidebar_right"), "Toggle &Tools Panel", self)
        act_tools.setShortcut(QKeySequence("Shift+F4"))
        act_tools.triggered.connect(self.toggleToolsRequested.emit)
        view_menu.addAction(act_tools)

    def _build_tools_menu(self):
        tools_menu = self.addMenu("&Tools")

        categories = [
            ("Organize Pages", "organize"),
            ("Edit PDF", "edit"),
            ("Comment & Annotate", "comment"),
            ("Protect & Sign", "protect"),
            ("Export PDF", "export")
        ]
        for name, key in categories:
            act = QAction(name, self)
            act.triggered.connect(lambda ch=False, k=key: self.showToolCategory.emit(k))
            tools_menu.addAction(act)

    def _build_help_menu(self):
        help_menu = self.addMenu("&Help")

        act_shortcuts = QAction("Keyboard Shortcuts", self)
        act_shortcuts.triggered.connect(self._show_shortcuts)
        help_menu.addAction(act_shortcuts)

        act_about = QAction("About Spdf...", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _show_shortcuts(self):
        shortcuts_text = (
            "<b>Keyboard Shortcuts:</b><br><br>"
            "<b>Ctrl + O</b>: Open PDF File<br>"
            "<b>Ctrl + S</b>: Save PDF File<br>"
            "<b>Ctrl + Shift + S</b>: Save As<br>"
            "<b>Ctrl + P</b>: Print Document<br>"
            "<b>Ctrl + W</b>: Close Active Document Tab<br>"
            "<b>Ctrl + D</b>: Document Properties<br>"
            "<b>Ctrl + F</b>: Search Text in Document<br>"
            "<b>Ctrl + Z / Ctrl + Y</b>: Undo / Redo Annotation<br>"
            "<b>Delete / Backspace</b>: Delete Selected Annotation<br>"
            "<b>Ctrl + C</b>: Copy Selected Text / Note<br>"
            "<b>Ctrl + I</b>: Invert Colors (Night Reading Mode)<br>"
            "<b>F11</b>: Toggle Fullscreen Mode<br>"
            "<b>Ctrl + Plus / Minus</b>: Zoom In / Zoom Out<br>"
            "<b>Ctrl + Mouse Wheel</b>: Smooth Zoom<br>"
            "<b>Ctrl + 0</b>: Reset to 100% Zoom<br>"
            "<b>F4</b>: Toggle Left Navigation Sidebar<br>"
            "<b>Shift + F4</b>: Toggle Right Tools Panel<br>"
            "<b>Left / Right Arrow / PageUp / PageDown</b>: Navigate Pages<br>"
            "<b>Escape</b>: Revert to Hand Tool & Clear Selection<br>"
        )
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text)

    def _show_about(self):
        about_text = (
            f"<h3>{APP_TITLE}</h3>"
            f"<p>Version {APP_VERSION}</p>"
            f"<p>A complete, high-performance PDF Reader, Editor, and Management system "
            f"built with Python, PySide6, and PyMuPDF.</p>"
            f"<p>Full Adobe Acrobat Pro DC layout, asynchronous high-DPI rendering, "
            f"annotation baking, page manipulation, digital signatures, and AES-256 encryption.</p>"
        )
        QMessageBox.about(self, f"About {APP_NAME}", about_text)
