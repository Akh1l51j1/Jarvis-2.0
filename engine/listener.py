import pyaudio
import numpy as np
import torch
from faster_whisper import WhisperModel

# --- UNIVERSAL CONFIGURATION ---
CHANNELS = 1
RATE = 16000
CHUNK = 512 
SILENCE_THRESHOLD = 1.6  # Increased to stop him from cutting you off when you pause to think
VAD_SENSITIVITY = 0.5    # Increased slightly to ignore keyboard clicks

class AudioListener:
    def __init__(self):
        print(">> Loading VAD Model...")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f">> VAD/Whisper offloaded to: {torch.cuda.get_device_name(0)}")

        # Load VAD
        self.vad_model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False
        )
        self.vad_model.to(self.device)
        
        # --- THE UPGRADE: SMALL.EN MODEL ---
        print(">> Loading Faster-Whisper (small.en)...")
        # 'small.en' is much better at technical terms than 'base'
        self.whisper = WhisperModel("small.en", device="cuda", compute_type="int8")
        
        self.p = pyaudio.PyAudio()
        
        # FORCE DEVICE ID 1 (Based on your mic_test.py results)
        # We explicitly ask for index 1 to ensure we don't accidentally grab the Array
        try:
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      input_device_index=1, # <--- HARDCODED TO YOUR BOYA MIC
                                      frames_per_buffer=CHUNK)
        except:
            # Fallback if ID 1 fails
            print(">> Warning: Device 1 failed. Falling back to default.")
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      frames_per_buffer=CHUNK)

    def is_speech(self, audio_chunk):
        audio_float32 = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        input_tensor = torch.from_numpy(audio_float32).to(self.device)
        with torch.no_grad(): 
            confidence = self.vad_model(input_tensor, RATE).item()
        return confidence > VAD_SENSITIVITY

    def listen(self):
        self.stream.stop_stream()
        self.stream.start_stream()
        
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

        if not frames: return ""

        audio_data = b''.join(frames)
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # --- TRANSCRIBE WITH TECH CONTEXT ---
        segments, _ = self.whisper.transcribe(
            audio_np, 
            beam_size=5,
            language="en", 
            vad_filter=True, 
            # We tell the model to expect Coding and Indian names
            initial_prompt="Jarvis, listen carefully. Akshara, Akhil. Bubble Sort, Python, Code, Algorithm, Function, Variable, Shutdown, Volume, Brightness, Torque."
        )
        
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "

        return full_text.strip()