import pystray
from PIL import Image, ImageDraw
import subprocess
import os

# --- CONFIGURATION ---
# 1. Define the exact folder and file
PROJECT_DIR = r"D:\jarvis 2.0"
BATCH_FILE = "boot.bat"
ICON_PATH = None 

running_process = None

def create_default_icon():
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), (0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((10, 10, 54, 54), fill=(0, 255, 0)) # Green
    return image

def launch_jarvis(icon, item):
    full_path = os.path.join(PROJECT_DIR, BATCH_FILE)
    print(f"Launching: {full_path}")
    
    try:
        # CRITICAL FIX: We add 'cwd=PROJECT_DIR'
        # This tells Windows: "Pretend I am inside D:\jarvis 2.0 before running this"
        subprocess.Popen(
            [full_path],
            cwd=PROJECT_DIR, 
            shell=True
        )
        icon.notify("Systems Initiating...", "Jarvis")
    except Exception as e:
        icon.notify(f"Error: {e}", "Launch Failed")

def stop_jarvis(icon, item):
    icon.notify("Terminating Protocols...", "Jarvis")
    
    # Get the PID of this Tray Script so we don't kill ourselves
    my_pid = os.getpid()
    
    # 1. KILL THE FACE (UI)
    subprocess.call("taskkill /F /IM node.exe /T", shell=True)
    subprocess.call("taskkill /F /IM electron.exe /T", shell=True)
    
    # 2. KILL THE BRAIN & LAUNCHER (But spare the Tray!)
    # /FI "PID ne <my_pid>" means "Where PID is NOT equal to Mine"
    subprocess.call(f'taskkill /F /FI "PID ne {my_pid}" /IM python.exe /T', shell=True)
    subprocess.call(f'taskkill /F /FI "PID ne {my_pid}" /IM pythonw.exe /T', shell=True)
    
    icon.notify("Systems Offline. Standing By.", "Jarvis")  

def exit_app(icon, item):
    stop_jarvis(icon, item)
    icon.stop()

def setup_tray():
    if ICON_PATH and os.path.exists(ICON_PATH):
        image = Image.open(ICON_PATH)
    else:
        image = create_default_icon()

    menu = pystray.Menu(
        pystray.MenuItem("Boot Jarvis", launch_jarvis, default=True),
        pystray.MenuItem("Shut Down", stop_jarvis),
        pystray.MenuItem("Exit Tray", exit_app)
    )

    icon = pystray.Icon("Jarvis", image, "Jarvis System", menu)
    icon.run()

if __name__ == "__main__":
    setup_tray()