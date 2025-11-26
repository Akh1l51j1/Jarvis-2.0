import edge_tts
import pygame
import asyncio
import os
import keyboard # <--- NEW LIBRARY

# SETTINGS
VOICE = "en-US-ChristopherNeural"
RATE = "+20%" 
PITCH = "-2Hz"

class Speaker:
    def __init__(self):
        print(f">> Loading Speaker (Press 'ESC' to interrupt)...")
        try:
            pygame.mixer.init()
            self.use_sounds = True
        except:
            self.use_sounds = False
            
        self.assets_dir = os.path.join(os.getcwd(), "assets")

    def play_sound(self, name):
        if not self.use_sounds: return
        path = os.path.join(self.assets_dir, f"{name}.mp3")
        if os.path.exists(path):
            try:
                pygame.mixer.Sound(path).play()
            except: pass

    def speak(self, text):
        clean_text = text.replace("*", "").replace("#", "")
        print(f">> Speaking: {clean_text}")
        
        output_file = "response.mp3"
        
        try:
            # Generate
            asyncio.run(self._generate_audio(clean_text, output_file))
            
            # Play
            if not os.path.exists(output_file): return
            
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            # --- THE KILL SWITCH LOOP ---
            while pygame.mixer.music.get_busy():
                # If user presses ESC, kill audio instantly
                if keyboard.is_pressed('esc'):
                    print(">> 🛑 Speech Interrupted by User (ESC).")
                    pygame.mixer.music.stop()
                    break
                
                pygame.time.Clock().tick(10)
            
            pygame.mixer.music.unload()
            try: os.remove(output_file)
            except: pass
            
        except Exception as e:
            print(f"Audio Error: {e}")

    async def _generate_audio(self, text, filename):
        communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
        await communicate.save(filename)

if __name__ == "__main__":
    bot = Speaker()
    bot.speak("I am speaking a very long sentence. Press Escape now to shut me up immediately.")