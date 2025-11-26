from capabilities.system_ops import SystemOps
from capabilities.music_ops import music_engine
from capabilities.volume_ops import volume_engine
from capabilities.comm_ops import comm_engine
from capabilities.shazam_ops import identify_music

tool_registry = {
    # System
    "open_app": { "func": SystemOps.open_application, "desc": "Opens apps." },
    "close_app": { "func": SystemOps.close_application, "desc": "Closes apps." },
    "search_google": { "func": SystemOps.search_google, "desc": "Opens a browser tab with google search." },
    "system_status": { "func": SystemOps.get_system_status, "desc": "Checks CPU." },
    "terminate": { "func": SystemOps.close_jarvis, "desc": "Shuts down." },
    
    # Music
    "play_music": { "func": music_engine.play_music, "desc": "Plays Spotify." },
    "pause_music": { "func": music_engine.pause_music, "desc": "Pauses music." },
    "resume_music": { "func": music_engine.resume_music, "desc": "Resumes music." },
    "identify_song": { "func": identify_music, "desc": "Identifies playing song." },

    # Volume
    "set_volume": { "func": volume_engine.set_volume, "desc": "Sets volume 0-100." },
    "volume_up": { "func": volume_engine.volume_up, "desc": "Increases volume." },
    "volume_down": { "func": volume_engine.volume_down, "desc": "Decreases volume." },
    "mute": { "func": volume_engine.mute, "desc": "Mutes sound." },
    
    # Phone (FIXED THE NAMES HERE)
    "call_phone": { 
        "func": comm_engine.make_phone_call,
        "desc": "Makes a mobile call via Phone Link." 
    },
    "whatsapp_call": { 
        "func": comm_engine.whatsapp_call, 
        "desc": "Calls someone on WhatsApp." 
    }
}