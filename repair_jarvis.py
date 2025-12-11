import os
import requests
import sys

# --- CONFIGURATION (v1.0 Standard) ---
ENGINE_DIR = os.path.join(os.getcwd(), "engine")
# New filenames
MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"

# Official v1.0 Release URLs
URL_MODEL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
URL_VOICES = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

def download_file(url, filename):
    path = os.path.join(ENGINE_DIR, filename)
    
    if os.path.exists(path):
        print(f"🗑️  Deleting old version: {filename}")
        try: os.remove(path)
        except: pass

    print(f"⬇️  Downloading {filename} (v1.0)...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = downloaded * 100 / total_size
                    sys.stdout.write(f"\r   Progress: {percent:.1f}%")
                    sys.stdout.flush()
        
        print(f"\n✅ Download Complete: {filename}")
             
    except Exception as e:
        print(f"\n❌ Download Error: {e}")

if __name__ == "__main__":
    print(">> STARTING v1.0 UPGRADE...")
    if not os.path.exists(ENGINE_DIR): os.makedirs(ENGINE_DIR)

    # 1. Clean up old v0.19 files if they exist
    old_files = ["kokoro-v0_19.onnx", "voices.json"]
    for f in old_files:
        p = os.path.join(ENGINE_DIR, f)
        if os.path.exists(p):
            print(f"🧹 Removing obsolete file: {f}")
            os.remove(p)

    # 2. Download new files
    download_file(URL_MODEL, MODEL_FILE)
    download_file(URL_VOICES, VOICES_FILE)
    
    print("\n>> UPGRADE COMPLETE. Please update 'speaker.py' next.")