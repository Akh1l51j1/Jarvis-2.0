import sys
import os
import time
import psutil

# Ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from capabilities.file_ops import FileOps
    from capabilities.music_ops import music_engine
    from capabilities.gaming_ops import gaming_engine
except ImportError:
    # Fallback if your folder structure is flat
    from file_ops import FileOps
    from music_ops import music_engine
    from gaming_ops import gaming_engine

def run_test():
    print("=======================================")
    print("   TESTING JARVIS TOOLS")
    print("=======================================")
    
    # --- TEST 1: FILE CREATION ---
    print("\n>> Test 1: File Operations (Smart Path)")
    filename = "Jarvis_Test_Log.txt"
    content = "System Status: Nominal.\nPhase 4 Test Successful."
    
    print(f"   Creating file '{filename}' on Desktop...")
    # We pass "filename|content" because that's how the tool receives args from the LLM
    result = FileOps.write_to_file(f"{filename}|{content}")
    print(f"   Result: {result}")
    
    if "Success" in result:
        print("   ✅ CHECK YOUR DESKTOP! The file should be there.")
    else:
        print("   ❌ File creation failed.")

    # --- TEST 2: GAMING MODE ---
    print("\n>> Test 2: Gaming Mode (Resource Throttling)")
    print("   Engaging Gaming Mode (Low Priority)...")
    res = gaming_engine.toggle_gaming_mode(True)
    print(f"   Result: {res}")
    
    # Check actual process priority
    p = psutil.Process(os.getpid())
    prio = p.nice()
    print(f"   Current PID Priority: {prio}")
    
    if prio == psutil.BELOW_NORMAL_PRIORITY_CLASS:
        print("   ✅ Priority successfully lowered.")
    else:
        print("   ⚠️  Priority didn't change (Might need Admin, but usually fine).")

    # Restore
    gaming_engine.toggle_gaming_mode(False)
    print("   Restored to Normal Priority.")

    # --- TEST 3: SPOTIFY ---
    print("\n>> Test 3: Music Control")
    song = "Blinding Lights"
    print(f"   Requesting: '{song}'")
    
    # Note: This will actually open Spotify and play audio!
    res_music = music_engine.play_music(song)
    print(f"   Result: {res_music}")
    
    print("\n>> Waiting 10 seconds (Enjoy the music)...")
    time.sleep(10)
    
    print("   Pausing Music...")
    music_engine.pause_music()
    print("   ✅ Test Complete.")

if __name__ == "__main__":
    run_test()