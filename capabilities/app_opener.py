import os
import subprocess
from capabilities.file_ops import FileOps

class AppOpener:
    
    # 1. ALIASES (Fixes typos like 'Fortify')
    ALIASES = {
        "fortify": "spotify",
        "sportify": "spotify",
        "chrom": "chrome",
        "google chrome": "chrome",
    }

    # 2. SYSTEM SETTINGS (Windows URI)
    SYSTEM_APPS = {
        "bluetooth": "start ms-settings:bluetooth",
        "wifi": "start ms-settings:network-wifi",
        "settings": "start ms-settings:",
        "display": "start ms-settings:display",
        "sound": "start ms-settings:sound",
        "volume": "start ms-settings:sound",
        "update": "start ms-settings:windowsupdate",
        "security": "start ms-settings:windowsdefender",
    }

    # 3. DIRECT COMMANDS (The "Fast Lane" - Bypasses Hunter)
    DIRECT_COMMANDS = {
        "spotify": "start spotify:",
        "forza horizon 4": "start shell:AppsFolder\\Microsoft.SunriseBaseGame_8wekyb3d8bbwe!SunriseReleaseFinal",
        "whatsapp": "start whatsapp:",
        "calculator": "calc",
        "notepad": "notepad"
    }

    @staticmethod
    def open_app(app_name):
        target = app_name.lower().replace("settings", "").strip()
        
        # NEW: FILE EXTENSION CHECK - If input has a file extension, open it directly
        import re
        file_extension_pattern = r'\.(txt|pdf|py|docx|doc|pptx|ppt|xlsx|xls|jpg|jpeg|png|gif|mp3|mp4|avi|mov|zip|rar)$'
        if re.search(file_extension_pattern, target):
            print(f"   [System] Opening file directly: {target}")
            try:
                os.startfile(target)
                return f"Opened {target}."
            except Exception as e:
                return f"Error opening file: {e}"
        
        # A. ALIAS CHECK
        if target in AppOpener.ALIASES:
            target = AppOpener.ALIASES[target]

        # B. DIRECT COMMAND CHECK (Spotify/Forza/WhatsApp)
        # This acts as the HARD BYPASS you wanted.
        if target in AppOpener.DIRECT_COMMANDS:
            print(f"   [System] Fast Launch: {target}")
            subprocess.run(AppOpener.DIRECT_COMMANDS[target], shell=True)
            return f"Opening {target}..."

        # C. SYSTEM SETTINGS CHECK
        if target in AppOpener.SYSTEM_APPS:
            print(f"   [System] Opening Settings: {target}")
            os.system(AppOpener.SYSTEM_APPS[target])
            return f"Opened {target} settings."

        # D. THE HUNTER (Only runs if A, B, and C fail)
        print(f"   [System] Hunting for: {target}")
        matches = FileOps.find_all_files(f"{target}.exe")
        
        if not matches:
             matches = FileOps.find_all_files(f"{target}.lnk")

        if matches:
            file_path = matches[0]
            print(f"   [Hunter] Launching: {file_path}")
            try:
                os.startfile(file_path)
                return f"Opened {target}."
            except Exception as e:
                return f"Error: {e}"
        
        return f"Could not find app '{target}'."

    @staticmethod
    def play_music(song_name):
        # Specific function for "Play [Song]"
        print(f"   [Music] Searching: {song_name}")
        cmd = f'start spotify:search:"{song_name}"'
        subprocess.run(cmd, shell=True)
        return f"Playing {song_name}."