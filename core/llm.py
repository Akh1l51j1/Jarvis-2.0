import os
import sys
import re
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

        # Dynamic Menu
        tools_desc = ""
        for tool_name, tool_info in tool_registry.items():
            tools_desc += f"- {tool_name}: {tool_info['desc']}\n"

        today = datetime.now().strftime("%A, %B %d, %Y")
        
        self.system_instruction = f"""
        You are J.A.R.V.I.S., a highly advanced AI Assistant on a Windows PC.
        CURRENT DATE: {today}
        
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
        5. **FACT EXTRACTION:** When using 'search_google', NEVER read snippets. Extract the single specific answer (e.g., "It's 2:59 PM") and report it witty and briefly.
        6. **MAX_LENGTH:** Keep responses under 2 sentences unless explaining a complex design task.

        SILENT_MUSIC_RULE (CRITICAL):
        - If the user asks for **MUSIC CONTROLS** (play_music, pause_music, resume_music), you must execute the ACTION and respond with NOTHING (an empty string).
        - For **ALL OTHER ACTIONS** (open_app, close_app, set_volume, locate_file, etc.), you MUST provide a witty confirmation first.
        
        TOOL ARGUMENT RULES (CRITICAL):
        - **ARGUMENTS ONLY:** The 'argument' part of an ACTION must contain ONLY the data needed (e.g., "Song Name", "C:/Path/File.txt").
        - **NO CONVERSATION IN ACTION:** Never include wit, questions, or commentary inside the ACTION line.
        - **WIT FIRST:** Always put your conversational wit on the lines BEFORE the ACTION line.

        RESPONSE FORMAT:
        [Wit/Commentary First]
        ACTION: tool_name | argument
        (Remember: Empty response if it is a music control action).
        
        (If no tool is needed, do NOT write ACTION: None. Just speak.)
        """
        
        self.history.append({"role": "system", "content": self.system_instruction})
        print("   ✅ Brain Connected (Groq Online).")

    def get_greeting(self):
        return "Systems online, Sir. Ready to begin."

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
            # This prevents him from ever saying the word "ACTION" out loud.
            speech_part = re.sub(r"ACTION:.*", "", response_text, flags=re.IGNORECASE).strip()
            speech_part = speech_part.replace("ACTION: None", "").strip()

            # 3. Handle recursion or return speech
            recursive_tools = ["search_google", "read_file", "identify_song", "read_memory", "locate_file", "write_file"]
            if tool_name in recursive_tools:
                return (True, tool_output, tool_name) 
            
            # If he didn't write any wit, but did a tool, say "Done"
            if not speech_part and tool_name:
                return (False, f"Done. {str(tool_output)}", None)
                
            return (False, speech_part, None)

    def think(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        if len(self.history) > self.max_history:
            self.history = [self.history[0]] + self.history[-(self.max_history-1):]

        try:
            completion = self.client.chat.completions.create(
                messages=self.history,
                model=self.model,
                temperature=0.6,
                max_tokens=800
            )
            response_text = completion.choices[0].message.content
            
            recurse, output_or_speech, tool_used = self._process_response(response_text)
            
            if recurse:
                print(f"   [Brain Logic] Digesting info from {tool_used}...")
                
                # --- PROACTIVE FOLLOW-UP (Strict Mode) ---
                follow_up_prompt = (
                    f"TOOL_OUTPUT: {output_or_speech}\n\n"
                    f"INSTRUCTION: The action is complete. Report the result naturally in your witty persona. "
                    f"If there is a logical next step, you may ask a follow-up question. "
                    f"If the task is finished and requires no further input, simply end the response."
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

            self.history.append({"role": "assistant", "content": response_text})
            return output_or_speech

        except Exception as e:
            return f"Error: {e}"

if __name__ == "__main__":
    bot = Brain()
    print(bot.get_greeting())