# FocusTime ⏰  
A lightweight Windows **system tray app** that reminds you of your top priorities every hour.  
Built with **Python + PySide6**, it runs in the background, shows a tray icon, and fires native Windows notifications.  

---

## ✨ Features (current MVP)
- Runs silently in the **Windows system tray**.  
- **Right-click menu** with:
  - 🔔 **Ping now** → instantly test a notification.  
  - ⏱ **Enable hourly pings** → toggle automatic top-of-the-hour reminders.  
  - ❌ **Quit** → exit the app.  
- **Native Windows toast notifications** (bottom-right of the screen above the clock).  

Future milestones:  
- Task manager (daily, seasonal, project-based tasks).  
- SQLite database storage.  
- Snooze & mark-done actions.  
- Packaging to a standalone `.exe` (PyInstaller).  

---

## 🛠 Requirements
- Python **3.10+**  
- Windows 10/11  

---

## 🚀 Setup & Run
Clone this repo and set up a virtual environment:

```powershell
git clone https://github.com/adarshnb95/focustime.git
cd focustime

# Create virtual env
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python -m app.main
