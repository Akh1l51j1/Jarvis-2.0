import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import sys
import os
import time
import pyautogui
# 1. Import Fuzzy Matcher
from difflib import SequenceMatcher

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
        if not self.sp: return False
        try:
            current = self.sp.current_playback()
            return current is not None and current.get('is_playing', False)
        except:
            return False

    # Helper: Check similarity between two strings (0.0 to 1.0)
    def _similarity(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def play_music(self, song_name=None):
        if song_name is None:
            return self.resume_music()
            
        if not self.sp: return "Spotify connection failed."
        
        try:
            print(f"   [Spotify] Searching for: {song_name}")
            
            # 2. Get 5 results to find the best match
            results = self.sp.search(q=song_name, limit=5, type='track')
            items = results['tracks']['items']
            
            if not items:
                return f"I couldn't find {song_name} on Spotify."

            # 3. SMART FILTERING (The Fix)
            # Look for a result that actually contains words from the request
            best_track = items[0] # Default to first
            
            for item in items:
                track_title = item['name']
                artist_name = item['artists'][0]['name']
                full_str = f"{track_title} {artist_name}"
                
                # If the result matches the query significantly better, switch to it
                # or if the query words are literally IN the result name
                query_parts = song_name.lower().split()
                matches = sum(1 for part in query_parts if part in full_str.lower())
                
                if matches >= len(query_parts) - 1: # Allow 1 missing word
                    best_track = item
                    break

            track_uri = best_track['uri']
            track_name = best_track['name']
            artist = best_track['artists'][0]['name']
            
            print(f"   [Spotify] Selected: {track_name} by {artist}")
            
            try:
                # Try Premium API
                self.sp.start_playback(uris=[track_uri])
                return f"Playing {track_name} by {artist}."
            
            except SpotifyException as e:
                # Auto-Wake Logic
                if "NO_ACTIVE_DEVICE" in str(e):
                    print("   [Spotify] Device not found. Launching App...")
                    
                    # FORCE OPEN TO SPECIFIC SONG (Prevents "One Dance" resume error)
                    os.system(f"start {track_uri}") 
                    time.sleep(8) 
                    
                    try:
                        self.sp.start_playback(uris=[track_uri])
                    except:
                        pyautogui.press("space")
                        
                    return f"Opening Spotify for {track_name}."
                
                elif "PREMIUM_REQUIRED" in str(e):
                    print("   [Spotify] Free Tier detected. Using Deep Link.")
                    os.system(f"start {track_uri}")
                    return f"Opening {track_name}."
                
                else:
                    return f"Spotify Error: {e}"

        except Exception as e:
            return f"Search Error: {e}"

    def pause_music(self):
        try:
            if self.sp: self.sp.pause_playback()
        except:
            pass 
        return "Paused."

    def resume_music(self):
        try:
            if self.sp: self.sp.start_playback()
        except:
            pyautogui.press("playpause") 
        return "Resumed."

music_engine = MusicOps()