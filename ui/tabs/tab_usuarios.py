"""
ui/tabs/tab_usuarios.py — Pestaña de gestión de usuarios.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QGroupBox,
)

from ui.widgets.filterable_list import FilterableListWidget


class TabUsuarios(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        # ── Lista de usuarios ────────────────────────────────
        user_group = QGroupBox("Usuarios del Router")
        user_layout = QVBoxLayout(user_group)
        self.users_list = FilterableListWidget(placeholder="🔍 Filtrar usuarios…")
        self.users_list.setToolTip("Seleccione un usuario para eliminarlo")
        user_layout.addWidget(self.users_list)
        layout.addWidget(user_group)

        # ── Crear usuario ────────────────────────────────────
        create_group = QGroupBox("Crear Nuevo Usuario")
        create_layout = QGridLayout(create_group)

        self.new_user_input = QLineEdit()
        self.new_user_input.setPlaceholderText("Nombre de usuario")

        self.new_pass_input = QLineEdit()
        self.new_pass_input.setPlaceholderText("Contraseña")
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.new_pass_confirm_input = QLineEdit()
        self.new_pass_confirm_input.setPlaceholderText("Confirmar contraseña")
        self.new_pass_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.group_select = QComboBox()
        self.group_select.addItems(["read", "write", "full"])

        self.create_user_button = QPushButton("➕ Crear Usuario")
        self.create_user_button.setEnabled(False)

        create_layout.addWidget(QLabel("Nombre:"),           0, 0)
        create_layout.addWidget(self.new_user_input,          0, 1)
        create_layout.addWidget(QLabel("Contraseña:"),        0, 2)
        create_layout.addWidget(self.new_pass_input,          0, 3)
        create_layout.addWidget(QLabel("Confirmar:"),         0, 4)
        create_layout.addWidget(self.new_pass_confirm_input,  0, 5)
        create_layout.addWidget(QLabel("Grupo:"),             0, 6)
        create_layout.addWidget(self.group_select,            0, 7)
        create_layout.addWidget(self.create_user_button,      0, 8)
        layout.addWidget(create_group)

        # ── Eliminar usuario ─────────────────────────────────
        delete_group = QGroupBox("Eliminar Usuario")
        delete_layout = QHBoxLayout(delete_group)
        self.delete_user_button = QPushButton("🗑️ Eliminar Usuario Seleccionado")
        self.delete_user_button.setObjectName("danger")
        self.delete_user_button.setEnabled(False)
        delete_layout.addWidget(self.delete_user_button)
        layout.addWidget(delete_group)

        layout.addStretch()
