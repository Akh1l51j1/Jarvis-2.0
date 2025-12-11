import sys
import time
from datetime import datetime
from engine.listener import AudioListener
from engine.speaker import Speaker
from core.llm import Brain
import config
from capabilities.music_ops import music_engine 

# SETTINGS
CONVERSATION_TIMEOUT = 15 

def startup_sequence(mouth, brain):
    print("\n>> INITIALIZING SYSTEMS...")
    mouth.play_sound("startup")
    time.sleep(0.5)
    greeting = brain.get_greeting()
    print(f"JARVIS: {greeting}")
    mouth.speak(greeting)

def main():
    print("\n>> STARTING JARVIS 2.0")
    print("------------------------")
    
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
                remaining = int(CONVERSATION_TIMEOUT - (time.time() - last_active_time))
                print(f"\n>> Active Mode (Timeout in {remaining}s)...")
            else:
                print("\n>> Waiting for Wake Word...")

            user_text = ear.listen()
            
            # 1. TIMEOUT CHECK
            if conversation_mode and (time.time() - last_active_time > CONVERSATION_TIMEOUT):
                print(">> Time out. Returning to Standby.")
                mouth.play_sound("shutdown") 
                conversation_mode = False
                if len(user_text) < 3: continue

            # 2. NOISE FILTER
            if len(user_text) < 3: continue 

            # 3. WAKE WORD CHECK
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
                should_process = True
                last_active_time = time.time()
            
            if should_process:
                print(f"USER: {user_text}")
                if is_wake_word: mouth.play_sound("listen")

                was_playing = music_engine.is_playing()
                if was_playing: music_engine.pause_music()

                command = user_text.lower()
                for word in config.WAKE_WORDS:
                    command = command.replace(word, "").strip()
                
                if "braille" in command: command = command.replace("braille", "brave")

                # --- DISMISSAL (Soft Sleep) ---
                soft_triggers = [
                    "nothing", "no thanks", "no thank you",
                    "turn off mic", "stop listening",
                    "that is all", "thats all", "done",
                    "thank you", "thanks", "thankue",
                    "bye", "see you", "goodbye"
                ]
                if any(trigger in command for trigger in soft_triggers):
                    print(">> Conversation Dismissed.")
                    mouth.speak("Standing by, Sir.")
                    conversation_mode = False
                    if was_playing: music_engine.resume_music()
                    continue 

                # --- KILL SWITCH (Hard Exit) ---
                # This catches manual commands like "Jarvis shut down"
                exit_triggers = ["shut down", "shutdown", "power off", "terminate", "exit jarvis", "kill program"]
                if any(trigger in command for trigger in exit_triggers):
                    print(">> Termination Sequence Initiated.")
                    mouth.speak("Shutting down systems. Goodbye.")
                    time.sleep(2)
                    sys.exit(0)

                # Handle "Jarvis" only
                if len(command) < 2:
                    print(">> Listening for command...")
                    command = ear.listen()
                    if len(command) > 2:
                        last_active_time = time.time()

                # BRAIN
                if len(command) > 2:
                    response = brain.think(command)
                    print(f"JARVIS: {response}")
                    mouth.speak(response)
                    last_active_time = time.time() 
                    
                    # --- BRAIN KILL SWITCH ---
                    # If the Brain tool decided to terminate, we must obey.
                    if "terminating" in response.lower() or "shutting down" in response.lower():
                        print(">> System Exit Triggered by Brain.")
                        time.sleep(2)
                        sys.exit(0)
                else:
                    print("   (No command heard)")

                # Resume Music Logic
                music_keywords = ["play", "song", "music", "track", "spotify", "start"]
                stop_keywords = ["stop", "pause", "quiet", "silence"]
                is_music_command = any(k in command for k in music_keywords)
                is_stop_command = any(k in command for k in stop_keywords)

                if was_playing and not is_music_command and not is_stop_command:
                    time.sleep(1)
                    print(">> Resuming background audio...")
                    music_engine.resume_music()
                elif is_music_command:
                    print(">> New song requested.")
            
            else:
                print(f"   [Ignored]: '{user_text}'")
                
        except KeyboardInterrupt:
            print("\n>> Shutting down...")
            break
        except Exception as e:
            print(f">> Loop Error: {e}")

if __name__ == "__main__":
    main()