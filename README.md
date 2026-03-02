🇵🇰 Pakistan History QA Chatbot — RAG + LLM + Web Search
An NLP-based intelligent chatbot that answers questions exclusively about Pakistan's history. Built as part of a university NLP assignment, this system combines multiple AI techniques to give accurate, hallucination-minimized responses.

🗃️ Dataset Creation
A custom Pakistan history dataset was built from scratch using:
Wikipedia scraping (

wikipedia
, wikipedia-api, BeautifulSoup4) for articles on Partition of India, Muhammad Ali Jinnah, Indo-Pak Wars, Kashmir, Kargil, etc.
Manually curated text files covering: Pre-Partition history, Post-Independence events, Military coups, Constitutional history, Key political figures (Jinnah, Benazir Bhutto, Imran Khan, etc.)
Official document summaries (Constitution of 1973, National Assembly history)
Metadata files: timelines (JSON), important dates, bibliography
Text is organized into a folder structure: data/topics/, data/raw_sources/, data/processed/, data/metadata/
🔢 Embeddings & Vector Database
All historical text is chunked (400–500 words per chunk with 50-word overlap) to preserve context
Each chunk is converted into a 384-dimensional embedding using sentence-transformers (all-MiniLM-L6-v2)
Embeddings are stored and indexed in Pinecone (cloud-based vector database) with cosine similarity search
On startup, the system auto-checks if Pinecone is populated — and loads data if needed
🛡️ Hallucination Avoidance
Query Classification (Step 1): Before searching anything, an LLM prompt (Groq/LLaMA 3) checks if the question is actually about Pakistan's history. Off-topic queries are rejected immediately with a clear message — no answer is hallucinated for irrelevant questions.
Fallback keyword check: If the Groq API fails, a keyword list (

pakistan
, jinnah, partition, etc.) acts as a safety net classifier.
RAG (Retrieval-Augmented Generation): The LLM only answers based on the retrieved context chunks — not from its training memory alone. This grounds answers in real documents.
Similarity threshold (0.7): Vector search results below the threshold are discarded, preventing low-quality context from being fed to the LLM.
Source attribution: Every answer shows its source — RAG (Local Knowledge Base) or Web Search — so the user knows how the answer was generated.
Web search fallback (Tavily): If Pinecone returns no relevant results, Tavily performs a live web search scoped to Pakistan history, ensuring up-to-date answers without guessing.
🤖 LLM & Answer Generation
Uses LLaMA 3.3 70B (via Groq API) for both query classification and answer generation
Answers are generated using a structured PromptTemplate (LangChain) that injects retrieved context + source
Temperature 0 for classification (deterministic), 0.3 for answer generation (slight creativity)
🖥️ Interface
Built with Gradio — launches a clean web UI at http://localhost:7860
Features: conversation history, source display, example questions, clear button
