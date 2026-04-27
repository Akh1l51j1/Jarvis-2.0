from capabilities.system_ops import SystemOps
from capabilities.music_ops import music_engine
from capabilities.volume_ops import volume_engine
from capabilities.comm_ops import comm_engine
from capabilities.shazam_ops import identify_music
from capabilities.rag_ops import rag_engine
from capabilities.file_ops import FileOps
from capabilities.ui_ops import UIOps

tool_registry = {
    # System
    "open_app": { "func": SystemOps.open_application, "desc": "Opens apps." },
    "close_app": { "func": SystemOps.close_application, "desc": "Closes apps." },
    "search_google": { "func": SystemOps.search_web, "desc": "Searches web." },
    "system_status": { "func": SystemOps.get_system_status, "desc": "Checks CPU." },
    "terminate": { "func": SystemOps.close_jarvis, "desc": "Shuts down." },
    
    # Music
    "play_music": { "func": music_engine.play_music, "desc": "Plays Spotify." },
    "pause_music": { "func": music_engine.pause_music, "desc": "Pauses music." },
    "resume_music": { "func": music_engine.resume_music, "desc": "Resumes music." },
    "identify_song": { "func": identify_music, "desc": "Identifies song." },

    # Volume
    "set_volume": { "func": volume_engine.set_volume, "desc": "Sets volume 0-100." },
    "volume_up": { "func": volume_engine.volume_up, "desc": "Vol Up." },
    "volume_down": { "func": volume_engine.volume_down, "desc": "Vol Down." },
    "mute": { "func": volume_engine.mute, "desc": "Mutes." },
    
    # Comm
    "call_phone": { "func": comm_engine.make_phone_call, "desc": "Mobile call." },
    "whatsapp_call": { "func": comm_engine.whatsapp_call, "desc": "WhatsApp call." },

    # Memory
    "save_memory": { "func": rag_engine.save_memory, "desc": "Saves fact." },
    "read_memory": { "func": rag_engine.retrieve_memory, "desc": "Reads fact." },
    "forget_memory": { "func": rag_engine.delete_memory, "desc": "Deletes fact." },

    # File Ops
    "locate_file": { "func": FileOps.locate_file, "desc": "Finds path." },
    "create_file": { "func": FileOps.create_file, "desc": "Creates file." },
    "create_folder": { "func": FileOps.create_folder, "desc": "Creates folder." },
    "write_file": { "func": FileOps.write_to_file, "desc": "Writes content. Arg: file|content" },
    "move_file": { "func": FileOps.move_file, "desc": "Moves file/folder. Arg: name|dest" }, # <--- NEW
    "delete_file": { "func": FileOps.delete_file, "desc": "Deletes file." },
    
    # Legacy (Keep for compatibility)
    "read_file": { "func": FileOps.read_file, "desc": "Reads file." },
    "copy_file": { "func": FileOps.copy_file, "desc": "Copy to clipboard." },
    "cut_file": { "func": FileOps.cut_file, "desc": "Cut to clipboard." },
    "paste_file": { "func": FileOps.paste_file, "desc": "Paste clipboard." },
    
    # UI Controls
    "scroll_down": { "func": UIOps.scroll_down, "desc": "Scrolls the screen down." },
    "scroll_up": { "func": UIOps.scroll_up, "desc": "Scrolls the screen up." },
    "press_space": { "func": UIOps.press_space, "desc": "Presses spacebar (Play/Pause video)." },
    "toggle_fullscreen": { "func": UIOps.toggle_fullscreen, "desc": "Presses 'f' for fullscreen." },
}