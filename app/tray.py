from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer, QTime, Qt

class TrayApp(QSystemTrayIcon):
    def __init__(self, icon: QIcon, parent=None):
        super().__init__(icon, parent)
        self.setToolTip("FocusTime")

        # Context menu
        menu = QMenu()
        ping_now = QAction("Ping now", self, triggered=self.ping_now)
        hourly_toggle = QAction("Enable hourly pings", self, checkable=True)
        hourly_toggle.setChecked(True)
        hourly_toggle.toggled.connect(self.toggle_hourly)

        menu.addAction(ping_now)
        menu.addSeparator()
        menu.addAction(hourly_toggle)
        menu.addSeparator()
        quit_action = QAction("Quit", self, triggered=QApplication.instance().quit)
        menu.addAction(quit_action)
        self.setContextMenu(menu)

        # Notification timer (fires at top of each hour)
        self.timer = QTimer(self)
        self.timer.setInterval(60_000)  # check every 60s
        self.timer.timeout.connect(self._maybe_fire_hourly)
        self.timer.start()

        self.show()  # show tray icon

    def ping_now(self):
        # Native Windows toast via QSystemTrayIcon.showMessage
        self.showMessage(
            "FocusTime",
            "🔔 Test ping — you’re set up!",
            QSystemTrayIcon.Information,
            5000
        )

    def toggle_hourly(self, enabled: bool):
        if enabled and not self.timer.isActive():
            self.timer.start()
        elif not enabled and self.timer.isActive():
            self.timer.stop()

    def _maybe_fire_hourly(self):
        # Fire at the top of the hour (minute == 0)
        now = QTime.currentTime()
        if now.minute() == 0:
            self.showMessage(
                "FocusTime — Hourly Check-in",
                "What’s your top priority for this hour?",
                QSystemTrayIcon.Information,
                5000
            )