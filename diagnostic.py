import sys
import time
import os

# --- IMPORT CAPABILITIES ---
print(">> [Init] Loading Modules... (This may take a moment)")
try:
    from engine.speaker import Speaker
    from engine.listener import AudioListener
    from core.llm import Brain
    from capabilities.music_ops import music_engine
    from capabilities.system_ops import SystemOps
    from capabilities.file_ops import FileOps
    from capabilities.rag_ops import rag_engine
    from server_bridge import bridge
    print(">> [Init] All Modules Loaded Successfully.\n")
except Exception as e:
    print(f"\n❌ CRITICAL IMPORT ERROR: {e}")
    print("   Make sure you are running this from the 'D:\\jarvis 2.0' folder.")
    sys.exit(1)

def test_speaker():
    print("\n--- TESTING SPEAKER (TTS) ---")
    print("   Action: Attempting to speak 'Diagnostic test initiated'.")
    try:
        mouth = Speaker()
        mouth.speak("Diagnostic test initiated.")
        print("   ✅ SUCCESS: Did you hear the voice?")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

def test_listener():
    print("\n--- TESTING LISTENER (STT) ---")
    print("   Action: Speak something into your mic NOW.")
    try:
        ear = AudioListener()
        text = ear.listen()
        print(f"   ✅ SUCCESS: I heard: '{text}'")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

def test_brain():
    print("\n--- TESTING BRAIN (LLM) ---")
    print("   Action: Sending 'Hello' to Llama 3.3...")
    try:
        brain = Brain()
        response = brain.think("Hello Jarvis, are you online?")
        print(f"   ✅ SUCCESS: Response: {response}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

def test_music():
    print("\n--- TESTING MUSIC (SPOTIFY) ---")
    print("   Action: Searching for 'Starboy'...")
    try:
        # Test Search & Play
        result = music_engine.play_music("Starboy by The Weeknd")
        print(f"   [Play Result]: {result}")
        
        print("   Action: Waiting 10 seconds (Listen for music)...")
        time.sleep(10)
        
        # Test Pause
        print("   Action: Testing Pause...")
        print(f"   [Pause Result]: {music_engine.pause_music()}")
        
        print("   ✅ SUCCESS: If music played and paused, this module is perfect.")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

def test_system():
    print("\n--- TESTING SYSTEM OPS ---")
    try:
        # Test System Status
        stats = SystemOps.get_system_status()
        print(f"   [Status]: {stats}")
        
        # Test Calculator (Safe App)
        print("   Action: Opening Calculator...")
        SystemOps.open_application("calculator")
        time.sleep(3)
        print("   Action: Closing Calculator...")
        SystemOps.close_application("calculator")
        
        print("   ✅ SUCCESS: Apps opened/closed.")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

def test_files():
    print("\n--- TESTING FILE OPS ---")
    test_file = "diagnostic_test.txt"
    try:
        # Create Dummy File
        with open(test_file, "w") as f: f.write("This is a test.")
        print(f"   [Setup] Created {test_file}")
        
        # Test Locate
        loc = FileOps.locate_file(test_file)
        print(f"   [Locate]: {loc}")
        
        # Test Delete
        print(f"   [Delete]: Attempting to delete {test_file}...")
        res = FileOps.delete_file(test_file)
        print(f"   [Result]: {res}")
        
        print("   ✅ SUCCESS: File operations working.")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

def test_memory():
    print("\n--- TESTING MEMORY (RAG) ---")
    try:
        # Test Save
        fact = "The diagnostic test run was successful."
        print(f"   Action: Saving memory -> '{fact}'")
        rag_engine.save_memory(fact)
        
        # Test Read
        print("   Action: Reading back memory...")
        retrieved = rag_engine.retrieve_memory("diagnostic test")
        print(f"   [Memory Found]: {retrieved}")
        
        print("   ✅ SUCCESS: RAG database is active.")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

def test_ui():
    print("\n--- TESTING UI BRIDGE ---")
    print("   ⚠️  REQUIREMENT: Run 'python launcher.py' in a separate terminal FIRST.")
    print("   This test only works if the UI window is already open.")
    print("   Action: Sending Color Cycle to UI...")
    
    try:
        bridge.start()
        time.sleep(1)
        
        colors = [
            ("LISTENING", "Testing Red (Listening)"),
            ("PROCESSING", "Testing Orange (Thinking)"),
            ("SPEAKING", "Testing Blue (Speaking)"),
            ("IDLE", "Testing Grey (Idle)")
        ]
        
        for status, msg in colors:
            print(f"   -> Sending {status}...")
            bridge.update_status(status, msg)
            bridge.log(f"DIAGNOSTIC: {msg}")
            time.sleep(2)
            
        print("   ✅ SUCCESS: Did the UI change colors?")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

def main_menu():
    while True:
        print("\n=================================")
        print("   JARVIS DIAGNOSTIC TOOL v1.0   ")
        print("=================================")
        print("1. Test Speaker (TTS)")
        print("2. Test Listener (Mic)")
        print("3. Test Brain (LLM Connection)")
        print("4. Test Music (Spotify)")
        print("5. Test System (Apps)")
        print("6. Test Files (Search/Delete)")
        print("7. Test Memory (Database)")
        print("8. Test UI Bridge (Visuals)")
        print("0. EXIT")
        
        choice = input("\nSelect Module to Test (0-8): ")
        
        if choice == '1': test_speaker()
        elif choice == '2': test_listener()
        elif choice == '3': test_brain()
        elif choice == '4': test_music()
        elif choice == '5': test_system()
        elif choice == '6': test_files()
        elif choice == '7': test_memory()
        elif choice == '8': test_ui()
        elif choice == '0': break
        else: print("Invalid choice.")
        
        input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    main_menu()