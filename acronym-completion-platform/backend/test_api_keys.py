import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

async def test_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = await model.generate_content_async("Hello, are you working?")
        print(f"API Key {api_key[:10]}... worked!")
        return True
    except Exception as e:
        print(f"API Key {api_key[:10]}... failed: {str(e)}")
        return False

async def main():
    load_dotenv()
    
    # Test all three API keys
    api_keys = [
        os.getenv('GEMINI_API_KEY'),
        os.getenv('GEMINI_API_KEY_2'),
        os.getenv('GEMINI_API_KEY_3')
    ]
    
    for api_key in api_keys:
        if api_key:
            await test_api_key(api_key)

def test_api_key_loading():
    # Test environment variables
    os.environ["GEMINI_API_KEY_1"] = "test_key_1"
    os.environ["GEMINI_API_KEY_2"] = "test_key_2"
    os.environ["GEMINI_API_KEY_3"] = "test_key_3"
    os.environ["GEMINI_API_KEY_4"] = "test_key_4"
    os.environ["GEMINI_API_KEY_5"] = "test_key_5"
    
    api_key_manager = APIKeyManager()
    assert len(api_key_manager.api_keys) == 5
    assert "test_key_1" in api_key_manager.api_keys
    assert "test_key_2" in api_key_manager.api_keys
    assert "test_key_3" in api_key_manager.api_keys
    assert "test_key_4" in api_key_manager.api_keys
    assert "test_key_5" in api_key_manager.api_keys

if __name__ == "__main__":
    asyncio.run(main()) 