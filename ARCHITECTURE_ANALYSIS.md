# Jarvis 2.0 - Complete Architecture Analysis

## System Overview

Jarvis 2.0 is a local AI Operating System Assistant built with a modular architecture. It uses a **Listen-Think-Act** cycle orchestrated by `main.py`, powered by dual LLM brains (Groq + OpenRouter), and executes actions through a tool registry system.

---

## Step-by-Step Flow: "Open Spotify"

### 1. **Audio Capture** (`engine/listener.py`)
- **Entry Point**: `main.py` line 79 calls `ear.listen(timeout=1.0)`
- **Process**:
  - AudioListener uses **Faster-Whisper (large-v3)** with CUDA acceleration
  - **Silero VAD** detects voice activity (confidence > 0.5)
  - Continuously reads audio chunks (512 frames @ 16kHz)
  - Detects speech start → collects frames → detects silence (1.6s threshold) → stops
  - Transcribes audio using Whisper with VAD filtering
  - Returns: `"jarvis open spotify"` (or similar)

### 2. **Wake Word Detection** (`main.py` lines 96-103)
- Checks if any wake word from `config.WAKE_WORDS` is in the transcribed text
- Wake words: `["jarvis", "javis", "service", "travis", "davis", "garvis", "jahvis"]`
- If detected:
  - Plays "listen.mp3" sound effect
  - Sets `conversation_mode = True`
  - Updates UI status to "LISTENING"

### 3. **Command Preprocessing** (`main.py` lines 122-124)
- Strips wake word from command: `"open spotify"`
- Checks for special triggers (gaming mode, shutdown, music commands)
- For "Open Spotify": proceeds to normal processing

### 4. **Brain Processing** (`core/llm.py` - `think()` method)

#### 4a. **Context Injection** (lines 166-189)
- `window_engine.get_active_window()` detects current app/mode
- Generates context instruction based on:
  - **Active Window**: e.g., "code" → WORK mode, "valorant" → GAMING mode
  - **Time of Day**: Late night (1-5 AM) → brief responses
  - **Mode Personality**:
    - WORK: Extremely concise, consultant-style
    - GAMING: Minimal distraction, 1 sentence max
    - CASUAL: Full Stark personality, witty

#### 4b. **LLM Query** (lines 191-219)
- Builds conversation history (max 10 messages)
- Appends context instruction + user command
- **Primary**: Sends to Groq API (`llama-3.3-70b-versatile`)
- **Backup**: If Groq fails (429/rate limit) → OpenRouter (`meta-llama/llama-3-8b-instruct:free`)
- Temperature: 0.6, Max tokens: 500

#### 4c. **Response Parsing** (lines 137-163)
- LLM returns: `"Opening Spotify, Sir.\nACTION: open_app | spotify"`
- `_process_response()` extracts:
  - **Tool Name**: `open_app`
  - **Tool Argument**: `spotify`
  - **Speech Part**: `"Opening Spotify, Sir."` (ACTION line stripped)

#### 4d. **Tool Execution** (lines 126-135)
- Looks up `open_app` in `tool_registry` → maps to `SystemOps.open_application`
- Calls `SystemOps.open_application("spotify")`

### 5. **Action Execution** (`capabilities/system_ops.py`)

#### 5a. **Direct Command Check** (`app_opener.py` lines 44-49)
- Checks `DIRECT_COMMANDS` dictionary
- Finds: `"spotify": "start spotify:"`
- Executes: `subprocess.run("start spotify:", shell=True)`
- **Returns**: `"Opening spotify..."`

#### 5b. **Fallback: The Hunter** (if direct command fails)
- If Spotify URI doesn't work, falls back to `AppOpener.open_app()`
- Uses `FileOps.find_all_files("spotify.exe")` to scan:
  - Desktop, Downloads, D:\, E:\, F:\ drives
  - Uses fuzzy matching (85% similarity threshold)
  - Launches first match found

### 6. **Response & Speech** (`main.py` lines 189-196)
- Brain returns: `"Opening Spotify, Sir."`
- Prints to console: `"JARVIS: Opening Spotify, Sir."`
- Updates UI status: "SPEAKING"
- `mouth.speak()` uses **Kokoro TTS (v1.0 ONNX)** to generate speech
- Plays audio via `sounddevice`

### 7. **Conversation Mode Management**
- `last_active_time` updated
- System stays in conversation mode for 15 seconds (`CONVERSATION_TIMEOUT`)
- If no speech detected → timeout → returns to standby

