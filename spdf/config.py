"""
Application Configuration and Constants for Spdf.
Defines theme colors, zoom presets, tool modes, and layout dimensions.
"""

from enum import Enum, auto


class ToolMode(Enum):
    HAND = auto()
    SELECT = auto()
    HIGHLIGHT = auto()
    UNDERLINE = auto()
    STRIKETHROUGH = auto()
    INK = auto()
    TEXT = auto()
    STICKY_NOTE = auto()
    SIGNATURE = auto()
    STAMP = auto()
    REDACT = auto()


class Colors:
    # Adobe Acrobat Pro DC Dark Theme Palette
    BG_MAIN = "#121212"
    BG_WORKSPACE = "#181818"
    BG_PANEL = "#1E1E1E"
    BG_TOOLBAR = "#242424"
    BG_SURFACE = "#2B2B2B"
    BG_HOVER = "#363636"
    BG_ACTIVE = "#424242"
    BG_INPUT = "#1A1A1A"
    
    # Page Canvas Colors
    PAGE_BG = "#FFFFFF"
    PAGE_BORDER = "#3A3A3A"
    PAGE_SHADOW = "#000000"
    
    # Borders and Dividers
    BORDER_SUBTLE = "#2D2D2D"
    BORDER_LIGHT = "#3D3D3D"
    BORDER_FOCUS = "#E5A93C"
    
    # Accents
    ACCENT_GOLD = "#E5A93C"
    ACCENT_CRIMSON = "#E53935"
    ACCENT_BLUE = "#1E88E5"
    ACCENT_GREEN = "#43A047"
    
    # Typography
    TEXT_PRIMARY = "#EEEEEE"
    TEXT_SECONDARY = "#AAAAAA"
    TEXT_MUTED = "#666666"
    TEXT_DISABLED = "#444444"
    
    # Annotation Defaults
    ANNOT_HIGHLIGHT = "#FFE600"
    ANNOT_UNDERLINE = "#E53935"
    ANNOT_STRIKETHROUGH = "#E53935"
    ANNOT_INK = "#1E88E5"
    ANNOT_TEXT = "#000000"
    ANNOT_REDACT = "#000000"
    ANNOT_NOTE = "#FFD54F"


ZOOM_PRESETS = [0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 3.00, 4.00, 5.00]
DEFAULT_ZOOM = 1.00
MIN_ZOOM = 0.10
MAX_ZOOM = 6.00
PAGE_SPACING = 24  # pixels between pages vertically
PAGE_MARGIN = 24   # horizontal canvas margin

APP_NAME = "Spdf"
APP_TITLE = "Spdf - Professional PDF Editor"
APP_VERSION = "1.0.0"
