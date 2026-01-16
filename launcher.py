import subprocess
import os
import sys
import time
import datetime

# --- LOGGER SETUP ---
# --- LOGGER SETUP ---
def log(message):
    """Writes messages to a text file so we can see what's wrong."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    # ADDED encoding='utf-8' to support emojis
    with open("debug_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def launch_system():
    # Clear previous log
    # ADDED encoding='utf-8' here too
    with open("debug_log.txt", "w", encoding="utf-8") as f:
        f.write("=== JARVIS LAUNCH LOG ===\n")

    log("Launcher started.")

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    log(f"Root Directory: {ROOT_DIR}")

    # Find UI
    UI_DIR = None
    possible_names = ["JarvisUI", "jarvisui", "ui", "UI", "client"]
    for name in possible_names:
        candidate = os.path.join(ROOT_DIR, name)
        if os.path.isdir(candidate):
            UI_DIR = candidate
            break
            
    if not UI_DIR:
        log("CRITICAL: UI Folder not found.")
        return

    log(f"UI Directory found: {UI_DIR}")

    # --- CRITICAL SETTINGS ---
    # We force stdout to DEVNULL so 'print' statements don't crash the background process
    MODE = 0 

    try:
        # 1. START UI
        log("Attempting to launch UI (npm run dev)...")
        ui_process = subprocess.Popen(
            "npm run dev", 
            cwd=UI_DIR, 
            shell=True, 
            creationflags=MODE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log(f"UI Process spawned. PID: {ui_process.pid}")
        
        time.sleep(3) 

        # 2. START BRAIN
        log("Attempting to launch Brain (main.py)...")
        # We redirect the Brain's output to a SEPARATE file so we can see its specific crash
        brain_log = open("brain_error_log.txt", "w")
        
        brain_process = subprocess.Popen(
            [sys.executable, "main.py"], 
            cwd=ROOT_DIR, 
            creationflags=MODE,
            stdout=brain_log, # Write normal prints here
            stderr=brain_log  # Write crashes/errors here
        )
        log(f"Brain Process spawned. PID: {brain_process.pid}")

        # 3. MONITOR
        log("Monitoring processes...")
        exit_code = brain_process.wait() # <--- This pauses script until Brain dies
        
        log(f"⚠️ Brain has exited with code: {exit_code}")
        log("Terminating UI...")
        
        subprocess.call(f"taskkill /F /T /PID {ui_process.pid}", shell=True)
        brain_log.close()
        log("Cleanup complete. Goodbye.")
        
    except Exception as e:
        log(f"❌ LAUNCHER CRASHED: {e}")
        try:
            if 'ui_process' in locals():
                subprocess.call(f"taskkill /F /T /PID {ui_process.pid}", shell=True)
        except: pass

if __name__ == "__main__":
    launch_system()