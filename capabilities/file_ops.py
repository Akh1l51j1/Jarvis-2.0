import os
import shutil
import send2trash
from concurrent.futures import ThreadPoolExecutor

class FileOps:
    clipboard_path = None
    clipboard_action = None 

    USER_PATH = os.path.expanduser("~") 
    
    # 🛡️ WRITE WHITELIST
    SAFE_WRITE_PATHS = [
        USER_PATH.lower(),
        "d:\\",
        "e:\\"
    ]

    @staticmethod
    def _is_safe_to_write(path):
        path = os.path.abspath(path).lower()
        is_safe = any(path.startswith(safe) for safe in FileOps.SAFE_WRITE_PATHS)
        if "c:\\windows" in path or "c:\\program files" in path: return False
        return is_safe

    @staticmethod
    def find_file(filename):
        print(f"   [Analyst] Searching for: {filename}...")
        
        search_roots = [
            os.path.join(FileOps.USER_PATH, "Desktop"),
            os.path.join(FileOps.USER_PATH, "Downloads"),
            os.path.join(FileOps.USER_PATH, "Documents"),
            "D:\\",
            "E:\\"
        ]
        
        if filename.endswith(".exe"):
            search_roots.append(r"C:\Program Files")
            search_roots.append(r"C:\Program Files (x86)")
            search_roots.append(r"C:\Riot Games") # <--- ADDED FOR VALORANT
        
        def scan_root(root):
            try:
                for dirpath, _, filenames in os.walk(root):
                    if "windows" in dirpath.lower() or "$recycle" in dirpath.lower(): continue
                    if filename.lower() in [f.lower() for f in filenames]:
                        return os.path.join(dirpath, filename)
            except: pass
            return None

        with ThreadPoolExecutor() as executor:
            results = executor.map(scan_root, search_roots)
            
        for res in results:
            if res: return res

        return None

    # --- NEW TOOL ---
    @staticmethod
    def locate_file(filename):
        """Finds a file and returns its path (without reading content)."""
        path = FileOps.find_file(filename)
        if path:
            return f"Found it: {path}"
        return f"Could not locate '{filename}' in standard folders."

    # ... (Keep read_file, copy_file, cut_file, paste_file, delete_file exactly as before) ...
    # PASTE THE REST OF THE PREVIOUS file_ops.py CODE HERE (methods read_file down to delete_file)
    # If you want me to paste the full file again to be safe, let me know!
    
    @staticmethod
    def read_file(file_name):
        path = FileOps.find_file(file_name) if not os.path.exists(file_name) else file_name
        if not path or not os.path.exists(path): return f"Error: Could not find '{file_name}'."
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f"--- Content of {os.path.basename(path)} ---\n" + f.read()[:5000]
        except Exception as e: return f"Read Error: {e}"

    @staticmethod
    def copy_file(file_name):
        path = FileOps.find_file(file_name) if not os.path.exists(file_name) else file_name
        if path and os.path.exists(path):
            FileOps.clipboard_path = path
            FileOps.clipboard_action = 'copy'
            return f"Copied '{os.path.basename(path)}' to clipboard."
        return "File not found."

    @staticmethod
    def cut_file(file_name):
        path = FileOps.find_file(file_name) if not os.path.exists(file_name) else file_name
        if path and os.path.exists(path):
            if not FileOps._is_safe_to_write(path): return f"Safety Alert: Cannot cut from {path}."
            FileOps.clipboard_path = path
            FileOps.clipboard_action = 'cut'
            return f"Cut '{os.path.basename(path)}'."
        return "File not found."

    @staticmethod
    def paste_file(folder_path):
        if not FileOps.clipboard_path: return "Clipboard is empty."
        if "desktop" in folder_path.lower(): target_dir = os.path.join(FileOps.USER_PATH, "Desktop")
        elif "downloads" in folder_path.lower(): target_dir = os.path.join(FileOps.USER_PATH, "Downloads")
        elif "documents" in folder_path.lower(): target_dir = os.path.join(FileOps.USER_PATH, "Documents")
        else: target_dir = folder_path

        if not FileOps._is_safe_to_write(target_dir): return f"Safety Alert: Cannot paste into {target_dir}."
        if not os.path.exists(target_dir): return f"Error: Directory '{target_dir}' not found."

        try:
            filename = os.path.basename(FileOps.clipboard_path)
            destination = os.path.join(target_dir, filename)
            if FileOps.clipboard_action == 'copy': shutil.copy2(FileOps.clipboard_path, destination)
            elif FileOps.clipboard_action == 'cut': 
                shutil.move(FileOps.clipboard_path, destination)
                FileOps.clipboard_path = None
            return f"Success: Pasted '{filename}' to {target_dir}"
        except Exception as e: return f"Paste Error: {e}"

    @staticmethod
    def delete_file(file_name):
        path = FileOps.find_file(file_name) if not os.path.exists(file_name) else file_name
        if not path or not os.path.exists(path): return "File not found."
        if not FileOps._is_safe_to_write(path): return f"Safety Alert: Cannot delete system files in {path}."
        try:
            send2trash.send2trash(path)
            return f"Moved '{os.path.basename(path)}' to Recycle Bin."
        except Exception as e: return f"Delete Error: {e}"