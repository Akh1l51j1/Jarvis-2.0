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
        1. **BE PROACTIVE:** Anticipate needs (e.g., "Shall I run the code?").
        2. **BE INTERACTIVE:** Ask clarifying questions.
        3. **BE CONCISE:** Do **NOT** read back code or long text you write. Just say "Code written" or "Content updated".
        
        CRITICAL OPERATING RULES:
        1. **NO HALLUCINATIONS:** Use tools for all actions.
        2. **SMART PATHS:** Do NOT guess 'C:\\Users\\<user>'. Use relative paths like 'Desktop/Folder'.
        3. **WRITE_FILE:** Put ENTIRE content (including newlines) into the argument.
        
        RESPONSE FORMAT (STRICT):
        [Optional Reasoning/Speech]
        ACTION: tool_name | argument
        
        IMPORTANT: ALWAYS put your speech **BEFORE** the ACTION command.
        - WRONG: ACTION: ... \n Done.
        - CORRECT: Done. \n ACTION: ...
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
        # 1. SPECIAL CASE: write_file (Captures multi-line code)
        action_match = re.search(r"ACTION:\s*(write_file)\s*\|\s*(.*?)(?=\nACTION:|$)", response_text, re.IGNORECASE | re.DOTALL)
        
        # 2. STANDARD CASE: Other tools (Stop at newline)
        if not action_match:
            action_match = re.search(r"ACTION:\s*(\w+)\s*\|\s*(.*)", response_text, re.IGNORECASE)

        if action_match:
            tool_name = action_match.group(1).strip()
            tool_arg = action_match.group(2).strip()
            if tool_arg.lower() == "none" or tool_arg == "": tool_arg = None
            
            tool_output = self._execute_tool(tool_name, tool_arg)
            
            # Remove the ACTION part. Since we enforced "Speech First", the speech remains at the top.
            speech_part = response_text.replace(action_match.group(0), "").strip()
            
            # Recurse for data retrieval tools
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
            completion = self.client.chat.completions.create(
                messages=self.history,
                model=self.model,
                temperature=0.6,
                max_tokens=800
            )
            response_text = completion.choices[0].message.content
            self.history.append({"role": "assistant", "content": response_text})

            recurse, output_or_speech, tool_used = self._process_response(response_text)
            
            if recurse:
                print(f"   [Brain Logic] Digesting info from {tool_used}...")
                
                # --- PROACTIVE FOLLOW-UP ---
                follow_up_prompt = (
                    f"DATA: {output_or_speech}\n\n"
                    f"INSTRUCTION: Report this result naturally. "
                    f"Then, SUGGEST A RELEVANT NEXT STEP based on the data. "
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