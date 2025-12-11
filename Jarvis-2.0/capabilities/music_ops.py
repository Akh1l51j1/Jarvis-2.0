import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import sys
import os
import pyautogui

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

class MusicOps:
    def __init__(self):
        print("   [Spotify] Connecting...")
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=config.SPOTIPY_CLIENT_ID,
                client_secret=config.SPOTIPY_CLIENT_SECRET,
                redirect_uri=config.SPOTIPY_REDIRECT_URI,
                scope="user-read-playback-state,user-modify-playback-state"
            ))
            print("   [Spotify] Connection Successful.")
        except Exception as e:
            print(f"   [Spotify] CRITICAL ERROR: {e}")
            self.sp = None

    def is_playing(self):
        """Checks if Spotify is currently playing music."""
        if not self.sp: return False
        try:
            current = self.sp.current_playback()
            return current is not None and current.get('is_playing', False)
        except Exception:
            return False

    # THE FIX: song_name=None makes the argument optional
    def play_music(self, song_name=None):
        # If no song is provided (User just said "Play"), treat it as RESUME
        if song_name is None:
            return self.resume_music()
            
        if not self.sp: return "Spotify connection failed."
        
        try:
            print(f"   [Spotify] Searching for: {song_name}")
            results = self.sp.search(q=song_name, limit=1, type='track')
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_uri = track['uri']
                track_name = track['name']
                artist = track['artists'][0]['name']
                
                try:
                    self.sp.start_playback(uris=[track_uri])
                    return f"Playing {track_name} by {artist}."
                except SpotifyException as e:
                    # FREE TIER FALLBACK
                    if "PREMIUM_REQUIRED" in str(e) or "403" in str(e):
                        print("   [Spotify] Premium not detected. Using Deep Link.")
                        os.system(f"start {track_uri}")
                        return f"Opening {track_name} by {artist} on Desktop."
                    elif "NO_ACTIVE_DEVICE" in str(e):
                        return "Please open Spotify first."
                    else:
                        return f"Spotify Error: {e}"
            else:
                return f"I couldn't find {song_name}."
        except Exception as e:
            return f"Error searching for song: {e}"

    def pause_music(self):
        if not self.is_playing():
            return "Music is already paused."

        try:
            if self.sp: self.sp.pause_playback()
        except SpotifyException:
            pyautogui.press("playpause")
        return "Music paused."

    def resume_music(self):
        if self.is_playing():
            return "Music is already playing."

        try:
            if self.sp: self.sp.start_playback()
        except SpotifyException:
            pyautogui.press("playpause")
        return "Music resumed."

# Create instance
music_engine = MusicOps()