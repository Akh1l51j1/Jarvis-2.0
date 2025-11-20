import pyttsx3
import winsound
import time

print("--- AUDIO DIAGNOSTIC ---")

# TEST 1: The Beep (System Sound)
print("\n1. Testing System Beep (Winsound)...")
try:
    print("   >> BEEP! (Listen now)")
    winsound.Beep(1000, 500) # 1000Hz for 0.5 seconds
    print("   ✅ Beep command sent.")
except Exception as e:
    print(f"   ❌ Beep Failed: {e}")

time.sleep(1)

# TEST 2: The Voice (SAPI5 Specific)
print("\n2. Testing Voice (SAPI5 driver)...")
try:
    engine = pyttsx3.init('sapi5') # Force Windows Driver
    voices = engine.getProperty('voices')
    
    print(f"   Found {len(voices)} voices.")
    if len(voices) > 0:
        print(f"   Using Voice: {voices[0].name}")
        engine.setProperty('voice', voices[0].id)
        
    engine.say("This is a test of the emergency broadcast system.")
    engine.runAndWait()
    print("   ✅ Voice command sent.")
except Exception as e:
    print(f"   ❌ Voice Failed: {e}")

print("\n--- END ---")