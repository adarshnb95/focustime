import os, sys
from pathlib import Path

STARTUP_DIR = Path(os.environ["APPDATA"]) / r"Microsoft\Windows\Start Menu\Programs\Startup"
APP_NAME = "FocusTime"
SHORTCUT_PATH = STARTUP_DIR / f"{APP_NAME}.lnk"

def _exe_path() -> str:
    # When packaged with PyInstaller, use the executable; otherwise use the Python file
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys.executable
    # dev mode: run the module
    return f'"{sys.executable}" -m app.main'

def is_autostart_enabled() -> bool:
    return SHORTCUT_PATH.exists()

def enable_autostart():
    """Create a .lnk in the Startup folder pointing to the exe/module."""
    STARTUP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        import win32com.client  # pywin32
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(SHORTCUT_PATH))
        # TargetPath must be the exe; if we're not frozen, use python.exe and Arguments
        if getattr(sys, 'frozen', False):
            shortcut.TargetPath = sys.executable
            shortcut.Arguments = ""
            shortcut.WorkingDirectory = str(Path(sys.executable).parent)
        else:
            shortcut.TargetPath = sys.executable
            shortcut.Arguments = "-m app.main"
            shortcut.WorkingDirectory = str(Path(__file__).resolve().parents[1])
        shortcut.IconLocation = shortcut.TargetPath
        shortcut.Save()
        return True
    except Exception as e:
        # Fallback: write a tiny .cmd that launches the app (works even without pywin32)
        cmd_path = STARTUP_DIR / f"{APP_NAME}.cmd"
        cmd_path.write_text(f'start "" {_exe_path()}\n', encoding="utf-8")
        return cmd_path.exists()

def disable_autostart():
    if SHORTCUT_PATH.exists():
        SHORTCUT_PATH.unlink()
    cmd_path = STARTUP_DIR / f"{APP_NAME}.cmd"
    if cmd_path.exists():
        cmd_path.unlink()