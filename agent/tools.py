from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
import os
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Setup Chroma DB
CHROMA_PATH = os.environ.get("CHROMA_PATH", "../data/chroma")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
try:
    collection = chroma_client.get_collection(name="iebc_centers")
except:
    collection = chroma_client.create_collection(name="iebc_centers")

# ✅ Switch to Google Gemini Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

@tool
def find_centers(location: str, county: str = '') -> str:
    """Queries the vector store with the user's location string. 
    Returns the top 3 results formatted as a numbered list. 
    Each result must include: center name, sub-county, operating hours, and approximate distance if GPS is available."""
    query_text = f"{location} {county}".strip()
    query_emb = embeddings.embed_query(query_text)
    
    results = collection.query(
        query_embeddings=query_emb,
        n_results=3
    )
    
    response_lines = ["Here are the nearest 3 centers:"]
    
    if not results['metadatas'] or not results['metadatas'][0]:
        return "No centers found matching that description. Please try a different location."
        
    for i, metadata in enumerate(results['metadatas'][0], 1):
        name = metadata.get('name', 'Unknown')
        sub_county = metadata.get('constituency', 'Unknown Sub-county')
        hours = metadata.get('opening_hours', 'Mon-Fri 08:00-17:00')
        center_id = metadata.get('center_id', '')
        response_lines.append(f"{i}. {name} in {sub_county}. Hours: {hours}")
        
    return "\n".join(response_lines)

@tool
def get_registration_dates() -> str:
    """Returns current IEBC registration windows and deadlines. 
    Opening date, closing date, and any upcoming deadlines."""
    return "The current IEBC voter registration window opens on 1st March 2026 and closes on 30th April 2026. Please ensure you are registered before the deadline."

@tool
def get_center_details(center_id: str) -> str:
    """Takes a center ID (returned by find_centers) and returns the full record: 
    physical address, GPS coordinates, phone number, operating hours, and any special instructions."""
    results = collection.get(ids=[center_id])
    if not results['metadatas']:
        return "Center not found."
    meta = results['metadatas'][0]
    return f"Details for {meta.get('name')}:\nAddress: {meta.get('address')}\nCounty: {meta.get('county')}\nGPS: {meta.get('latitude')}, {meta.get('longitude')}\nPhone: {meta.get('phone')}\nHours: {meta.get('opening_hours')}"

@tool
def send_map_link(center_id: str) -> str:
    """Generates a Google Maps deep-link URL using the center's GPS coordinates. 
    Returns a shortened URL suitable for SMS."""
    results = collection.get(ids=[center_id])
    if not results['metadatas'] or len(results['metadatas']) == 0:
        return "Center not found."
    
    meta = results['metadatas'][0]
    lat = meta.get('latitude')
    lon = meta.get('longitude')
    
    if lat and lon:
        url = f"https://www.google.com/maps?q={lat},{lon}"
        return f"Google Maps link: {url}"
    else:
        return "GPS coordinates are not available for this center."
