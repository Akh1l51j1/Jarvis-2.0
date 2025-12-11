import os
import requests

# Define paths
engine_dir = os.path.join(os.getcwd(), "engine")
model_path = os.path.join(engine_dir, "silero_vad.jit")

# --- FIXED URL (Using v4.0 tag for stability) ---
url = "https://github.com/snakers4/silero-vad/raw/v4.0/files/silero_vad.jit"

if __name__ == "__main__":
    if not os.path.exists(engine_dir):
        os.makedirs(engine_dir)
        
    print(f"⬇️  Downloading Silero VAD model (v4.0)...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Check for 404 errors
        
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"✅ Saved to: {model_path}")
        print("You can now run 'python main.py'")
        
    except Exception as e:
        print(f"❌ Error: {e}")