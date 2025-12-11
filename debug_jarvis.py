import os
import sys

print(">> DIAGNOSTIC MODE: STARTED")

# --- TEST 1: KOKORO (The likely culprit) ---
print("\n[TEST 1] Testing Kokoro TTS...")
try:
    from kokoro_onnx import Kokoro
    engine_dir = os.path.join(os.getcwd(), "engine")
    model_path = os.path.join(engine_dir, "kokoro-v0_19.onnx")
    voices_path = os.path.join(engine_dir, "voices.json")
    
    if not os.path.exists(model_path):
        print(f"   ❌ FAIL: Model file missing: {model_path}")
    elif not os.path.exists(voices_path):
        print(f"   ❌ FAIL: Voices file missing: {voices_path}")
    else:
        k = Kokoro(model_path, voices_path)
        print("   ✅ SUCCESS: Kokoro loaded perfectly.")
except Exception as e:
    print(f"   ❌ FAIL: Kokoro Crashed -> {e}")

# --- TEST 2: WHISPER ---
print("\n[TEST 2] Testing Whisper...")
try:
    from faster_whisper import WhisperModel
    w = WhisperModel("base", device="cpu", compute_type="int8")
    print("   ✅ SUCCESS: Whisper loaded perfectly.")
except Exception as e:
    print(f"   ❌ FAIL: Whisper Crashed -> {e}")

# --- TEST 3: SILERO VAD ---
print("\n[TEST 3] Testing Silero VAD (Torch)...")
try:
    import torch
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                  model='silero_vad',
                                  trust_repo=True)
    print("   ✅ SUCCESS: Silero VAD loaded perfectly.")
except Exception as e:
    print(f"   ❌ FAIL: Silero Crashed -> {e}")

print("\n>> DIAGNOSTIC COMPLETE.")