import asyncio
import edge_tts

async def test():
    print("Testing connection to Microsoft Edge Servers...")
    try:
        # Simple test with no special chars
        communicate = edge_tts.Communicate("Hello world", "en-US-AriaNeural")
        await communicate.save("test.mp3")
        print("✅ Success! 'test.mp3' was created.")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("👉 TRY THIS: Connect your laptop to a mobile hotspot and try again.")

if __name__ == "__main__":
    asyncio.run(test())