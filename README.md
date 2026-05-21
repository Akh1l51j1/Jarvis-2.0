# J.A.R.V.I.S. 2.0 — Autonomous AI Desktop Assistant

> **An agentic, voice-driven AI system** that perceives its environment, orchestrates multi-step tool calls, and controls a Windows PC through natural language — all while maintaining persistent, searchable long-term memory.

---

## Overview

J.A.R.V.I.S. 2.0 is a production-grade autonomous AI assistant built for the Windows desktop. It is not a simple chatbot wrapper — it is a **multi-model agentic system** that listens for a wake word, interprets intent, selects from a registered tool library, executes chained actions, and synthesizes a contextual voice response, all in real time.

The system implements a **dual-LLM architecture** (Groq's LLaMA 3.3 70B as primary, OpenRouter's Gemini 2.0 Flash Lite as automatic failover), a **custom RAG memory engine** powered by ChromaDB and sentence transformers, and a **context-aware personality matrix** that adapts its tone and verbosity based on the user's active application and time of day.

A polished **Electron + React** desktop UI streams live status and conversation logs via a WebSocket bridge, giving the assistant a visual presence beyond the terminal.

---

## Key Features

### 🤖 Agentic Tool Orchestration
- Maintains a **registered tool library** (`capabilities/library.py`) of 15+ callable functions covering file operations, system control, Spotify, web search, vision,and more.
- The LLM selects and executes the correct tool at inference time using a structured `ACTION: tool_name | argument` protocol.
- Supports **recursive tool chaining**: e.g., a `search_google` result is automatically fed back into the LLM for synthesis before being spoken.

### 🧠 Dual-Layer Persistent Memory
- **Short-term (SQLite):** A `jarvis.db` database stores structured facts with timestamps via `MemoryOps`.
- **Long-term (Vector RAG):** A ChromaDB vector store (`jarvis_memory_db`) uses `sentence-transformers/all-MiniLM-L6-v2` embeddings for semantic retrieval — Jarvis can recall relevant context from any past conversation.

### 🎙️ Local Voice Engine
- **Listening (ASR):** Real-time speech-to-text powered by `faster-whisper` with Silero VAD (Voice Activity Detection via `silero_vad.jit`) for low-latency, accurate transcription without cloud dependency.
- **Speaking (TTS):** High-quality neural synthesis using the Kokoro ONNX model (`kokoro-v1.0.onnx`) for natural, expressive voice output.
- **Fuzzy Wake Word Detection:** Configurable list of phonetically similar wake words to handle real-world speech variation.

### 🪟 Context-Aware Personality Matrix
- Detects the user's active application window in real time.
- Dynamically switches between four behavioral modes:
  - **WORK** — Terse, consultant-grade responses; no personality.
  - **GAMING** — Single-sentence tactical outputs; no interruptions.
  - **LATE NIGHT** — Calm, brief, wellness-aware.
  - **CASUAL** — Full Stark-persona wit and sarcasm enabled.

### 🖥️ Electron Desktop UI
- Built with **React 19 + Vite** inside an Electron shell.
- Communicates with the Python backend over a **Socket.IO WebSocket bridge** (`server_bridge.py`).
- Displays real-time status indicators (IDLE / LISTENING / PROCESSING / SPEAKING / GAMING), a live conversation log, and system state.

### 🔁 Automatic API Failover
- On a Groq rate-limit (`429`) hit, the system seamlessly re-routes the identical request to OpenRouter (Gemini 2.0 Flash Lite) without surfacing the failure to the user.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Primary LLM** | Groq API — LLaMA 3.3 70B Versatile |
| **Backup LLM** | OpenRouter API — Gemini 2.0 Flash Lite |
| **ASR (Speech-to-Text)** | `faster-whisper` + Silero VAD |
| **TTS (Text-to-Speech)** | Kokoro v1.0 (ONNX Runtime) |
| **Long-term Memory** | ChromaDB (vector store) + `sentence-transformers` |
| **Short-term Memory** | SQLite via Python's `sqlite3` |
| **Backend Language** | Python 3.11+ |
| **Frontend** | React 19 + Vite |
| **Desktop Shell** | Electron |
| **UI↔Backend Bridge** | Socket.IO (WebSocket) |
| **System Integration** | `psutil`, `pyaudio`, `spotipy` |
| **Music Control** | Spotify Web API via `spotipy` |

---

## Project Architecture

