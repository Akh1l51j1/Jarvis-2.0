import os
import time
import pyautogui
import webbrowser
import psutil
import subprocess

class CommunicationOps:
    def __init__(self):
        # --- CONTACTS ---
        MY_MOM_NUMBER = "919605108350"
        MY_GRANDFATHER_NUMBER = "918086939622"
        FRIEND_NUMBER = "919656317825"

        self.contacts = {
            "mom": MY_MOM_NUMBER,
            "mother": MY_MOM_NUMBER,
            "amma": MY_MOM_NUMBER,
            "mommy": MY_MOM_NUMBER,
            "mum": MY_MOM_NUMBER,
            "appachen": MY_GRANDFATHER_NUMBER,
            "pappa": MY_GRANDFATHER_NUMBER,
            "pappa nedumanni": MY_GRANDFATHER_NUMBER,
            "grandfather": MY_GRANDFATHER_NUMBER,
            "idiot": FRIEND_NUMBER,
            "bestie": FRIEND_NUMBER,
            "akshara": FRIEND_NUMBER,
        }
        
        self.brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        # Path to the image
        self.btn_image = os.path.join(os.getcwd(), "assets", "call_button.png")

    def _get_number(self, name):
        name = name.lower().strip()
        for contact in self.contacts:
            if contact in name:
                return self.contacts[contact]
        return None

    def _is_whatsapp_app_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                if "whatsapp.exe" in proc.info['name'].lower(): return True
            except: pass
        return False

    def make_phone_call(self, name):
        """Mobile Call using Visual Recognition"""
        number = self._get_number(name)
        if not number: return f"I couldn't find {name}."
        
        print(f"   [Comm] Triggering Phone Link...")
        os.system(f"start tel:{number}")
        
        # Wait for app to open
        time.sleep(5) # Gave it 1 extra second to be safe
        
        print("   [Comm] Scanning screen for Call Button...")
        try:
            # 1. TRY VISUAL CLICK (Needs opencv-python installed)
            # confidence=0.8 allows for slight differences in color/resolution
            button_location = pyautogui.locateOnScreen(self.btn_image, confidence=0.8)
            
            if button_location:
                print("   [Comm] Visual Match Found! Clicking...")
                # Click the center of the button
                pyautogui.click(pyautogui.center(button_location))
                return f"Dialing {name} on mobile."
            else:
                print("   [Comm] Visual match failed. Using Blind Enter.")
                # 2. FALLBACK: Just hit Enter (Often works if focus is correct)
                pyautogui.press('enter')
                return f"Attempting to dial {name} (Blind Mode)."
                
        except Exception as e:
            print(f"   [Visual Error] {e}")
            print("   [Comm] Fallback to Enter key.")
            pyautogui.press('enter')
            return f"Dialing {name}."

    def whatsapp_call(self, name):
        number = self._get_number(name)
        if not number: return f"I couldn't find {name}."
        
        if self._is_whatsapp_app_running():
            print(f"   [Comm] Using Desktop App...")
            os.system(f"start whatsapp://send?phone={number}")
            time.sleep(2.5)
            pyautogui.hotkey('ctrl', 'shift', 'c')
            return f"Calling {name} on Desktop App."
        else:
            print(f"   [Comm] Opening Web...")
            url = f"https://web.whatsapp.com/send?phone={number}"
            if os.path.exists(self.brave_path):
                subprocess.Popen([self.brave_path, url])
            else:
                webbrowser.open(url)
            return f"Opening WhatsApp Web for {name}. Please press the call button."

comm_engine = CommunicationOps()