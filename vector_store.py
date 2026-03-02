from pinecone import Pinecone, ServerlessSpec  # Updated imports
from sentence_transformers import SentenceTransformer
from config import Config
import time

class VectorStoreManager:
    def __init__(self):
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.pinecone_index = None
        self.pinecone_client = None  # New: Pinecone client instance
        self.initialize_pinecone()
    
    def initialize_pinecone(self):
        """Initialize Pinecone connection with new API"""
        try:
            # NEW: Initialize Pinecone client
            self.pinecone_client = Pinecone(
                api_key=Config.PINECONE_API_KEY
            )
            
            # Check if index exists
            existing_indexes = [idx.name for idx in self.pinecone_client.list_indexes()]
            
            # Create index if it doesn't exist
            if Config.PINECONE_INDEX_NAME not in existing_indexes:
                print(f"Creating new Pinecone index: {Config.PINECONE_INDEX_NAME}")
                self.pinecone_client.create_index(
                    name=Config.PINECONE_INDEX_NAME,
                    dimension=384,  # Dimension for all-MiniLM-L6-v2
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"  # Default region
                    )
                )
                time.sleep(1)  # Wait for index to be ready
            
            # Connect to index
            self.pinecone_index = self.pinecone_client.Index(Config.PINECONE_INDEX_NAME)
            print("✅ Pinecone initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Pinecone: {e}")
            # Fallback to local vector store
            self.use_local_store = True
    
    def create_embeddings(self, texts):
        """Create embeddings for texts"""
        return self.embedding_model.encode(texts).tolist()
    
    # def store_documents(self, chunks):
    #     """Store document chunks in vector database"""
    #     if not chunks:
    #         return
        
    #     texts = [chunk["text"] for chunk in chunks]
    #     embeddings = self.create_embeddings(texts)
        
    #     # Prepare vectors for Pinecone
    #     vectors = []
    #     for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    #         vectors.append({
    #             "id": f"chunk_{i}_{hash(chunk['text']) % 10000}",
    #             "values": embedding,
    #             "metadata": {
    #                 "text": chunk["text"],
    #                 "source": chunk["source"],
    #                 "topic": chunk["topic"],
    #                 **chunk.get("metadata", {})
    #             }
    #         })
        
    #     # Upsert to Pinecone in batches (max 100 vectors per batch)
    #     if self.pinecone_index:
    #         batch_size = 100
    #         for i in range(0, len(vectors), batch_size):
    #             batch = vectors[i:i+batch_size]
    #             self.pinecone_index.upsert(vectors=batch)
            
    #         print(f"✅ Stored {len(vectors)} chunks in Pinecone")
    def store_documents(self, chunks):
        """Store document chunks in vector database"""
        if not chunks:
            return
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.create_embeddings(texts)
        
        # Prepare vectors for Pinecone
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Create metadata dictionary with safe access
            metadata = {
                "text": chunk.get("text", ""),
                "source": chunk.get("source", "unknown"),
                # Use get() to avoid KeyError if 'topic' doesn't exist
                "topic": chunk.get("topic", "general"),
                **chunk.get("metadata", {})
            }
            
            vectors.append({
                "id": f"chunk_{i}_{hash(chunk['text']) % 10000}",
                "values": embedding,
                "metadata": metadata
            })
        
        # Upsert to Pinecone
        if self.pinecone_index:
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i+batch_size]
                self.pinecone_index.upsert(vectors=batch)
            print(f"✅ Stored {len(vectors)} chunks in Pinecone")
        

        
    def search_similar(self, query, top_k=5):
        """Search for similar documents"""
        try:
            # Create query embedding
            query_embedding = self.create_embeddings([query])[0]
            
            # Search in Pinecone
            results = self.pinecone_index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Extract relevant information
            matches = []
            if results and hasattr(results, 'matches'):
                for match in results.matches:
                    if match.score >= Config.SIMILARITY_THRESHOLD:
                        matches.append({
                            "text": match.metadata.get("text", ""),
                            "score": match.score,
                            "source": "RAG",
                            "metadata": match.metadata
                        })
            
            return matches
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def get_index_stats(self):
        """Get statistics about the Pinecone index"""
        try:
            if self.pinecone_index:
                stats = self.pinecone_index.describe_index_stats()
                return {
                    "total_vectors": stats.total_vector_count,
                    "index_fullness": stats.index_fullness,
                    "dimension": stats.dimension
                }
            return {}
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {}
    
    def clear_index(self):
        """Clear all vectors from the index"""
        try:
            if self.pinecone_index:
                self.pinecone_index.delete(delete_all=True)
                print("✅ Cleared all vectors from Pinecone index")
        except Exception as e:
            print(f"Error clearing index: {e}")