---

## Complete Capability List

### **System Operations** (`system_ops.py`)

1. **`open_app`** - Opens applications, files, or websites
   - Hardcoded apps: Chrome, Brave, Telegram, Figma, Photoshop, Valorant, Minecraft, etc.
   - Smart file opener: Detects PDFs, TXT, DOCX, PNG, JPG, PY, CPP files
   - Search trap: "search for X" → opens Google/YouTube/Reddit search
   - Hunter fallback: Scans entire drive if app not found
   - Direct commands: Spotify URI, WhatsApp URI, Windows Settings URIs

2. **`close_app`** - Closes applications by process name
   - Maps app names to process names (e.g., "chrome" → "chrome.exe")
   - Uses `taskkill /F /IM` to force close

3. **`search_google`** - Web search using Tavily API
   - Returns top 3 results with titles and content snippets
   - Better for AI consumption than raw Google results

4. **`system_status`** - Checks CPU and memory usage
   - Returns: "CPU is at X%. Memory is at Y%."

5. **`terminate`** - Shuts down Jarvis
   - Returns goodbye message

### **Music Operations** (`music_ops.py`)

6. **`play_music`** - Plays music on Spotify
   - Searches Spotify API for song (5 results)
   - Smart filtering: Matches query words to track/artist names
   - Auto-wake: Launches Spotify app if not active
   - Handles Premium/Free tier differences
   - Falls back to deep link if API fails

7. **`pause_music`** - Pauses Spotify playback
   - Uses Spotify API or keyboard fallback

8. **`resume_music`** - Resumes Spotify playback
   - Uses Spotify API or keyboard play/pause

9. **`identify_song`** - Shazam-like song identification
   - Records 10 seconds of audio
   - Uses Shazamio API to identify
   - Plays beep cues (800Hz start, 600Hz done)

### **Volume Operations** (`volume_ops.py`)

10. **`set_volume`** - Sets volume to specific level (0-100%)
    - Resets to 0, then presses volume up buttons
    - Each press ≈ 2% volume

11. **`volume_up`** - Increases volume by ~10%
    - Presses volume up 5 times

12. **`volume_down`** - Decreases volume by ~10%
    - Presses volume down 5 times

13. **`mute`** - Toggles mute
    - Uses Windows volume mute key

### **Communication Operations** (`comm_ops.py`)

14. **`call_phone`** - Makes mobile phone call
    - Contact list: Mom, Grandfather, Friend (Akshara)
    - Opens Phone Link app (`tel:` URI)
    - Uses visual recognition to click call button
    - Falls back to Enter key if visual fails

15. **`whatsapp_call`** - Initiates WhatsApp call
    - Checks if WhatsApp desktop app is running
    - Desktop: Uses `whatsapp://send?phone=` + Ctrl+Shift+C
    - Web: Opens WhatsApp Web in Brave browser

### **Memory Operations** (`rag_ops.py`)

16. **`save_memory`** - Stores facts in ChromaDB
    - Uses sentence-transformers (all-MiniLM-L6-v2) for embeddings
    - Stores with timestamp metadata
    - Returns confirmation with date

17. **`read_memory`** - Retrieves memories by semantic search
    - Encodes query → finds top 3 similar memories
    - Returns memories with creation dates

18. **`forget_memory`** - Deletes a memory
    - Finds memory by semantic similarity
    - Deletes from ChromaDB collection

### **File Operations** (`file_ops.py`)

19. **`locate_file`** - Finds files/folders by name
    - Checks direct paths first (handles D:/, Desktop/, etc.)
    - Deep scan: Searches Desktop, Downloads, D:\, E:\, F:\
    - Fuzzy matching (85% similarity)
    - Returns single path or list of matches

20. **`create_file`** - Creates empty file
    - Smart path builder: Handles absolute (D:/) or relative (Desktop/)
    - Safety check: Blocks C:\Windows, C:\Program Files
    - Creates parent directories if needed

21. **`create_folder`** - Creates directory
    - Uses smart path builder
    - Creates nested folders if needed

22. **`write_file`** - Writes content to file
    - Format: `filename|content`
    - **Safety lock**: Forces all writes to Desktop
    - UTF-8 encoding

23. **`move_file`** - Moves file/folder to destination
    - Format: `filename|destination`
    - Creates destination if doesn't exist
    - Safety checks before moving

