from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    priority: int = 1             # 0 is highest
    status: str = "active"        # active/paused/done/archived
    project: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Schedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    rrule: Optional[str] = None   # e.g., FREQ=HOURLY;INTERVAL=1;UNTIL=...
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    timezone: Optional[str] = "America/Chicago"

class Occurrence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    due_at: datetime
    status: str = "pending"       # pending/done/snoozed/missed
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    snooze_until: Optional[datetime] = None