import sys
import time
import os
from datetime import datetime
from engine.listener import AudioListener
from engine.speaker import Speaker
from core.llm import Brain
import config
from capabilities.music_ops import music_engine 
from server_bridge import bridge
from capabilities.gaming_ops import gaming_engine

# --- TEE LOGGER FOR VIDEO DEMO ---
class Tee:
    """
    Tee logger that writes to both terminal and log file simultaneously.
    """
    def __init__(self, filename):
        self.terminal = sys.__stdout__
        self.log = open(filename, "a", encoding="utf-8")
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()
    
    def reconfigure(self, **kwargs):
        """
        Pass through reconfigure to the terminal stdout.
        This is needed for encoding configuration.
        """
        if hasattr(self.terminal, 'reconfigure'):
            self.terminal.reconfigure(**kwargs)

# Redirect stdout to Tee logger for video demo
sys.stdout = Tee("Debug_log.txt")
sys.stdout.reconfigure(encoding='utf-8')

# --- HARDCODED NVIDIA DLL FIX (MARK III STABILITY) ---
def initialize_nvidia_dlls():
    nvidia_path = r"D:\jarvis 2.0\venv\Lib\site-packages\nvidia\cublas\bin"
    cudnn_path = r"D:\jarvis 2.0\venv\Lib\site-packages\nvidia\cudnn\bin"
    
    if os.path.exists(nvidia_path):
        os.add_dll_directory(nvidia_path)
        os.environ['PATH'] = nvidia_path + os.pathsep + os.environ['PATH']
        print(f">> NVIDIA cuBLAS Path Linked.")

    if os.path.exists(cudnn_path):
        os.add_dll_directory(cudnn_path)
        os.environ['PATH'] = cudnn_path + os.pathsep + os.environ['PATH']
        print(f">> NVIDIA cuDNN Path Linked.")

initialize_nvidia_dlls()

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
        brain = Brain(bridge=bridge)
    except Exception as e:
        print(f"\n>> CRITICAL STARTUP ERROR: {e}")
        return

    startup_sequence(mouth, brain)
    
    conversation_mode = False
    last_active_time = 0

    while True:
        try:
            # --- UI STATUS PERSISTENCE ---
            if conversation_mode:
                if not brain.gaming_mode:
                    bridge.update_status("LISTENING", "Active Mode")
                remaining = int(CONVERSATION_TIMEOUT - (time.time() - last_active_time))
                print(f"\n>> Active Mode (Timeout in {remaining}s)...")
            else:
                if not brain.gaming_mode:
                    bridge.update_status("IDLE", "Waiting for Wake Word...")
                print("\n>> Waiting for Wake Word...")

            # --- LISTEN ---
            user_text = ear.listen(timeout=1.0)
            has_spoken = len(user_text) > 3
            
            # --- SMART TIMEOUT CHECK ---
            if conversation_mode and not has_spoken:
                if (time.time() - last_active_time > CONVERSATION_TIMEOUT):
                    print(">> Time out. Returning to Standby.")
                    mouth.play_sound("shutdown") 
                    mouth.speak("Standing by, Sir.")
                    conversation_mode = False
                    continue
            
            if not has_spoken: 
                if not conversation_mode:
                    last_active_time = time.time()
                continue

            # --- WAKE WORD CHECK ---
            is_wake_word = False
            for word in config.WAKE_WORDS:
                if word in user_text.lower():
                    is_wake_word = True
                    mouth.play_sound("listen")
                    break
            
            should_process = False
            if is_wake_word:
                should_process = True
                conversation_mode = True
                last_active_time = time.time()
            elif conversation_mode:
                if has_spoken:
                    mouth.play_sound("listen")
                should_process = True
                last_active_time = time.time()
            
            if should_process:
                print(f"USER: {user_text}")
                bridge.log(f"USER: {user_text}")

                was_playing = music_engine.is_playing()         
                if was_playing: music_engine.pause_music()

                command = user_text.lower()
                for word in config.WAKE_WORDS:
                    command = command.replace(word, "").strip()
                
                # --- 1. FUZZY GAMING MODE TRIGGERS ---
                gaming_triggers = ["gaming mode", "game mode", "stealth mode"]
                
                if any(t in command for t in gaming_triggers) and any(x in command for x in ["on", "enable", "start", "activate", "donald"]):
                    brain.gaming_mode = True 
                    bridge.update_status("GAMING", "Stealth Mode Engaged")
                    response = gaming_engine.toggle_gaming_mode(True)
                    mouth.speak(response)
                    last_active_time = time.time()
                    continue 

                elif any(t in command for t in gaming_triggers) and any(x in command for x in ["off", "disable", "stop", "exit"]):
                    brain.gaming_mode = False
                    bridge.update_status("ONLINE", "Systems Restored")
                    response = gaming_engine.toggle_gaming_mode(False)
                    mouth.speak(response)
                    last_active_time = time.time()
                    continue

                # --- 2. SYSTEM COMMANDS ---
                soft_triggers = ["nothing","standby","stand by","no thanks", "stop listening", "bye", "goodbye"]
                if any(trigger in command for trigger in soft_triggers):    
                    mouth.speak("Standing by, Sir.")
                    conversation_mode = False
                    if was_playing: music_engine.resume_music()
                    continue 

                # Check for one-word AND two-word variants
                shutdown_triggers = ["shut down", "shutdown", "power off", "terminate", "go to sleep"]
                if any(trigger in command for trigger in shutdown_triggers):
                    bridge.update_status("OFFLINE", "Shutting Down...")
                    mouth.speak("Goodbye, Sir.")
                    time.sleep(1.5) # Let him finish speaking before cutting power
                    sys.exit(0)

                # --- 3. [FIXED] MUSIC MUZZLE & BRAIN PROCESSING ---
                music_start_keywords = ["play", "song", "spotify", "music", "youtube"]
                is_music_start = any(k in command for k in music_start_keywords)

                if len(command) > 2:
                    if is_music_start:
                        # Muzzle the ear immediately
                        print(">> Music command detected. Muzzling microphone...")
                        ear.stream.stop_stream() 
                        
                        response = brain.think(command)
                        
                        if response and response.strip():
                            print(f"JARVIS: {response}")
                            bridge.log(f"JARVIS: {response}")
                            mouth.speak(response)
                        
                        print(">> Waiting for audio environment to stabilize...")
                        time.sleep(3.5) 
                        ear.stream.start_stream()
                        last_active_time = time.time()
                        continue 

                    else:
                        # Normal Processing
                        if not brain.gaming_mode:
                            bridge.update_status("PROCESSING", "Thinking...")
                        
                        response = brain.think(command)
                        
                        if response and response.strip():
                            print(f"JARVIS: {response}")
                            bridge.log(f"JARVIS: {response}")
                            if not brain.gaming_mode:
                                bridge.update_status("SPEAKING", "Replying...")
                            mouth.speak(response)
                        
                        last_active_time = time.time()
                else:
                    print("   (No command heard)")

                # --- MUSIC RESUME LOGIC ---
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