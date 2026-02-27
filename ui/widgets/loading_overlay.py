"""
ui/widgets/loading_overlay.py — Overlay con spinner animado que se muestra
sobre toda la ventana mientras se ejecutan operaciones de red en segundo plano.
"""

import math
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont


class _SpinnerWidget(QWidget):
    """Canvas que dibuja un spinner circular animado."""

    def __init__(self, parent=None, size: int = 52,
                 color: str = "#0078d7", segments: int = 12):
        super().__init__(parent)
        self._angle    = 0
        self._size     = size
        self._color    = QColor(color)
        self._segments = segments
        self.setFixedSize(size, size)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self):
        self._timer.start(80)

    def stop(self):
        self._timer.stop()

    def _tick(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.translate(self._size / 2, self._size / 2)

        for i in range(self._segments):
            angle_deg = i * (360 / self._segments)
            angle_rad = math.radians(angle_deg - self._angle)

            # Opacidad varía según la posición relativa al ángulo actual
            alpha = int(255 * (i + 1) / self._segments)
            color = QColor(self._color)
            color.setAlpha(alpha)

            pen = QPen(color)
            pen.setWidth(4)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)

            r = self._size * 0.35
            x1 = math.cos(angle_rad) * r * 0.55
            y1 = math.sin(angle_rad) * r * 0.55
            x2 = math.cos(angle_rad) * r
            y2 = math.sin(angle_rad) * r
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        p.end()


class LoadingOverlay(QWidget):
    """
    Overlay semitransparente con spinner y mensaje de estado.
    Se coloca encima del widget padre y cubre toda su área.

    Uso:
        self._overlay = LoadingOverlay(self)
        self._overlay.show("Conectando…")   # mostrar
        self._overlay.hide_()               # ocultar
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")
        self.hide()

        # ── Layout centrado ──
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Caja blanca con sombra simulada
        self._box = QWidget(self)
        self._box.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,230);
                border-radius: 14px;
            }
        """)
        box_layout = QVBoxLayout(self._box)
        box_layout.setContentsMargins(30, 24, 30, 24)
        box_layout.setSpacing(12)
        box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._spinner = _SpinnerWidget(self._box, size=52, color="#0078d7")
        box_layout.addWidget(self._spinner,
                             alignment=Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel("Cargando…")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet(
            "color: #333333; font-size: 11pt; font-weight: bold; background: transparent;"
        )
        box_layout.addWidget(self._label)

        layout.addWidget(self._box, alignment=Qt.AlignmentFlag.AlignCenter)

    # ── API pública ───────────────────────────────────────────

    def show_(self, message: str = "Cargando…"):
        self._label.setText(message)
        self._spinner.start()
        self.raise_()
        self.resize(self.parent().size())
        self.show()

    def hide_(self):
        self._spinner.stop()
        self.hide()

    # ── Reposicionarse cuando cambia el tamaño del padre ──────

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.resize(self.parent().size())

    def paintEvent(self, event):
        """Fondo semitransparente oscuro."""
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, 90))
        p.end()
