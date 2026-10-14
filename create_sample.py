"""
Generates sample.pdf with Table of Contents and formatted content for quick demonstration.
"""

import fitz

doc = fitz.open()

# Page 1: Welcome & Overview
p1 = doc.new_page(width=612, height=792)
p1.insert_text(fitz.Point(72, 80), "Spdf - Adobe Acrobat Pro DC Clone", fontsize=22, fontname="helv", color=(0.9, 0.66, 0.24))
p1.insert_text(fitz.Point(72, 110), "Professional PDF Reader, Editor, and Document Management", fontsize=13, fontname="helv", color=(0.3, 0.3, 0.3))

intro = (
    "Welcome to Spdf! This application replicates the workflow, aesthetic, and feature set "
    "of Adobe Acrobat Pro DC natively in Python using PySide6 (Qt6) and PyMuPDF.\n\n"
    "Features implemented in Spdf:\n"
    "  * Modern Adobe Acrobat Dark Theme (#121212 / #1E1E1E) with Gold & Crimson accents\n"
    "  * High-DPI QGraphicsView & QGraphicsScene canvas with smooth drop shadows\n"
    "  * Interactive Page Thumbnails with drag-to-reorder and right-click context menu\n"
    "  * Bookmarks (Table of Contents) tree navigation\n"
    "  * Fast document text search with snippet previews and yellow glow highlights\n"
    "  * Commenting: Highlights, Underlines, Strikethroughs, Freehand Pen, Sticky Notes\n"
    "  * Editing: Draggable text overlays, Rubber stamps (Approved, Draft), Redactions\n"
    "  * Organizing: Merge multiple PDFs, Split by range/burst, Extract, Rotate, Delete\n"
    "  * Security: Digital signature drawing pad modal and AES-256 document encryption\n"
    "  * Exporting: PDF to PNG/JPG/TIFF (72, 150, 300 DPI) and full text extraction"
)
p1.insert_textbox(fitz.Rect(72, 150, 540, 480), intro, fontsize=11, fontname="helv", color=(0.1, 0.1, 0.1))

# Page 2: Sample Content for Annotation Testing
p2 = doc.new_page(width=612, height=792)
p2.insert_text(fitz.Point(72, 80), "Annotation & Editing Playground", fontsize=20, fontname="helv", color=(0.1, 0.1, 0.1))
sample_body = (
    "This page is designed for testing annotation tools.\n\n"
    "1. Test Highlight Tool:\n"
    "Select the Highlight tool from the top ribbon or right Comments panel, and drag over any sentence.\n\n"
    "2. Test Freehand Pen Tool:\n"
    "Draw circles, underlines, or handwriting notes smoothly with customizable thickness and colors.\n\n"
    "3. Test Redaction Tool:\n"
    "Mark any sensitive block on this page for redaction. Notice the dashed crimson outline and [REDACTED] label. "
    "Click 'Apply Redactions Permanently' to sanitize the text permanently.\n\n"
    "4. Test Digital Signature Pad:\n"
    "Open the Protect & Sign panel, click 'Draw Digital Signature', sign in the modal pad, and place it directly onto the document canvas!\n\n"
    "5. Test Save & Bake:\n"
    "Click File -> Save (Ctrl+S). All your live annotations are permanently encoded into the PDF file format!"
)
p2.insert_textbox(fitz.Rect(72, 130, 540, 550), sample_body, fontsize=11, fontname="helv", color=(0.1, 0.1, 0.1))

# Set Table of Contents
doc.set_toc([
    [1, "1. Welcome & Overview", 1],
    [1, "2. Annotation & Editing Playground", 2]
])

doc.save("sample.pdf")
doc.close()
print("Created sample.pdf successfully!")
