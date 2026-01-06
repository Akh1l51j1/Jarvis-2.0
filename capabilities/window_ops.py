import time
import psutil
import win32gui
import win32process

class WindowOps:
    def __init__(self):
        self.current_app = ""
        self.current_title = ""
        self.mode = "CASUAL"  # Default fallback

    def get_active_window(self):
        """
        Scans the active window and returns the 'Vibe' (WORK, GAMING, CASUAL).
        Designed to never crash the main loop.
        """
        try:
            # 1. Get Foreground Window Handle (The active window)
            hwnd = win32gui.GetForegroundWindow()
            
            # Safety Check: sometimes Windows returns 0 active window on startup
            if not hwnd:
                return {"app": "unknown", "title": "", "mode": self.mode}

            # 2. Get Process ID (PID) from that Handle
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # 3. Get the actual .exe name
            try:
                process = psutil.Process(pid)
                app_name = process.name().lower().replace(".exe", "")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # If we can't read the process (e.g., Admin task), stick to last known mode
                return {"app": "system_secure", "title": "System", "mode": self.mode}

            # 4. Get the Window Title (e.g., "main.py - VS Code")
            window_title = win32gui.GetWindowText(hwnd)

            self.current_app = app_name
            self.current_title = window_title

            # 5. DETERMINE THE MODE
            self._set_mode(app_name, window_title)

            return {
                "app": app_name,
                "title": window_title,
                "mode": self.mode
            }

        except Exception as e:
            # Silent fail - don't spam console
            return {"app": "error", "title": "", "mode": "CASUAL"}

    def _set_mode(self, app_name, window_title):
        """Classifies the user's activity into a 'Vibe'."""
        
        # --- WORK APPS (The "Consultant" Persona) ---
        # Focus: High Efficiency, Low Verbosity
        work_apps = [
            "code", "vscode", "pycharm", "cursor",  # Coding
            "winword", "excel", "powerpnt",         # Office
            "cmd", "powershell", "mintty",          # Terminals
            "figma", "blender", "photoshop",        # Creative
            "obs64"                                 # Streaming/Work
        ]
        
        # --- GAMING APPS (The "Tactical" Persona) ---
        # Focus: Silence, Performance, Critical Alerts Only
        game_apps = [
            "valorant", "riotclientservices", 
            "javaw", "minecraft", "tlauncher", 
            "shadowofmordor", "gta5", "steam", 
            "discord", "overlay" # Discord Overlay often triggers this
        ]
        
        # Check Work First
        if any(w in app_name for w in work_apps):
            self.mode = "WORK"
            
        # Check Gaming (Overrides work if you have a game running on top)
        elif any(g in app_name for g in game_apps):
            self.mode = "GAMING"
            
        # Fallback to Casual (Browser, Spotify, Desktop)
        else:
            self.mode = "CASUAL"

# Initialize for import
window_engine = WindowOps()

# --- TEST LOOP (Run this file directly to check) ---
if __name__ == "__main__":
    print(">> Sensor Active. Switch windows to test modes (Ctrl+C to stop).")
    try:
        while True:
            data = window_engine.get_active_window()
            # Clear line and print new status to look clean
            print(f"\r[STATUS] Mode: {data['mode']} | App: {data['app'].ljust(15)}", end="")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n>> Test Closed.")