```
jarvis 2.0/
│
├── main.py                  # Entrypoint: event loop, wake word, conversation state
├── server_bridge.py         # Socket.IO bridge: streams status/logs to Electron UI
├── config.py                # API keys & wake word config (gitignored — see Setup)
│
├── core/
│   └── llm.py               # Brain: dual-LLM client, tool dispatch, RAG context, failover
│
├── capabilities/            # Tool Library (15+ registered actions)
│   ├── library.py           # Central tool registry (name → function mapping)
│   ├── file_ops.py          # File CRUD, locate, read, write, delete
│   ├── system_ops.py        # Process management, CPU/RAM stats, shutdown
│   ├── music_ops.py         # Spotify playback control
│   ├── rag_ops.py           # ChromaDB RAG: save, retrieve, delete memories
│   ├── memory_ops.py        # SQLite structured memory
│   ├── vision_ops.py        # Screenshot + visual context
│   ├── window_ops.py        # Active window detection (for personality matrix)
│   └── ...                  # app_opener, comm, shazam, volume, etc.
│
├── engine/
│   ├── listener.py          # faster-whisper ASR + Silero VAD pipeline
│   ├── speaker.py           # Kokoro ONNX TTS pipeline
│   └── search_engine.py     # Web search abstraction
│
├── JarvisUI/                # Electron + React frontend
│   ├── electron.cjs         # Electron main process
│   ├── src/
│   │   ├── App.jsx          # Main UI component (status, logs, animations)
│   │   └── App.css          # Styling
│   └── package.json
│
└── assets/                  # Sound effects (startup, shutdown, listen chimes)
```

---

## Setup Instructions

### Prerequisites
- Python **3.11+**
- Node.js **18+** and npm
- A CUDA-capable GPU is strongly recommended (for Whisper ASR performance)
- API accounts for: **Groq**, **OpenRouter**, **Spotify Developer**

---

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/jarvis-2.0.git
cd "jarvis 2.0"
```

---

### 2. Create & Activate the Virtual Environment

```bash
# Create the virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
```

---

### 3. Install Python Dependencies

```bash
# Install PyTorch with CUDA 11.8 support first (for Whisper acceleration)
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Install all remaining dependencies
pip install -r requirements.txt
```

> **Note:** `faster-whisper`, `chromadb`, `sentence-transformers`, and `groq` are the core inference dependencies. Full install may take several minutes.

---

### 4. Configure API Keys

The `config.py` file is **gitignored** for security. You must create it manually:

```bash
# In the project root, create config.py
touch config.py
```

Paste the following template and fill in your keys:

```python
# Jarvis 2.0 — Configuration (DO NOT COMMIT)

# 1. LLM APIs
GROQ_API_KEY        = "gsk_..."          # https://console.groq.com
OPENROUTER_API_KEY  = "sk-or-v1-..."     # https://openrouter.ai

# 2. Spotify (for music control)
SPOTIPY_CLIENT_ID     = "..."            # https://developer.spotify.com/dashboard
SPOTIPY_CLIENT_SECRET = "..."
SPOTIPY_REDIRECT_URI  = "https://google.com/"

# 3. Wake Words (phonetically similar fallbacks for robustness)
WAKE_WORDS = ["jarvis", "javis", "service", "travis", "garvis"]

ASSISTANT_NAME = "Jarvis"
```

---

### 5. Install the UI Dependencies

```bash
cd JarvisUI
npm install
```

---

### 6. Launch Jarvis

**Option A — Full System (Backend + UI together):**

```bash
# Terminal 1: Start the Python backend
cd "d:\jarvis 2.0"
.venv\Scripts\activate
python main.py

# Terminal 2: Start the Electron UI
cd JarvisUI
npm run dev
```

**Option B — Headless (Backend only, terminal output):**

```bash
python main.py
```

**Option C — Silent Background Launch (Windows VBScript):**

```bash
wscript InvisibleJarvis.vbs
```

---

## Roadmap

- [ ] **Context-Aware Daily Orchestrator** — Proactive workspace snapshots, focus-mode automation, and activity tracking
- [ ] **Vision Pipeline** — Screen OCR + visual Q&A via multimodal LLM routing
- [ ] **Multi-User Profiles** — Per-user memory isolation and personalized system prompts
- [ ] **Plugin System** — Hot-loadable capability modules without core restarts
- [ ] **Packaged Installer** — Electron Builder distributable with bundled Python runtime

---

## License

MIT License. See `LICENSE` for details.

---

*Built with purpose. Inspired by Iron Man. Powered by Groq.*
