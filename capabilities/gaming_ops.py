import os
import psutil
from server_bridge import bridge

class GamingOps:
    def __init__(self):
        self.gaming_active = False

    def toggle_gaming_mode(self, state: bool):
        """Throttles Jarvis to save resources for gaming."""
        self.gaming_active = state
        process = psutil.Process(os.getpid())
        
        if state:
            # Set to lowest priority: Windows gives all power to the Game first
            process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            bridge.update_status("GAMING", "Throttled")
            return "Gaming Mode Engaged. I've moved to background priority, Sir."
        else:
            # Restore full power
            process.nice(psutil.NORMAL_PRIORITY_CLASS)
            bridge.update_status("IDLE", "Active")
            return "Systems back to full capacity."

# Initialize for the library
gaming_engine = GamingOps()