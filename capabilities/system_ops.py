import os
import sys
import psutil

class SystemOps:
    @staticmethod
    def search_google(query):
        """Opens a Google search in the default browser."""
        import webbrowser
        print(f"   [Tool] Googling: {query}")
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching for {query} on Google."

    @staticmethod
    def open_application(app_name):
        """
        Opens a Windows application using common paths.
        """
        print(f"   [Tool] Opening: {app_name}")
        app_name = app_name.lower()
        
        # Get User Path (e.g., C:\Users\Akhil)
        user_path = os.path.expanduser("~")
        appdata = os.getenv('APPDATA') 
        localappdata = os.getenv('LOCALAPPDATA') 

        # --- APP LIBRARY (For Opening) ---
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
            "telegram": r"C:\Users\Akhil\AppData\Roaming\Telegram Desktop\Telegram.exe",
            
            # 4. CREATIVE (Check your specific versions!)
            "figma": r"C:\Users\Akhil\AppData\Local\Figma\app-125.9.10\Figma.exe",
            "photoshop": r"C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe",

            # 5. GAMES & TOOLS
            "valorant": r"C:\Riot Games\Riot Client\RiotClientServices.exe",
            "tlauncher": r"C:\Users\Akhil\AppData\Roaming\.minecraft\TLauncher.exe",
            "ghelper": r"C:\Users\Akhil\Desktop\GHelper.exe",
            "phone link": "start ms-phone:",
            "phonelink": "start ms-phone:",
        }

        try:
            # Direct Match
            if app_name in apps:
                path = apps[app_name]
                # Check if file actually exists before trying (except for system commands)
                is_system_cmd = "start " in path or "explorer" in path or "calc" in path or "notepad" in path
                
                if is_system_cmd or os.path.exists(path) or "--launch" in path:
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
    def close_application(app_name):
        """
        Closes an application by killing its process.
        """
        print(f"   [Tool] Closing: {app_name}")
        app_name = app_name.lower().strip()

        # --- PROCESS MAP (For Closing) ---
        # Maps "Name" to "process.exe"
        processes = {
            "chrome": "chrome.exe",
            "brave": "brave.exe",
            "notepad": "notepad.exe",
            "calculator": "CalculatorApp.exe", # Win10/11 specific
            "calc": "CalculatorApp.exe",
            "spotify": "spotify.exe",
            "discord": "discord.exe",
            "telegram": "telegram.exe",
            "photoshop": "photoshop.exe",
            "figma": "figma.exe",
            "valorant": "VALORANT-Win64-Shipping.exe", # Actual game process
            "riot": "RiotClientUx.exe",
            "ghelper": "GHelper.exe",
            "tlauncher": "javaw.exe", # Minecraft runs as Java (Added comma here)
            "phonelink": "PhoneExperienceHost.exe", # (Added comma here)
            "phone link": "PhoneExperienceHost.exe"
        }

        try:
            # Determine process name
            process_name = processes.get(app_name, f"{app_name}.exe")
            
            # Command to kill process forcefully (/F)
            os.system(f"taskkill /F /IM {process_name}")
            return f"Closed {app_name}."
        except Exception as e:
            return f"Failed to close {app_name}: {e}"

    @staticmethod
    def get_system_status():
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        return f"CPU is at {cpu}%. Memory is at {memory}%."

    @staticmethod
    def close_jarvis():
        return "Shutting down systems. Goodbye, sir."