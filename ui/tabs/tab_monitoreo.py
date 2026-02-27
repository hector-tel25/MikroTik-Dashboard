"""
ui/tabs/tab_monitoreo.py — Pestaña de monitoreo de tráfico en tiempo real.

Mejoras UX:
  • Panel lateral con checkboxes para seleccionar qué interfaces graficar.
  • Los gráficos solo se crean/actualizan para las interfaces marcadas.
  • Botones "Todas / Ninguna" para control masivo.
"""

from collections import deque

import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSpinBox,
    QGroupBox, QTabWidget, QCheckBox,
    QScrollArea, QFrame, QSplitter,
)
from PyQt6.QtCore import Qt


class TabMonitoreo(QWidget):

    MAX_POINTS = 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self.trafico_data: dict = {}
        self.plots: dict = {}
        self._checkboxes: dict[str, QCheckBox] = {}
        self._build()

    def _build(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Panel izquierdo: selección de interfaces ──────────
        left_panel = QWidget()
        left_panel.setFixedWidth(210)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(6, 6, 6, 6)

        sel_group = QGroupBox("Interfaces a monitorear")
        sel_vbox = QVBoxLayout(sel_group)

        btn_row = QHBoxLayout()
        self.btn_all  = QPushButton("✅ Todas")
        self.btn_none = QPushButton("⬜ Ninguna")
        self.btn_all.setFixedHeight(26)
        self.btn_none.setFixedHeight(26)
        self.btn_all.clicked.connect(self._select_all)
        self.btn_none.clicked.connect(self._select_none)
        btn_row.addWidget(self.btn_all)
        btn_row.addWidget(self.btn_none)
        sel_vbox.addLayout(btn_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._cb_container = QWidget()
        self._cb_layout = QVBoxLayout(self._cb_container)
        self._cb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._cb_layout.setSpacing(4)
        scroll.setWidget(self._cb_container)
        sel_vbox.addWidget(scroll)

        left_layout.addWidget(sel_group)

        # ── Panel derecho: controles + gráficos ──────────────
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        ctrl_group = QGroupBox("Control de Monitoreo")
        ctrl_layout = QHBoxLayout(ctrl_group)

        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(60)
        self.interval_spin.setValue(5)
        self.interval_spin.setSuffix(" seg")
        self.interval_spin.setToolTip("Intervalo de actualización")

        self.start_button = QPushButton("▶️ Iniciar Monitoreo")
        self.start_button.setEnabled(False)

        self.clear_button = QPushButton("🧹 Limpiar Gráficos")
        self.clear_button.setEnabled(False)

        ctrl_layout.addWidget(QLabel("Intervalo:"))
        ctrl_layout.addWidget(self.interval_spin)
        ctrl_layout.addWidget(self.start_button)
        ctrl_layout.addWidget(self.clear_button)
        ctrl_layout.addStretch()
        right_layout.addWidget(ctrl_group)

        self.graph_tabs = QTabWidget()
        self.graph_tabs.setDocumentMode(True)
        self.graph_tabs.tabBar().setExpanding(False)
        right_layout.addWidget(self.graph_tabs)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(splitter)

    # ── API pública ───────────────────────────────────────────

    def set_available_interfaces(self, names: list[str]):
        """Sincroniza los checkboxes con las interfaces disponibles."""
        current_checked = {n for n, cb in self._checkboxes.items() if cb.isChecked()}

        for name in list(self._checkboxes.keys()):
            if name not in names:
                cb = self._checkboxes.pop(name)
                self._cb_layout.removeWidget(cb)
                cb.deleteLater()

        for name in names:
            if name not in self._checkboxes:
                cb = QCheckBox(name)
                cb.setChecked(name in current_checked or not current_checked)
                cb.setToolTip(f"Incluir '{name}' en el monitoreo")
                self._checkboxes[name] = cb
                self._cb_layout.addWidget(cb)

    def selected_interfaces(self) -> set[str]:
        return {n for n, cb in self._checkboxes.items() if cb.isChecked()}

    def update_traffic(self, traffic: dict, interval_s: int):
        selected = self.selected_interfaces()

        # Quitar pestañas de interfaces deseleccionadas / desaparecidas
        to_remove = [
            n for n in list(self.trafico_data.keys())
            if n not in traffic or n not in selected
        ]
        for name in to_remove:
            for i in range(self.graph_tabs.count()):
                if self.graph_tabs.tabText(i) == name:
                    self.graph_tabs.removeTab(i)
                    break
            self.plots.pop(name, None)
            self.trafico_data.pop(name, None)

        for name, values in traffic.items():
            if name not in selected:
                continue

            rx_mbps = values["rx"]
            tx_mbps = values["tx"]

            if name not in self.trafico_data:
                self._create_graph_tab(name, interval_s)

            data = self.trafico_data[name]
            x = (data["x"][-1] + 1) if data["x"] else 0
            data["x"].append(x)
            data["rx"].append(rx_mbps)
            data["tx"].append(tx_mbps)

            self.plots[name]["rx_curve"].setData(list(data["x"]), list(data["rx"]))
            self.plots[name]["tx_curve"].setData(list(data["x"]), list(data["tx"]))
            self.plots[name]["info"].setText(
                f"RX: {rx_mbps:.3f} Mbps  |  TX: {tx_mbps:.3f} Mbps")

    def clear(self):
        self.trafico_data.clear()
        self.plots.clear()
        self.graph_tabs.clear()

    # ── Privado ───────────────────────────────────────────────

    def _select_all(self):
        for cb in self._checkboxes.values():
            cb.setChecked(True)

    def _select_none(self):
        for cb in self._checkboxes.values():
            cb.setChecked(False)

    def _create_graph_tab(self, name: str, interval_s: int):
        self.trafico_data[name] = {
            "rx": deque(maxlen=self.MAX_POINTS),
            "tx": deque(maxlen=self.MAX_POINTS),
            "x":  deque(maxlen=self.MAX_POINTS),
        }

        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)

        info_label = QLabel()
        info_label.setStyleSheet(
            "font-weight: bold; color: #1565c0; padding: 2px 4px;")
        tab_layout.addWidget(info_label)

        plot_widget = pg.PlotWidget(title=f"Tráfico — {name}")
        plot_widget.addLegend()
        plot_widget.showGrid(x=True, y=True)
        plot_widget.setLabel("left",   "Mbps")
        plot_widget.setLabel("bottom", f"Muestras (cada {interval_s} s)")
        plot_widget.setBackground("#ffffff")

        rx_curve = plot_widget.plot(pen=pg.mkPen("#e53935", width=2), name="RX (↓)")
        tx_curve = plot_widget.plot(pen=pg.mkPen("#1e88e5", width=2), name="TX (↑)")

        tab_layout.addWidget(plot_widget)
        self.graph_tabs.addTab(tab_widget, name)

        self.plots[name] = {
            "plot":     plot_widget,
            "rx_curve": rx_curve,
            "tx_curve": tx_curve,
            "info":     info_label,
        }
