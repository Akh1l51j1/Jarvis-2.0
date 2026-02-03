import os
import sys
import re
import psutil
from tavily import TavilyClient
import config

class SystemOps:
    @staticmethod
    def search_web(query):
        """Searches the web using Tavily (better for AI)."""
        print(f"   [Tavily] Searching: {query}")
        try:
            client = TavilyClient(api_key=config.TAVILY_API_KEY)
            response = client.search(query=query, search_depth="basic", max_results=3)
            
            results = []
            for result in response.get('results', []):
                results.append(f"- {result['title']}: {result['content']}")
            
            return "\n".join(results)
        except Exception as e:
            return f"Search Error: {e}"

    @staticmethod
    def open_application(app_name):
        """Opens Apps, Websites, or Specific Files (PDFs, Docs)."""
        print(f"   [Tool] Processing: {app_name}")
        target = app_name.lower().strip()
        
        # --- 0. SMART FILE OPENER (FIXED) ---
        # 1. Clean the name (Remove "Desktop/" if the Brain added it)
        # Also strip standalone "Desktop" word to prevent Desktop\Desktop duplication
        clean_name = app_name.replace("Desktop/", "").replace("Desktop\\", "").replace("desktop/", "").replace("desktop\\", "")
        # Additional fix: Remove "Desktop" word if it appears at the start (case-insensitive)
        clean_name = re.sub(r'^[Dd]esktop[\\/]?', '', clean_name).strip()
        # Remove any remaining "Desktop" word that might cause duplication
        if clean_name.lower().startswith("desktop"):
            clean_name = clean_name[7:].lstrip("\\/").strip()
        
        # 2. Build Paths
        # Path A: Exactly what was asked (e.g. "D:/Folder/file.txt")
        abs_path = app_name 
        # Path B: On the Desktop (e.g. "C:/Users/Akhil/Desktop/file.txt")
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", clean_name)
        
        # 3. Check and Open
        if target.endswith(('.pdf', '.txt', '.docx', '.png', '.jpg', '.py', '.cpp')):
            if os.path.exists(abs_path): 
                os.system(f'start "" "{abs_path}"')
                return f"Opened file: {app_name}"
            elif os.path.exists(desktop_path):
                os.system(f'start "" "{desktop_path}"')
                return f"Opened file from Desktop: {clean_name}"

        # --- 1. THE SEARCH TRAP ---
        if "search for" in target:
            query = target.split("search for")[-1].strip()
            safe_query = query.replace(" ", "+") 
            
            if "youtube" in target:
                os.system(f"start https://www.youtube.com/results?search_query={safe_query}")
                return f"Searching YouTube for '{query}'"
            elif "reddit" in target:
                os.system(f"start https://www.reddit.com/search/?q={safe_query}")
                return f"Searching Reddit for '{query}'"
            else:
                os.system(f"start https://www.google.com/search?q={safe_query}")
                return f"Searching Google for '{query}'"

        # --- 2. APP LIBRARY (Hardcoded Speed) ---
        user_path = os.path.expanduser("~")
        
        apps = {
            "file explorer": "explorer.exe",
            "explorer": "explorer.exe",
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "settings": "start ms-settings:",
            "cmd": "start cmd.exe",
            "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            "chrome": "chrome.exe",
            "telegram": r"C:\Users\Akhil\AppData\Roaming\Telegram Desktop\Telegram.exe",
            "figma": r"C:\Users\Akhil\AppData\Local\Figma\app-125.9.10\Figma.exe",
            "photoshop": r"C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe",
            "valorant": r"C:\Riot Games\Riot Client\RiotClientServices.exe",
            "tlauncher": r"C:\Users\Akhil\AppData\Roaming\.minecraft\TLauncher.exe",
            "ghelper": r"C:\Users\Akhil\Desktop\GHelper.exe",
            "phone link": "start ms-phone:",
            "phonelink": "start ms-phone:",
        }

        if target in apps:
            path = apps[target]
            is_system_cmd = "start " in path or "explorer" in path or "calc" in path or "notepad" in path
            
            if is_system_cmd or os.path.exists(path) or "--launch" in path:
                if "start " in path: os.system(path)
                else: os.system(f'start "" "{path}"')
                return f"Opening {target}..."

        # --- 3. THE HUNTER (Fallback) ---
        # Import inside function to prevent circular import crash
        from capabilities.app_opener import AppOpener
        return AppOpener.open_app(app_name)
        
    @staticmethod
    def close_application(app_name):
        """Closes an application by killing its process."""
        print(f"   [Tool] Closing: {app_name}")
        target = app_name.lower().strip()

        # --- PROCESS MAP (For Closing) ---
        processes = {
            "chrome": "chrome.exe",
            "brave": "brave.exe",
            "notepad": "notepad.exe",
            "calculator": "CalculatorApp.exe",
            "calc": "CalculatorApp.exe",
            "spotify": "spotify.exe",
            "discord": "discord.exe",
            "telegram": "telegram.exe",
            "photoshop": "photoshop.exe",
            "figma": "figma.exe",
            "valorant": "VALORANT-Win64-Shipping.exe",
            "riot": "RiotClientUx.exe",
            "ghelper": "GHelper.exe",
            "tlauncher": "javaw.exe",
            "minecraft": "javaw.exe",
            "phonelink": "PhoneExperienceHost.exe",
            "phone link": "PhoneExperienceHost.exe"
        }

        try:
            process_name = processes.get(target, f"{target}.exe")
            os.system(f"taskkill /F /IM {process_name} /T")
            return f"Closed {target}."
        except Exception as e:
            return f"Failed to close {target}: {e}"

    @staticmethod
    def get_system_status():
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        return f"CPU is at {cpu}%. Memory is at {memory}%."

    @staticmethod
    def close_jarvis():
        return "Shutting down systems. Goodbye, sir."