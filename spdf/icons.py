"""
Vector SVG Icon Factory for Spdf.
Generates razor-sharp, resolution-independent QIcon objects with custom colors
without using any emojis or low-res raster assets.
"""

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QByteArray, QSize
from spdf.config import Colors

# Curated, professional SVG paths (24x24 viewBox)
SVG_PATHS = {
    "open": (
        '<path d="M20 6h-8l-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/>'
    ),
    "save": (
        '<path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/>'
    ),
    "save_as": (
        '<path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm2 16H5V5h10v4h4v10zm-7-2h2v-2h-2v2zm0-4h2v-2h-2v2z"/>'
    ),
    "print": (
        '<path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/>'
    ),
    "close": (
        '<path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>'
    ),
    "hand": (
        '<path d="M21 9c0-.83-.67-1.5-1.5-1.5-.2 0-.39.04-.57.11C18.66 6.72 17.7 6 16.5 6c-.28 0-.55.06-.8.16-.36-.69-1.07-1.16-1.9-1.16-.38 0-.74.1-1.05.28V3.5C12.75 2.67 12.08 2 11.25 2s-1.5.67-1.5 1.5v8.66l-.77-.42c-.59-.32-1.3-.23-1.8.22l-1.31 1.18 5.76 5.86c.64.65 1.5 1 2.37 1H18c1.66 0 3-1.34 3-3V9z"/>'
    ),
    "select": (
        '<path d="M7 2l12 11.2-5.8.5 3.3 6.8-2.6 1.3-3.2-6.9L7 18.5V2z"/>'
    ),
    "zoom_in": (
        '<path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14zm.5-7H9v2H7v1h2v2h1v-2h2V9h-2z"/>'
    ),
    "zoom_out": (
        '<path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14zM7 9h5v1H7z"/>'
    ),
    "fit_width": (
        '<path d="M3 4v16h2V4H3zm16 0v16h2V4h-2zM7 13h10v-2H7v2zm2.5-3.5L6 12l3.5 2.5V13h5v1.5l3.5-2.5-3.5-2.5V11h-5V9.5z"/>'
    ),
    "fit_page": (
        '<path d="M4 4h6v2H6v4H4V4zm16 0h-6v2h4v4h2V4zM4 20h6v-2H6v-4H4v6zm16 0h-6v-2h4v-4h2v6z"/>'
    ),
    "actual_size": (
        '<path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM8 7h2v10H8zm6 0h2v10h-2z"/>'
    ),
    "prev_page": (
        '<path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>'
    ),
    "next_page": (
        '<path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>'
    ),
    "rotate_cw": (
        '<path d="M15.55 5.55L11 1v3.07C7.06 4.56 4 7.92 4 12s3.05 7.44 7 7.93v-2.02c-2.84-.48-5-2.94-5-5.91s2.16-5.43 5-5.91V10l4.55-4.45zM19.93 11c-.17-1.39-.72-2.66-1.54-3.69l-1.44 1.44c.55.72.92 1.58 1.03 2.52l1.95-.27zm-1.54 5.69l1.44 1.44c.82-1.03 1.37-2.3 1.54-3.69l-1.95-.27c-.11.94-.48 1.8-1.03 2.52z"/>'
    ),
    "rotate_ccw": (
        '<path d="M8.45 5.55L13 1v3.07c3.94.49 7 3.85 7 7.93s-3.05 7.44-7 7.93v-2.02c2.84-.48 5-2.94 5-5.91s-2.16-5.43-5-5.91V10L8.45 5.55zM4.07 11c.17-1.39.72-2.66 1.54-3.69l1.44 1.44c-.55.72-.92 1.58-1.03 2.52l-1.95-.27zm1.54 5.69l-1.44 1.44c-.82-1.03-1.37-2.3-1.54-3.69l1.95-.27c.11.94.48 1.8 1.03 2.52z"/>'
    ),
    "highlight": (
        '<path d="M18.5 2.5c-.83 0-1.5.67-1.5 1.5v2.09l-7.29 7.29c-.39.39-.39 1.02 0 1.41l3.5 3.5c.39.39 1.02.39 1.41 0L21.91 11H24c.83 0 1.5-.67 1.5-1.5s-.67-1.5-1.5-1.5v-4c0-.83-.67-1.5-1.5-1.5h-4zM2 19h20v3H2z"/>'
    ),
    "underline": (
        '<path d="M12 17c3.31 0 6-2.69 6-6V3h-2.5v8c0 1.93-1.57 3.5-3.5 3.5S8.5 12.93 8.5 11V3H6v8c0 3.31 2.69 6 6 6zm-7 2v2h14v-2H5z"/>'
    ),
    "strikethrough": (
        '<path d="M10 19h4v-3h-4v3zM5 4v3h5v3h4V7h5V4H5zM3 13h18v-2H3v2z"/>'
    ),
    "ink": (
        '<path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>'
    ),
    "text": (
        '<path d="M5 4v3h5.5v12h3V7H19V4H5z"/>'
    ),
    "note": (
        '<path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>'
    ),
    "stamp": (
        '<path d="M19 14V6c0-1.1-.9-2-2-2H7c-1.1 0-2 .9-2 2v8H3v4h18v-4h-2zm-2 2H7V6h10v10zm-5-3c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm10 7H2v2h20v-2z"/>'
    ),
    "signature": (
        '<path d="M2.5 18.5c2.5-1 4.5-5 5.5-8 .5-1.5 1-3.5 2-3.5s1.5 1.5 1.5 3c0 3-1 6.5-1 9.5 0 2 1.5 2 2.5 1 2-2 3.5-5 5-8 1-2 2-3 3-3s1 1 1 2.5c0 2-1 4-1.5 6s-.5 4 1 4c2 0 3.5-3 4-5l1.5.5c-.8 3-2.8 6.5-5.5 6.5-3 0-3-3-2.5-5.5.5-2 1.5-4 1.5-5.5 0-.5-.3-.9-.7-.9s-.9.8-1.5 2c-1.5 3-3 6.5-5 8.5-2 2-4.5 1-4.5-1.5 0-2.5 1-6 1-9 0-2-.7-2-1-2s-.7 1.5-1.1 3c-1 3.5-2.5 7.5-5.2 8.9L2.5 18.5z"/>'
    ),
    "redact": (
        '<path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10H7v-2h10v2z"/>'
    ),
    "merge": (
        '<path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 14h-3v3h-2v-3H8v-2h3v-3h2v3h3v2zm-3-7V3.5L18.5 9H13z"/>'
    ),
    "split": (
        '<path d="M9.64 7.64c.23-.5.36-1.05.36-1.64 0-2.21-1.79-4-4-4S2 3.79 2 6s1.79 4 4 4c.59 0 1.14-.13 1.64-.36L10 12l-2.36 2.36C7.14 14.13 6.59 14 6 14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4c0-.59-.13-1.14-.36-1.64L12 14l7 7h3v-1L9.64 7.64zM6 8c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm0 12c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm6-7.5c-.28 0-.5-.22-.5-.5s.22-.5.5-.5.5.22.5.5-.22.5-.5.5zM19 3l-6 6 2 2 7-7V3h-3z"/>'
    ),
    "extract": (
        '<path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>'
    ),
    "delete": (
        '<path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>'
    ),
    "insert": (
        '<path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 14h-3v3h-2v-3H8v-2h3v-3h2v3h3v2zm-3-7V3.5L18.5 9H13z"/>'
    ),
    "search": (
        '<path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>'
    ),
    "sidebar_left": (
        '<path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H9V5h10v14z"/>'
    ),
    "sidebar_right": (
        '<path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-4 16H5V5h10v14z"/>'
    ),
    "lock": (
        '<path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>'
    ),
    "export_image": (
        '<path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>'
    ),
    "export_text": (
        '<path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>'
    ),
    "properties": (
        '<path d="M11 17h2v-6h-2v6zm1-15C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zM11 9h2V7h-2v2z"/>'
    ),
    "thumbnails": (
        '<path d="M4 4h6v6H4V4zm8 0h8v6h-8V4zM4 14h6v6H4v-6zm8 0h8v6h-8v-6z"/>'
    ),
    "bookmarks": (
        '<path d="M19 18l2 1V3c0-1.1-.9-2-2-2H8.99C7.89 1 7 1.9 7 3h10c1.1 0 2 .9 2 2v13zM15 5H5c-1.1 0-2 .9-2 2v16l7-3 7 3V7c0-1.1-.9-2-2-2z"/>'
    ),
    "add": (
        '<path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>'
    ),
    "check": (
        '<path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>'
    ),
    "clear": (
        '<path d="M19.36 10.04L14 4.67c-.78-.78-2.05-.78-2.83 0L3.64 12.2c-.78.78-.78 2.05 0 2.83l5.5 5.5c.78.78 2.05.78 2.83 0l7.39-7.39c.78-.78.78-2.05 0-2.83zM6.46 14.32l4.87-4.87 3.54 3.54-4.87 4.87-3.54-3.54z"/>'
    ),
    "refresh": (
        '<path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>'
    ),
    "undo": (
        '<path d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"/>'
    ),
    "redo": (
        '<path d="M18.4 10.6C16.55 8.99 14.15 8 11.5 8c-4.65 0-8.58 3.03-9.96 7.22L3.9 16c1.05-3.19 4.05-5.5 7.6-5.5 1.95 0 3.73.72 5.12 1.88L13 16h9V7l-3.6 3.6z"/>'
    ),
    "night_mode": (
        '<path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/>'
    ),
    "fullscreen": (
        '<path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>'
    ),
    "single_page": (
        '<path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>'
    ),
    "continuous_page": (
        '<path d="M3 3h18v4H3V3zm0 7h18v4H3v-4zm0 7h18v4H3v-4z"/>'
    ),
    "copy": (
        '<path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>'
    ),
    "recent": (
        '<path d="M13 3a9 9 0 0 0-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0 0 13 21a9 9 0 0 0 0-18zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/>'
    ),
}

