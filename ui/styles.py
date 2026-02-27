"""
ui/styles.py — Estilos globales de la aplicación.
"""

APP_STYLE = """
    QWidget {
        background-color: #f5f5f5;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
    }
    QGroupBox {
        font-weight: bold;
        border: 2px solid #cccccc;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
    QPushButton {
        background-color: #0078d7;
        color: white;
        border: none;
        padding: 5px 12px;
        border-radius: 3px;
        min-width: 80px;
    }
    QPushButton:hover  { background-color: #005a9e; }
    QPushButton:pressed { background-color: #004578; }
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    QPushButton#danger {
        background-color: #d32f2f;
    }
    QPushButton#danger:hover  { background-color: #b71c1c; }
    QPushButton#danger:pressed { background-color: #7f0000; }
    QLineEdit, QComboBox, QSpinBox, QListWidget {
        border: 1px solid #cccccc;
        border-radius: 3px;
        padding: 3px;
        background-color: white;
    }
    QTabWidget::pane {
        border: 1px solid #cccccc;
        border-radius: 5px;
        background-color: white;
    }
    QTabBar::tab {
        background-color: #e0e0e0;
        border: 1px solid #cccccc;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 5px 12px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 1px solid white;
    }
    QTabBar::tab:disabled { color: #aaaaaa; }
    QStatusBar { background: #e0e0e0; font-weight: bold; }
"""
