import pyautogui

class UIOps:
    @staticmethod
    def scroll_down(self):
        # 1. Get screen size
        width, height = pyautogui.size()
        
        # 2. Click center to FOCUS the window (crucial for scrolling to work)
        pyautogui.click(width/2, height/2)
        
        # 3. Scroll down (Negative number)
        pyautogui.scroll(-1500)
        
        # 4. Return None = Silent Mode (Jarvis won't speak)
        return None 

    def scroll_up(self):
        width, height = pyautogui.size()
        
        # Click center to focus
        pyautogui.click(width/2, height/2)
        
        # Scroll up (Positive number)
        pyautogui.scroll(1500)
        
        # Silent Mode
        return None
    
    @staticmethod
    def page_down():
        """Presses the Page Down key."""
        print("   [UI] Pressing Page Down")
        pyautogui.press('pagedown')
        return "Pressed Page Down"
    
    @staticmethod
    def page_up():
        """Presses the Page Up key."""
        print("   [UI] Pressing Page Up")
        pyautogui.press('pageup')
        return "Pressed Page Up"
    
    @staticmethod
    def press_key(key):
        """Presses a specific key."""
        print(f"   [UI] Pressing '{key}' key")
        pyautogui.press(key)
        return f"Pressed '{key}' key"
    
    @staticmethod
    def press_space():
        """Presses spacebar (Play/Pause video)."""
        print("   [UI] Pressing Spacebar (Play/Pause)")
        pyautogui.press('space')
        return "Pressed Spacebar (Play/Pause)"
    
    @staticmethod
    def toggle_fullscreen():
        """Presses 'f' for fullscreen."""
        print("   [UI] Pressing 'f' (Toggle Fullscreen)")
        pyautogui.press('f')
        return "Pressed 'f' (Toggle Fullscreen)"