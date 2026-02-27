"""
ui/tabs/tab_conexion.py — Pestaña de conexión con el router.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox,
    QGroupBox, QSplitter,
)
from PyQt6.QtCore import Qt

from ui.widgets.filterable_list import FilterableListWidget


class TabConexion(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        # ── Grupo conexión ──────────────────────────────────
        conn_group = QGroupBox("Conectar al Router")
        conn_layout = QGridLayout(conn_group)

        self.host_input = QLineEdit("192.168.88.1")
        self.host_input.setPlaceholderText("IP del router")
        self.host_input.setToolTip("Dirección IP del MikroTik")

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(8728)
        self.port_input.setToolTip("Puerto API de RouterOS (por defecto 8728)")

        self.user_input = QLineEdit("admin")
        self.user_input.setPlaceholderText("Usuario")

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.connect_button = QPushButton("🔌 Conectar")
        self.connect_button.setDefault(True)

        conn_layout.addWidget(QLabel("IP:"),        0, 0)
        conn_layout.addWidget(self.host_input,       0, 1)
        conn_layout.addWidget(QLabel("Puerto:"),     0, 2)
        conn_layout.addWidget(self.port_input,       0, 3)
        conn_layout.addWidget(QLabel("Usuario:"),    0, 4)
        conn_layout.addWidget(self.user_input,       0, 5)
        conn_layout.addWidget(QLabel("Contraseña:"), 0, 6)
        conn_layout.addWidget(self.pass_input,       0, 7)
        conn_layout.addWidget(self.connect_button,   0, 8)
        layout.addWidget(conn_group)

        # ── Listas con filtro ───────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        iface_group = QGroupBox("Interfaces")
        iface_vbox = QVBoxLayout(iface_group)
        self.interfaces_list = FilterableListWidget(
            placeholder="🔍 Filtrar interfaces…")
        self.interfaces_list.setToolTip("Interfaces del router")
        iface_vbox.addWidget(self.interfaces_list)
        splitter.addWidget(iface_group)

        user_group = QGroupBox("Usuarios")
        user_vbox = QVBoxLayout(user_group)
        self.users_list = FilterableListWidget(
            placeholder="🔍 Filtrar usuarios…")
        self.users_list.setToolTip("Usuarios del router")
        user_vbox.addWidget(self.users_list)
        splitter.addWidget(user_group)

        layout.addWidget(splitter)

        self.update_button = QPushButton("🔄 Actualizar Listas")
        self.update_button.setEnabled(False)
        layout.addWidget(
            self.update_button,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
