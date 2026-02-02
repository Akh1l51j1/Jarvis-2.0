import pyaudio
import numpy as np
import torch
from faster_whisper import WhisperModel
import time

# --- UNIVERSAL CONFIGURATION ---
CHANNELS = 1
RATE = 16000
CHUNK = 512 
SILENCE_THRESHOLD = 1.6  
VAD_SENSITIVITY = 0.5    

class AudioListener:
    def __init__(self):
        print(">> Loading VAD Model...")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f">> VAD/Whisper offloaded to: {torch.cuda.get_device_name(0)}")

        self.vad_model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False
        )
        self.vad_model.to(self.device)
        
        print(">> Loading Faster-Whisper (small.en)...")
        self.whisper = WhisperModel("large-v3", device="cuda", compute_type="int8")
        
        self.p = pyaudio.PyAudio()
        
        try:
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      input_device_index=1, 
                                      frames_per_buffer=CHUNK)
        except:
            print(">> Warning: Device 1 failed. Falling back to default.")
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      frames_per_buffer=CHUNK)
        
        # --- FIX: START STREAM ONCE AND KEEP IT OPEN ---
        self.stream.start_stream()

    def is_speech(self, audio_chunk):
        audio_float32 = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        input_tensor = torch.from_numpy(audio_float32).to(self.device)
        with torch.no_grad(): 
            confidence = self.vad_model(input_tensor, RATE).item()
        return confidence > VAD_SENSITIVITY

    def listen(self, timeout=None):
        # --- FIX: FLUSH OLD AUDIO INSTEAD OF RESTARTING ---
        # This keeps the mic active so we don't miss words
        while self.stream.get_read_available() > CHUNK:
            self.stream.read(CHUNK, exception_on_overflow=False)

        # print("\n>> Listening...") 
        frames = []
        started = False
        silence_frames = 0
        start_time = time.time()
        
        while True:
            # Check timeout inside the loop
            if timeout and not started:
                if time.time() - start_time > timeout:
                    return "" 

            try:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
            except:
                continue # Skip bad frames

            if self.is_speech(data):
                if not started:
                    started = True
                    # print(">> Hearing voice...") # Visual cue
                frames.append(data)
                silence_frames = 0 
            
            elif started:
                frames.append(data)
                silence_frames += 1
                if silence_frames > (RATE / CHUNK * SILENCE_THRESHOLD):
                    break

        if not frames: return ""

        audio_data = b''.join(frames)
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        segments, _ = self.whisper.transcribe(
            audio_np, 
            beam_size=5,
            language="en", 
            vad_filter=True, 
            initial_prompt="Jarvis, listen carefully. Akshara, Akhil. Bubble Sort, Python, Code, Algorithm, Function, Variable, Shutdown, Volume, Brightness, Torque."
        )
        
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "

        return full_text.strip()