24. **`delete_file`** - Deletes file/folder
    - Uses `send2trash` (moves to Recycle Bin)
    - Safety checks before deletion
    - Handles multiple matches

25. **`read_file`** - Reads file contents
    - Returns first 5000 characters
    - UTF-8 encoding with error ignore

26. **`copy_file`** - Copy to clipboard (legacy, placeholder)

27. **`cut_file`** - Cut to clipboard (legacy, placeholder)

28. **`paste_file`** - Paste from clipboard (legacy, placeholder)

### **Gaming Operations** (`gaming_ops.py`)

29. **Gaming Mode Toggle** (handled in `main.py`, not a tool)
    - Lowers Jarvis process priority to BELOW_NORMAL
    - Reduces UI updates
    - Minimal responses (1 sentence max)
    - Trigger: "gaming mode on" / "stealth mode activate"

### **Window Operations** (`window_ops.py`)

30. **Active Window Detection** (used for context, not a tool)
    - Detects foreground window using Win32 API
    - Classifies mode: WORK / GAMING / CASUAL
    - WORK apps: VS Code, Office, Figma, Photoshop, etc.
    - GAMING apps: Valorant, Minecraft, Steam, Discord overlay
    - Influences LLM personality and verbosity

### **Vision Operations** (`vision_ops.py`)

31. **Image Analysis** (not registered as tool, but available)
    - Uses Groq Llama 3.2 90B Vision model
    - Encodes image to base64
    - Returns detailed description
    - **Note**: Not in tool_registry, so LLM can't call it directly

### **Bluetooth Operations** (`bluetooth_ops.py`)

32. **Bluetooth Device Connection** (not registered as tool, but available)
    - Known devices: JBL Charge 5, Buds, Headphones, Home Theater, Phone
    - Uses Bluetooth Command Line Tools
    - Reset handshake: Disconnect → Wait → Connect
    - **Note**: Not in tool_registry, so LLM can't call it directly

---

## Architecture Components

### **Core Loop** (`main.py`)
- Event loop with 1-second timeout checks
- Conversation mode state machine
- Music pause/resume logic
- Gaming mode triggers
- Shutdown handlers

### **Dual-Brain System** (`core/llm.py`)
- **Primary**: Groq (Llama 3.3 70B) - Fast, versatile
- **Backup**: OpenRouter (Llama 3 8B Free) - Fallback
- Recursive tool execution for search/read operations
- Context-aware personality switching

### **Audio Pipeline**
- **Input**: Faster-Whisper (large-v3) + Silero VAD
- **Output**: Kokoro TTS (v1.0 ONNX) - Local, high-quality
- Non-blocking listen mode for status checks

### **UI Bridge** (`server_bridge.py`)
- Flask-SocketIO server on port 5000
- Real-time status updates to React/Electron frontend
- Terminal log streaming

### **Tool Registry** (`capabilities/library.py`)
- Central registry mapping tool names to functions
- Descriptions fed to LLM system prompt
- Enables dynamic tool discovery

---

## Data Flow Summary

```
User Speech
    ↓
[listener.py] Faster-Whisper + VAD → Text
    ↓
[main.py] Wake Word Check → Command Extraction
    ↓
[llm.py] Context Injection → LLM Query → Response Parsing
    ↓
[library.py] Tool Registry Lookup
    ↓
[capabilities/*.py] Tool Execution
    ↓
[main.py] Response → [speaker.py] TTS → Audio Output
```

---

## Key Design Patterns

1. **Failover Architecture**: Groq → OpenRouter if rate limited
2. **Context-Aware Responses**: Window detection → Personality switching
3. **Safety First**: File operations blocked from system directories
4. **Smart Path Resolution**: Handles absolute/relative paths, Desktop detection
5. **Fuzzy Matching**: App/file finding uses similarity scoring
6. **Non-Blocking Audio**: Timeout-based listening allows status checks
7. **Recursive Tool Execution**: Search/read operations trigger follow-up LLM calls

---

## Total Capabilities: 32 Tools/Features

- **System**: 5 tools
- **Music**: 4 tools
- **Volume**: 4 tools
- **Communication**: 2 tools
- **Memory**: 3 tools
- **File Operations**: 9 tools
- **Gaming**: 1 mode (not a tool)
- **Window Detection**: Context feature
- **Vision**: Available but not registered
- **Bluetooth**: Available but not registered

---

*Analysis completed: February 2, 2026*