_ICON_CACHE = {}


def get_icon(name: str, color: str = Colors.TEXT_PRIMARY, size: int = 24) -> QIcon:
    """
    Get a QIcon rendered cleanly from vector SVG path definition with custom color.
    Caches icons for maximum performance.
    """
    cache_key = (name, color, size)
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    path_data = SVG_PATHS.get(name, SVG_PATHS["properties"])
    svg_str = (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="{color}" xmlns="http://www.w3.org/2000/svg">'
        f'<g fill="{color}">'
        f'{path_data}'
        f'</g>'
        f'</svg>'
    )

    renderer = QSvgRenderer(QByteArray(svg_str.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    renderer.render(painter)
    painter.end()

    icon = QIcon(pixmap)
    _ICON_CACHE[cache_key] = icon
    return icon


def get_pixmap(name: str, color: str = Colors.TEXT_PRIMARY, size: int = 24) -> QPixmap:
    """Get raw QPixmap for direct drawing."""
    path_data = SVG_PATHS.get(name, SVG_PATHS["properties"])
    svg_str = (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="{color}" xmlns="http://www.w3.org/2000/svg">'
        f'<g fill="{color}">'
        f'{path_data}'
        f'</g>'
        f'</svg>'
    )
    renderer = QSvgRenderer(QByteArray(svg_str.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    renderer.render(painter)
    painter.end()
    return pixmap

