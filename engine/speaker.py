import pyttsx3
import pygame
import os
import winsound # We bring this back as a backup

class Speaker:
    def __init__(self):
        print(">> Loading Speaker...")
        
        # 1. Try to load Sound Effects
        try:
            pygame.mixer.init()
            self.use_sounds = True
        except:
            print(">> Warning: Pygame failed. Using Beeps.")
            self.use_sounds = False
            
        # Load SFX (Check if files exist)
        self.sounds = {}
        self.assets_dir = os.path.join(os.getcwd(), "assets")
        
        # We try to load them, but we won't crash if they are missing
        self._load_sound("startup", "startup.mp3")
        self._load_sound("listen", "listen.mp3")

    def _load_sound(self, name, filename):
        if not self.use_sounds: return
        path = os.path.join(self.assets_dir, filename)
        if os.path.exists(path):
            self.sounds[name] = pygame.mixer.Sound(path)

    def play_sound(self, name):
        """
        Plays MP3 if available, otherwise plays System Beep.
        """
        if self.use_sounds and name in self.sounds:
            # Option A: Cool MP3
            self.sounds[name].play()
        else:
            # Option B: Fallback System Beep (So you never miss a trigger)
            if name == "listen":
                winsound.Beep(1000, 200) # High pitch ding
            elif name == "startup":
                winsound.Beep(600, 300)  # Low pitch boot sound

    def speak(self, text):
        clean_text = text.replace("*", "")
        print(f">> Speaking: {clean_text}")
        
        try:
            engine = pyttsx3.init('sapi5')
            voices = engine.getProperty('voices')
            try:
                engine.setProperty('voice', voices[1].id) # Try Zira (Female)
            except:
                engine.setProperty('voice', voices[0].id) # Fallback David (Male)
                
            engine.setProperty('rate', 175)
            engine.setProperty('volume', 1.0)
            
            engine.say(clean_text)
            engine.runAndWait()
            del engine
        except Exception as e:
            print(f"Audio Error: {e}")

if __name__ == "__main__":
    bot = Speaker()
    print("Testing Sound...")
    bot.play_sound("listen") # Should Beep or Ding
    bot.speak("Audio systems fully operational.")