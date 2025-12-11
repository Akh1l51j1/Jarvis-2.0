import asyncio
from shazamio import Shazam
import pyaudio
import wave
import os
import winsound # <--- For the Beep

class ShazamOps:
    def __init__(self):
        print("   [Shazam] Initializing Recognition Engine...")
        self.shazam = Shazam()

    async def recognize_song(self):
        filename = "clip.wav"
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 10
        
        p = pyaudio.PyAudio()
        
        # --- THE CUE ---
        print("   [Shazam]  LISTENING NOW! (Play Music)")
        winsound.Beep(800, 500) # High Pitch Beep (0.5s)
        
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Play a 'Done' beep
        winsound.Beep(600, 200) 

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        try:
            out = await self.shazam.recognize(filename)
            if 'track' in out:
                title = out['track']['title']
                subtitle = out['track']['subtitle']
                return f"I identified the song. It is {title} by {subtitle}."
            else:
                return "I could not identify that song, Sir. It might be too quiet."
        except Exception as e:
            print(f"   [Shazam Error] {e}")
            return "An error occurred during recognition."
        finally:
            if os.path.exists(filename):
                os.remove(filename)

def identify_music():
    engine = ShazamOps()
    return asyncio.run(engine.recognize_song())