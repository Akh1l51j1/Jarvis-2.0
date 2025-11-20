import google.generativeai as genai
import config

print("🔍 Checking available models for your API Key...")
try:
    genai.configure(api_key=config.GEMINI_API_KEY)
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"   - {m.name}")
            available_models.append(m.name)
            
    if not available_models:
        print("\n❌ No models found! Check if your API Key is active.")
except Exception as e:
    print(f"\n❌ Error: {e}")