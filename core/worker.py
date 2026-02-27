"""
core/worker.py — Worker genérico para ejecutar operaciones de red
en un hilo separado y no bloquear la interfaz gráfica.
"""

from PyQt6.QtCore import QThread, pyqtSignal
from librouteros.exceptions import TrapError, LibRouterosError


class NetworkWorker(QThread):
    """
    Ejecuta una función arbitraria en un hilo separado.

    Señales:
        finished(object) — emitida con el valor de retorno si no hubo error.
        error(str)       — emitida con el mensaje de error si falla.
    """

    finished = pyqtSignal(object)
    error    = pyqtSignal(str)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn     = fn
        self._args   = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs)
            self.finished.emit(result)
        except (TrapError, LibRouterosError) as e:
            self.error.emit(f"Error de API RouterOS: {e}")
        except Exception as e:
            self.error.emit(str(e))
