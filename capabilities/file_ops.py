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
        
        if "volume" in clean or "drive" in clean:
            for word in clean.split():
                if len(word) == 1 and word.isalpha(): return f"{word.upper()}:\\"
        
        if len(clean) == 1 and clean.isalpha(): return f"{clean.upper()}:\\"
        return path_str

    @staticmethod
    def find_all_files(filename):
        print(f"   [Analyst] Scanning ALL drives for: {filename}...")
        
        if os.path.isabs(filename) and os.path.exists(filename):
            return [filename]

        clean_name = filename.lower().replace(".exe", "")
        
        roots = [
            os.path.join(FileOps.USER_PATH, "Desktop"),
            os.path.join(FileOps.USER_PATH, "Downloads"),
            "D:\\", "E:\\", "F:\\"
        ]
        
        appdata = os.getenv('APPDATA')
        if appdata: roots.append(os.path.join(appdata, "Spotify"))
        roots += [r"C:\Program Files", r"C:\Program Files (x86)"]

        found_files = []

        def scan(root):
            local_matches = []
            try:
                if not os.path.exists(root): return []
                for dirpath, dirnames, filenames in os.walk(root):
                    if "windows" in dirpath.lower() or "$recycle" in dirpath.lower(): continue
                    
                    for f in filenames:
                        if f.lower() == filename.lower():
                            local_matches.append(os.path.join(dirpath, f))
                    for d in dirnames:
                        if d.lower() == filename.lower():
                            local_matches.append(os.path.join(dirpath, d))
                    if not local_matches:
                        for f in filenames:
                            if SequenceMatcher(None, clean_name, f.lower()).ratio() > 0.85:
                                local_matches.append(os.path.join(dirpath, f))
            except: pass
            return local_matches

        with ThreadPoolExecutor() as ex:
            results = ex.map(scan, roots)
            
        for r in results:
            found_files.extend(r)
        return list(set(found_files))

    # --- TOOLS ---

    @staticmethod
    def _smart_path_builder(file_info):
        """Helper to decide if path is absolute (D:/) or relative (Desktop)."""
        clean_info = file_info.replace("/", "\\")
        
        # 1. Check for "D:\Folder" format
        if ":" in clean_info:
            return clean_info
            
        # 2. Check for "D/Folder" format (Brain often sends this)
        # If it starts with single letter + slash (e.g. "D\Mark 5")
        if len(clean_info) > 1 and clean_info[1] == "\\":
             first_char = clean_info[0].lower()
             if first_char in "defg":
                 return f"{first_char.upper()}:{clean_info[1:]}"

        # 3. Remove "Desktop" prefix if Brain added it redundantly
        if clean_info.lower().startswith("desktop\\"):
            clean_info = clean_info[8:]
            
        # 4. Default to Desktop
        return os.path.join(FileOps.USER_PATH, "Desktop", clean_info)

    @staticmethod
    def create_file(file_info):
        target_path = FileOps._smart_path_builder(file_info)

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
    def create_folder(folder_name):
        target_path = FileOps._smart_path_builder(folder_name)
        try:
            os.makedirs(target_path, exist_ok=True)
            return f"Success: Created folder '{target_path}'."
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def write_to_file(args):
        if "|" not in args: return "Error: Use format 'filename|content'"
        filename, content = args.split("|", 1)
        
        # Try to find existing first
        matches = FileOps.find_all_files(filename.strip())
        if matches and len(matches) == 1:
            path = matches[0]
        else:
            # If not found, create new using smart builder
            path = FileOps._smart_path_builder(filename.strip())

        if not FileOps._is_safe_to_write(path): return "Safety Alert."

        try:
            with open(path, 'w', encoding='utf-8') as f: f.write(content)
            return f"Success: Wrote to '{os.path.basename(path)}'."
        except Exception as e: return f"Write Error: {e}"

    @staticmethod
    def locate_file(filename):
        matches = FileOps.find_all_files(filename)
        if not matches: return f"Could not locate '{filename}'."
        if len(matches) == 1: return matches[0]
        
        response = f"I found {len(matches)} matches. Please specify which one:\n"
        for i, match in enumerate(matches, 1): response += f"{i}. {match}\n"
        return response

    @staticmethod
    def delete_file(filename):
        matches = FileOps.find_all_files(filename)
        if not matches: return "File not found."
        
        if len(matches) > 1:
            response = f"Found {len(matches)} files. Which one to delete?\n"
            for m in matches: response += f"- {m}\n"
            return response

        target = matches[0]
        if not FileOps._is_safe_to_write(target): return f"Safety Alert: Cannot delete {target}"
        
        try:
            send2trash.send2trash(target)
            return f"Deleted '{os.path.basename(target)}' from {os.path.dirname(target)}."
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def move_file(args):
        if "|" not in args: return "Error: Use format 'filename|destination'"
        file_name, dest_name = args.split("|", 1)
        
        matches = FileOps.find_all_files(file_name.strip())
        if not matches: return f"Error: Could not find '{file_name}'."
        if len(matches) > 1:
            return f"Found multiple files. Please specify source."
            
        src_path = matches[0]
        
        # Smart resolve for destination too
        if ":" in dest_name or dest_name.strip().lower().startswith("d") and len(dest_name) < 4:
             dest_dir = FileOps._resolve_path(dest_name.strip())
        else:
             dest_dir = FileOps._smart_path_builder(dest_name.strip())

        if not os.path.exists(dest_dir): 
            # Try creating directory if it looks like a folder path
            try: os.makedirs(dest_dir, exist_ok=True)
            except: return f"Error: Destination '{dest_dir}' invalid."
        
        if not FileOps._is_safe_to_write(src_path): return "Safety Alert."

        try:
            filename = os.path.basename(src_path)
            final_path = os.path.join(dest_dir, filename)
            shutil.move(src_path, final_path)
            return f"Success: Moved '{filename}' to '{dest_dir}'."
        except Exception as e: return f"Move Error: {e}"

    @staticmethod
    def read_file(file_name):
        matches = FileOps.find_all_files(file_name)
        if not matches: return "File not found."
        if len(matches) > 1: return f"Multiple files found."
        try:
            with open(matches[0], 'r', encoding='utf-8', errors='ignore') as f:
                return f"--- {os.path.basename(matches[0])} ---\n" + f.read()[:5000]
        except Exception as e: return f"Read Error: {e}"

    @staticmethod
    def copy_file(a): pass
    @staticmethod
    def cut_file(a): pass
    @staticmethod
    def paste_file(a): pass