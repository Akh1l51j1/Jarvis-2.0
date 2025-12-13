import subprocess
import os
import sys
import time

def launch_system():
    print(">> STARTING JARVIS...")

    # 1. GET PATHS
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    UI_DIR = os.path.join(ROOT_DIR, "JarvisUI")

    # 2. CHECK IF UI EXISTS
    if not os.path.exists(UI_DIR):
        print(f"\n❌ ERROR: Cannot find '{UI_DIR}'")
        print("   Make sure the folder is named 'JarvisUI' exactly.")
        input("Press Enter to exit...")
        return

    # 3. LAUNCH COMMANDS
    # We use 0 (Visible) instead of 0x08000000 (Hidden) for now so we can debug.
    MODE = 0 
    
    try:
        print("   [1/2] Igniting Interface...")
        # Start React (npm run dev)
        subprocess.Popen("npm run dev", cwd=UI_DIR, shell=True, creationflags=MODE)
        time.sleep(3) # Wait for it to load

        print("   [2/2] Awakening Brain...")
        # Start Python (main.py) using the current venv
        subprocess.Popen([sys.executable, "main.py"], cwd=ROOT_DIR, creationflags=MODE)

        print("   [OK] Systems Online. Closing this launcher...")
        time.sleep(2)
        
    except Exception as e:
        print(f"\n❌ Launch Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    launch_system()