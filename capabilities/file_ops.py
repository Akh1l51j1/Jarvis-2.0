import os
import shutil
import send2trash
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher

class FileOps:
    clipboard_path = None
    clipboard_action = None 
    USER_PATH = os.path.expanduser("~") 
    
    # Smart OneDrive Detection
    onedrive_desktop = os.path.join(USER_PATH, "OneDrive", "Desktop")
    local_desktop = os.path.join(USER_PATH, "Desktop")
    DESKTOP_PATH = onedrive_desktop if os.path.exists(onedrive_desktop) else local_desktop

    SAFE_WRITE_PATHS = [USER_PATH.lower(), "d:\\", "e:\\", "f:\\", "g:\\", "b:\\"]

    @staticmethod
    def _is_safe_to_write(path):
        path = os.path.abspath(path).lower()
        if "c:\\windows" in path or "c:\\program files" in path: return False
        return any(path.startswith(safe) for safe in FileOps.SAFE_WRITE_PATHS)

    @staticmethod
    def _smart_path_builder(file_info):
        """Helper to decide if path is absolute (D:/) or relative (Desktop)."""
        # --- THE FIX: STRIP QUOTES AND SPACES ---
        clean_info = file_info.replace("/", "\\").strip().strip('"').strip("'")
        
        # 1. Check for "D:\Folder" format
        if ":" in clean_info:
            return clean_info
            
        # 2. Check for "D/Folder" format (Brain often sends this)
        if len(clean_info) > 1 and clean_info[1] == "\\":
             first_char = clean_info[0].lower()
             if first_char in "defg":
                 return f"{first_char.upper()}:{clean_info[1:]}"

        # 3. Handle "Desktop\File.txt"
        if clean_info.lower().startswith("desktop\\"):
            clean_info = clean_info[8:] # Strip "desktop\"
            return os.path.join(FileOps.DESKTOP_PATH, clean_info)
            
        # 4. Default to Desktop if just a name
        return os.path.join(FileOps.DESKTOP_PATH, clean_info)

    @staticmethod
    def find_all_files(filename):
        print(f"   [Analyst] Scanning ALL drives for: {filename}...")
        
        base = filename.strip().strip('"').strip("'")
        variants = {base, base.replace("_", " "), base.replace(" ", "_")}
        
        # Fast Path: If it's already an absolute path, check it immediately
        if os.path.isabs(base):
            if os.path.exists(base): return [base]
            # Check variants
            folder = os.path.dirname(base)
            name = os.path.basename(base)
            name_variants = {name, name.replace("_", " "), name.replace(" ", "_")}
            if os.path.exists(folder):
                for v in name_variants:
                    test_path = os.path.join(folder, v)
                    if os.path.exists(test_path): return [test_path]

        clean_name = base.lower().replace(".exe", "")
        
        roots = [
            FileOps.DESKTOP_PATH,
            os.path.join(FileOps.USER_PATH, "Downloads"),
            "D:\\", "E:\\", "F:\\"
        ]
        
        found_files = []

        def scan(root):
            local_matches = []
            try:
                if not os.path.exists(root): return []
                for dirpath, dirnames, filenames in os.walk(root):
                    if "windows" in dirpath.lower() or "$recycle" in dirpath.lower(): continue
                    if ".git" in dirpath.lower() or "node_modules" in dirpath.lower(): continue
                    
                    for f in filenames:
                        if any(v.lower() == f.lower() for v in variants):
                            local_matches.append(os.path.join(dirpath, f))
                    
                    for d in dirnames:
                        if any(v.lower() == d.lower() for v in variants):
                            local_matches.append(os.path.join(dirpath, d))
                            
                    if not local_matches:
                        for f in filenames:
                            if SequenceMatcher(None, clean_name, f.lower()).ratio() > 0.85:
                                local_matches.append(os.path.join(dirpath, f))
                        for d in dirnames:
                            if SequenceMatcher(None, clean_name, d.lower()).ratio() > 0.85:
                                local_matches.append(os.path.join(dirpath, d))
            except: pass
            return local_matches

        with ThreadPoolExecutor() as ex:
            results = ex.map(scan, roots)
            
        for r in results:
            found_files.extend(r)
        return list(set(found_files))

    # --- TOOLS ---

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
        
        if "/" in filename or "\\" in filename:
             path = FileOps._smart_path_builder(filename.strip())
        else:
             matches = FileOps.find_all_files(filename.strip())
             if matches and len(matches) == 1:
                 path = matches[0]
             else:
                 path = FileOps._smart_path_builder(filename.strip())

        if not FileOps._is_safe_to_write(path): return "Safety Alert."

        try:
            with open(path, 'w', encoding='utf-8') as f: f.write(content)
            return f"Success: Wrote to '{os.path.basename(path)}'."
        except Exception as e: return f"Write Error: {e}"

    @staticmethod
    def locate_file(filename):
        # 1. PATH PRIORITY (Strip Quotes too!)
        if "/" in filename or "\\" in filename:
             direct_path = FileOps._smart_path_builder(filename)
             if os.path.exists(direct_path):
                 return direct_path

        # 2. DEEP SCAN
        matches = FileOps.find_all_files(filename)
        if not matches: return f"Could not locate '{filename}'."
        if len(matches) == 1: return matches[0]
        
        response = f"I found {len(matches)} matches. Please specify which one:\n"
        for i, match in enumerate(matches, 1): response += f"{i}. {match}\n"
        return response

    @staticmethod
    def delete_file(filename):
        # 1. PATH PRIORITY (Strip Quotes too!)
        if "/" in filename or "\\" in filename:
             direct_path = FileOps._smart_path_builder(filename)
             if os.path.exists(direct_path):
                 target = direct_path
                 if not FileOps._is_safe_to_write(target): return "Safety Alert."
                 try:
                     if os.path.isfile(target):
                         send2trash.send2trash(target)
                         return f"Success: Deleted file '{os.path.basename(target)}'."
                     elif os.path.isdir(target):
                         send2trash.send2trash(target)
                         return f"Success: Deleted folder '{os.path.basename(target)}'."
                 except Exception as e: return f"Error: {e}"

        matches = FileOps.find_all_files(filename)
        
        if not matches: return f"File '{filename}' not found."
        
        if len(matches) > 1:
            response = f"Found {len(matches)} files. Which one to delete?\n"
            for m in matches: response += f"- {m}\n"
            return response

        target = matches[0]
        if not FileOps._is_safe_to_write(target): return f"Safety Alert: Cannot delete {target}"
        
        try:
            if os.path.isfile(target):
                send2trash.send2trash(target)
                return f"Success: Deleted file '{os.path.basename(target)}'."
            elif os.path.isdir(target):
                send2trash.send2trash(target)
                return f"Success: Deleted folder '{os.path.basename(target)}'."
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def move_file(args):
        if "|" not in args: return "Error: Use format 'filename|destination'"
        file_name, dest_name = args.split("|", 1)
        
        src_path = None
        if "/" in file_name or "\\" in file_name:
             check_path = FileOps._smart_path_builder(file_name.strip())
             if os.path.exists(check_path): src_path = check_path
        
        if not src_path:
            matches = FileOps.find_all_files(file_name.strip())
            if not matches: return f"Error: Could not find '{file_name}'."
            if len(matches) > 1: return f"Found multiple files. Please specify source."
            src_path = matches[0]
        
        dest_dir = FileOps._smart_path_builder(dest_name.strip())

        if not os.path.exists(dest_dir): 
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
        if "/" in file_name or "\\" in file_name:
             direct_path = FileOps._smart_path_builder(file_name.strip())
             if os.path.exists(direct_path):
                 try:
                     with open(direct_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f"--- {os.path.basename(direct_path)} ---\n" + f.read()[:5000]
                 except Exception as e: return f"Read Error: {e}"

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