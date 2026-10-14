"""
Main Application Window for Spdf (Adobe Acrobat Pro DC Clone).
Assembles the menu bar, ribbon bar, left collapsible sidebar, center tabbed workspace,
right collapsible tools panel, and status bar into a unified, high-performance interface.
"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QFileDialog, QMessageBox
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt, QUrl
from spdf.config import APP_TITLE, Colors, ToolMode
from spdf.models.document import PDFDocument
from spdf.ui.menu_bar import SpdfMenuBar
from spdf.ui.ribbon_bar import RibbonBar
from spdf.ui.tab_manager import TabManager
from spdf.ui.left_sidebar.sidebar import LeftSidebar
from spdf.ui.right_tools.tools_panel import RightToolsPanel
from spdf.ui.status_bar import SpdfStatusBar
from spdf.ui.dialogs.password_dialog import PasswordPromptDialog
from spdf.ui.dialogs.properties_dialog import PropertiesDialog
from spdf.utils.helpers import RecentFilesManager


class MainWindow(QMainWindow):
    """Adobe Acrobat Pro DC clone top-level application window."""
    def __init__(self, initial_pdf: str = None):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1340, 880)
        self.setAcceptDrops(True)

        # 1. Menu Bar
        self.menu_bar = SpdfMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # 2. Ribbon Bar
        self.ribbon = RibbonBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.ribbon)

        # 3. Central Layout with Splitters
        central_widget = QWidget(self)
        central_widget.setObjectName("CentralContainer")
        self.setCentralWidget(central_widget)

        central_layout = QHBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self.main_splitter = QSplitter(Qt.Horizontal, central_widget)
        central_layout.addWidget(self.main_splitter)

        # Left Sidebar (Thumbnails, Bookmarks, Search)
        self.left_sidebar = LeftSidebar(None, None, self.main_splitter)
        self.main_splitter.addWidget(self.left_sidebar)

        # Center Workspace (Tab Manager)
        self.tab_manager = TabManager(self.main_splitter)
        self.main_splitter.addWidget(self.tab_manager)

        # Right Tools Panel (Organize, Edit, Comment, Protect, Export)
        self.right_tools = RightToolsPanel(None, self.main_splitter)
        self.main_splitter.addWidget(self.right_tools)

        # Initial splitter proportions: Left=260px, Center=remaining, Right=280px
        self.main_splitter.setSizes([260, 800, 280])

        # 4. Status Bar
        self.status_bar = SpdfStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Connect Signals & Wiring
        self._wire_signals()

        # Load initial document or create welcome tab
        if initial_pdf and os.path.exists(initial_pdf):
            self.open_pdf_file(initial_pdf)
        else:
            self.create_blank_document()

    def _wire_signals(self):
        # Menu Bar Actions
        self.menu_bar.newDocumentRequested.connect(self.create_blank_document)
        self.menu_bar.openDocumentRequested.connect(self.prompt_open_file)
        self.menu_bar.openRecentRequested.connect(self.open_pdf_file)
        self.menu_bar.saveDocumentRequested.connect(self.save_current_document)
        self.menu_bar.saveAsDocumentRequested.connect(self.save_as_current_document)
        self.menu_bar.closeTabRequested.connect(self.tab_manager.close_current_tab)
        self.menu_bar.propertiesRequested.connect(self._show_properties)
        self.menu_bar.printRequested.connect(self._print_document)
        self.menu_bar.exitRequested.connect(self.close)

        self.menu_bar.undoRequested.connect(self._undo)
        self.menu_bar.redoRequested.connect(self._redo)
        self.menu_bar.copyRequested.connect(self._copy_selection)
        self.menu_bar.deleteAnnotationRequested.connect(self._delete_annotation)
        self.menu_bar.findRequested.connect(self._on_find_requested)

        self.menu_bar.zoomInRequested.connect(self._zoom_in)
        self.menu_bar.zoomOutRequested.connect(self._zoom_out)
        self.menu_bar.zoomActualRequested.connect(self._zoom_actual)
        self.menu_bar.fitWidthRequested.connect(self._fit_width)
        self.menu_bar.fitPageRequested.connect(self._fit_page)
        self.menu_bar.rotateCWRequested.connect(self._rotate_cw)
        self.menu_bar.rotateCCWRequested.connect(self._rotate_ccw)
        self.menu_bar.toggleSidebarRequested.connect(self._toggle_left_sidebar)
        self.menu_bar.toggleToolsRequested.connect(self._toggle_right_panel)
        self.menu_bar.toggleNightModeRequested.connect(self._toggle_night_mode)
        self.menu_bar.fullscreenRequested.connect(self._toggle_fullscreen)
        self.menu_bar.showToolCategory.connect(self._show_tool_category)

        # Ribbon Bar Actions
        self.ribbon.toggleLeftSidebar.connect(self._toggle_left_sidebar)
        self.ribbon.toggleRightPanel.connect(self._toggle_right_panel)
        self.ribbon.undoRequested.connect(self._undo)
        self.ribbon.redoRequested.connect(self._redo)
        self.ribbon.deleteAnnotationRequested.connect(self._delete_annotation)
        self.ribbon.toggleNightMode.connect(self._toggle_night_mode)
        self.ribbon.toolChanged.connect(self._on_tool_changed)
        self.ribbon.pageJumpRequested.connect(self._on_page_jump)
        self.ribbon.zoomRequested.connect(self._on_zoom_requested)
        self.ribbon.fitWidthRequested.connect(self._fit_width)
        self.ribbon.fitPageRequested.connect(self._fit_page)
        self.ribbon.rotateCWRequested.connect(self._rotate_cw)
        self.ribbon.rotateCCWRequested.connect(self._rotate_ccw)

        # Tab Manager Actions
        self.tab_manager.currentDocumentChanged.connect(self._on_current_document_changed)
        self.tab_manager.home_screen.openRequested.connect(self.prompt_open_file)
        self.tab_manager.home_screen.blankRequested.connect(self.create_blank_document)
        self.tab_manager.home_screen.mergeRequested.connect(lambda: self.right_tools.organize_panel._on_merge())
        self.tab_manager.home_screen.fileSelected.connect(self.open_pdf_file)

        # Left Sidebar Actions
        self.left_sidebar.pageJumpRequested.connect(self._on_page_jump)
        self.left_sidebar.documentModified.connect(self._refresh_current_view)
        self.left_sidebar.matchesUpdated.connect(self._on_search_matches_updated)

        # Right Tools Actions
        self.right_tools.toolRequested.connect(self._on_tool_changed)
        self.right_tools.colorChanged.connect(self._on_color_changed)
        self.right_tools.strokeWidthChanged.connect(self._on_stroke_width_changed)
        self.right_tools.fontSizeChanged.connect(self._on_font_size_changed)
        self.right_tools.stampSelected.connect(self._on_stamp_selected)
        self.right_tools.documentModified.connect(self._refresh_current_view)
        self.right_tools.pagesRebuilt.connect(self._on_pages_rebuilt)

    # ==================== DOCUMENT MANAGEMENT ====================

    def prompt_open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*.*)"
        )
        if path:
            self.open_pdf_file(path)

    def open_pdf_file(self, file_path: str):
        try:
            doc = PDFDocument(file_path, self)

            # Check if password protected
            if doc.is_locked():
                pw_dlg = PasswordPromptDialog(doc.file_name, self)
                while doc.is_locked():
                    if pw_dlg.exec_():
                        password = pw_dlg.get_password()
                        if doc.authenticate(password):
                            break
                        else:
                            QMessageBox.warning(self, "Invalid Password", "Incorrect password. Please try again.")
                    else:
                        # Canceled password prompt
                        doc.close()
                        return

            tab = self.tab_manager.add_document(doc)
            self._bind_tab_view(tab)
            RecentFilesManager.add_recent_file(file_path)
            self.status_bar.set_status_message(f'Opened "{doc.file_name}"')
        except Exception as e:
            QMessageBox.critical(self, "Open Error", f"Failed to open PDF document:\n{str(e)}")

    def create_blank_document(self):
        doc = PDFDocument(parent=self)
        tab = self.tab_manager.add_document(doc)
        self._bind_tab_view(tab)
        self.status_bar.set_status_message("Created new blank PDF document.")

    def save_current_document(self):
        doc = self.tab_manager.current_doc()
        if not doc:
            return
        view = self.tab_manager.current_view()
        if view:
            view.sync_annotations_to_document()
        if doc.file_path:
            try:
                doc.save()
                RecentFilesManager.add_recent_file(doc.file_path)
                self.status_bar.set_status_message(f'Saved "{doc.file_name}"')
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save PDF:\n{str(e)}")
        else:
            self.save_as_current_document()

    def save_as_current_document(self):
        doc = self.tab_manager.current_doc()
        if not doc:
            return
        view = self.tab_manager.current_view()
        if view:
            view.sync_annotations_to_document()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF As", doc.file_name, "PDF Files (*.pdf)"
        )
        if path:
            try:
                doc.save(path)
                RecentFilesManager.add_recent_file(path)
                self.setWindowTitle(f"{doc.file_name} - {APP_TITLE}")
                self.status_bar.set_status_message(f'Saved as "{doc.file_name}"')
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save PDF:\n{str(e)}")

    def _show_properties(self):
        doc = self.tab_manager.current_doc()
        if doc:
            dlg = PropertiesDialog(doc, self)
            dlg.exec_()

    def _print_document(self):
        doc = self.tab_manager.current_doc()
        if not doc or doc.is_locked() or doc.page_count == 0:
            QMessageBox.information(self, "Print", "No active document to print.")
            return

        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        from PySide6.QtGui import QPainter, QImage

        printer = QPrinter(QPrinter.HighResolution)
        printer.setDocName(doc.file_name)
        dlg = QPrintDialog(printer, self)
        dlg.setWindowTitle(f"Print - {doc.file_name}")

        if dlg.exec_():
            view = self.tab_manager.current_view()
            if view:
                view.sync_annotations_to_document()
            doc.bake_annotations()

            painter = QPainter(printer)
            for idx in range(doc.page_count):
                if idx > 0:
                    printer.newPage()
                page = doc.get_page(idx)
                pix = page.get_pixmap(dpi=300)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888).copy()
                target_rect = printer.pageRect(QPrinter.DevicePixel).toRect()
                scaled_img = img.scaled(target_rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawImage(target_rect.topLeft(), scaled_img)
            painter.end()
            self.status_bar.set_status_message(f'Printed "{doc.file_name}" successfully.')

    # ==================== VIEW BINDING & EVENTS ====================

    def _bind_tab_view(self, tab):
        view = tab.view
        view.pageChanged.connect(self._on_view_page_changed)
        view.zoomChanged.connect(self._on_view_zoom_changed)
        view.annotationAdded.connect(lambda _: self._on_annotation_added())
        view.statusMessageRequested.connect(self.status_bar.set_status_message)

    def _on_current_document_changed(self, doc: PDFDocument, view):
        if not doc or not view:
            self.setWindowTitle(APP_TITLE)
            self.left_sidebar.hide()
            self.right_tools.hide()
            self.ribbon.setEnabled(False)
            self.status_bar.set_status_message("No open document")
            return

        self.ribbon.setEnabled(True)
        self.left_sidebar.show()
        self.right_tools.show()
        self.setWindowTitle(f"{doc.file_name} - {APP_TITLE}")

        # Update left sidebar & right tools
        cur_tab = self.tab_manager.current_tab()
        render_mgr = cur_tab.render_mgr if cur_tab else None
        self.left_sidebar.set_document(doc, render_mgr)
        self.right_tools.set_document(doc)

        # Update metrics
        cur_page = view.get_most_visible_page()
        w, h = doc.get_page_size(cur_page)
        self.ribbon.update_page_info(cur_page, doc.page_count)
        self.ribbon.update_zoom_display(view.zoom_factor)
        self.status_bar.update_metrics(
            cur_page, doc.page_count, w, h, doc.file_size_str, view.zoom_factor
        )

    def _on_view_page_changed(self, page_idx: int):
        doc = self.tab_manager.current_doc()
        view = self.tab_manager.current_view()
        if doc and view:
            w, h = doc.get_page_size(page_idx)
            self.ribbon.update_page_info(page_idx, doc.page_count)
            self.left_sidebar.select_page(page_idx)
            self.status_bar.update_metrics(
                page_idx, doc.page_count, w, h, doc.file_size_str, view.zoom_factor
            )

    def _on_view_zoom_changed(self, zoom: float):
        self.ribbon.update_zoom_display(zoom)
        doc = self.tab_manager.current_doc()
        view = self.tab_manager.current_view()
        if doc and view:
            cur_page = view.get_most_visible_page()
            w, h = doc.get_page_size(cur_page)
            self.status_bar.update_metrics(
                cur_page, doc.page_count, w, h, doc.file_size_str, zoom
            )

    def _on_annotation_added(self):
        doc = self.tab_manager.current_doc()
        if doc:
            doc.is_modified = True

    def _refresh_current_view(self):
        view = self.tab_manager.current_view()
        if view:
            view.rebuild_pages()
        self.left_sidebar.refresh()

    def _on_pages_rebuilt(self):
        self._refresh_current_view()
        doc = self.tab_manager.current_doc()
        view = self.tab_manager.current_view()
        if doc and view:
            self._on_view_page_changed(view.get_most_visible_page())

    # ==================== ACTIONS & TOOL CONTROLS ====================

    def _undo(self):
        view = self.tab_manager.current_view()
        if view:
            view.undo()

    def _redo(self):
        view = self.tab_manager.current_view()
        if view:
            view.redo()

    def _copy_selection(self):
        view = self.tab_manager.current_view()
        if view:
            if not view.copy_selected_text():
                self.status_bar.set_status_message("No text or content selected to copy.")

    def _delete_annotation(self):
        view = self.tab_manager.current_view()
        if view:
            view.delete_selected_annotations()

    def _toggle_night_mode(self):
        view = self.tab_manager.current_view()
        if view:
            is_night = view.toggle_invert_colors()
            self.ribbon.btn_night.setChecked(is_night)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _on_page_jump(self, page_idx: int):
        view = self.tab_manager.current_view()
        if view:
            view.jump_to_page(page_idx)

    def _on_tool_changed(self, mode: ToolMode):
        view = self.tab_manager.current_view()
        if view:
            view.set_tool_mode(mode)
        self.status_bar.set_status_message(f"Tool: {mode.name.title()}")

    def _on_color_changed(self, color_hex: str):
        view = self.tab_manager.current_view()
        if view:
            view.active_color = color_hex

    def _on_stroke_width_changed(self, width: float):
        view = self.tab_manager.current_view()
        if view:
            view.active_stroke_width = width

    def _on_font_size_changed(self, size: int):
        view = self.tab_manager.current_view()
        if view:
            view.active_font_size = size

    def _on_stamp_selected(self, pixmap, raw_bytes: bytes):
        view = self.tab_manager.current_view()
        if view:
            view.active_stamp_pixmap = pixmap
            view.active_stamp_bytes = raw_bytes
            view.set_tool_mode(ToolMode.STAMP)

    def _on_zoom_requested(self, delta_or_factor: float):
        view = self.tab_manager.current_view()
        if not view:
            return
        if delta_or_factor == 1.0:
            view.zoom_in()
        elif delta_or_factor == -1.0:
            view.zoom_out()
        else:
            view.set_zoom(delta_or_factor)

    def _zoom_in(self):
        view = self.tab_manager.current_view()
        if view:
            view.zoom_in()

    def _zoom_out(self):
        view = self.tab_manager.current_view()
        if view:
            view.zoom_out()

    def _zoom_actual(self):
        view = self.tab_manager.current_view()
        if view:
            view.set_zoom(1.00)

    def _fit_width(self):
        view = self.tab_manager.current_view()
        if view:
            view.fit_width()

    def _fit_page(self):
        view = self.tab_manager.current_view()
        if view:
            view.fit_page()

    def _rotate_cw(self):
        doc = self.tab_manager.current_doc()
        view = self.tab_manager.current_view()
        if doc and view:
            cur_page = view.get_most_visible_page()
            doc.rotate_page(cur_page, 90)
            view.rebuild_pages()
            self.left_sidebar.refresh()

    def _rotate_ccw(self):
        doc = self.tab_manager.current_doc()
        view = self.tab_manager.current_view()
        if doc and view:
            cur_page = view.get_most_visible_page()
            doc.rotate_page(cur_page, -90)
            view.rebuild_pages()
            self.left_sidebar.refresh()

    def _toggle_left_sidebar(self):
        self.left_sidebar.setVisible(not self.left_sidebar.isVisible())

    def _toggle_right_panel(self):
        self.right_tools.setVisible(not self.right_tools.isVisible())

    def _show_tool_category(self, key: str):
        self.right_tools.show()
        self.right_tools.show_category(key)

    def _on_find_requested(self):
        self.left_sidebar.show()
        self.left_sidebar.tabs.setCurrentIndex(2)  # Search tab
        self.left_sidebar.search_tab.query_edit.setFocus()
        self.left_sidebar.search_tab.query_edit.selectAll()

    def _on_search_matches_updated(self, matches: list, active_idx: int):
        view = self.tab_manager.current_view()
        if view:
            view.display_search_matches(matches, active_idx)

    # ==================== DRAG & DROP ====================

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    return
        super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            local_path = url.toLocalFile()
            if local_path.lower().endswith(".pdf"):
                self.open_pdf_file(local_path)
        event.acceptProposedAction()
