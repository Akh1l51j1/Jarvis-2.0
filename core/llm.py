from google import genai
from google.genai import types
import sys
import os
import time
import re 
from datetime import datetime 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from capabilities.library import tool_registry

class Brain:
    def __init__(self):
        print(">> Connecting to Gemini 2.0 (Flash)...")
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        # --- NEW DATE CALCULATION ---
        today = datetime.now().strftime("%A, %B %d, %Y")
        
        # Note the 'f' before the quotes for the f-string!
        self.sys_instruction = f"""
        You are J.A.R.V.I.S.
        
        CURRENT DATE: {today}
        
        YOUR PERSONA:
        - You are a loyal, highly intelligent, and professional AI assistant.
        - You address the user as "Sir."
        - You have a dry, British wit.
        
        TOOLS:
        1. USE 'search_google' tool for facts/events. (Do not use internal knowledge for news).
        2. LOCAL TOOLS: open_app, play_music, set_volume, call_phone, terminate, identify_song.
        
        RESPONSE FORMAT:
        (Conversational text) ACTION: tool_name | argument
        
        INTELLIGENT AUTOCORRECT (PHONETIC FIXES):
        # --- MUSIC ---
        - "Play Therapy" -> ACTION: play_music | Tere Bina
        - "Play Fortify" -> ACTION: play_music | Spotify
        - "Post music" -> ACTION: pause_music | None
        - "Resume" -> ACTION: resume_music | None
        - "Mute" -> ACTION: mute | None
        
        # --- CONTACTS (The New Fixes) ---
        - "Call Apechan" -> ACTION: call_phone | appachen
        - "Call Appa Chan" -> ACTION: call_phone | appachen
        - "Call Pampangadamani" -> ACTION: call_phone | pappa nedumanni
        - "Call Pampa" -> ACTION: call_phone | pappa nedumanni
        - "Call Grandfather" -> ACTION: call_phone | grandfather
        - "Call Accessor" -> ACTION: call_phone | Akshara
        - "Call Action" -> ACTION: call_phone | Akshara
        - "Call Collection" -> ACTION: call_phone | Akshara
        
        # --- APPS ---
        - "Open G Helper" -> ACTION: open_app | ghelper
        - "Open J Helper" -> ACTION: open_app | ghelper
        - "Open Valo" -> ACTION: open_app | valorant
        """
        
        self.chat = self.client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=self.sys_instruction,
                temperature=0.8 
            )
        )
        print("   ✅ Brain Connected (Online).")

    def get_greeting(self):
        try:
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
                    
                    # --- NEW INTELLIGENT DIGESTION ---
                    # 1. If the tool gave information (like Search), read and summarize it.
                    if tool_name in ["search_google", "read_file", "identify_song", "system_status"]:
                        print(f"   [Brain Logic] Digesting info from {tool_name}...")
                        follow_up_prompt = (
                            f"SYSTEM_OUTPUT: The tool '{tool_name}' returned this data:\n"
                            f"{tool_output}\n\n"
                            f"INSTRUCTION: Summarize this answer for the user professionally and briefly."
                        )
                        final_response = self.chat.send_message(follow_up_prompt)
                        return final_response.text

                    # 2. For simple actions (Volume, Music, Apps), just speak the result.
                    speech_part = text_response.split("ACTION:")[0].strip()
                    
                    if not speech_part:
                        return f"Done. {str(tool_output)}"
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