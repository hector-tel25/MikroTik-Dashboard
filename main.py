"""
MikroTik Dashboard 
Punto de entrada principal de la aplicación.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MikroTikDashboard


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MikroTikDashboard()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
