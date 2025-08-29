from sqlmodel import create_engine, SQLModel, Session
from pathlib import Path
import os

def appdata_dir() -> Path:
    base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData/Roaming")))
    d = base / "FocusTime"
    d.mkdir(parents=True, exist_ok=True)
    return d

DB_PATH = appdata_dir() / "focus.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

def init_db():
    from .models import Task, Schedule, Occurrence  # noqa
    SQLModel.metadata.create_all(engine)

def session() -> Session:
    return Session(engine)