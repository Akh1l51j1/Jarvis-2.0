import os
import sys
import re
from datetime import datetime
from groq import Groq
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from capabilities.library import tool_registry
from capabilities.window_ops import window_engine  # <--- NEW: THE EYES
from openai import OpenAI

class Brain:
    def __init__(self, bridge=None):
        print(">> Connecting to Groq (Llama 3.3)...")
        # --- BRAIN 1: GROQ (Primary, Fast) ---
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

        print(">> Connecting to OpenRouter (Backup)...")
        # --- BRAIN 2: OPENROUTER (Backup & Vision) ---
        self.openrouter_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.OPENROUTER_API_KEY,
            # OpenRouter REQUIRES these headers for free models
            default_headers={
                "HTTP-Referer": "https://github.com/akhil/jarvis",
                "X-Title": "Jarvis 2.0"
            }
        )
        # UPDATED: Using Gemini 2.0 Flash Lite (Free & Fast)
        self.backup_model = "google/gemini-2.0-flash-lite-preview-02-05:free"

        # --- EXISTING JARVIS STATE ---
        self.bridge = bridge  # <--- STORES THE CONNECTION
        self.gaming_mode = False 
        self.history = [] 
        self.max_history = 10 
        
        self.profile = self.load_user_profile()
        self.user_name = self.profile.get("user_name", "Sir")
        preferences = self.profile.get("preferences", {})
        allergies = preferences.get("gf_allergies", ["No known allergies"])
        
        # --- BUILD TOOLS DESCRIPTION ---
        tools_desc = ""
        for tool_name, tool_info in tool_registry.items():
            tools_desc += f"- {tool_name}: {tool_info['desc']}\n"

        today = datetime.now().strftime("%A, %B %d, %Y")
        
        self.system_instruction = fr"""
        You are J.A.R.V.I.S., a highly advanced AI Assistant on a Windows PC.
        CURRENT DATE: {today}
        
        USER IDENTITY:
        - Primary User: {self.user_name}
        - Critical Context: User's girlfriend is ALLERGIC to {', '.join(allergies)}. 
          Always cross-reference food or environmental suggestions with this safety fact.
        
        AVAILABLE TOOLS:
        {tools_desc}
        
        CORE PERSONALITY:
        1. **STARK MODE:** Be sophisticated and witty, but NEVER explain your internal logic.
        2. **NO COMMENTARY ON TOOLS:** Do NOT say things like "I'm executing the tool" or "Let me search that for you." Just perform the action.
        3. **CONCISE WIT:** If an action is obvious (like pausing music), don't speak at all.
        
        CRITICAL OPERATING RULES:
        1. **NO HALLUCINATIONS:** Use tools for all actions.
        2. **SMART PATHS:** Do NOT guess 'C:\\Users\\<user>'. Use relative paths like 'Desktop/Folder'.
        3. **WRITE_FILE:** Put ENTIRE content (including newlines) into the argument.
        4. **FOLLOW-THROUGH:** If the user selects a file (e.g., "The desktop one"), perform the ORIGINAL ACTION (Delete/Move).
        5. **FACT EXTRACTION:** When using 'search_google', NEVER read snippets. Extract the single specific answer.
        6. **MAX_LENGTH:** Keep responses under 2 sentences unless explaining a complex design task OR writing file content.
        7. **GAMING SAFETY (CRITICAL):** If the user mentions "Lag", "FPS", or "Performance" while in GAMING mode, NEVER close the active game process. Only close BACKGROUND apps (Chrome, Spotify, Discord).
        
        FILE WRITING QUALITY RULES (CRITICAL):
        1. **COMPREHENSIVE CONTENT:** When the user asks to write/create a file, the content you generate MUST be comprehensive, detailed, and professionally structured. Aim for full-page documents, not brief summaries.
        2. **FORMAL TONE FOR FILES:** Do NOT use the 'Casual/Sarcastic' persona for file content. Use a formal, academic, professional tone for the file content itself. Your conversational wit should ONLY appear in your spoken response, NOT in the file content.
        3. **NO CONTEXT HALLUCINATION:** Never reference previous unrelated conversations (like 'beef allergies', 'girlfriend preferences', etc.) inside a new file unless explicitly asked. Each file should be self-contained and focused on the requested topic.
        4. **MARKDOWN STRUCTURE:** File content must ALWAYS use proper Markdown formatting:
           - Use # for main title, ## for sections, ### for subsections
           - Use bullet points (- or *) for lists
           - Use numbered lists (1., 2., 3.) for sequential items
           - Use **bold** for emphasis on key terms
           - Organize content into clear sections with headers
        5. **LENGTH REQUIREMENT:** For documents like roadmaps, guides, or articles, generate at least 500-1000 words of detailed, structured content. Short 3-line responses are unacceptable.
        
        RULES:
        1. **EXECUTE FIRST:** Do not talk about doing it. Just use the tool.
        2. **NO SCRIPTING:** Do NOT generate text for the User. Only reply as Jarvis.
        3. **WEB SEARCH VS BROWSER SEARCH (CRITICAL):** - General questions: Use `search_google` and summarize.
           - "Open [Browser] and search for [X]": Use `open_app` with the exact string.
        4. **SILENCE:** If you play music, output ONLY the ACTION line.
        5. **FILE MEMORY (CRITICAL):** If the user says "Open the first one", "Open it", or "Open that file", look at the file path you just found using `locate_file` and pass the EXACT PATH to `open_app`. 
           - Correct: ACTION: open_app | C:\Users\Akhil\Downloads\notes.pdf
        6. **MULTIPLE FILES:** If a tool returns a list of multiple files (e.g. string starting with "Found multiple files" or "Found multiple matches"), present them to the user and ask them to select one (e.g., "I found several. Which one—1, 2, or 3?" or "Open the second one."). Do NOT open the first one or the newest one automatically.
        7. **FOLLOW-UP SELECTION:** When the user replies with a number (e.g., "Open the 3rd one", "The second one", "Number 1"), look at the "Found multiple files" / "Found multiple matches" list in the chat history. Map that number to the corresponding full path (e.g., 3 → the path on line "3. ...") and pass that EXACT path to open_app (or delete_file/move_file as requested).
        
        SILENT_MUSIC_RULE (CRITICAL):
        - If the user asks for **MUSIC CONTROLS** (play_music, pause_music, resume_music), you must execute the ACTION and respond with NOTHING (an empty string).
        - For **ALL OTHER ACTIONS** (open_app, close_app, set_volume, locate_file, etc.), you MUST provide a witty confirmation first.
        
        TOOL ARGUMENT RULES (CRITICAL):
        - **ARGUMENTS ONLY:** The 'argument' part of an ACTION must contain ONLY the data needed (e.g., "Song Name", "C:/Path/File.txt").
        - **NO CONVERSATION IN ACTION:** Never include wit, questions, or commentary inside the ACTION line.
        - **WIT FIRST:** Always put your conversational wit on the lines BEFORE the ACTION line.

        VERBAL RESPONSE RULES (Casual & Professional personas):
        1. **NO RAW PATHS:** Never read full file paths (like C:/Users/... or D:\\Folder\\file.txt) out loud. Instead, refer to the location naturally, e.g., "I've saved it to your Desktop", "File located.", or "It's on your Desktop."
        2. **NATURAL CONFIRMATION:** When a tool returns a technical success message (e.g., "Success: Wrote to 'notes.txt' on Desktop."), do NOT repeat it verbatim. Paraphrase naturally, e.g., "Done. It's on your Desktop." or "Saved to your Desktop."
        3. **LOCATE_FILE:** When locate_file returns a path, do NOT read the directory string aloud. Say something like "Here is your file." or "Found it." and use the path only in the ACTION line if the user asks to open/move/delete it.

        RESPONSE FORMAT:
        [Wit/Commentary First]
        ACTION: tool_name | argument
        (Remember: Empty response if it is a music control action).
        
        (If no tool is needed, do NOT write ACTION: None. Just speak.)
        """
        
        self.history.append({"role": "system", "content": self.system_instruction})
        print("    Brain Connected (Groq Online).")

    def load_user_profile(self):
        if os.path.exists("user_profile.json"):
            try:
                with open("user_profile.json", "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"    Profile Load Error: {e}")
        return {}

    def get_greeting(self):
        # NEW: Time-Aware Greeting
        hour = datetime.now().hour
        if 5 <= hour < 12: time_greet = "Good morning"
        elif 12 <= hour < 17: time_greet = "Good afternoon"
        elif 17 <= hour < 22: time_greet = "Good evening"
        else: time_greet = "Welcome back"
        
        return f"{time_greet}, {self.user_name}. Systems online."

    def _execute_tool(self, tool_name, tool_arg):
        print(f"   [Brain Logic] Executing: {tool_name} -> {tool_arg}")
        if tool_name in tool_registry:
            func = tool_registry[tool_name]["func"]
            try:
                if tool_arg: return func(tool_arg)
                else: return func()
            except Exception as e:
                return f"Tool Error: {e}"
        return "Tool not found."

    def _process_response(self, response_text):
        # 1. First, extract the ACTION for the computer to run
        action_match = re.search(r"ACTION:\s*(write_file)\s*\|\s*(.*?)(?=\nACTION:|$)", response_text, re.IGNORECASE | re.DOTALL)
        if not action_match:
            action_match = re.search(r"ACTION:\s*(\w+)(?:\s*\|\s*|\s+)([^\n]*)", response_text, re.IGNORECASE)

        tool_output = None
        tool_name = None
        if action_match:
            tool_name = action_match.group(1).strip()
            tool_arg = action_match.group(2).strip()
            if tool_arg and (tool_arg.lower() == "none" or tool_arg == ""): tool_arg = None
            tool_output = self._execute_tool(tool_name, tool_arg)

        # 2. THE SPEECH FILTER: Strip ALL "ACTION:" lines from what is spoken
        speech_part = re.sub(r"ACTION:.*", "", response_text, flags=re.IGNORECASE).strip()
        speech_part = speech_part.replace("ACTION: None", "").strip()

        # 3. Handle recursion or return speech
        recursive_tools = ["search_google", "read_file", "identify_song", "read_memory", "locate_file", "write_file"]
        if tool_name in recursive_tools:
            return (True, tool_output, tool_name) 
        
        if not speech_part and tool_name:
            return (False, f"Done. {str(tool_output)}", None)
            
        return (False, speech_part, None)

    # --- NEW: The Context Engine ---
    def _get_context_instruction(self):
        """Generates specific instructions based on Active Window & Time."""
        # 1. Get Visual Context
        status = window_engine.get_active_window()
        app = status['app']
        mode = status['mode']
        
        # 2. Get Time Context
        hour = datetime.now().hour
        is_late_night = (hour >= 1) and (hour < 5)
        
        instruction = f" [CURRENT STATUS: Active App='{app}' | Mode='{mode}']"

        # 3. The Personality Matrix
        if mode == "WORK":
            instruction += "\n MODE: DEEP WORK. Be extremely concise. No jokes. No pleasantries. Efficient, consultant-style responses."
        elif mode == "GAMING" or self.gaming_mode:
            instruction += "\n MODE: GAMING TACTICAL. Minimal distraction. Use max 1 sentence. If the user asks for info, give it raw."
        elif is_late_night:
            instruction += "\n MODE: LATE NIGHT. Speak softly. Be brief. Remind user to rest if they seem stressed."
        else:
            instruction += "\n MODE: CASUAL. Full Stark Personality allowed. Be witty, sarcastic, and conversational."

        return instruction

    def think(self, user_input):
        context_note = self._get_context_instruction()
        
        # --- SEND LOGS TO UI ---
        if self.bridge:
            try: self.bridge.log(context_note)
            except: pass
        print(f"\n   [Context] {context_note.strip()}")

        temp_history = self.history.copy()
        temp_history.append({"role": "system", "content": context_note})
        temp_history.append({"role": "user", "content": user_input})

        self.history.append({"role": "user", "content": user_input})
        if len(self.history) > self.max_history:
            self.history = [self.history[0]] + self.history[-(self.max_history-1):]

        # ==========================================
        # STEP 1: INITIAL THOUGHT (With Failover)
        # ==========================================
        # Detect if this is a file writing request to use higher token limit
        is_file_write = any(keyword in user_input.lower() for keyword in ["write", "create", "file", "document", "roadmap", "guide", "article"])
        token_limit = 4096 if is_file_write else 500
        
        try:
            completion = self.client.chat.completions.create(
                messages=temp_history,
                model=self.model,
                temperature=0.6,
                max_tokens=token_limit,
                stop=["USER:", "User:", "Akhil:"] 
            )
            response_text = completion.choices[0].message.content

        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                print("   [Brain Warning] Groq Limit Hit (Step 1). Rerouting to OpenRouter...")
                try:
                    completion = self.openrouter_client.chat.completions.create(
                        messages=temp_history,
                        model=self.backup_model,
                        temperature=0.6,
                        max_tokens=token_limit,
                        stop=["USER:", "User:", "Akhil:"] 
                    )
                    response_text = completion.choices[0].message.content
                except Exception as backup_e:
                    return f"System Failure: Both APIs down. {backup_e}"
            else:
                return f"Groq Error: {e}"

        # --- PROCESS THE RESPONSE ---
        recurse, output_or_speech, tool_used = self._process_response(response_text)
        
        # ==========================================
        # STEP 2: RECURSION / TOOL DIGESTION (With Failover)
        # ==========================================
        if recurse:
            print(f"   [Brain Logic] Digesting info from {tool_used}...")
            # For write_file recursion, use comprehensive prompt and higher token limit
            if tool_used == "write_file":
                follow_up_prompt = f"TOOL_OUTPUT: {output_or_speech}\nINSTRUCTION: Generate comprehensive, detailed file content. Use formal tone, Markdown structure with headers and bullet points. Make it at least 500-1000 words for substantial documents. Do NOT reference unrelated previous conversations."
                recursion_token_limit = 4096
            else:
                follow_up_prompt = f"TOOL_OUTPUT: {output_or_speech}\nINSTRUCTION: Report result briefly."
                recursion_token_limit = 500
            
            recurse_history = temp_history + [
                {"role": "assistant", "content": response_text},
                {"role": "system", "content": follow_up_prompt}
            ]
            
            try:
                follow_up_completion = self.client.chat.completions.create(
                    messages=recurse_history,
                    model=self.model,
                    max_tokens=recursion_token_limit,
                    stop=["USER:", "User:"] 
                )
                final_response = follow_up_completion.choices[0].message.content

            except Exception as e:
                # --- RECURSION FAILOVER TRIGGER ---
                if "429" in str(e) or "rate limit" in str(e).lower():
                    print("   [Brain Warning] Groq Limit Hit (Step 2). Rerouting to OpenRouter...")
                    try:
                        follow_up_completion = self.openrouter_client.chat.completions.create(
                            messages=recurse_history,
                            model=self.backup_model,
                            max_tokens=recursion_token_limit,
                            stop=["USER:", "User:"] 
                        )
                        final_response = follow_up_completion.choices[0].message.content
                    except Exception as backup_e:
                        return f"System Failure: Both APIs down during follow-up. {backup_e}"
                else:
                    return f"Groq Error during follow-up: {e}"

            self.history.append({"role": "assistant", "content": final_response})
            _, final_speech, _ = self._process_response(final_response)
            return final_speech

        self.history.append({"role": "assistant", "content": response_text})
        return output_or_speech
if __name__ == "__main__":
    bot = Brain()
    print(bot.get_greeting())