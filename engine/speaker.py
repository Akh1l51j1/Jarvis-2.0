import edge_tts
import pygame
import asyncio
import os

# --- VOICE SETTINGS ---
VOICE = "en-US-ChristopherNeural"
RATE = "+1%"
PITCH = "-2Hz"

class Speaker:
    def __init__(self):
        print(f">> Loading Human Neural Speaker ({VOICE})...")
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

    # Dummy stop function for compatibility
    def stop(self):
        pass

    # Boolean check for compatibility
    @property
    def is_speaking(self):
        return False

    def speak(self, text):
        clean_text = text.replace("*", "").replace("#", "")
        print(f">> Speaking: {clean_text}")
        
        output_file = "response.mp3"
        
        try:
            # Generate
            asyncio.run(self._generate_audio(clean_text, output_file))
            
            # Play (Blocking)
            if not os.path.exists(output_file): return
            
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
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
    bot.speak("Systems restored to stable protocol.")