import sys
import time
from datetime import datetime
from engine.listener import AudioListener
from engine.speaker import Speaker
from core.llm import Brain
import config
from capabilities.music_ops import music_engine 
from server_bridge import bridge

# SETTINGS
CONVERSATION_TIMEOUT = 15 

def startup_sequence(mouth, brain):
    bridge.update_status("BOOTING", "Systems Initializing...")
    print("\n>> INITIALIZING SYSTEMS...")
    mouth.play_sound("startup")
    time.sleep(0.5)
    greeting = brain.get_greeting()
    print(f"JARVIS: {greeting}")
    bridge.update_status("SPEAKING", "Online")
    bridge.log(f"JARVIS: {greeting}")
    mouth.speak(greeting)

def main():
    print("\n>> STARTING JARVIS 2.0")
    print("------------------------")
    
    try: bridge.start()
    except Exception as e: print(f"Bridge Error: {e}")

    try:
        ear = AudioListener()
        mouth = Speaker()
        brain = Brain()
    except Exception as e:
        print(f"\n>> CRITICAL STARTUP ERROR: {e}")
        return

    startup_sequence(mouth, brain)
    
    conversation_mode = False
    last_active_time = 0

    while True:
        try:
            if conversation_mode:
                bridge.update_status("LISTENING", "Active Mode")
                remaining = int(CONVERSATION_TIMEOUT - (time.time() - last_active_time))
                print(f"\n>> Active Mode (Timeout in {remaining}s)...")
            else:
                bridge.update_status("IDLE", "Waiting for Wake Word...")
                print("\n>> Waiting for Wake Word...")

            # --- LISTEN ---
            user_text = ear.listen()
            
            # --- 1. SMART TIMEOUT CHECK (THE FIX) ---
            # Only timeout if user said NOTHING.
            # If user spoke (len > 3), reset timer and process.
            has_spoken = len(user_text) > 3
            
            if conversation_mode and not has_spoken:
                if (time.time() - last_active_time > CONVERSATION_TIMEOUT):
                    print(">> Time out. Returning to Standby.")
                    mouth.play_sound("shutdown") 
                    mouth.speak("Standing by, Sir.") # <--- ADDED VOICE
                    conversation_mode = False
                    continue
            
            if not has_spoken: 
                if not conversation_mode:
                    last_active_time = time.time() # Keep it fresh
                continue

            # --- 2. WAKE WORD CHECK ---
            is_wake_word = False
            for word in config.WAKE_WORDS:
                if word in user_text.lower():
                    is_wake_word = True
                    break
            
            should_process = False
            
            if is_wake_word:
                should_process = True
                conversation_mode = True
                last_active_time = time.time()
            elif conversation_mode:
                # User spoke in active mode -> Process it AND Reset Timer
                should_process = True
                last_active_time = time.time() # Reset timer because they spoke
            
            if should_process:
                print(f"USER: {user_text}")
                bridge.log(f"USER: {user_text}")

                if is_wake_word: mouth.play_sound("listen")

                was_playing = music_engine.is_playing()
                if was_playing: music_engine.pause_music()

                command = user_text.lower()
                for word in config.WAKE_WORDS:
                    command = command.replace(word, "").strip()
                if "braille" in command: command = command.replace("braille", "brave")

                soft_triggers = ["nothing", "no thanks", "stop listening", "bye", "goodbye"]
                if any(trigger in command for trigger in soft_triggers):
                    mouth.speak("Standing by, Sir.")
                    conversation_mode = False
                    if was_playing: music_engine.resume_music()
                    continue 

                if "shut down" in command or "power off" in command:
                    mouth.speak("Goodbye, Sir.")
                    sys.exit(0)

                if len(command) > 2:
                    bridge.update_status("PROCESSING", "Thinking...")
                    response = brain.think(command)
                    
                    # --- THE FIX: Only print if there is actually a response ---
                    if response and response.strip():
                        print(f"JARVIS: {response}")
                        bridge.log(f"JARVIS: {response}")
                        bridge.update_status("SPEAKING", "Replying...")
                        mouth.speak(response)
                    
                    last_active_time = time.time() 
                       
                else:
                    print("   (No command heard)")

                stop_keywords = ["stop", "pause", "quiet", "silence", "play", "song", "close", "terminate", "exit", "quit"]
                is_stop_command = any(k in command for k in stop_keywords)

                if was_playing and not is_stop_command:
                    time.sleep(0.5)
                    music_engine.resume_music()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f">> Loop Error: {e}")

if __name__ == "__main__":
    main()