"""
ui/tabs/tab_interfaces.py — Pestaña de gestión de interfaces.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QGroupBox,
)

from ui.widgets.filterable_list import FilterableListWidget


class TabInterfaces(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        # ── Lista de interfaces ──────────────────────────────
        iface_group = QGroupBox("Interfaces del Router")
        iface_layout = QVBoxLayout(iface_group)
        self.interfaces_list = FilterableListWidget(placeholder="🔍 Filtrar interfaces…")
        self.interfaces_list.setToolTip("Seleccione una interfaz")
        iface_layout.addWidget(self.interfaces_list)
        layout.addWidget(iface_group)

        # ── Reiniciar ────────────────────────────────────────
        restart_group = QGroupBox("Reiniciar Interfaz")
        restart_layout = QHBoxLayout(restart_group)
        self.restart_button = QPushButton("🔁 Reiniciar Interfaz Seleccionada")
        self.restart_button.setObjectName("danger")
        self.restart_button.setEnabled(False)
        restart_layout.addWidget(self.restart_button)
        layout.addWidget(restart_group)

        # ── Cambiar IP ───────────────────────────────────────
        ip_group = QGroupBox("Cambiar Dirección IP")
        ip_layout = QGridLayout(ip_group)

        self.ip_iface_combo = QComboBox()
        self.ip_iface_combo.setToolTip("Seleccione la interfaz destino")

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP/CIDR  ej. 192.168.1.1/24")

        self.change_ip_button = QPushButton("💾 Cambiar IP")
        self.change_ip_button.setEnabled(False)

        ip_layout.addWidget(QLabel("Interfaz:"),      0, 0)
        ip_layout.addWidget(self.ip_iface_combo,       0, 1)
        ip_layout.addWidget(QLabel("Nueva IP/CIDR:"), 0, 2)
        ip_layout.addWidget(self.ip_input,             0, 3)
        ip_layout.addWidget(self.change_ip_button,     0, 4)
        layout.addWidget(ip_group)

        layout.addStretch()
