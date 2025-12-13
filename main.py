import sys
import time
from datetime import datetime
from engine.listener import AudioListener
from engine.speaker import Speaker
from core.llm import Brain
import config
from capabilities.music_ops import music_engine 
from server_bridge import bridge # <--- 1. IMPORT BRIDGE

# SETTINGS
CONVERSATION_TIMEOUT = 15 

def startup_sequence(mouth, brain):
    bridge.update_status("BOOTING", "Systems Initializing...") # <--- 2. UI STATUS
    print("\n>> INITIALIZING SYSTEMS...")
    mouth.play_sound("startup")
    time.sleep(0.5)
    greeting = brain.get_greeting()
    print(f"JARVIS: {greeting}")
    
    bridge.update_status("SPEAKING", "Online") # <--- 3. UI STATUS
    bridge.log(f"JARVIS: {greeting}")          # <--- 4. UI LOG
    mouth.speak(greeting)

def main():
    print("\n>> STARTING JARVIS 2.0")
    print("------------------------")
    
    # --- ADD THIS BLOCK HERE ---
    try:
        bridge.start()
    except Exception as e:
        print(f"Bridge Error: {e}")
    # ---------------------------

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
            # --- STATUS DISPLAY ---
            if conversation_mode:
                bridge.update_status("LISTENING", "Active Mode") # <--- 5. UI UPDATE
                remaining = int(CONVERSATION_TIMEOUT - (time.time() - last_active_time))
                print(f"\n>> Active Mode (Timeout in {remaining}s)...")
            else:
                bridge.update_status("IDLE", "Waiting for Wake Word...") # <--- 6. UI UPDATE
                print("\n>> Waiting for Wake Word...")

            # --- LISTEN ---
            user_text = ear.listen()
            
            # 1. TIMEOUT CHECK
            if conversation_mode and (time.time() - last_active_time > CONVERSATION_TIMEOUT):
                print(">> Time out. Returning to Standby.")
                mouth.play_sound("shutdown") 
                conversation_mode = False
                # If we timed out, ignore whatever was just heard (usually noise)
                continue

            # 2. NOISE FILTER
            if len(user_text) < 3: continue 

            # 3. WAKE WORD CHECK
            is_wake_word = False
            for word in config.WAKE_WORDS:
                if word in user_text.lower():
                    is_wake_word = True
                    break
            
            should_process = False
            
            # LOGIC: If we hear wake word, we ALWAYS process.
            # If we are in conversation mode, we process everything.
            if is_wake_word:
                should_process = True
                conversation_mode = True
                last_active_time = time.time()
            elif conversation_mode:
                should_process = True
                last_active_time = time.time()
            
            if should_process:
                print(f"USER: {user_text}")
                bridge.log(f"USER: {user_text}") # <--- 7. UI LOG

                if is_wake_word: mouth.play_sound("listen")

                # Auto-Duck (Pause Music while listening/thinking)
                was_playing = music_engine.is_playing()
                if was_playing: music_engine.pause_music()

                # Clean Command
                command = user_text.lower()
                for word in config.WAKE_WORDS:
                    command = command.replace(word, "").strip()
                
                # --- PHONETIC CLEANUP ---
                if "braille" in command: command = command.replace("braille", "brave")

                # --- DISMISSAL ---
                soft_triggers = ["nothing", "no thanks", "stop listening", "bye", "goodbye"]
                if any(trigger in command for trigger in soft_triggers):
                    mouth.speak("Standing by, Sir.")
                    conversation_mode = False
                    if was_playing: music_engine.resume_music()
                    continue 

                # --- KILL SWITCH ---
                if "shut down" in command or "power off" in command:
                    mouth.speak("Goodbye, Sir.")
                    sys.exit(0)

                # --- BRAIN EXECUTION ---
                if len(command) > 2:
                    bridge.update_status("PROCESSING", "Thinking...") # <--- 8. UI THINKING
                    response = brain.think(command)
                    print(f"JARVIS: {response}")
                    
                    bridge.log(f"JARVIS: {response}") # <--- 9. UI LOG
                    bridge.update_status("SPEAKING", "Replying...") # <--- 10. UI SPEAKING
                    
                    mouth.speak(response)
                    last_active_time = time.time() 
                    
                    # --- MUSIC MODE FIX (Crucial) ---
                    # If the user asked for music, DISABLE Active Mode immediately
                    # so Jarvis doesn't listen to the song and hallucinate.
                    music_triggers = ["play", "song", "spotify", "music", "track"]
                    if any(x in command for x in music_triggers) and "pause" not in command:
                        print(">> Music detected. Exiting Active Mode to prevent echo.")
                        conversation_mode = False 
                else:
                    print("   (No command heard)")

                # --- SMART RESUME ---
                # Only resume if we were playing BEFORE, and the user didn't ask to stop/pause/change song
                stop_keywords = ["stop", "pause", "quiet", "silence", "play", "song"]
                is_stop_command = any(k in command for k in stop_keywords)

                if was_playing and not is_stop_command:
                    time.sleep(0.5)
                    print(">> Resuming background audio...")
                    music_engine.resume_music()
            
            else:
                # In standby, we ignore everything that isn't the wake word
                pass
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f">> Loop Error: {e}")

if __name__ == "__main__":
    main()