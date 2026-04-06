import os
try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    pass

class PineconeStore:
    def __init__(self):
        self.api_key = os.environ.get("PINECONE_API_KEY")
        self.index_name = os.environ.get("PINECONE_INDEX", "iebc-centers")
        if self.api_key:
            self.pc = Pinecone(api_key=self.api_key)
            if self.index_name not in self.pc.list_indexes().names():
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
            self.index = self.pc.Index(self.index_name)
    
    def query(self, vector, top_k=3):
        if not self.api_key:
            return None
        res = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
        return res

if __name__ == "__main__":
    print("Pinecone store configuration loaded for production use.")
