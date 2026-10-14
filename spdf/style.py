"""
Comprehensive QSS Stylesheet for Spdf.
Implements the Adobe Acrobat Pro DC modern dark theme with deep charcoal/black
surfaces (#121212, #1E1E1E, #252525), crisp borders (#2D2D2D), and gold/amber highlights (#E5A93C).
"""

from spdf.config import Colors

DARK_THEME_QSS = f"""
/* ==================== GLOBAL BASE ==================== */
* {{
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: {Colors.TEXT_PRIMARY};
    outline: none;
}}

QMainWindow, QDialog {{
    background-color: {Colors.BG_MAIN};
}}

QWidget {{
    background-color: transparent;
}}

QWidget#CentralContainer, QWidget#WorkspaceArea {{
    background-color: {Colors.BG_WORKSPACE};
}}

/* ==================== MENU BAR & MENUS ==================== */
QMenuBar {{
    background-color: {Colors.BG_MAIN};
    border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    padding: 2px 6px;
    spacing: 4px;
}}

QMenuBar::item {{
    background: transparent;
    padding: 5px 10px;
    border-radius: 4px;
    color: {Colors.TEXT_PRIMARY};
}}

QMenuBar::item:selected {{
    background-color: {Colors.BG_HOVER};
    color: {Colors.ACCENT_GOLD};
}}

QMenuBar::item:pressed {{
    background-color: {Colors.BG_ACTIVE};
}}

QMenu {{
    background-color: {Colors.BG_PANEL};
    border: 1px solid {Colors.BORDER_LIGHT};
    border-radius: 6px;
    padding: 4px 0px;
}}

QMenu::item {{
    padding: 6px 28px 6px 24px;
    border-radius: 3px;
    margin: 1px 4px;
    color: {Colors.TEXT_PRIMARY};
}}

QMenu::item:selected {{
    background-color: {Colors.BG_HOVER};
    color: {Colors.ACCENT_GOLD};
}}

QMenu::separator {{
    height: 1px;
    background: {Colors.BORDER_SUBTLE};
    margin: 4px 8px;
}}

/* ==================== TOOLBARS & QUICK ACTIONS ==================== */
QToolBar {{
    background-color: {Colors.BG_TOOLBAR};
    border-top: none;
    border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    border-left: none;
    border-right: none;
    padding: 4px 8px;
    spacing: 4px;
}}

QToolBar::separator {{
    width: 1px;
    background-color: {Colors.BORDER_SUBTLE};
    margin: 4px 6px;
}}

QToolButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 3px 5px;
    margin: 1px;
    color: {Colors.TEXT_PRIMARY};
}}

QToolButton:hover {{
    background-color: {Colors.BG_HOVER};
    border: 1px solid {Colors.BORDER_LIGHT};
}}

QToolButton:pressed {{
    background-color: {Colors.BG_ACTIVE};
}}

QToolButton:checked {{
    background-color: rgba(229, 169, 60, 0.18);
    border: 1px solid {Colors.ACCENT_GOLD};
    color: {Colors.ACCENT_GOLD};
}}

QToolButton#AccentButton {{
    background-color: {Colors.ACCENT_GOLD};
    color: #121212;
    font-weight: bold;
    padding: 4px 10px;
}}

QToolButton#AccentButton:hover {{
    background-color: #F0B74E;
}}

/* ==================== DOCUMENT TAB BAR ==================== */
QTabWidget#DocumentTabs::pane {{
    border: none;
    background-color: {Colors.BG_WORKSPACE};
}}

QTabBar {{
    background-color: {Colors.BG_MAIN};
    border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    qproperty-drawBase: 0;
}}

QTabBar::tab {{
    background-color: #181818;
    color: {Colors.TEXT_SECONDARY};
    padding: 8px 18px 8px 14px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-bottom: none;
    margin-right: 2px;
    min-width: 100px;
    max-width: 240px;
}}

QTabBar::tab:hover {{
    background-color: {Colors.BG_HOVER};
    color: {Colors.TEXT_PRIMARY};
}}

QTabBar::tab:selected {{
    background-color: {Colors.BG_PANEL};
    color: {Colors.ACCENT_GOLD};
    border-top: 2px solid {Colors.ACCENT_GOLD};
    font-weight: 600;
}}

QTabBar::close-button {{
    subcontrol-position: right;
    margin-left: 6px;
    padding: 2px;
    border-radius: 2px;
}}

QTabBar::close-button:hover {{
    background-color: {Colors.ACCENT_CRIMSON};
}}

/* ==================== SIDEBAR & DOCKS ==================== */
QDockWidget {{
    titlebar-close-icon: url(none);
    titlebar-normal-icon: url(none);
    border: 1px solid {Colors.BORDER_SUBTLE};
}}

QDockWidget::title {{
    background-color: {Colors.BG_TOOLBAR};
    padding: 8px 12px;
    font-weight: bold;
    border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    color: {Colors.TEXT_PRIMARY};
}}

QTabWidget#SidebarTabs::pane {{
    border: 1px solid {Colors.BORDER_SUBTLE};
    background-color: {Colors.BG_PANEL};
}}

QTabWidget#SidebarTabs QTabBar::tab {{
    background-color: {Colors.BG_MAIN};
    padding: 5px 6px;
    font-size: 11px;
    min-width: 0px;
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-bottom: none;
    margin-right: 1px;
}}

QTabWidget#SidebarTabs QTabBar::tab:selected {{
    background-color: {Colors.BG_PANEL};
    color: {Colors.ACCENT_GOLD};
    border-top: 2px solid {Colors.ACCENT_GOLD};
}}

/* ==================== BUTTONS ==================== */
QPushButton {{
    background-color: {Colors.BG_SURFACE};
    border: 1px solid {Colors.BORDER_LIGHT};
    border-radius: 4px;
    padding: 6px 14px;
    color: {Colors.TEXT_PRIMARY};
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {Colors.BG_HOVER};
    border-color: #555555;
}}

QPushButton:pressed {{
    background-color: {Colors.BG_ACTIVE};
}}

QPushButton:disabled {{
    background-color: #1A1A1A;
    color: {Colors.TEXT_DISABLED};
    border-color: #262626;
}}

QPushButton#PrimaryButton {{
    background-color: {Colors.ACCENT_GOLD};
    color: #121212;
    font-weight: bold;
    border: 1px solid #D49B30;
}}

QPushButton#PrimaryButton:hover {{
    background-color: #F0B74E;
}}

QPushButton#DangerButton {{
    background-color: {Colors.ACCENT_CRIMSON};
    color: #FFFFFF;
    font-weight: bold;
    border: 1px solid #C62828;
}}

QPushButton#DangerButton:hover {{
    background-color: #EF5350;
}}

/* ==================== INPUT FIELDS & CONTROLS ==================== */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {Colors.BG_INPUT};
    border: 1px solid {Colors.BORDER_LIGHT};
    border-radius: 4px;
    padding: 5px 8px;
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.ACCENT_GOLD};
    selection-color: #121212;
}}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {Colors.ACCENT_GOLD};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: {Colors.BG_PANEL};
    border: 1px solid {Colors.BORDER_LIGHT};
    selection-background-color: {Colors.BG_HOVER};
    selection-color: {Colors.ACCENT_GOLD};
    padding: 4px;
}}

/* ==================== LISTS & TREES ==================== */
QListWidget, QTreeWidget, QListView, QTreeView {{
    background-color: {Colors.BG_PANEL};
    border: 1px solid {Colors.BORDER_SUBTLE};
    color: {Colors.TEXT_PRIMARY};
    padding: 4px;
    outline: none;
}}

QListWidget::item, QTreeWidget::item {{
    padding: 6px 8px;
    border-radius: 4px;
    margin-bottom: 2px;
}}

QListWidget::item:hover, QTreeWidget::item:hover {{
    background-color: {Colors.BG_HOVER};
}}

QListWidget::item:selected, QTreeWidget::item:selected {{
    background-color: rgba(229, 169, 60, 0.2);
    color: {Colors.ACCENT_GOLD};
    border-left: 2px solid {Colors.ACCENT_GOLD};
}}

QListWidget#ThumbnailListWidget::item {{
    padding: 6px;
    border: 1px solid transparent;
    border-radius: 6px;
    background-color: transparent;
}}

QListWidget#ThumbnailListWidget::item:hover {{
    background-color: {Colors.BG_HOVER};
    border: 1px solid {Colors.BORDER_LIGHT};
}}

QListWidget#ThumbnailListWidget::item:selected {{
    background-color: rgba(229, 169, 60, 0.15);
    border: 1px solid {Colors.ACCENT_GOLD};
    border-radius: 6px;
    color: {Colors.ACCENT_GOLD};
}}

/* ==================== SCROLL BARS ==================== */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: #404040;
    min-height: 24px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: #555555;
}}

QScrollBar::handle:vertical:pressed {{
    background: {Colors.ACCENT_GOLD};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: #404040;
    min-width: 24px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #555555;
}}

QScrollBar::handle:horizontal:pressed {{
    background: {Colors.ACCENT_GOLD};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ==================== SPLITTER ==================== */
QSplitter::handle {{
    background-color: {Colors.BORDER_SUBTLE};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

/* ==================== STATUS BAR ==================== */
QStatusBar {{
    background-color: #141414;
    border-top: 1px solid {Colors.BORDER_SUBTLE};
    color: {Colors.TEXT_SECONDARY};
    padding: 2px 8px;
}}

QStatusBar QLabel {{
    color: {Colors.TEXT_SECONDARY};
    padding: 0 6px;
}}

/* ==================== TOOLTIPS ==================== */
QToolTip {{
    background-color: {Colors.BG_PANEL};
    border: 1px solid {Colors.ACCENT_GOLD};
    color: {Colors.TEXT_PRIMARY};
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
}}

/* ==================== GROUP BOX ==================== */
QGroupBox {{
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
    color: {Colors.TEXT_PRIMARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 4px;
    color: {Colors.ACCENT_GOLD};
}}
"""
