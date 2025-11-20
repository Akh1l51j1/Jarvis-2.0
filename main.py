import sys
import time
from datetime import datetime
from engine.listener import AudioListener
from engine.speaker import Speaker
from core.llm import Brain
import config
from capabilities.music_ops import music_engine 

def startup_sequence(mouth):
    print("\n>> INITIALIZING SYSTEMS...")
    mouth.play_sound("startup")
    time.sleep(1)
    hour = datetime.now().hour
    if 0 <= hour < 12:
        mouth.speak(f"Good morning, sir. {config.ASSISTANT_NAME} is online.")
    else:
        mouth.speak("System initialized. Prepared for command.")

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

    startup_sequence(mouth)
    
    while True:
        try:
            print("\n>> 💤 Waiting for Wake Word...")
            initial_text = ear.listen()
            
            if len(initial_text) < 3: continue 

            is_wake_word = False
            for word in config.WAKE_WORDS:
                if word in initial_text.lower():
                    is_wake_word = True
                    break
            
            if is_wake_word:
                print(f"USER: {initial_text}")
                mouth.play_sound("listen")

                # Auto-Pause
                was_playing = music_engine.is_playing()
                if was_playing: music_engine.pause_music()

                # Extract Command
                command = initial_text.lower()
                for word in config.WAKE_WORDS:
                    command = command.replace(word, "").strip()
                
                if "braille" in command: command = command.replace("braille", "brave")

                # Handle "Jarvis" only
                if len(command) < 2:
                    print("   ⚡ Listening for command...")
                    command = ear.listen()

                # Shutdown
                if any(trigger in command.lower() for trigger in ["shut down", "shutdown", "stop", "exit"]):
                    mouth.speak("Shutting down systems. Goodbye.")
                    sys.exit(0)

                # --- BRAIN ---
                if len(command) > 2:
                    response = brain.think(command)
                    print(f"JARVIS: {response}")
                    mouth.speak(response)

                    # --- NEW: CONVERSATION MODE ---
                    # If Jarvis asks a question, listen immediately for the answer
                    if response.strip().endswith("?") or "would you like" in response.lower():
                        print("   ⚡ Conversation Active (Waiting for answer)...")
                        # We don't play 'ding', we just listen
                        follow_up = ear.listen()
                        
                        if len(follow_up) > 2:
                            print(f"USER (Follow-up): {follow_up}")
                            # Send follow-up to brain
                            response_2 = brain.think(follow_up)
                            print(f"JARVIS: {response_2}")
                            mouth.speak(response_2)
                
                else:
                    print("   (No command heard)")

                # Smart Resume
                music_keywords = ["play", "song", "music", "track", "spotify", "start"]
                stop_keywords = ["stop", "pause", "quiet", "silence"]
                
                is_music_command = any(k in command.lower() for k in music_keywords)
                is_stop_command = any(k in command.lower() for k in stop_keywords)

                if was_playing and not is_music_command and not is_stop_command:
                    print(">> Resuming background audio...")
                    music_engine.resume_music()
                elif is_music_command:
                    print(">> New song requested. Letting it play.")
                else:
                    print(">> Audio state preserved.")
            
            else:
                print(f"   [Ignored]: '{initial_text}'")
                
        except KeyboardInterrupt:
            print("\n>> Shutting down...")
            break
        except Exception as e:
            print(f">> Loop Error: {e}")

if __name__ == "__main__":
    main()