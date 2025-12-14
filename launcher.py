import subprocess
import os
import sys
import time

def launch_system():
    print(">> STARTING JARVIS (MANAGER MODE)...")

    # 1. FIND THE UI FOLDER
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    UI_DIR = None
    
    # Smart search for the folder
    possible_names = ["JarvisUI", "jarvisui", "ui", "UI", "client"]
    for name in possible_names:
        candidate = os.path.join(ROOT_DIR, name)
        if os.path.isdir(candidate):
            UI_DIR = candidate
            break
            
    if not UI_DIR:
        print("\n❌ CRITICAL ERROR: UI FOLDER NOT FOUND")
        print("   Make sure your React folder is next to this script.")
        input("Press Enter to exit...")
        return

    # 2. LAUNCH
    # 0 = Visible Windows (Debug)
    # Change to 0x08000000 later to hide them!
    MODE = 0 
    
    try:
        print("   [1/2] Igniting Interface...")
        # Start UI and keep the process handle
        ui_process = subprocess.Popen("npm run dev", cwd=UI_DIR, shell=True, creationflags=MODE)
        time.sleep(3) 

        print("   [2/2] Awakening Brain...")
        # Start Brain and keep the process handle
        brain_process = subprocess.Popen([sys.executable, "main.py"], cwd=ROOT_DIR, creationflags=MODE)

        print(">> SYSTEM ONLINE. MONITORING...")
        print("   (Use 'Jarvis, shut down' to close everything)")

        # 3. MONITORING LOOP (The Fix)
        # This line pauses the script here until main.py stops running
        brain_process.wait()

        # 4. CLEANUP (When Brain dies, kill UI)
        print("\n>> Brain has shut down. Terminating Interface...")
        
        # This command forcefully kills the entire UI process tree (npm -> vite -> electron)
        subprocess.call(f"taskkill /F /T /PID {ui_process.pid}", shell=True)
        
        print(">> GOODBYE.")
        time.sleep(1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        try:
            # Emergency cleanup if launch fails
            if 'ui_process' in locals():
                subprocess.call(f"taskkill /F /T /PID {ui_process.pid}", shell=True)
        except: pass
        input("Press Enter to exit...")

if __name__ == "__main__":
    launch_system()