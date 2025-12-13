import sqlite3
import os
import shutil

# CONFIGURATION
SQLITE_DB = "jarvis.db"
CHROMA_DB_FOLDER = "jarvis_memory_db"

def wipe_all():
    print("\n>> STARTING DATABASE WIPE...")

    # 1. WIPE SQLITE (Short Term / Logs)
    if os.path.exists(SQLITE_DB):
        try:
            conn = sqlite3.connect(SQLITE_DB)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                print(f"   [SQLite] Connected to '{SQLITE_DB}', but it is empty.")
            else:
                for table_name in tables:
                    table = table_name[0]
                    if table != "sqlite_sequence": # Don't delete internal sequence data
                        cursor.execute(f"DELETE FROM {table}")
                        print(f"   [SQLite] Deleted all rows from table: '{table}'")
            
            conn.commit()
            conn.close()
            print("   [SQLite] Wipe Complete.")
            
        except Exception as e:
            print(f"   [SQLite Error] {e}")
    else:
        print(f"   [SQLite] '{SQLITE_DB}' not found (Already Clean).")

    # 2. WIPE CHROMADB (Long Term Vectors)
    if os.path.exists(CHROMA_DB_FOLDER):
        try:
            # For Chroma, it is safer to just delete the folder. 
            # The code will auto-recreate it next time you run Jarvis.
            shutil.rmtree(CHROMA_DB_FOLDER)
            print(f"   [ChromaDB] Deleted folder '{CHROMA_DB_FOLDER}'.")
            print("   (It will be automatically recreated on next startup).")
        except Exception as e:
            print(f"   [ChromaDB Error] {e}")
    else:
        print(f"   [ChromaDB] Memory folder not found (Already Clean).")

    print("\n>> SUCCESS. Jarvis memory has been erased.")

if __name__ == "__main__":
    print("WARNING: This will delete ALL memories, logs, and facts.")
    choice = input("Are you sure you want to proceed? (type 'yes'): ")
    
    if choice.lower() == "yes":
        wipe_all()
    else:
        print("Cancelled.")