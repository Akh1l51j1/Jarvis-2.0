import os
import PyPDF2
import docx

class FileOps:
    @staticmethod
    def read_file(file_path):
        """Reads content from TXT, PDF, or DOCX files."""
        print(f"   [Analyst] Reading: {file_path}")
        
        # Handle relative paths (e.g., "notes.txt" -> "D:\jarvis 2.0\notes.txt")
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
            
        try:
            ext = file_path.split('.')[-1].lower()
            
            if ext in ['txt', 'py', 'md', 'json', 'csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()[:10000] # Limit to 10k chars to save token costs
                    
            elif ext == 'pdf':
                text = ""
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    # Read first 10 pages max
                    for i, page in enumerate(reader.pages):
                        if i > 10: break
                        text += page.extract_text() + "\n"
                return text
                
            elif ext == 'docx':
                doc = docx.Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text
                
            else:
                return "Error: Unsupported file format. I can read .txt, .pdf, .docx, .py"
                
        except Exception as e:
            return f"Read Error: {e}"

    @staticmethod
    def create_file(file_name, content):
        """Creates a text file with the given content."""
        print(f"   [Analyst] Writing File: {file_name}")
        try:
            # Default to Desktop if no path given
            if "\\" not in file_name and "/" not in file_name:
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                file_path = os.path.join(desktop, file_name)
            else:
                file_path = file_name
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Success: File created at {file_path}"
        except Exception as e:
            return f"Write Error: {e}"
            
    @staticmethod
    def list_files(directory):
        """Lists files in a specific directory."""
        print(f"   [Analyst] Scanning: {directory}")
        
        # Smart Shortcuts
        if "download" in directory.lower():
            directory = os.path.join(os.path.expanduser("~"), "Downloads")
        elif "desktop" in directory.lower():
            directory = os.path.join(os.path.expanduser("~"), "Desktop")
        elif "document" in directory.lower():
            directory = os.path.join(os.path.expanduser("~"), "Documents")
            
        if not os.path.exists(directory):
             return f"Error: Directory {directory} not found."
             
        try:
            files = os.listdir(directory)
            # Filter for readable files to keep list clean
            readable = [f for f in files if not f.startswith('.')]
            return "Files found:\n" + "\n".join(readable[:20]) # Limit to 20
        except Exception as e:
            return f"Scan Error: {e}"