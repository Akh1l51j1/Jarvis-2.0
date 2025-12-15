import os
import shutil
import send2trash
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher

class FileOps:
    clipboard_path = None
    clipboard_action = None 
    USER_PATH = os.path.expanduser("~") 
    SAFE_WRITE_PATHS = [USER_PATH.lower(), "d:\\", "e:\\", "f:\\", "g:\\", "b:\\"]

    @staticmethod
    def _is_safe_to_write(path):
        path = os.path.abspath(path).lower()
        if "c:\\windows" in path or "c:\\program files" in path: return False
        return any(path.startswith(safe) for safe in FileOps.SAFE_WRITE_PATHS)

    @staticmethod
    def _resolve_path(path_str):
        clean = path_str.strip().strip('"').strip("'").lower()
        if "desktop" in clean: return os.path.join(FileOps.USER_PATH, "Desktop")
        if "downloads" in clean: return os.path.join(FileOps.USER_PATH, "Downloads")
        if "documents" in clean: return os.path.join(FileOps.USER_PATH, "Documents")
        
        # Handle "Drive D", "Volume E"
        if "volume" in clean or "drive" in clean:
            for word in clean.split():
                if len(word) == 1 and word.isalpha(): return f"{word.upper()}:\\"
        
        if len(clean) == 1 and clean.isalpha(): return f"{clean.upper()}:\\"
        return path_str

    @staticmethod
    def find_file(filename):
        print(f"   [Analyst] Searching for: {filename}...")
        clean_name = filename.lower().replace(".exe", "")
        
        roots = [
            os.path.join(FileOps.USER_PATH, "Desktop"),
            os.path.join(FileOps.USER_PATH, "Downloads"),
            "D:\\", "E:\\", "F:\\"
        ]
        
        appdata = os.getenv('APPDATA')
        if appdata: roots.append(os.path.join(appdata, "Spotify"))
        roots += [r"C:\Program Files", r"C:\Program Files (x86)"]

        def scan(root):
            try:
                if not os.path.exists(root): return None
                for dirpath, dirnames, filenames in os.walk(root):
                    if "windows" in dirpath.lower() or "$recycle" in dirpath.lower(): continue
                    
                    for f in filenames:
                        if f.lower() == filename.lower(): return os.path.join(dirpath, f)
                    for d in dirnames:
                        if d.lower() == filename.lower(): return os.path.join(dirpath, d)
                    for f in filenames:
                        if SequenceMatcher(None, clean_name, f.lower()).ratio() > 0.85:
                            return os.path.join(dirpath, f)
            except: pass
            return None

        with ThreadPoolExecutor() as ex:
            results = ex.map(scan, roots)
        for r in results: 
            if r: return r
        return None

    # --- TOOLS ---

    @staticmethod
    def move_file(args):
        """Moves a file/folder to a destination. Arg: filename|destination"""
        try:
            if "|" not in args: return "Error: Use format 'filename|destination'"
            file_name, dest_name = args.split("|", 1)
            
            # 1. Find Source
            src_path = FileOps.find_file(file_name.strip())
            if not src_path: return f"Error: Could not find '{file_name}'."
            
            # 2. Resolve Destination
            dest_dir = FileOps._resolve_path(dest_name.strip())
            if not os.path.exists(dest_dir): return f"Error: Destination '{dest_dir}' does not exist."
            
            # 3. Security Check
            if not FileOps._is_safe_to_write(src_path) or not FileOps._is_safe_to_write(dest_dir):
                return "Safety Alert: Access Denied to system paths."

            # 4. Move
            filename = os.path.basename(src_path)
            final_path = os.path.join(dest_dir, filename)
            shutil.move(src_path, final_path)
            
            return f"Success: Moved '{filename}' to '{dest_dir}'."
            
        except Exception as e: return f"Move Error: {e}"

    @staticmethod
    def create_file(file_info):
        clean_info = file_info.replace("/", "\\")
        if clean_info.lower().startswith("desktop\\"): clean_info = clean_info[8:] 

        if ":" in clean_info: target_path = clean_info
        else: target_path = os.path.join(FileOps.USER_PATH, "Desktop", clean_info)

        if not FileOps._is_safe_to_write(target_path): return "Safety Alert: Access Denied."
        
        try:
            folder = os.path.dirname(target_path)
            if folder and not os.path.exists(folder): os.makedirs(folder)
            
            if not os.path.exists(target_path):
                with open(target_path, 'w') as f: f.write("")
                return f"Success: Created '{os.path.basename(target_path)}' in '{folder}'."
            else:
                return f"File '{os.path.basename(target_path)}' already exists."
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def write_to_file(args):
        try:
            if "|" not in args: return "Error: Use format 'filename|content'"
            filename, content = args.split("|", 1)
            path = FileOps.find_file(filename.strip())
            if not path: path = os.path.join(FileOps.USER_PATH, "Desktop", filename.strip())

            if not FileOps._is_safe_to_write(path): return "Safety Alert: Access Denied."

            with open(path, 'w', encoding='utf-8') as f: f.write(content)
            return f"Success: Wrote to '{os.path.basename(path)}'."
        except Exception as e: return f"Write Error: {e}"

    @staticmethod
    def create_folder(folder_name):
        clean_name = folder_name.replace("/", "\\")
        if clean_name.lower().startswith("desktop\\"): clean_name = clean_name[8:]
        target_path = os.path.join(FileOps.USER_PATH, "Desktop", clean_name)
        try:
            os.makedirs(target_path, exist_ok=True)
            return f"Success: Created folder '{clean_name}'."
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def locate_file(filename):
        path = FileOps.find_file(filename)
        return path if path else f"Could not locate '{filename}'."

    @staticmethod
    def read_file(file_name):
        path = FileOps.find_file(file_name)
        if not path: return "File not found."
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f"--- {os.path.basename(path)} ---\n" + f.read()[:5000]
        except Exception as e: return f"Read Error: {e}"

    @staticmethod
    def delete_file(file_name):
        path = FileOps.find_file(file_name)
        if path:
            try:
                send2trash.send2trash(path)
                return f"Deleted '{os.path.basename(path)}'."
            except Exception as e: return f"Error: {e}"
        return "File not found."

    # Keep these for compatibility, but 'move_file' is better
    @staticmethod
    def copy_file(file_name):
        path = FileOps.find_file(file_name)
        if path:
            FileOps.clipboard_path = path
            FileOps.clipboard_action = 'copy'
            return f"Copied '{os.path.basename(path)}'."
        return "File not found."

    @staticmethod
    def cut_file(file_name):
        path = FileOps.find_file(file_name)
        if path:
            if not FileOps._is_safe_to_write(path): return "Safety Alert."
            FileOps.clipboard_path = path
            FileOps.clipboard_action = 'cut'
            return f"Cut '{os.path.basename(path)}'."
        return "File not found."

    @staticmethod
    def paste_file(destination):
        if not FileOps.clipboard_path: return "Clipboard empty."
        target_dir = FileOps._resolve_path(destination)
        if not os.path.exists(target_dir): return f"Error: '{target_dir}' not found."
        try:
            filename = os.path.basename(FileOps.clipboard_path)
            final_path = os.path.join(target_dir, filename)
            if FileOps.clipboard_action == 'copy': 
                if os.path.isdir(FileOps.clipboard_path): shutil.copytree(FileOps.clipboard_path, final_path)
                else: shutil.copy2(FileOps.clipboard_path, final_path)
            elif FileOps.clipboard_action == 'cut': 
                shutil.move(FileOps.clipboard_path, final_path)
                FileOps.clipboard_path = None
            return f"Pasted to {target_dir}"
        except Exception as e: return f"Paste Error: {e}"