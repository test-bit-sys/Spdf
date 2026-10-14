"""
Search Panel Component for Spdf.
Performs fast document-wide text queries with match count summary,
context snippets, and interactive match selection.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QCheckBox, QLabel, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from spdf.models.document import PDFDocument
from spdf.icons import get_icon
from spdf.config import Colors


class SearchPanel(QWidget):
    """Full-text search interface with snippet preview list."""
    matchSelected = Signal(int)             # active match index
    matchesUpdated = Signal(list, int)      # all matches, active match index

    def __init__(self, doc: PDFDocument, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.matches = []
        self.current_match_idx = -1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Query input row
        search_row = QHBoxLayout()
        self.query_edit = QLineEdit(self)
        self.query_edit.setPlaceholderText("Search in document...")
        self.query_edit.returnPressed.connect(self.perform_search)
        search_row.addWidget(self.query_edit)

        self.btn_search = QPushButton(self)
        self.btn_search.setIcon(get_icon("search", color="#121212", size=16))
        self.btn_search.setObjectName("PrimaryButton")
        self.btn_search.setToolTip("Search")
        self.btn_search.clicked.connect(self.perform_search)
        search_row.addWidget(self.btn_search)
        layout.addLayout(search_row)

        # Options row
        opt_row = QHBoxLayout()
        self.case_check = QCheckBox("Match Case", self)
        opt_row.addWidget(self.case_check)

        self.btn_prev = QPushButton(self)
        self.btn_prev.setIcon(get_icon("prev_page", size=14))
        self.btn_prev.setToolTip("Previous match")
        self.btn_prev.clicked.connect(self.prev_match)
        opt_row.addWidget(self.btn_prev)

        self.btn_next = QPushButton(self)
        self.btn_next.setIcon(get_icon("next_page", size=14))
        self.btn_next.setToolTip("Next match")
        self.btn_next.clicked.connect(self.next_match)
        opt_row.addWidget(self.btn_next)
        layout.addLayout(opt_row)

        # Summary label
        self.status_label = QLabel("Enter text to find occurrences", self)
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(self.status_label)

        # Results list
        self.results_list = QListWidget(self)
        self.results_list.itemClicked.connect(self._on_result_clicked)
        layout.addWidget(self.results_list)

    def set_document(self, doc: PDFDocument):
        self.doc = doc
        self.clear()

    def clear(self):
        self.matches.clear()
        self.current_match_idx = -1
        self.results_list.clear()
        self.status_label.setText("Enter text to find occurrences")
        self.matchesUpdated.emit([], -1)

    def perform_search(self):
        query = self.query_edit.text().strip()
        if not query or not self.doc or self.doc.is_locked():
            self.clear()
            return

        self.matches = self.doc.search_text(query, match_case=self.case_check.isChecked())
        self.results_list.clear()

        if not self.matches:
            self.status_label.setText(f'No matches found for "{query}"')
            self.matchesUpdated.emit([], -1)
            return

        pages_count = len(set(m["page"] for m in self.matches))
        self.status_label.setText(f"Found {len(self.matches)} matches across {pages_count} pages")

        for idx, m in enumerate(self.matches):
            item = QListWidgetItem(f"Page {m['page'] + 1}: {m['snippet']}")
            item.setData(Qt.UserRole, idx)
            item.setIcon(get_icon("search", color=Colors.ACCENT_GOLD, size=14))
            self.results_list.addItem(item)

        self.current_match_idx = 0
        self.results_list.setCurrentRow(0)
        self.matchesUpdated.emit(self.matches, 0)

    def next_match(self):
        if not self.matches:
            return
        self.current_match_idx = (self.current_match_idx + 1) % len(self.matches)
        self.results_list.setCurrentRow(self.current_match_idx)
        self.matchesUpdated.emit(self.matches, self.current_match_idx)

    def prev_match(self):
        if not self.matches:
            return
        self.current_match_idx = (self.current_match_idx - 1) % len(self.matches)
        self.results_list.setCurrentRow(self.current_match_idx)
        self.matchesUpdated.emit(self.matches, self.current_match_idx)

    def _on_result_clicked(self, item: QListWidgetItem):
        idx = item.data(Qt.UserRole)
        self.current_match_idx = idx
        self.matchesUpdated.emit(self.matches, idx)
