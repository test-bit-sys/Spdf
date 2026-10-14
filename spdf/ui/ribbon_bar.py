"""
Ribbon Bar & Quick Action Toolbar for Spdf.
Houses page navigation, zoom controls, tool toggles, page rotation, and panel toggles.
"""

from PySide6.QtWidgets import (
    QToolBar, QWidget, QHBoxLayout, QToolButton,
    QLineEdit, QLabel, QComboBox, QButtonGroup
)
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Qt, Signal
from spdf.config import Colors, ToolMode, ZOOM_PRESETS
from spdf.icons import get_icon


class RibbonBar(QToolBar):
    """Primary Quick Action Ribbon Toolbar."""
    pageJumpRequested = Signal(int)
    zoomRequested = Signal(float)
    fitWidthRequested = Signal()
    fitPageRequested = Signal()
    toolChanged = Signal(object)      # ToolMode
    rotateCWRequested = Signal()
    rotateCCWRequested = Signal()
    toggleLeftSidebar = Signal()
    toggleRightPanel = Signal()
    undoRequested = Signal()
    redoRequested = Signal()
    deleteAnnotationRequested = Signal()
    toggleNightMode = Signal()

    def __init__(self, parent=None):
        super().__init__("Quick Actions", parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(self.iconSize())

        self.current_page = 0
        self.total_pages = 1

        # 1. Left Sidebar Toggle
        self.btn_sidebar_left = QToolButton(self)
        self.btn_sidebar_left.setIcon(get_icon("sidebar_left", size=18))
        self.btn_sidebar_left.setToolTip("Toggle Navigation Panels (F4)")
        self.btn_sidebar_left.clicked.connect(self.toggleLeftSidebar.emit)
        self.addWidget(self.btn_sidebar_left)

        self.addSeparator()

        # Undo / Redo / Delete
        self.btn_undo = QToolButton(self)
        self.btn_undo.setIcon(get_icon("undo", size=16))
        self.btn_undo.setToolTip("Undo Annotation (Ctrl+Z)")
        self.btn_undo.clicked.connect(self.undoRequested.emit)
        self.addWidget(self.btn_undo)

        self.btn_redo = QToolButton(self)
        self.btn_redo.setIcon(get_icon("redo", size=16))
        self.btn_redo.setToolTip("Redo Annotation (Ctrl+Y)")
        self.btn_redo.clicked.connect(self.redoRequested.emit)
        self.addWidget(self.btn_redo)

        self.btn_del_annot = QToolButton(self)
        self.btn_del_annot.setIcon(get_icon("delete", color=Colors.ACCENT_CRIMSON, size=16))
        self.btn_del_annot.setToolTip("Delete Selected Annotation (Delete / Backspace)")
        self.btn_del_annot.clicked.connect(self.deleteAnnotationRequested.emit)
        self.addWidget(self.btn_del_annot)

        self.addSeparator()

        # 2. Hand / Selection Tool toggle group
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)

        self.btn_hand = QToolButton(self)
        self.btn_hand.setIcon(get_icon("hand", size=18))
        self.btn_hand.setCheckable(True)
        self.btn_hand.setChecked(True)
        self.btn_hand.setToolTip("Hand / Pan Tool (H)")
        self.btn_hand.clicked.connect(lambda: self.toolChanged.emit(ToolMode.HAND))
        self.tool_group.addButton(self.btn_hand)
        self.addWidget(self.btn_hand)

        self.btn_select = QToolButton(self)
        self.btn_select.setIcon(get_icon("select", size=18))
        self.btn_select.setCheckable(True)
        self.btn_select.setToolTip("Selection Tool (V)")
        self.btn_select.clicked.connect(lambda: self.toolChanged.emit(ToolMode.SELECT))
        self.tool_group.addButton(self.btn_select)
        self.addWidget(self.btn_select)

        self.addSeparator()

        # 3. Quick Annotations
        self.btn_high = QToolButton(self)
        self.btn_high.setIcon(get_icon("highlight", color=Colors.ANNOT_HIGHLIGHT, size=18))
        self.btn_high.setCheckable(True)
        self.btn_high.setToolTip("Highlight Text / Area")
        self.btn_high.clicked.connect(lambda: self.toolChanged.emit(ToolMode.HIGHLIGHT))
        self.tool_group.addButton(self.btn_high)
        self.addWidget(self.btn_high)

        self.btn_pen = QToolButton(self)
        self.btn_pen.setIcon(get_icon("ink", color=Colors.ANNOT_INK, size=18))
        self.btn_pen.setCheckable(True)
        self.btn_pen.setToolTip("Freehand Drawing Pen")
        self.btn_pen.clicked.connect(lambda: self.toolChanged.emit(ToolMode.INK))
        self.tool_group.addButton(self.btn_pen)
        self.addWidget(self.btn_pen)

        self.btn_text = QToolButton(self)
        self.btn_text.setIcon(get_icon("text", size=18))
        self.btn_text.setCheckable(True)
        self.btn_text.setToolTip("Add Text Overlay")
        self.btn_text.clicked.connect(lambda: self.toolChanged.emit(ToolMode.TEXT))
        self.tool_group.addButton(self.btn_text)
        self.addWidget(self.btn_text)

        self.btn_note = QToolButton(self)
        self.btn_note.setIcon(get_icon("note", color=Colors.ANNOT_NOTE, size=18))
        self.btn_note.setCheckable(True)
        self.btn_note.setToolTip("Add Sticky Note")
        self.btn_note.clicked.connect(lambda: self.toolChanged.emit(ToolMode.STICKY_NOTE))
        self.tool_group.addButton(self.btn_note)
        self.addWidget(self.btn_note)

        self.addSeparator()

        # 4. Page Navigation
        self.btn_prev = QToolButton(self)
        self.btn_prev.setIcon(get_icon("prev_page", size=16))
        self.btn_prev.setToolTip("Previous Page (Left Arrow)")
        self.btn_prev.clicked.connect(self._prev_page)
        self.addWidget(self.btn_prev)

        # Page jump edit
        self.page_input = QLineEdit("1", self)
        self.page_input.setFixedWidth(40)
        self.page_input.setAlignment(Qt.AlignCenter)
        self.page_input.setValidator(QIntValidator(1, 99999, self))
        self.page_input.returnPressed.connect(self._on_page_input)
        self.addWidget(self.page_input)

        self.page_total_lbl = QLabel(" / 1", self)
        self.page_total_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 0 4px;")
        self.addWidget(self.page_total_lbl)

        self.btn_next = QToolButton(self)
        self.btn_next.setIcon(get_icon("next_page", size=16))
        self.btn_next.setToolTip("Next Page (Right Arrow)")
        self.btn_next.clicked.connect(self._next_page)
        self.addWidget(self.btn_next)

        self.addSeparator()

        # 5. Zoom Controls
        self.btn_zoom_out = QToolButton(self)
        self.btn_zoom_out.setIcon(get_icon("zoom_out", size=16))
        self.btn_zoom_out.setToolTip("Zoom Out (Ctrl+-)")
        self.btn_zoom_out.clicked.connect(lambda: self.zoomRequested.emit(-1.0))  # -1 indicates zoom out
        self.addWidget(self.btn_zoom_out)

        self.zoom_combo = QComboBox(self)
        self.zoom_combo.setFixedWidth(90)
        self.zoom_combo.addItems([
            "50%", "75%", "100%", "125%", "150%", "200%", "300%", "Fit Width", "Fit Page"
        ])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.activated.connect(self._on_zoom_combo_activated)
        self.addWidget(self.zoom_combo)

        self.btn_zoom_in = QToolButton(self)
        self.btn_zoom_in.setIcon(get_icon("zoom_in", size=16))
        self.btn_zoom_in.setToolTip("Zoom In (Ctrl++)")
        self.btn_zoom_in.clicked.connect(lambda: self.zoomRequested.emit(1.0))   # 1 indicates zoom in
        self.addWidget(self.btn_zoom_in)

        self.btn_fit_width = QToolButton(self)
        self.btn_fit_width.setIcon(get_icon("fit_width", size=16))
        self.btn_fit_width.setToolTip("Fit to Page Width")
        self.btn_fit_width.clicked.connect(self.fitWidthRequested.emit)
        self.addWidget(self.btn_fit_width)

        self.btn_fit_page = QToolButton(self)
        self.btn_fit_page.setIcon(get_icon("fit_page", size=16))
        self.btn_fit_page.setToolTip("Fit Entire Page in Window")
        self.btn_fit_page.clicked.connect(self.fitPageRequested.emit)
        self.addWidget(self.btn_fit_page)

        self.addSeparator()

        # 6. Page Rotation
        self.btn_rot_cw = QToolButton(self)
        self.btn_rot_cw.setIcon(get_icon("rotate_cw", size=16))
        self.btn_rot_cw.setToolTip("Rotate Page Clockwise (Ctrl+Shift++)")
        self.btn_rot_cw.clicked.connect(self.rotateCWRequested.emit)
        self.addWidget(self.btn_rot_cw)

        self.btn_rot_ccw = QToolButton(self)
        self.btn_rot_ccw.setIcon(get_icon("rotate_ccw", size=16))
        self.btn_rot_ccw.setToolTip("Rotate Page Counter-Clockwise (Ctrl+Shift+-)")
        self.btn_rot_ccw.clicked.connect(self.rotateCCWRequested.emit)
        self.addWidget(self.btn_rot_ccw)

        self.addSeparator()

        # 7. Night / Inverted Reading Mode
        self.btn_night = QToolButton(self)
        self.btn_night.setIcon(get_icon("night_mode", size=16))
        self.btn_night.setCheckable(True)
        self.btn_night.setToolTip("Invert Colors / Night Reading Mode (Ctrl+I)")
        self.btn_night.clicked.connect(self.toggleNightMode.emit)
        self.addWidget(self.btn_night)

        # Spacer to push right sidebar toggle to far right
        spacer = QWidget(self)
        from PySide6.QtWidgets import QSizePolicy
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.addWidget(spacer)

        # 7. Right Tools Panel Toggle
        self.btn_tools_right = QToolButton(self)
        self.btn_tools_right.setIcon(get_icon("sidebar_right", size=18))
        self.btn_tools_right.setToolTip("Toggle Tools Panel (Shift+F4)")
        self.btn_tools_right.clicked.connect(self.toggleRightPanel.emit)
        self.addWidget(self.btn_tools_right)

    def update_page_info(self, current: int, total: int):
        self.current_page = current
        self.total_pages = max(1, total)
        self.page_input.blockSignals(True)
        self.page_input.setText(str(current + 1))
        self.page_input.blockSignals(False)
        self.page_total_lbl.setText(f" / {self.total_pages}")

    def update_zoom_display(self, factor: float):
        pct = int(round(factor * 100))
        self.zoom_combo.blockSignals(True)
        self.zoom_combo.setCurrentText(f"{pct}%")
        self.zoom_combo.blockSignals(False)

    def _prev_page(self):
        if self.current_page > 0:
            self.pageJumpRequested.emit(self.current_page - 1)

    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self.pageJumpRequested.emit(self.current_page + 1)

    def _on_page_input(self):
        try:
            val = int(self.page_input.text())
            if 1 <= val <= self.total_pages:
                self.pageJumpRequested.emit(val - 1)
        except ValueError:
            pass

    def _on_zoom_combo_activated(self, index: int):
        text = self.zoom_combo.currentText()
        if text == "Fit Width":
            self.fitWidthRequested.emit()
        elif text == "Fit Page":
            self.fitPageRequested.emit()
        else:
            try:
                pct = int(text.replace("%", "").strip())
                self.zoomRequested.emit(pct / 100.0)
            except ValueError:
                pass
