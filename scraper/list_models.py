import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

def list_models():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key or "your_gemini_api_key" in api_key:
        print("❌ GOOGLE_API_KEY is not set or is still a placeholder in .env")
        return

    genai.configure(api_key=api_key)
    print("--- Available Models ---")
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(f"Embedding Model: {m.name}")
        else:
            print(f"Generative Model: {m.name}")

if __name__ == "__main__":
    list_models()
