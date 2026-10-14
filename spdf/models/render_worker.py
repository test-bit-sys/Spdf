"""
Asynchronous High-Resolution PDF Page Renderer.
Uses QThreadPool and isolated PyMuPDF instances to render pages sharply
without blocking the GUI main thread.
"""

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
from PySide6.QtGui import QImage, QPixmap
import fitz
from typing import Dict, Tuple, Optional


class RenderSignals(QObject):
    page_rendered = Signal(int, float, QImage)  # page_idx, zoom, qimage
    thumbnail_rendered = Signal(int, QImage)    # page_idx, qimage
    error = Signal(int, str)


class PageRenderTask(QRunnable):
    """Worker task for high-res page rendering in background thread."""
    def __init__(self, doc_bytes: bytes, page_idx: int, zoom: float, signals: RenderSignals):
        super().__init__()
        self.doc_bytes = doc_bytes
        self.page_idx = page_idx
        self.zoom = zoom
        self.signals = signals
        self.setAutoDelete(True)

    def run(self):
        try:
            doc = fitz.open(stream=self.doc_bytes, filetype="pdf")
            if self.page_idx < 0 or self.page_idx >= len(doc):
                return
            page = doc[self.page_idx]
            matrix = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            format_type = QImage.Format_RGB888 if pix.n < 4 else QImage.Format_RGBA8888
            qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, format_type).copy()
            doc.close()
            try:
                self.signals.page_rendered.emit(self.page_idx, self.zoom, qimg)
            except RuntimeError:
                pass
        except Exception as e:
            try:
                self.signals.error.emit(self.page_idx, str(e))
            except RuntimeError:
                pass


class ThumbnailRenderTask(QRunnable):
    """Worker task for rendering page thumbnails."""
    def __init__(self, doc_bytes: bytes, page_idx: int, target_width: int, signals: RenderSignals):
        super().__init__()
        self.doc_bytes = doc_bytes
        self.page_idx = page_idx
        self.target_width = target_width
        self.signals = signals
        self.setAutoDelete(True)

    def run(self):
        try:
            doc = fitz.open(stream=self.doc_bytes, filetype="pdf")
            if self.page_idx < 0 or self.page_idx >= len(doc):
                return
            page = doc[self.page_idx]
            rect = page.rect
            zoom = self.target_width / max(1.0, rect.width)
            matrix = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            format_type = QImage.Format_RGB888 if pix.n < 4 else QImage.Format_RGBA8888
            qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, format_type).copy()
            doc.close()
            try:
                self.signals.thumbnail_rendered.emit(self.page_idx, qimg)
            except RuntimeError:
                pass
        except Exception as e:
            try:
                self.signals.error.emit(self.page_idx, str(e))
            except RuntimeError:
                pass


class AsyncRenderManager(QObject):
    """
    Manages background rendering queue and in-memory caches.
    """
    pageReady = Signal(int, float, QPixmap)
    thumbnailReady = Signal(int, QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_pool = QThreadPool.globalInstance()
        self.signals = RenderSignals()
        self.signals.page_rendered.connect(self._on_page_rendered)
        self.signals.thumbnail_rendered.connect(self._on_thumbnail_rendered)
        
        self._pixmap_cache: Dict[Tuple[int, float], QPixmap] = {}
        self._thumb_cache: Dict[int, QPixmap] = {}
        self._current_doc_bytes: Optional[bytes] = None

    def set_document_bytes(self, doc_bytes: bytes):
        """Set new document bytes and clear obsolete cache."""
        self._current_doc_bytes = doc_bytes
        self._pixmap_cache.clear()
        self._thumb_cache.clear()

    def get_cached_pixmap(self, page_idx: int, zoom: float) -> Optional[QPixmap]:
        key = (page_idx, round(zoom, 2))
        return self._pixmap_cache.get(key)

    def get_cached_thumbnail(self, page_idx: int) -> Optional[QPixmap]:
        return self._thumb_cache.get(page_idx)

    def request_page(self, page_idx: int, zoom: float):
        key = (page_idx, round(zoom, 2))
        if key in self._pixmap_cache:
            self.pageReady.emit(page_idx, zoom, self._pixmap_cache[key])
            return

        if not self._current_doc_bytes:
            return

        task = PageRenderTask(self._current_doc_bytes, page_idx, zoom, self.signals)
        self.thread_pool.start(task)

    def request_thumbnail(self, page_idx: int, target_width: int = 140):
        if page_idx in self._thumb_cache:
            self.thumbnailReady.emit(page_idx, self._thumb_cache[page_idx])
            return

        if not self._current_doc_bytes:
            return

        task = ThumbnailRenderTask(self._current_doc_bytes, page_idx, target_width, self.signals)
        self.thread_pool.start(task)

    def _on_page_rendered(self, page_idx: int, zoom: float, qimg: QImage):
        pix = QPixmap.fromImage(qimg)
        key = (page_idx, round(zoom, 2))
        self._pixmap_cache[key] = pix
        self.pageReady.emit(page_idx, zoom, pix)

    def _on_thumbnail_rendered(self, page_idx: int, qimg: QImage):
        pix = QPixmap.fromImage(qimg)
        self._thumb_cache[page_idx] = pix
        self.thumbnailReady.emit(page_idx, pix)

    def clear_cache(self):
        self._pixmap_cache.clear()
        self._thumb_cache.clear()
