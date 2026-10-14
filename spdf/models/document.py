"""
Document Model for Spdf.
Wraps PyMuPDF (fitz) Document with comprehensive support for loading, saving,
encryption, page manipulation, text search, and annotation baking.
"""

import os
import fitz
from typing import List, Dict, Optional, Tuple
from PySide6.QtCore import QObject, Signal
from spdf.utils.helpers import hex_to_fitz_color, format_file_size


class PDFDocument(QObject):
    """Encapsulates a PDF document, state changes, and manipulation operations."""
    modifiedChanged = Signal(bool)
    pagesChanged = Signal()
    pageRotated = Signal(int, int)  # page_idx, new_rotation

    def __init__(self, file_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.file_path: Optional[str] = file_path
        self.file_name: str = os.path.basename(file_path) if file_path else "Untitled.pdf"
        self.doc: Optional[fitz.Document] = None
        self._is_modified: bool = False
        self._is_encrypted: bool = False
        self._needs_password: bool = False
        
        # Pending in-memory annotations before save:
        # Dict[page_idx, List[dict]]
        self.pending_annotations: Dict[int, List[dict]] = {}

        if file_path:
            self.load_from_path(file_path)
        else:
            self.create_blank()

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @is_modified.setter
    def is_modified(self, val: bool):
        if self._is_modified != val:
            self._is_modified = val
            self.modifiedChanged.emit(val)

    @property
    def page_count(self) -> int:
        return len(self.doc) if self.doc else 0

    @property
    def file_size_str(self) -> str:
        if self.file_path and os.path.exists(self.file_path):
            return format_file_size(os.path.getsize(self.file_path))
        if self.doc:
            return format_file_size(len(self.to_bytes()))
        return "0 B"

    def create_blank(self, width: float = 612.0, height: float = 792.0):
        """Create a new blank single-page PDF document."""
        if self.doc:
            self.doc.close()
        self.doc = fitz.open()
        self.doc.new_page(width=width, height=height)
        self.file_path = None
        self.file_name = "Untitled.pdf"
        self._is_modified = False
        self._is_encrypted = False
        self._needs_password = False
        self.pending_annotations.clear()
        self.pagesChanged.emit()

    def load_from_path(self, path: str):
        """Open PDF document from disk with encryption detection."""
        if self.doc:
            self.doc.close()
        self.file_path = path
        self.file_name = os.path.basename(path)
        self.doc = fitz.open(path)
        self._is_encrypted = self.doc.is_encrypted
        self._needs_password = self._is_encrypted and (self.doc.authenticate("") <= 0)
        self._is_modified = False
        self.pending_annotations.clear()
        self.pagesChanged.emit()

    def authenticate(self, password: str) -> bool:
        """Attempt to authenticate password-protected PDF."""
        if not self.doc or not self._is_encrypted:
            return True
        res = self.doc.authenticate(password)
        if res > 0:
            self._needs_password = False
            self.pagesChanged.emit()
            return True
        return False

    def is_locked(self) -> bool:
        """Check if document still requires password to read pages."""
        return self._needs_password

    def to_bytes(self) -> bytes:
        """Export current document as in-memory bytes."""
        if not self.doc:
            return b""
        return self.doc.tobytes()

    def get_page(self, index: int) -> Optional[fitz.Page]:
        if not self.doc or self.is_locked() or index < 0 or index >= len(self.doc):
            return None
        return self.doc[index]

    def get_page_size(self, index: int) -> Tuple[float, float]:
        """Get (width, height) in PDF points."""
        page = self.get_page(index)
        if page:
            r = page.rect
            return (r.width, r.height)
        return (612.0, 792.0)

    def get_toc(self) -> List[List]:
        """Get Table of Contents hierarchy [ [lvl, title, page, dest], ... ]."""
        if not self.doc or self.is_locked():
            return []
        try:
            return self.doc.get_toc()
        except Exception:
            return []

    # ==================== PAGE MANIPULATION ====================

    def rotate_page(self, page_idx: int, angle_delta: int = 90):
        """Rotate page clockwise by angle_delta (e.g. 90 or -90)."""
        page = self.get_page(page_idx)
        if page:
            new_rot = (page.rotation + angle_delta) % 360
            page.set_rotation(new_rot)
            self.is_modified = True
            self.pageRotated.emit(page_idx, new_rot)
            self.pagesChanged.emit()

    def rotate_all_pages(self, angle_delta: int = 90):
        """Rotate all pages in document."""
        if not self.doc or self.is_locked():
            return
        for idx in range(len(self.doc)):
            page = self.doc[idx]
            new_rot = (page.rotation + angle_delta) % 360
            page.set_rotation(new_rot)
        self.is_modified = True
        self.pagesChanged.emit()

    def delete_page(self, page_idx: int) -> bool:
        """Delete single page. Must leave at least 1 page."""
        if not self.doc or self.is_locked() or len(self.doc) <= 1:
            return False
        if 0 <= page_idx < len(self.doc):
            self.doc.delete_page(page_idx)
            self.is_modified = True
            self.pagesChanged.emit()
            return True
        return False

    def delete_pages(self, indices: List[int]) -> bool:
        """Delete multiple pages safely."""
        if not self.doc or self.is_locked():
            return False
        valid_indices = sorted([i for i in indices if 0 <= i < len(self.doc)], reverse=True)
        if len(valid_indices) >= len(self.doc):
            return False  # Cannot delete all pages
        for idx in valid_indices:
            self.doc.delete_page(idx)
        self.is_modified = True
        self.pagesChanged.emit()
        return True

    def move_page(self, from_idx: int, to_idx: int):
        """Reorder page from index to index."""
        if not self.doc or self.is_locked() or from_idx == to_idx:
            return
        if 0 <= from_idx < len(self.doc) and 0 <= to_idx < len(self.doc):
            self.doc.move_page(from_idx, to_idx)
            self.is_modified = True
            self.pagesChanged.emit()

    def insert_blank_page(self, at_idx: int = -1, width: float = 612.0, height: float = 792.0):
        """Insert a blank page at specified index."""
        if not self.doc or self.is_locked():
            return
        target_idx = at_idx if 0 <= at_idx <= len(self.doc) else len(self.doc)
        self.doc.new_page(target_idx, width=width, height=height)
        self.is_modified = True
        self.pagesChanged.emit()

    def insert_pdf_pages(self, source_path: str, at_idx: int = -1):
        """Insert all pages from another PDF at specified index."""
        if not self.doc or self.is_locked() or not os.path.exists(source_path):
            return
        src_doc = fitz.open(source_path)
        target_idx = at_idx if 0 <= at_idx <= len(self.doc) else len(self.doc)
        self.doc.insert_pdf(src_doc, start_at=target_idx)
        src_doc.close()
        self.is_modified = True
        self.pagesChanged.emit()

    def extract_pages(self, indices: List[int], output_path: str):
        """Extract given page indices into a new standalone PDF."""
        if not self.doc or self.is_locked() or not indices:
            return
        new_doc = fitz.open()
        valid_indices = [i for i in indices if 0 <= i < len(self.doc)]
        new_doc.insert_pdf(self.doc, from_page=valid_indices[0], to_page=valid_indices[0])
        # For non-contiguous, insert individually:
        for idx in valid_indices[1:]:
            new_doc.insert_pdf(self.doc, from_page=idx, to_page=idx)
        new_doc.save(output_path)
        new_doc.close()

    # ==================== ANNOTATIONS & EDITING ====================

    def add_pending_annotation(self, page_idx: int, annot_data: dict):
        """Register an in-memory annotation to be baked upon save or immediately."""
        if page_idx not in self.pending_annotations:
            self.pending_annotations[page_idx] = []
        self.pending_annotations[page_idx].append(annot_data)
        self.is_modified = True

    def bake_annotations(self):
        """
        Permanently bake all pending annotations onto PDF pages using PyMuPDF.
        Supports Highlights, Underlines, Strikethroughs, Ink, Text, Notes, Signatures, Redactions.
        """
        if not self.doc or self.is_locked():
            return

        for page_idx, annot_list in list(self.pending_annotations.items()):
            if page_idx < 0 or page_idx >= len(self.doc):
                continue
            page = self.doc[page_idx]

            for item in annot_list:
                kind = item.get("kind")
                color_hex = item.get("color", "#FFE600")
                rgb = hex_to_fitz_color(color_hex)

                if kind == "highlight":
                    rect = fitz.Rect(item["x"], item["y"], item["x"] + item["w"], item["y"] + item["h"])
                    annot = page.add_highlight_annot(rect)
                    annot.set_colors(stroke=rgb)
                    annot.update()

                elif kind == "underline":
                    rect = fitz.Rect(item["x"], item["y"], item["x"] + item["w"], item["y"] + item["h"])
                    annot = page.add_underline_annot(rect)
                    annot.set_colors(stroke=rgb)
                    annot.update()

                elif kind == "strikethrough":
                    rect = fitz.Rect(item["x"], item["y"], item["x"] + item["w"], item["y"] + item["h"])
                    annot = page.add_strikeout_annot(rect)
                    annot.set_colors(stroke=rgb)
                    annot.update()

                elif kind == "ink":
                    points = item.get("points", [])
                    if len(points) >= 2:
                        stroke_w = item.get("width", 2.0)
                        pair_seq = [[(pt[0], pt[1]) for pt in points]]
                        annot = page.add_ink_annot(pair_seq)
                        annot.set_border(width=stroke_w)
                        annot.set_colors(stroke=rgb)
                        annot.update()

                elif kind == "text":
                    rect = fitz.Rect(item["x"], item["y"], item["x"] + item["w"], item["y"] + item["h"])
                    text = item.get("text", "")
                    f_size = item.get("font_size", 14)
                    page.insert_textbox(rect, text, fontsize=f_size, color=rgb, fontname="helv")

                elif kind == "note":
                    pt = fitz.Point(item["x"], item["y"])
                    comment = item.get("text", "Sticky Note")
                    annot = page.add_text_annot(pt, comment, icon="Note")
                    annot.set_colors(stroke=rgb)
                    annot.update()

                elif kind == "image" or kind == "signature":
                    rect = fitz.Rect(item["x"], item["y"], item["x"] + item["w"], item["y"] + item["h"])
                    img_bytes = item.get("image_bytes")
                    if img_bytes:
                        page.insert_image(rect, stream=img_bytes)

                elif kind == "redact":
                    rect = fitz.Rect(item["x"], item["y"], item["x"] + item["w"], item["y"] + item["h"])
                    page.add_redact_annot(rect, fill=(0, 0, 0))
                    page.apply_redactions()

        self.pending_annotations.clear()

    # ==================== SEARCH ENGINE ====================

    def search_text(self, query: str, match_case: bool = False) -> List[Dict]:
        """
        Fast document-wide text search. Returns list of matches with page, rect, and snippet.
        """
        results = []
        if not self.doc or self.is_locked() or not query.strip():
            return results

        flags = 0 if match_case else fitz.TEXT_DEHYPHENATE
        for page_idx in range(len(self.doc)):
            page = self.doc[page_idx]
            matches = page.search_for(query, flags=flags)
            if matches:
                full_text = page.get_text("text")
                for rect in matches:
                    snippet = self._extract_snippet(full_text, query)
                    results.append({
                        "page": page_idx,
                        "rect": rect,
                        "snippet": snippet
                    })
        return results

    def _extract_snippet(self, text: str, query: str, radius: int = 40) -> str:
        """Create a short excerpt surrounding the search match."""
        idx = text.lower().find(query.lower())
        if idx == -1:
            return query
        start = max(0, idx - radius)
        end = min(len(text), idx + len(query) + radius)
        snip = text[start:end].replace("\n", " ").strip()
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        return f"{prefix}{snip}{suffix}"

    # ==================== EXPORT & CONVERSION ====================

    def extract_all_text(self) -> str:
        """Extract complete document text."""
        if not self.doc or self.is_locked():
            return ""
        text_parts = []
        for idx in range(len(self.doc)):
            page = self.doc[idx]
            text_parts.append(f"--- Page {idx + 1} ---\n" + page.get_text("text"))
        return "\n\n".join(text_parts)

    def export_page_image(self, page_idx: int, output_path: str, dpi: int = 300, fmt: str = "png"):
        """Render single page and save as crisp image (PNG/JPG/TIFF)."""
        page = self.get_page(page_idx)
        if not page:
            return
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=(fmt.lower() == "png"))
        pix.save(output_path)

    # ==================== SAVE & ENCRYPTION ====================

    def save(self, path: Optional[str] = None):
        """Bake all annotations and save to file."""
        self.bake_annotations()
        target_path = path or self.file_path
        if not target_path:
            raise ValueError("No destination path specified.")

        # Save to temporary path if overwriting same file to prevent PyMuPDF lock
        if self.file_path and os.path.abspath(target_path) == os.path.abspath(self.file_path):
            temp_path = target_path + ".tmp.pdf"
            self.doc.save(temp_path, garbage=3, deflate=True)
            self.doc.close()
            if os.path.exists(target_path):
                os.remove(target_path)
            os.rename(temp_path, target_path)
            self.doc = fitz.open(target_path)
        else:
            self.doc.save(target_path, garbage=3, deflate=True)
            self.file_path = target_path
            self.file_name = os.path.basename(target_path)

        self.is_modified = False

    def save_encrypted(self, output_path: str, user_pw: str, owner_pw: str):
        """Save document with standard AES-256 password encryption."""
        self.bake_annotations()
        perm = fitz.PDF_PERM_PRINT | fitz.PDF_PERM_COPY | fitz.PDF_PERM_ANNOTATE
        self.doc.save(
            output_path,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            user_pw=user_pw,
            owner_pw=owner_pw or user_pw,
            permissions=perm,
            garbage=3,
            deflate=True
        )
        self.is_modified = False

    def close(self):
        if self.doc:
            self.doc.close()
            self.doc = None
        self.pending_annotations.clear()
