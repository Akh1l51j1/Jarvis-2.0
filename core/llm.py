from google import genai
from google.genai import types
import sys
import os
import time
import re 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from capabilities.library import tool_registry

class Brain:
    def __init__(self):
        print(">> Connecting to Gemini 2.0 (Flash)...")
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        self.search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        # --- THE "LOYAL BUTLER" PERSONA ---
        self.sys_instruction = """
        You are J.A.R.V.I.S.
        
        YOUR PERSONA:
        - You are a loyal, highly intelligent, and professional AI assistant.
        - You address the user as "Sir."
        - You have a dry, British wit (like a classic butler), but you are NEVER rude or disrespectful.
        - You are efficient and proactive. You exist to serve the user.
        - If the user asks something silly, you respond with playful, subtle humor, not insults.
        
        YOUR VOICE STYLE:
        - Speak clearly and concisely.
        - Use polite fillers like "Certainly," "Of course," "As you wish," "Right away."
        - Avoid long, robotic paragraphs. Keep it conversational.
        
        EXAMPLES:
        User: "Open Spotify."
        You: "Queueing up your playlist now, Sir. ACTION: open_app | spotify"
        
        User: "What is 2 + 2?"
        You: "I believe it's still four, Sir. Unless mathematics has changed overnight." (Playful, not rude)
        
        User: "I'm tired."
        You: "Perhaps a break is in order, Sir. Shall I put on some relaxing music?"

        TOOLS:
        1. USE GOOGLE SEARCH for facts.
        2. LOCAL TOOLS: open_app, play_music, set_volume, call_phone, terminate.
        
        RESPONSE FORMAT:
        (Conversational text) ACTION: tool_name | argument
        
        INTELLIGENT AUTOCORRECT:
        - "Play Therapy" -> ACTION: play_music | Tere Bina
        - "Play Fortify" -> ACTION: play_music | Spotify
        - "Post music" -> ACTION: pause_music | None
        - "Resume" -> ACTION: resume_music | None
        - "Mute" -> ACTION: mute | None
        - "Set volume 50" -> ACTION: set_volume | 50
        """
        
        self.chat = self.client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                tools=[self.search_tool],
                system_instruction=self.sys_instruction,
                temperature=0.8 # Slightly lower creativity for more stability/politeness
            )
        )
        print("   ✅ Brain Connected (Online).")

    def get_greeting(self):
        try:
            # Prompt for a respectful greeting
            prompt = "I just powered you on. Give me a short, professional, and loyal greeting. Call me Sir. Max 1 sentence."
            response = self.chat.send_message(prompt)
            return response.text
        except:
            return "At your service, Sir. Systems are ready."

    def think(self, user_input):
        retries = 3
        for attempt in range(retries):
            try:
                response = self.chat.send_message(user_input)
                text_response = response.text
                
                action_match = re.search(r"ACTION:\s*(\w+)\s*\|\s*(.*)", text_response, re.IGNORECASE)
                
                if action_match:
                    tool_name = action_match.group(1).strip()
                    tool_arg = action_match.group(2).strip()
                    
                    if tool_arg.lower() == "none" or tool_arg == "":
                        tool_arg = None
                    
                    print(f"   [Brain Logic] Executing: {tool_name} -> {tool_arg}")
                    
                    tool_output = "Done."
                    if tool_name in tool_registry:
                        func = tool_registry[tool_name]["func"]
                        if tool_arg: 
                            tool_output = func(tool_arg)
                        else: 
                            tool_output = func()
                    else:
                        tool_output = "Tool not found."

                    speech_part = text_response.split("ACTION:")[0].strip()
                    if not speech_part:
                        return tool_output
                    return speech_part
                
                return text_response

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    print(f"   [Rate Limit] Cooling down... (Attempt {attempt+1}/{retries})")
                    time.sleep(5)
                    continue
                else:
                    return f"Error: {e}"
        
        return "I seem to be overloaded, Sir. My apologies."

if __name__ == "__main__":
    bot = Brain()
    print(bot.get_greeting())