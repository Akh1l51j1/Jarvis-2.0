import os
import sys
import psutil

class SystemOps:
    @staticmethod
    def open_application(app_name):
        """
        Opens a Windows application using common paths.
        """
        print(f"   [Tool] Opening: {app_name}")
        app_name = app_name.lower()
        
        # Get User Path (e.g., C:\Users\Akhil)
        user_path = os.path.expanduser("~")
        appdata = os.getenv('APPDATA') # C:\Users\Akhil\AppData\Roaming
        localappdata = os.getenv('LOCALAPPDATA') # C:\Users\Akhil\AppData\Local

        # --- APP LIBRARY ---
        apps = {
            # 1. SYSTEM
            "file explorer": "explorer.exe",
            "explorer": "explorer.exe",
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "settings": "start ms-settings:",
            "cmd": "start cmd.exe",
            
            # 2. BROWSERS
            "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            "chrome": "chrome.exe",

            # 3. SOCIALS
            "telegram": os.path.join(appdata, r"Telegram Desktop\Telegram.exe"),
            
            # 4. CREATIVE (Check your specific versions!)
            "figma": os.path.join(localappdata, r"Figma\Figma.exe"),
            "photoshop": r"C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe", 

            # 5. GAMES & TOOLS
            "valorant": r"C:\Riot Games\Riot Client\RiotClientServices.exe --launch-product=valorant --launch-patchline=live",
            "tlauncher": os.path.join(appdata, r".minecraft\TLauncher.exe"),
            "ghelper": r"C:\GHelper\GHelper.exe", # <--- COMMON PATH, MIGHT BE DIFFERENT FOR YOU!
        }

        try:
            # Direct Match
            if app_name in apps:
                path = apps[app_name]
                # Check if file actually exists before trying (except for system commands)
                if "start " in path or os.path.exists(path) or "--launch" in path:
                    if "start " in path:
                        os.system(path)
                    else:
                        os.system(f'start "" "{path}"')
                    return f"Opening {app_name}..."
                else:
                    return f"Path not found for {app_name}. Please check system_ops.py"
            
            # Generic Attempt (Try to just run the name)
            else:
                os.system(f"start {app_name}")
                return f"Attempting to open {app_name}..."
                
        except Exception as e:
            return f"Failed to open {app_name}: {e}"

    @staticmethod
    def get_system_status():
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        return f"CPU is at {cpu}%. Memory is at {memory}%."

    @staticmethod
    def close_jarvis():
        return "Shutting down systems. Goodbye, sir."