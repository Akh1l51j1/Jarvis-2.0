import os
import base64
from groq import Groq
import sys

# Add root directory to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

class VisionOps:
    def __init__(self):
        print("   [Vision] Initializing Groq Client...")
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.2-90b-vision-preview"

    def analyze_image(self, image_path, prompt="Describe this image in detail."):
        print(f"   [Vision] Analyzing: {image_path}")
        
        if not os.path.exists(image_path):
            return "Error: Image file not found."

        try:
            # 1. Encode Image to Base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # 2. Send to Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                model=self.model,
            )

            return chat_completion.choices[0].message.content

        except Exception as e:
            return f"Vision Error: {e}"

vision_engine = VisionOps()