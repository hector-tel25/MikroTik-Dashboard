"""
ui/main_window.py — Ventana principal.
Orquesta las pestañas y conecta la UI con la capa de servicio (RouterAPI).
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QStatusBar, QListWidgetItem, QMessageBox, QApplication,
)
from PyQt6.QtCore import QTimer, Qt

from core.api_service import RouterAPI
from core.worker import NetworkWorker
from utils.validators import is_valid_cidr, is_valid_username
from ui.styles import APP_STYLE
from ui.tabs.tab_conexion import TabConexion
from ui.tabs.tab_usuarios import TabUsuarios
from ui.tabs.tab_interfaces import TabInterfaces
from ui.tabs.tab_monitoreo import TabMonitoreo
from ui.widgets.loading_overlay import LoadingOverlay


class MikroTikDashboard(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MikroTik Dashboard Pro")
        self.setGeometry(100, 100, 1350, 900)
        self.setStyleSheet(APP_STYLE)

        self._api    = RouterAPI()
        self._worker = None        # hilo de operación activo
        self._poll_worker = None   # hilo de polling de tráfico
        self._monitoring  = False

        # ── Barra de estado ──
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._set_status("Desconectado", error=True)

        # ── Timer de monitoreo ──
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll_traffic)

        # ── Layout principal ──
        central = QWidget()
        self.setCentralWidget(central)
        QVBoxLayout(central).addWidget(self._build_tabs())

        # ── Overlay de carga (encima de todo) ──
        self._overlay = LoadingOverlay(self)

        self._set_tabs_enabled(False)

    # ─────────────────────────────────────────────────────────
    # Construcción de la ventana
    # ─────────────────────────────────────────────────────────

    def _build_tabs(self) -> QTabWidget:
        self.tabs = QTabWidget()

        self.tab_conexion   = TabConexion()
        self.tab_usuarios   = TabUsuarios()
        self.tab_interfaces = TabInterfaces()
        self.tab_monitoreo  = TabMonitoreo()

        self.tabs.addTab(self.tab_conexion,   "🔌 Conexión")
        self.tabs.addTab(self.tab_usuarios,   "👥 Usuarios")
        self.tabs.addTab(self.tab_interfaces, "🌐 Interfaces")
        self.tabs.addTab(self.tab_monitoreo,  "📊 Monitoreo")

        # Conectar señales de UI → controladores
        self.tab_conexion.connect_button.clicked.connect(self._on_connect)
        self.tab_conexion.pass_input.returnPressed.connect(self._on_connect)
        self.tab_conexion.update_button.clicked.connect(self._on_refresh)

        self.tab_usuarios.create_user_button.clicked.connect(self._on_create_user)
        self.tab_usuarios.delete_user_button.clicked.connect(self._on_delete_user)

        self.tab_interfaces.restart_button.clicked.connect(self._on_restart_iface)
        self.tab_interfaces.change_ip_button.clicked.connect(self._on_change_ip)

        self.tab_monitoreo.start_button.clicked.connect(self._on_toggle_monitoring)
        self.tab_monitoreo.clear_button.clicked.connect(self._on_clear_graphs)

        return self.tabs

    # ─────────────────────────────────────────────────────────
    # Utilidades de UI
    # ─────────────────────────────────────────────────────────

    def _set_status(self, msg: str, *, timeout: int = 0, error: bool = False):
        color = "#c62828" if error else "#1b5e20"
        self.status_bar.setStyleSheet(
            f"QStatusBar {{ background: #e0e0e0; "
            f"font-weight: bold; color: {color}; }}"
        )
        self.status_bar.showMessage(msg, timeout)

    def _set_tabs_enabled(self, enabled: bool):
        for i in range(1, self.tabs.count()):
            self.tabs.setTabEnabled(i, enabled)

    def _all_action_buttons(self):
        return [
            self.tab_conexion.update_button,
            self.tab_usuarios.create_user_button,
            self.tab_usuarios.delete_user_button,
            self.tab_interfaces.restart_button,
            self.tab_interfaces.change_ip_button,
            self.tab_monitoreo.start_button,
            self.tab_monitoreo.clear_button,
        ]

    def _set_loading(self, loading: bool, message: str = "Cargando…"):
        if loading:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.tab_conexion.connect_button.setEnabled(False)
            for btn in self._all_action_buttons():
                btn.setEnabled(False)
            self._set_tabs_enabled(False)
            self._overlay.show_(message)
        else:
            QApplication.restoreOverrideCursor()
            self._overlay.hide_()
            connected = self._api.connected
            self.tab_conexion.connect_button.setEnabled(True)
            self._set_tabs_enabled(connected)
            for btn in self._all_action_buttons():
                btn.setEnabled(connected)

    def _show_error(self, msg: str):
        self._set_status(msg, error=True)
        QMessageBox.critical(self, "Error", msg)

    def _run_in_thread(self, fn, *, on_success=None, on_error=None,
                       message: str = "Cargando…"):
        """Ejecuta `fn` en un hilo; restaura la UI al terminar."""
        self._set_loading(True, message)
        self._worker = NetworkWorker(fn)
        if on_success:
            self._worker.finished.connect(on_success)
        self._worker.error.connect(on_error or self._show_error)
        self._worker.finished.connect(lambda _: self._set_loading(False))
        self._worker.error.connect(   lambda _: self._set_loading(False))
        self._worker.start()

    # ─────────────────────────────────────────────────────────
    # Actualización de listas sincronizadas (ambas pestañas)
    # ─────────────────────────────────────────────────────────

    def _populate_lists(self, result):
        """Puebla las listas de interfaces y usuarios en todas las pestañas."""
        interfaces, usuarios = result

        # Limpiar todas las listas
        for lst in (self.tab_conexion.interfaces_list,
                    self.tab_interfaces.interfaces_list):
            lst.clear()
        for lst in (self.tab_conexion.users_list,
                    self.tab_usuarios.users_list):
            lst.clear()
        self.tab_interfaces.ip_iface_combo.clear()

        # Interfaces
        for iface in interfaces:
            name    = iface.get("name", "?")
            itype   = iface.get("type", "desconocido")
            running = "✅" if iface.get("running", False) else "🔴"
            text    = f"{running} {name}  [{itype}]"
            for lst in (self.tab_conexion.interfaces_list,
                        self.tab_interfaces.interfaces_list):
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole,     iface[".id"])
                item.setData(Qt.ItemDataRole.UserRole + 1, name)
                lst.addItem(item)
            self.tab_interfaces.ip_iface_combo.addItem(name)

        # Usuarios
        for user in usuarios:
            name  = user.get("name", "?")
            group = user.get("group", "?")
            text  = f"👤 {name}  ({group})"
            for lst in (self.tab_conexion.users_list,
                        self.tab_usuarios.users_list):
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole,     user[".id"])
                item.setData(Qt.ItemDataRole.UserRole + 1, name)
                lst.addItem(item)

        self._set_status(
            f"Listas actualizadas  —  "
            f"{len(interfaces)} interfaces, {len(usuarios)} usuarios",
            timeout=4000,
        )

        # Sincronizar checkboxes de monitoreo
        iface_names = [iface.get("name", "?") for iface in interfaces]
        self.tab_monitoreo.set_available_interfaces(iface_names)

    # ─────────────────────────────────────────────────────────
    # Controladores de eventos
    # ─────────────────────────────────────────────────────────

    def _on_connect(self):
        host     = self.tab_conexion.host_input.text().strip()
        username = self.tab_conexion.user_input.text().strip()
        password = self.tab_conexion.pass_input.text()
        port     = self.tab_conexion.port_input.value()

        if not host or not username:
            QMessageBox.warning(self, "Atención", "Complete la IP y el usuario.")
            return

        def _do():
            self._api.connect(host, username, password, port)

        def _on_success(_):
            self._set_status(f"✅ Conectado a {host}:{port}")
            self.tab_conexion.connect_button.setText("🔌 Reconectar")
            self._on_refresh()

        self._run_in_thread(_do, on_success=_on_success,
                            on_error=self._show_error,
                            message="Conectando al router…")

    def _on_refresh(self):
        if not self._api.connected:
            return

        def _do():
            return self._api.get_interfaces(), self._api.get_users()

        self._run_in_thread(_do, on_success=self._populate_lists,
                            on_error=self._show_error,
                            message="Actualizando listas…")

    def _on_create_user(self):
        username = self.tab_usuarios.new_user_input.text().strip()
        password = self.tab_usuarios.new_pass_input.text()
        confirm  = self.tab_usuarios.new_pass_confirm_input.text()
        group    = self.tab_usuarios.group_select.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Atención", "Complete nombre y contraseña.")
            return
        if password != confirm:
            QMessageBox.warning(self, "Atención", "Las contraseñas no coinciden.")
            return
        if not is_valid_username(username):
            QMessageBox.warning(self, "Atención",
                                "El nombre solo puede contener letras, números y '_'.")
            return
        if len(password) < 4:
            QMessageBox.warning(self, "Atención",
                                "La contraseña debe tener al menos 4 caracteres.")
            return

        def _do():
            self._api.create_user(username, password, group)

        def _on_success(_):
            QMessageBox.information(self, "Listo",
                                    f"✅ Usuario '{username}' creado en grupo '{group}'.")
            self.tab_usuarios.new_user_input.clear()
            self.tab_usuarios.new_pass_input.clear()
            self.tab_usuarios.new_pass_confirm_input.clear()
            self._on_refresh()

        self._run_in_thread(_do, on_success=_on_success,
                            on_error=self._show_error,
                            message=f"Creando usuario '{username}'…")

    def _on_delete_user(self):
        selected = self.tab_usuarios.users_list.currentItem()
        if not selected:
            QMessageBox.information(self, "Info", "Seleccione un usuario en la lista.")
            return

        user_id  = selected.data(Qt.ItemDataRole.UserRole)
        username = selected.data(Qt.ItemDataRole.UserRole + 1)

        if username == "admin":
            QMessageBox.warning(self, "Atención",
                                "No se puede eliminar el usuario 'admin'.")
            return
        if QMessageBox.question(
            self, "Confirmar", f"¿Eliminar usuario '{username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return

        def _do():
            self._api.delete_user(user_id)

        def _on_success(_):
            QMessageBox.information(self, "Listo", f"✅ Usuario '{username}' eliminado.")
            self._on_refresh()

        self._run_in_thread(_do, on_success=_on_success,
                            on_error=self._show_error,
                            message=f"Eliminando usuario '{username}'…")

    def _on_restart_iface(self):
        selected = self.tab_interfaces.interfaces_list.currentItem()
        if not selected:
            QMessageBox.information(self, "Info", "Seleccione una interfaz en la lista.")
            return

        iface_id   = selected.data(Qt.ItemDataRole.UserRole)
        iface_name = selected.data(Qt.ItemDataRole.UserRole + 1)

        if QMessageBox.question(
            self, "Confirmar",
            f"¿Reiniciar interfaz '{iface_name}'?\nHabrá una breve interrupción.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return

        def _do():
            self._api.restart_interface(iface_id)

        def _on_success(_):
            QMessageBox.information(self, "Listo",
                                    f"✅ Interfaz '{iface_name}' reiniciada.")

        self._run_in_thread(_do, on_success=_on_success,
                            on_error=self._show_error,
                            message=f"Reiniciando '{iface_name}'…")

    def _on_change_ip(self):
        iface_name = self.tab_interfaces.ip_iface_combo.currentText().strip()
        ip_cidr    = self.tab_interfaces.ip_input.text().strip()

        if not iface_name or not ip_cidr:
            QMessageBox.warning(self, "Atención",
                                "Seleccione interfaz y escriba la nueva IP.")
            return
        if not is_valid_cidr(ip_cidr):
            QMessageBox.warning(self, "Formato inválido",
                                "Use el formato IP/CIDR.\nEjemplo: 192.168.1.1/24")
            return
        if QMessageBox.question(
            self, "Confirmar",
            f"Se eliminarán TODAS las IPs de '{iface_name}'\n"
            f"y se asignará '{ip_cidr}'.\n\n¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return

        def _do():
            self._api.set_interface_ip(iface_name, ip_cidr)

        def _on_success(_):
            QMessageBox.information(
                self, "Listo",
                f"✅ IP de '{iface_name}' cambiada a '{ip_cidr}'.",
            )
            self.tab_interfaces.ip_input.clear()

        self._run_in_thread(_do, on_success=_on_success,
                            on_error=self._show_error,
                            message=f"Cambiando IP de '{iface_name}'…")

    # ── Monitoreo ─────────────────────────────────────────────

    def _on_toggle_monitoring(self):
        if self._monitoring:
            self._stop_monitoring()
        else:
            self._start_monitoring()

    def _start_monitoring(self):
        self._monitoring = True
        interval = self.tab_monitoreo.interval_spin.value()
        self._timer.start(interval * 1000)
        self.tab_monitoreo.start_button.setText("⏹️ Detener Monitoreo")
        self._set_status("📡 Monitoreo en curso…")

    def _stop_monitoring(self):
        self._monitoring = False
        self._timer.stop()
        self.tab_monitoreo.start_button.setText("▶️ Iniciar Monitoreo")
        self._set_status("Monitoreo detenido.", timeout=3000)

    def _on_clear_graphs(self):
        self._stop_monitoring()
        self.tab_monitoreo.clear()
        self._set_status("Gráficos limpiados.", timeout=3000)

    def _poll_traffic(self):
        if not self._api.connected or not self._monitoring:
            return

        def _do():
            return self._api.get_traffic_snapshot()

        def _on_success(traffic: dict):
            interval = self.tab_monitoreo.interval_spin.value()
            self.tab_monitoreo.update_traffic(traffic, interval)

        def _on_error(msg):
            self._stop_monitoring()
            self._api.close()
            self._set_tabs_enabled(False)
            self._show_error(f"Conexión perdida durante el monitoreo:\n{msg}")

        self._poll_worker = NetworkWorker(self._api.get_traffic_snapshot)
        self._poll_worker.finished.connect(_on_success)
        self._poll_worker.error.connect(_on_error)
        self._poll_worker.start()

    # ── Cierre limpio ─────────────────────────────────────────

    def closeEvent(self, event):
        self._timer.stop()
        self._api.close()
        event.accept()
