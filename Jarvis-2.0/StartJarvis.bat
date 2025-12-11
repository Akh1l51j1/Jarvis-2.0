@echo off
title J.A.R.V.I.S. CONTROL CENTER

echo [1/3] Launching Bridge...
start /min cmd /c "cd /d D:\jarvis 2.0 && python server.py"

echo [2/3] Launching Interface...
cd /d D:\JarvisUI
start /min cmd /c "npm run dev"

echo [3/3] Awakening Jarvis...
cd /d D:\jarvis 2.0
python main.py

pause