from google import genai
from google.genai import types
import sys
import os
import time
import re  # <--- ADDED REGEX FOR SMARTER PARSING

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from capabilities.library import tool_registry

class Brain:
    def __init__(self):
        print(">> Connecting to Gemini 2.0...")
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.search_tool = types.Tool(google_search=types.GoogleSearch())
        
        self.sys_instruction = """
        You are Jarvis.
        RULES:
        1. USE GOOGLE SEARCH for facts.
        2. LOCAL TOOLS: open_app, play_music, set_volume, etc.
        
        RESPONSE FORMAT:
        ACTION: tool_name | argument

        INTELLIGENT AUTOCORRECT:
        - "Set volume to 50" -> ACTION: set_volume | 50
        - "Mute the sound" -> ACTION: mute | None
        - "Unmute" -> ACTION: unmute | None
        - "Play Therapy" -> ACTION: play_music | Tere Bina
        """
        
        self.chat = self.client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                tools=[self.search_tool],
                system_instruction=self.sys_instruction
            )
        )
        print("   ✅ Brain Connected (Online).")

    def think(self, user_input):
        retries = 3
        for attempt in range(retries):
            try:
                response = self.chat.send_message(user_input)
                text_response = response.text
                
                # --- NEW ROBUST PARSER ---
                # Looks for the pattern: "ACTION: word | rest_of_line"
                # This ignores "Okay, I will..." fluff.
                action_match = re.search(r"ACTION:\s*(\w+)\s*\|\s*(.*)", text_response, re.IGNORECASE)
                
                if action_match:
                    tool_name = action_match.group(1).strip()
                    tool_arg = action_match.group(2).strip()
                    print(f"   [Brain Logic] Executing: {tool_name} -> {tool_arg}")
                    
                    if tool_name in tool_registry:
                        func = tool_registry[tool_name]["func"]
                        if tool_arg: return func(tool_arg)
                        else: return func()
                    return "Tool not found in registry."
                
                return text_response

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    print(f"   [Rate Limit] Cooling down... (Attempt {attempt+1}/{retries})")
                    time.sleep(5)
                    continue
                else:
                    return f"Error: {e}"
        
        return "I am overloaded. Please try again."

if __name__ == "__main__":
    bot = Brain()
    # Test the new parser with a messy response
    print(bot.think("Jarvis play therapy now"))