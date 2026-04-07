import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv(dotenv_path="../.env")

def test_gemini_setup():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key or "your_gemini_api_key" in api_key:
        print("❌ GOOGLE_API_KEY is not set or is still a placeholder in .env")
        return

    print("--- Testing Embeddings ---")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector = embeddings.embed_query("Nairobi voter registration")
        print(f"✅ Embeddings working. Vector size: {len(vector)}")
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")

    print("\n--- Testing Chat Model ---")
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        response = llm.invoke("Hello, who are you?")
        print(f"✅ Chat model working. Response: {response.content}")
    except Exception as e:
        print(f"❌ Chat model failed: {e}")

if __name__ == "__main__":
    test_gemini_setup()
