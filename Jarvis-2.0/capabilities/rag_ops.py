# Jarvis 2.0 - rag_ops.py
import chromadb
from sentence_transformers import SentenceTransformer
import os

class MemoryRAG:
    def __init__(self):
        print("   [Memory] Loading RAG Model (This may take a moment)...")
        # 1. Setup ChromaDB (The Database)
        self.client = chromadb.PersistentClient(path="jarvis_memory_db")
        
        # 2. Setup Embedding Model (The Translator)
        # 'all-MiniLM-L6-v2' is small, fast, and runs locally on your CPU
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 3. Create/Connect to Collection
        self.collection = self.client.get_or_create_collection(
            name="jarvis_facts",
            metadata={"hnsw:space": "cosine"} # Measures similarity
        )
        print("   [Memory] RAG System Online.")

    def save_memory(self, text):
        """Stores a fact permanently."""
        try:
            # Generate a unique ID (simple hash)
            fact_id = str(hash(text))
            
            # Convert text to numbers (embedding)
            vector = self.encoder.encode(text).tolist()
            
            # Add to database
            self.collection.add(
                documents=[text],
                embeddings=[vector],
                ids=[fact_id]
            )
            return f"Memory stored: '{text}'"
        except Exception as e:
            return f"Memory Error: {e}"

    def retrieve_memory(self, query, n_results=1):
        """Finds the most relevant fact for a query."""
        try:
            # Convert query to numbers
            query_vector = self.encoder.encode(query).tolist()
            
            # Search database
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=n_results
            )
            
            # Check if we found anything
            if results['documents'] and results['documents'][0]:
                best_match = results['documents'][0][0]
                return best_match
            else:
                return None
                
        except Exception as e:
            return f"Retrieval Error: {e}"

# Create Instance
rag_engine = MemoryRAG()