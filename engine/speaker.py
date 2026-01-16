import os
import sounddevice as sd
import soundfile as sf
from kokoro_onnx import Kokoro
import pygame
import asyncio
import time
import keyboard # <--- Re-added for ESC key

# --- SETTINGS ---
VOICE_NAME = "af_sarah" 

class Speaker:
    def __init__(self):
        print(">> Loading Kokoro TTS (v1.0)...")
        
        try:
            pygame.mixer.init()
            self.use_sfx = True
        except Exception as e:
            print(f"   [Speaker] Pygame Init Failed: {e}")
            self.use_sfx = False

        self.assets_dir = os.path.join(os.getcwd(), "assets")
        
        engine_dir = os.path.dirname(__file__)
        model_path = os.path.join(engine_dir, "kokoro-v1.0.onnx")
        voices_path = os.path.join(engine_dir, "voices-v1.0.bin")
        
        if not os.path.exists(model_path) or not os.path.exists(voices_path):
            print(f"   [Error] v1.0 Models missing at {engine_dir}")
            self.kokoro = None
        else:
            try:
                self.kokoro = Kokoro(model_path, voices_path)
                print("    Kokoro TTS Loaded.")
            except Exception as e:
                print(f"   [Speaker Error] Failed to load model: {e}")
                self.kokoro = None

    def play_sound(self, name):
        if not self.use_sfx: return
        path = os.path.join(self.assets_dir, f"{name}.mp3")
        if os.path.exists(path):
            try:
                pygame.mixer.Sound(path).play()
            except: pass

    def speak(self, text):
        if not self.kokoro: return
        
        # --- THE FIX: Split text by sentences ---
        import re
        sentences = re.split(r'(?<=[.!?]) +', text)
        
        for sentence in sentences:
            clean_text = sentence.replace("*", "").replace("#", "").strip()
            if not clean_text: continue

            print(f">> Speaking: {clean_text}")
            try:
                samples, sample_rate = self.kokoro.create(clean_text, voice=VOICE_NAME, speed=1.0, lang="en-us")
                sd.play(samples, sample_rate)
                
                # Wait for CURRENT sentence to finish (or ESC)
                duration = len(samples) / sample_rate
                start_time = time.time()
                while time.time() - start_time < duration:
                    if keyboard.is_pressed('esc'):
                        sd.stop()
                        return # Exit the entire speech loop
                    time.sleep(0.01)
            except Exception as e:
                print(f"   [Speaker Error] {e}")

if __name__ == "__main__":
    bot = Speaker()
    bot.speak("Testing interruption. Press escape to stop me.")