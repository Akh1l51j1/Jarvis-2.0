import chromadb
from sentence_transformers import SentenceTransformer
import os
from datetime import datetime

class MemoryRAG:
    def __init__(self):
        print("   [Memory] Loading RAG Model...")
        self.client = chromadb.PersistentClient(path="jarvis_memory_db")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = self.client.get_or_create_collection(
            name="jarvis_facts",
            metadata={"hnsw:space": "cosine"}
        )
        print("   [Memory] RAG System Online.")

    def save_memory(self, text):
        """Stores a fact with a timestamp."""
        try:
            timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            import time
            fact_id = str(hash(text + str(time.time())))
            vector = self.encoder.encode(text).tolist()
            
            self.collection.add(
                documents=[text],
                embeddings=[vector],
                ids=[fact_id],
                metadatas=[{"created": timestamp}]
            )
            return f"Memory stored: '{text}' (Date: {timestamp})"
        except Exception as e:
            return f"Memory Error: {e}"

    def retrieve_memory(self, query, n_results=3):
        """Finds facts safely, handling old memories without dates."""
        try:
            query_vector = self.encoder.encode(query).tolist()
            
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=n_results
            )
            
            if results['documents'] and results['documents'][0]:
                response = "Found these memories:\n"
                
                # Loop through results
                for i, doc in enumerate(results['documents'][0]):
                    # --- SAFETY CHECK FOR OLD MEMORIES ---
                    date = "Unknown Date (Old Memory)"
                    
                    # Check if metadata exists and is not None
                    if results['metadatas'] and results['metadatas'][0]:
                        meta_entry = results['metadatas'][0][i]
                        # Check if the specific entry is not None
                        if meta_entry:
                            date = meta_entry.get('created', date)
                            
                    response += f"- {doc} (Recorded: {date})\n"
                    
                return response
            else:
                return "No relevant memories found."
                
        except Exception as e:
            return f"Retrieval Error: {e}"

    def delete_memory(self, query):
        """Finds the memory matching the query and deletes it."""
        try:
            query_vector = self.encoder.encode(query).tolist()
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=1
            )
            
            if results['ids'] and results['ids'][0]:
                best_id = results['ids'][0][0]
                best_text = results['documents'][0][0]
                self.collection.delete(ids=[best_id])
                return f"I have deleted the memory: '{best_text}'"
            else:
                return f"I couldn't find a memory matching '{query}' to delete."
                
        except Exception as e:
            return f"Deletion Error: {e}"

# Create Instance
rag_engine = MemoryRAG()