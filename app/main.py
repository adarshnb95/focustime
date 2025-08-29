import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from .tray import TrayApp
from .db import init_db

def _icon_path() -> str:
    here = Path(__file__).resolve().parent
    ico = here / "assets" / "app.ico"
    return str(ico) if ico.exists() else ""

def main():
    init_db()
    app = QApplication(sys.argv)
    icon = QIcon(_icon_path())
    tray = TrayApp(icon)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()