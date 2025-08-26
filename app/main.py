import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from tray import TrayApp

def _icon_path() -> str:
    # Try app/assets/app.ico; fall back to a default empty icon
    here = Path(__file__).resolve().parent
    ico = here / "assets" / "app.ico"
    return str(ico) if ico.exists() else ""

def main():
    app = QApplication(sys.argv)
    icon = QIcon(_icon_path())
    tray = TrayApp(icon)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()