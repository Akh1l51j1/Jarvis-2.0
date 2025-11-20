import os

# The Project Map
project_structure = {
    "Jarvis2.0": [
        "main.py",
        "config.py",
        "requirements.txt",
    ],
    "Jarvis2.0/core": [
        "__init__.py",
        "agent.py",
        "llm.py",
        "prompts.py",
    ],
    "Jarvis2.0/capabilities": [
        "__init__.py",
        "library.py",
        "system_ops.py",
        "music_ops.py",
        "rag_ops.py",
    ],
    "Jarvis2.0/engine": [
        "__init__.py",
        "listener.py",
        "speaker.py",
    ],
    "Jarvis2.0/utils": [
        "__init__.py",
        "helper.py",
    ]
}

def create_structure():
    print("🚀 Initializing Jarvis 2.0 Protocol...")
    
    for folder, files in project_structure.items():
        # Create the folder
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"   [OK] Created Folder: {folder}")
        except Exception as e:
            print(f"   [Error] Could not create {folder}: {e}")
        
        # Create the files inside
        for file in files:
            file_path = os.path.join(folder, file)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    # Write a tiny comment so the file isn't empty
                    f.write(f"# Jarvis 2.0 - {file}\n")
                print(f"      - Created File: {file}")
            else:
                print(f"      - File already exists: {file}")

    print("\n✅ Jarvis 2.0 Environment Ready.")
    print("👉 Next Step: Open 'Jarvis2.0/requirements.txt' and install dependencies.")

if __name__ == "__main__":
    create_structure()