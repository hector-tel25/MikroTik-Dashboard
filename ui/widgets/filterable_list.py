"""
ui/widgets/filterable_list.py — QListWidget con barra de búsqueda integrada.
Filtra los ítems en tiempo real mientras el usuario escribe.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem, QLabel,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon


class FilterableListWidget(QWidget):
    """
    Reemplaza a QListWidget añadiendo un campo de búsqueda superior.
    Expone la misma interfaz básica que QListWidget para que el resto
    del código no necesite cambios (addItem, clear, currentItem, count…).

    Señales:
        currentItemChanged(QListWidgetItem, QListWidgetItem)
        itemDoubleClicked(QListWidgetItem)
    """

    currentItemChanged = pyqtSignal(QListWidgetItem, QListWidgetItem)
    itemDoubleClicked  = pyqtSignal(QListWidgetItem)

    def __init__(self, placeholder: str = "🔍 Filtrar…", parent=None):
        super().__init__(parent)
        self._all_items: list[QListWidgetItem] = []   # copia maestra
        self._build(placeholder)

    def _build(self, placeholder: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # ── Barra de búsqueda ──
        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText(placeholder)
        self._search.setClearButtonEnabled(True)
        self._search.setToolTip("Escribe para filtrar la lista")
        self._search.textChanged.connect(self._apply_filter)
        search_row.addWidget(self._search)

        self._count_label = QLabel("0 items")
        self._count_label.setStyleSheet("color: #666; font-size: 9pt;")
        search_row.addWidget(self._count_label)
        layout.addLayout(search_row)

        # ── Lista ──
        self._list = QListWidget()
        self._list.currentItemChanged.connect(self.currentItemChanged)
        self._list.itemDoubleClicked.connect(self.itemDoubleClicked)
        layout.addWidget(self._list)

    # ── Delegación de la interfaz QListWidget ─────────────────

    def addItem(self, item: QListWidgetItem | str):
        """Añade un ítem y lo guarda en la lista maestra."""
        if isinstance(item, str):
            item = QListWidgetItem(item)
        # Clonar para la lista maestra (con todos los datos)
        master_item = QListWidgetItem(item.text())
        master_item.setData(Qt.ItemDataRole.UserRole,     item.data(Qt.ItemDataRole.UserRole))
        master_item.setData(Qt.ItemDataRole.UserRole + 1, item.data(Qt.ItemDataRole.UserRole + 1))
        self._all_items.append(master_item)
        self._apply_filter(self._search.text())

    def clear(self):
        self._all_items.clear()
        self._list.clear()
        self._update_count()

    def currentItem(self) -> QListWidgetItem | None:
        return self._list.currentItem()

    def count(self) -> int:
        return self._list.count()

    def item(self, row: int) -> QListWidgetItem | None:
        return self._list.item(row)

    def setToolTip(self, tip: str):
        self._list.setToolTip(tip)

    def total_count(self) -> int:
        """Total de ítems (incluyendo los ocultos por el filtro)."""
        return len(self._all_items)

    # ── Lógica de filtrado ────────────────────────────────────

    def _apply_filter(self, text: str):
        query = text.strip().lower()
        self._list.clear()

        for master in self._all_items:
            if query in master.text().lower():
                display = QListWidgetItem(master.text())
                display.setData(Qt.ItemDataRole.UserRole,
                                master.data(Qt.ItemDataRole.UserRole))
                display.setData(Qt.ItemDataRole.UserRole + 1,
                                master.data(Qt.ItemDataRole.UserRole + 1))
                self._list.addItem(display)

        self._update_count()

    def _update_count(self):
        visible = self._list.count()
        total   = len(self._all_items)
        if visible == total:
            self._count_label.setText(f"{total} items")
        else:
            self._count_label.setText(f"{visible} / {total}")
