import pyautogui
import math

class VolumeOps:
    def __init__(self):
        print("   [Volume] Safe Mode (Keyboard Control) Initialized.")

    def set_volume(self, level):
        """
        Hack: Presses 'Volume Down' 50 times to zero it out, 
        then 'Volume Up' to reach target.
        """
        try:
            # Clean input
            level = str(level).replace("%", "").strip()
            level = int(level)
            
            # Clamp
            if level < 0: level = 0
            if level > 100: level = 100
            
            # 1. Zero out the volume (Mute isn't reliable, we need 0%)
            # We press down 50 times to ensure we are at 0
            # interval=0.01 makes it super fast
            pyautogui.press('volumedown', presses=50, interval=0.01)
            
            # 2. Calculate presses needed (1 press is usually 2% on Windows)
            presses_needed = math.ceil(level / 2)
            
            # 3. Press Up
            pyautogui.press('volumeup', presses=presses_needed, interval=0.01)
            
            return f"Volume set to {level}%."
        except Exception as e:
            return f"Error setting volume: {e}"

    def mute(self):
        pyautogui.press("volumemute")
        return "Toggled Mute."

    def unmute(self):
        pyautogui.press("volumemute")
        return "Toggled Mute."

# Instance
volume_engine = VolumeOps()