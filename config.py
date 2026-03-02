import os
from dotenv import load_dotenv

load_dotenv()

# API Keys Configuration
class Config:
    # Groq API (for LLama LLM)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Pinecone (Vector Database)
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = "us-east-1-aws"
    PINECONE_INDEX_NAME = "pakistan-history-rag"
    
    # Tavily (Web Search)
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Embeddings Model
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # LLM Model
    LLM_MODEL = "llama-3.3-70b-versatile" # Groq compatible model
    
    # Similarity Threshold
    SIMILARITY_THRESHOLD = 0.7
    
    # Data paths
    DATA_DIR = "data"
    DATASET_PATH = os.path.join(DATA_DIR, "pakistan_history_dataset.txt")