import os
from google import genai
from dotenv import load_dotenv

load_dotenv(dotenv_path='config/.env')
api_key = os.getenv('GEMINI_API_KEY')

print(f"Key Found: {'YES' if api_key else 'NO'}")

try:
    client = genai.Client(api_key=api_key)
    # The models list returns an iterator of Model objects
    all_models = list(client.models.list())
    print(f"Total Models Found: {len(all_models)}")
    for m in all_models:
        print(f"Model: {m.name} | Display: {m.display_name}")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
