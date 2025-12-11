import os
import sys
import re
import time
from datetime import datetime
from groq import Groq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from capabilities.library import tool_registry

class Brain:
    def __init__(self):
        print(">> Connecting to Groq (Llama 3.3)...")
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        
        self.history = [] 
        self.max_history = 15 

        today = datetime.now().strftime("%A, %B %d, %Y")
        
        self.system_instruction = f"""
        You are J.A.R.V.I.S.
        CURRENT DATE: {today}
        
        GUIDELINES:
        1. **MEMORY RULE (CRITICAL):**
           - IF the user ASKS a question about themselves (e.g., "What is my car?", "Who am I?"), you MUST use 'read_memory'.
           - ONLY use 'save_memory' if the user explicitly TELLS you a fact (e.g., "My car is red", "Remember that I like pizza").
        
        2. **FILE RULE:**
           - IF the user asks "Where is [file]?", use 'locate_file'.
        
        TOOLS:
        1. USE 'search_google' for news/world facts.
        2. MEMORY TOOLS: 'read_memory' (for questions), 'save_memory' (for statements), 'forget_memory'.
        3. FILE TOOLS: 'locate_file', 'read_file', 'copy_file', 'cut_file', 'paste_file', 'delete_file'.
        4. LOCAL TOOLS: open_app, close_app, play_music, pause_music, resume_music, set_volume, call_phone, terminate.
        
        RESPONSE FORMAT:
        (Conversational text) ACTION: tool_name | argument
        
        INTELLIGENT AUTOCORRECT:
        - "Pause music" -> ACTION: pause_music | None
        - "Stop music" -> ACTION: pause_music | None
        - "Resume" -> ACTION: resume_music | None
        - "Volume 100" -> ACTION: set_volume | 100
        - "Close not bad" -> ACTION: close_app | notepad
        """
        
        self.history.append({"role": "system", "content": self.system_instruction})
        print("   ✅ Brain Connected (Groq Online).")

    def get_greeting(self):
        return "Systems online, Sir."

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
        action_match = re.search(r"ACTION:\s*(\w+)\s*\|\s*(.*)", response_text, re.IGNORECASE | re.DOTALL)
        
        if action_match:
            tool_name = action_match.group(1).strip()
            tool_arg = action_match.group(2).strip()
            if tool_arg.lower() == "none" or tool_arg == "": tool_arg = None
            
            tool_output = self._execute_tool(tool_name, tool_arg)
            speech_part = response_text.split("ACTION:")[0].strip()
            
            # Recurse for data tools
            if tool_name in ["search_google", "read_file", "identify_song", "read_memory", "locate_file"]:
                return (True, tool_output, tool_name) 
            
            if not speech_part:
                return (False, f"Done. {str(tool_output)}", None)
            
            return (False, speech_part, None)
            
        return (False, response_text, None)

    def think(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        if len(self.history) > self.max_history:
            self.history = [self.history[0]] + self.history[-(self.max_history-1):]

        try:
            # 1. INITIAL THINK
            completion = self.client.chat.completions.create(
                messages=self.history,
                model=self.model,
                temperature=0.6,
                max_tokens=500
            )
            response_text = completion.choices[0].message.content
            self.history.append({"role": "assistant", "content": response_text})

            # 2. PROCESS ACTION
            recurse, output_or_speech, tool_used = self._process_response(response_text)
            
            # 3. RECURSION (Digest Info)
            if recurse:
                print(f"   [Brain Logic] Digesting info from {tool_used}...")
                
                follow_up_prompt = (
                    f"SYSTEM_OUTPUT: The tool '{tool_used}' returned this data:\n"
                    f"{output_or_speech}\n\n"
                    f"INSTRUCTION: Answer the user's question based on this data. "
                    f"Do NOT say 'The tool returned' or list other unrelated memories. "
                    f"Do NOT mention dates unless asked. Just give the specific answer."
                )
                self.history.append({"role": "system", "content": follow_up_prompt})
                
                follow_up_completion = self.client.chat.completions.create(
                    messages=self.history,
                    model=self.model
                )
                final_response = follow_up_completion.choices[0].message.content
                self.history.append({"role": "assistant", "content": final_response})
                
                _, final_speech, _ = self._process_response(final_response)
                return final_speech

            return output_or_speech

        except Exception as e:
            return f"Error: {e}"

if __name__ == "__main__":
    bot = Brain()
    print(bot.get_greeting())