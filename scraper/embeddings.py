import os
import uuid
import datetime
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize Chroma client
CHROMA_PATH = os.environ.get("CHROMA_PATH", "../data/chroma")
os.makedirs(CHROMA_PATH, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection_name = "iebc_centers"

try:
    collection = chroma_client.get_collection(name=collection_name)
except:
    collection = chroma_client.create_collection(name=collection_name)

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def upsert_centers(centers_data: list):
    if not centers_data:
        return
        
    ids = []
    documents = []
    metadatas = []
    
    for c in centers_data:
        center_id = c.get("center_id", str(uuid.uuid4()))
        c["center_id"] = center_id
        
        text_rep = f"{c.get('name', '')}, {c.get('ward', '')}, {c.get('constituency', '')}, {c.get('county', '')}, {c.get('address', '')}"
        
        ids.append(center_id)
        documents.append(text_rep)
        c_filtered = {k: (str(v) if v is not None else "") for k, v in c.items()}
        metadatas.append(c_filtered)
        
    embeddings = model.encode(documents).tolist()
    
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )
    print(f"Upserted {len(ids)} centers into Chroma DB.")
