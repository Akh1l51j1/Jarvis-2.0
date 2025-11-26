import pyautogui
import math

class VolumeOps:
    def __init__(self):
        print("   [Volume] Keyboard Control Active.")

    def set_volume(self, level):
        try:
            level = str(level).replace("%", "").strip()
            level = int(level)
            if level < 0: level = 0
            if level > 100: level = 100
            
            # Reset to 0 then go up
            pyautogui.press('volumedown', presses=50, interval=0.01)
            presses_needed = math.ceil(level / 2)
            pyautogui.press('volumeup', presses=presses_needed, interval=0.01)
            
            return f"Volume set to {level}%."
        except:
            return "Error setting volume."

    def volume_up(self):
        # Press Up 5 times (approx 10%)
        pyautogui.press('volumeup', presses=5)
        return "Volume increased."

    def volume_down(self):
        # Press Down 5 times (approx 10%)
        pyautogui.press('volumedown', presses=5)
        return "Volume decreased."

    def mute(self):
        pyautogui.press("volumemute")
        return "Mute toggled."

    def unmute(self):
        pyautogui.press("volumemute")
        return "Mute toggled."

volume_engine = VolumeOps()