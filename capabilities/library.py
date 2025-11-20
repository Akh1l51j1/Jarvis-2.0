from capabilities.system_ops import SystemOps
from capabilities.music_ops import music_engine
from capabilities.volume_ops import volume_engine # <--- IMPORT THIS

tool_registry = {
    # ... (Keep existing System and Music tools) ...
    "open_app": { "func": SystemOps.open_application, "desc": "Opens apps." },
    "system_status": { "func": SystemOps.get_system_status, "desc": "Checks CPU." },
    "terminate": { "func": SystemOps.close_jarvis, "desc": "Shuts down." },
    "play_music": { "func": music_engine.play_music, "desc": "Plays Spotify." },
    "pause_music": { "func": music_engine.pause_music, "desc": "Pauses music." },
    "resume_music": { "func": music_engine.resume_music, "desc": "Resumes music." },

    # --- NEW VOLUME TOOLS ---
    "set_volume": {
        "func": volume_engine.set_volume,
        "desc": "Sets volume percentage. Args: level (integer 0-100)"
    },
    "mute": {
        "func": volume_engine.mute,
        "desc": "Mutes sound."
    },
    "unmute": {
        "func": volume_engine.unmute,
        "desc": "Unmutes sound."
    }
}