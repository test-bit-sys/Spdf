"""
Helper utilities for Spdf.
Contains conversions for PDF points, dimensions, file sizes, colors, and geometries.
"""

from PySide6.QtCore import QRectF, QPointF
import fitz


def format_file_size(size_bytes: int) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    if size_bytes <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_idx = 0
    size = float(size_bytes)
    while size >= 1024.0 and unit_idx < len(units) - 1:
        size /= 1024.0
        unit_idx += 1
    if unit_idx == 0:
        return f"{int(size)} {units[unit_idx]}"
    return f"{size:.2f} {units[unit_idx]}"


def points_to_inches(points: float) -> float:
    """Convert PDF points (1/72 inch) to inches."""
    return points / 72.0


def points_to_mm(points: float) -> float:
    """Convert PDF points to millimeters."""
    return points * 25.4 / 72.0


def format_page_dimensions(width_pt: float, height_pt: float) -> str:
    """Format page size into readable inches and points string."""
    w_in = points_to_inches(width_pt)
    h_in = points_to_inches(height_pt)
    return f"{w_in:.2f} × {h_in:.2f} in ({int(width_pt)} × {int(height_pt)} pt)"


def hex_to_fitz_color(hex_color: str) -> tuple:
    """Convert hex string (e.g. #E5A93C) to fitz float tuple (0.0 to 1.0)."""
    clean_hex = hex_color.lstrip("#")
    if len(clean_hex) == 6:
        r = int(clean_hex[0:2], 16) / 255.0
        g = int(clean_hex[2:4], 16) / 255.0
        b = int(clean_hex[4:6], 16) / 255.0
        return (r, g, b)
    elif len(clean_hex) == 8:
        r = int(clean_hex[0:2], 16) / 255.0
        g = int(clean_hex[2:4], 16) / 255.0
        b = int(clean_hex[4:6], 16) / 255.0
        return (r, g, b)
    return (0.0, 0.0, 0.0)


def fitz_color_to_hex(r: float, g: float, b: float) -> str:
    """Convert fitz float RGB tuple to hex string."""
    ir = int(max(0.0, min(1.0, r)) * 255)
    ig = int(max(0.0, min(1.0, g)) * 255)
    ib = int(max(0.0, min(1.0, b)) * 255)
    return f"#{ir:02X}{ig:02X}{ib:02X}"


def fitz_rect_to_qrect(r: fitz.Rect) -> QRectF:
    """Convert fitz.Rect to PySide6 QRectF."""
    return QRectF(r.x0, r.y0, r.width, r.height)


def qrect_to_fitz_rect(r: QRectF) -> fitz.Rect:
    """Convert PySide6 QRectF to fitz.Rect."""
    return fitz.Rect(r.x(), r.y(), r.x() + r.width(), r.y() + r.height())


def parse_page_ranges(range_str: str, max_pages: int) -> list:
    """
    Parse a page range string (e.g., '1-3, 5, 8-10') into a list of 0-based page indices.
    """
    indices = []
    parts = [p.strip() for p in range_str.split(",") if p.strip()]
    for part in parts:
        if "-" in part:
            bounds = part.split("-")
            if len(bounds) == 2:
                try:
                    start = int(bounds[0].strip())
                    end = int(bounds[1].strip())
                    for p in range(start, end + 1):
                        if 1 <= p <= max_pages:
                            indices.append(p - 1)
                except ValueError:
                    continue
        else:
            try:
                p = int(part.strip())
                if 1 <= p <= max_pages:
                    indices.append(p - 1)
            except ValueError:
                continue
    # Preserve order or sort unique: sorted unique
    return sorted(list(set(indices)))


class RecentFilesManager:
    """Manages persistent recent files history using QSettings."""
    SETTINGS_KEY = "recent_files"
    MAX_RECENT = 10

    @classmethod
    def get_recent_files(cls) -> list:
        from PySide6.QtCore import QSettings
        import os
        settings = QSettings("Spdf", "SpdfApp")
        files = settings.value(cls.SETTINGS_KEY, [])
        if isinstance(files, str):
            files = [files] if files else []
        elif not isinstance(files, list):
            files = []
        return [f for f in files if os.path.exists(f)]

    @classmethod
    def add_recent_file(cls, path: str):
        if not path:
            return
        from PySide6.QtCore import QSettings
        import os
        norm_path = os.path.abspath(path)
        current = cls.get_recent_files()
        if norm_path in current:
            current.remove(norm_path)
        current.insert(0, norm_path)
        current = current[:cls.MAX_RECENT]
        settings = QSettings("Spdf", "SpdfApp")
        settings.setValue(cls.SETTINGS_KEY, current)

    @classmethod
    def clear_recent_files(cls):
        from PySide6.QtCore import QSettings
        settings = QSettings("Spdf", "SpdfApp")
        settings.setValue(cls.SETTINGS_KEY, [])
