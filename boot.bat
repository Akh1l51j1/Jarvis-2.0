@echo off
cd /d "D:\jarvis 2.0"

:: 1. Force Activate the VENV
call venv\Scripts\activate.bat

:: 2. Run the Launcher silently (pythonw.exe)
:: We use 'start ""' to launch it as a separate background process
start "" "venv\Scripts\pythonw.exe" launcher.py

exit