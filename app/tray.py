from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer, QTime
from datetime import datetime, timedelta
from sqlmodel import select
from .db import session
from .models import Task, Schedule, Occurrence
from .schedules import occurrences_between
from .autostart import is_autostart_enabled, enable_autostart, disable_autostart

LOOKAHEAD_HOURS = 24

class TrayApp(QSystemTrayIcon):
    def __init__(self, icon: QIcon, parent=None):
        super().__init__(icon, parent)
        self.setToolTip("FocusTime")

        menu = QMenu()
        menu.addAction(QAction("Ping now", self, triggered=self.ping_now))
        menu.addAction(QAction("Add Hourly Task (today)", self, triggered=self.add_hourly_today))
        menu.addSeparator()
        hourly_toggle = QAction("Enable hourly pings", self, checkable=True)
        hourly_toggle.setChecked(True)
        hourly_toggle.toggled.connect(self.toggle_hourly)
        menu.addAction(hourly_toggle)
        menu.addSeparator()
        
        # Autostart toggle
        auto = QAction("Launch at startup", self, checkable=True)
        auto.setChecked(is_autostart_enabled())

        def _toggle_autostart(checked):
            ok = enable_autostart() if checked else (disable_autostart() or True)
            if not ok:
                self.showMessage(
                    "FocusTime",
                    "Could not update startup setting.",
                    QSystemTrayIcon.Warning,
                    4000
                )

        auto.toggled.connect(_toggle_autostart)
        menu.addAction(auto)
        menu.addSeparator()

        menu.addAction(QAction("Quit", self, triggered=QApplication.instance().quit))
        self.setContextMenu(menu)
        # Timer: tick each minute (expand schedules + dispatch due)
        self.timer = QTimer(self)
        self.timer.setInterval(60_000)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        self.show()

    def ping_now(self):
        self.showMessage("FocusTime", "🔔 Test ping — you’re set up!", QSystemTrayIcon.Information, 5000)

    def toggle_hourly(self, enabled: bool):
        if enabled and not self.timer.isActive():
            self.timer.start()
        elif not enabled and self.timer.isActive():
            self.timer.stop()

    def tick(self):
        # Expand schedules for the next 24h and insert missing Occurrence rows
        self.expand_schedules()
        # Dispatch any due occurrences (due_at <= now and pending)
        self.dispatch_due()

        # Optional: also fire a motivational hourly toast at top of hour
        now = QTime.currentTime()
        if now.minute() == 0:
            self.showMessage(
                "FocusTime — Hourly Check-in",
                "What’s your top priority for this hour?",
                QSystemTrayIcon.Information,
                5000
            )

    def add_hourly_today(self):
        """Quick helper: creates a P0 task that pings every hour until midnight local."""
        local_now = datetime.now()
        until = local_now.replace(hour=23, minute=59, second=0, microsecond=0)
        # RFC5545 UNTIL must be UTC-like (Z); for MVP we keep local; works for between(start,end)
        rrule = f"FREQ=HOURLY;INTERVAL=1;UNTIL={until.strftime('%Y%m%dT%H%M%S')}"
        with session() as s:
            t = Task(title="Top priority this hour", priority=0)
            s.add(t); s.commit(); s.refresh(t)
            sched = Schedule(task_id=t.id, rrule=rrule)
            s.add(sched); s.commit()
        self.showMessage("FocusTime", "✅ Added hourly task for today", QSystemTrayIcon.Information, 3000)

    def expand_schedules(self):
        now = datetime.now().replace(second=0, microsecond=0)
        horizon = now + timedelta(hours=LOOKAHEAD_HOURS)
        with session() as s:
            schedules = s.exec(select(Schedule)).all()
            for sch in schedules:
                if not sch.rrule:
                    continue
                for dt in occurrences_between(sch.rrule, now, horizon):
                    exists = s.exec(
                        select(Occurrence).where(
                            Occurrence.task_id == sch.task_id,
                            Occurrence.due_at == dt
                        )
                    ).first()
                    if not exists:
                        s.add(Occurrence(task_id=sch.task_id, due_at=dt))
            s.commit()

    def dispatch_due(self):
        now = datetime.now()
        with session() as s:
            rows = s.exec(
                select(Occurrence, Task)
                .join(Task, Task.id == Occurrence.task_id)
                .where(Occurrence.status == "pending")
                .where(Occurrence.due_at <= now)
            ).all()
            for occ, task in rows:
                # Show toast
                self.showMessage(
                    f"FocusTime — [P{task.priority}]",
                    f"{task.title}",
                    QSystemTrayIcon.Information,
                    6000
                )
                # Mark as notified by pushing snooze_until a minute ahead to avoid spamming;
                # later you can add "Done/Snooze" UI and status transitions.
                occ.snooze_until = now + timedelta(minutes=1)
                s.add(occ)
            s.commit()