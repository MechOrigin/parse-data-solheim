import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_api_key(api_key):
    print(f"\nTesting API key: {api_key[:10]}...")
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    try:
        # List available models first
        print("Available models:")
        for m in genai.list_models():
            print(f"- {m.name}")
        
        # Try to use the model
        print("\nTesting content generation:")
        model = genai.GenerativeModel('models/gemini-1.5-pro')  # Updated model name
        response = model.generate_content("Hello, are you working?")
        print("Success! Response:", response.text)
        return True
    except Exception as e:
        print("Error:", str(e))
        return False

def main():
    # Load environment variables
    load_dotenv()
    
    # Get all API keys
    api_keys = [
        os.getenv('GEMINI_API_KEY'),
        os.getenv('GEMINI_API_KEY_2'),
        os.getenv('GEMINI_API_KEY_3')
    ]
    
    # Test each key
    for i, key in enumerate(api_keys, 1):
        if key:
            print(f"\nTesting API Key {i}:")
            if test_api_key(key):
                print(f"\nAPI Key {i} is working!")
                return
    
    print("\nNo working API keys found.")

if __name__ == "__main__":
    main() 