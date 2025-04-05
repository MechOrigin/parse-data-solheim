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

if __name__ == "__main__":
    asyncio.run(main()) 