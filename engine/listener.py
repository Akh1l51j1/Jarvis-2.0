import pyaudio
import numpy as np
import torch
from faster_whisper import WhisperModel

# --- CONFIGURATION ---
CHANNELS = 1
RATE = 16000
CHUNK = 512
SILENCE_THRESHOLD = 0.8 
VAD_SENSITIVITY = 0.5 

class AudioListener:
    def __init__(self):
        print(">> Loading VAD Model...")
        self.vad_model, _ = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                           model='silero_vad',
                                           trust_repo=True)
        
        print(">> Loading Whisper Model...")
        self.whisper = WhisperModel("base", device="cpu", compute_type="int8") 
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)

    def is_speech(self, audio_chunk):
        audio_float32 = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        confidence = self.vad_model(torch.from_numpy(audio_float32), RATE).item()
        return confidence > VAD_SENSITIVITY

    def listen(self):
        print("\n>> Listening...")
        frames = []
        started = False
        silence_frames = 0
        
        while True:
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            
            if self.is_speech(data):
                if not started:
                    started = True
                frames.append(data)
                silence_frames = 0 
            
            elif started:
                frames.append(data)
                silence_frames += 1
                if silence_frames > (RATE / CHUNK * SILENCE_THRESHOLD):
                    break

        audio_data = b''.join(frames)
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # --- THE FIX: language="en" ---
        segments, _ = self.whisper.transcribe(
            audio_np, 
            beam_size=5,
            language="en",  # <--- FORCES ENGLISH ONLY
            vad_filter=True, 
            vad_parameters=dict(min_silence_duration_ms=500),
            # Add "Spotify" and your song names here
            initial_prompt="Jarvis, open Spotify. Play songs like Tere Bina, Tum Hi Ho."
        )
        
        full_text = ""
        for segment in segments:
            if segment.no_speech_prob > 0.5: continue 
            if segment.avg_logprob < -1.0: continue
            full_text += segment.text + " "

        return full_text.strip()