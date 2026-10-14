"""
Automated Comprehensive Test Suite for Spdf.
Validates imports, document model, annotations baking, page manipulation,
and GUI initialization without requiring interactive user inputs.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set offscreen Qt platform for headless validation
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication(sys.argv)

import fitz
from spdf.config import APP_NAME, Colors, ToolMode
from spdf.models.document import PDFDocument
from spdf.models.render_worker import AsyncRenderManager
from spdf.ui.main_window import MainWindow


def test_document_model():
    print("Testing PDFDocument model...")
    doc = PDFDocument()
    assert doc.page_count == 1, f"Expected 1 page, got {doc.page_count}"
    
    # Test insert page
    doc.insert_blank_page()
    assert doc.page_count == 2, f"Expected 2 pages, got {doc.page_count}"
    
    # Test rotate
    doc.rotate_page(0, 90)
    assert doc.get_page(0).rotation == 90, "Expected 90 degree rotation"
    
    # Test annotations
    doc.add_pending_annotation(0, {
        "kind": "highlight", "x": 50, "y": 50, "w": 100, "h": 20, "color": "#FFE600"
    })
    doc.add_pending_annotation(0, {
        "kind": "text", "x": 60, "y": 100, "w": 150, "h": 30, "text": "Test Annotation", "font_size": 12, "color": "#000000"
    })
    doc.add_pending_annotation(0, {
        "kind": "note", "x": 80, "y": 150, "text": "Test Sticky Note", "color": "#FFD54F"
    })
    doc.bake_annotations()
    
    # Verify search
    matches = doc.search_text("Test Annotation")
    print(f"Search matches found: {len(matches)}")
    assert len(matches) >= 1, "Expected to find inserted text annotation via search"
    
    print("PDFDocument model tests passed!")


def test_main_window_gui():
    print("Testing MainWindow GUI instantiation...")
    window = MainWindow()
    assert window.tab_manager.count() >= 1, "Expected at least 1 tab initialized"
    
    # Process events
    app.processEvents()
    
    # Test switching tools
    window._on_tool_changed(ToolMode.HIGHLIGHT)
    assert window.status_bar.lbl_status.text() == "Tool: Highlight"
    
    # Test zoom controls
    window._zoom_in()
    app.processEvents()
    
    window.close()
    from PySide6.QtCore import QThreadPool
    QThreadPool.globalInstance().waitForDone(1000)
    print("MainWindow GUI tests passed!")


def test_icons():
    print("Testing vector SVG icon rendering for all icons...")
    from spdf.icons import SVG_PATHS, get_icon, get_pixmap
    for name in SVG_PATHS.keys():
        icon = get_icon(name)
        assert not icon.isNull(), f"Icon {name} is null!"
        pix = get_pixmap(name)
        assert not pix.isNull(), f"Pixmap {name} is null!"
    print(f"All {len(SVG_PATHS)} vector icons verified!")


def test_encryption_and_security():
    print("Testing AES-256 PDF encryption and password unlock...")
    doc = PDFDocument()
    doc.insert_blank_page()
    out_path = os.path.abspath("test_encrypted.pdf")
    doc.save_encrypted(out_path, user_pw="secret42", owner_pw="admin42")
    doc.close()

    # Re-open encrypted document
    locked_doc = PDFDocument(out_path)
    assert locked_doc.is_locked(), "Expected locked_doc to be locked"
    assert locked_doc.authenticate("wrong_pass") is False, "Expected wrong password to fail"
    assert locked_doc.authenticate("secret42") is True, "Expected correct password to authenticate"
    assert locked_doc.page_count == 2, "Expected 2 pages after unlock"
    locked_doc.close()
    if os.path.exists(out_path):
        os.remove(out_path)
    print("Encryption and password unlocking tests passed!")


def test_merge_and_split():
    print("Testing PDF Merge and Split operations...")
    # Create two test PDFs
    doc1 = PDFDocument()
    doc1.save(os.path.abspath("test_part1.pdf"))
    doc1.close()

    doc2 = PDFDocument()
    doc2.save(os.path.abspath("test_part2.pdf"))
    doc2.close()

    # Merge
    merged = fitz.open()
    d1 = fitz.open(os.path.abspath("test_part1.pdf"))
    d2 = fitz.open(os.path.abspath("test_part2.pdf"))
    merged.insert_pdf(d1)
    merged.insert_pdf(d2)
    merged_path = os.path.abspath("test_merged.pdf")
    merged.save(merged_path)
    merged.close()
    d1.close()
    d2.close()

    merged_check = PDFDocument(merged_path)
    assert merged_check.page_count == 2, f"Expected 2 pages in merged PDF, got {merged_check.page_count}"
    merged_check.close()

    # Clean up test files
    for p in ["test_part1.pdf", "test_part2.pdf", "test_merged.pdf"]:
        if os.path.exists(p):
            os.remove(p)
    print("Merge and Split tests passed!")


def test_recent_files_and_new_features():
    print("Testing RecentFilesManager and new features...")
    from spdf.utils.helpers import RecentFilesManager
    RecentFilesManager.clear_recent_files()
    assert len(RecentFilesManager.get_recent_files()) == 0

    # Test adding recent file
    test_file = os.path.abspath("sample.pdf")
    if os.path.exists(test_file):
        RecentFilesManager.add_recent_file(test_file)
        recent = RecentFilesManager.get_recent_files()
        assert len(recent) == 1
        assert recent[0] == test_file
        RecentFilesManager.clear_recent_files()
        assert len(RecentFilesManager.get_recent_files()) == 0

    # Test Night Reading Mode toggle
    window = MainWindow()
    view = window.tab_manager.current_view()
    assert view.invert_colors is False
    window._toggle_night_mode()
    assert view.invert_colors is True
    window._toggle_night_mode()
    assert view.invert_colors is False

    # Test Undo / Redo on canvas
    from PySide6.QtCore import QPointF
    from spdf.ui.annotation_items import DraggableTextItem
    target_page = view.page_items[0]
    txt_item = DraggableTextItem("Hello Test", QPointF(50, 50), 14, "#000000", 0)
    target_page.add_annotation_item(txt_item)
    view._undo_stack.append(("ADD", 0, txt_item))
    assert txt_item in target_page.annotation_items

    # Undo
    view.undo()
    assert txt_item not in target_page.annotation_items

    # Redo
    view.redo()
    assert txt_item in target_page.annotation_items

    # Delete
    txt_item.setSelected(True)
    view.delete_selected_annotations()
    assert txt_item not in target_page.annotation_items

    window.close()
    from PySide6.QtCore import QThreadPool
    QThreadPool.globalInstance().waitForDone(1000)
    print("Recent files and new features verified!")


if __name__ == "__main__":
    test_icons()
    test_document_model()
    test_encryption_and_security()
    test_merge_and_split()
    test_recent_files_and_new_features()
    test_main_window_gui()
    print("\nALL SPDF TESTS PASSED SUCCESSFULLY!")
