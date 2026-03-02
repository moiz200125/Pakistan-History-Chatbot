# import gradio as gr
# from dataset_creation import PakistanHistoryDataset
# from vector_store import VectorStoreManager
# from utils import QueryClassifier, WebSearcher, AnswerGenerator, ContextFormatter
# from config import Config
# import os

# class PakistanHistoryChatbot:
#     def __init__(self):
#         # Initialize components
#         self.dataset_manager = PakistanHistoryDataset()
#         self.vector_store = VectorStoreManager()
#         self.web_searcher = WebSearcher()
#         self.query_classifier = QueryClassifier()
        
#         # Create dataset if not exists
#         if not os.path.exists(Config.DATASET_PATH):
#             print("Creating Pakistan history dataset...")
#             os.makedirs(Config.DATA_DIR, exist_ok=True)
#             self.dataset_manager.collect_history_data()
#             self.dataset_manager.save_dataset(Config.DATASET_PATH)
            
#             # Create chunks and store in vector database
#             chunks = self.dataset_manager.chunk_data()
#             self.vector_store.store_documents(chunks)
    
#     def process_query(self, query, history):
#         """Process user query and generate response"""
        
#         # Step 1: Classify query
#         is_pakistan_history = self.query_classifier.classify_query(query)
        
#         if not is_pakistan_history:
#             return "I'm sorry, I only answer questions related to Pakistan's history. Please ask about Pakistan's historical events, figures, or developments.", "Rejected"
        
#         # Step 2: Search in vector database
#         rag_results = self.vector_store.search_similar(query)
        
#         if rag_results:
#             # Use RAG context
#             context = ContextFormatter.format_rag_context(rag_results)
#             answer = AnswerGenerator.generate_answer(query, context, "RAG Database")
#             source = "RAG"
#         else:
#             # Fallback to web search
#             web_results = self.web_searcher.search(query)
            
#             if web_results:
#                 context = ContextFormatter.format_web_context(web_results)
#                 answer = AnswerGenerator.generate_answer(query, context, "Web Search")
#                 source = "Web"
#             else:
#                 answer = "I couldn't find sufficient information to answer your question about Pakistan's history."
#                 source = "No Source"
        
#         # Format final response
#         response = f"{answer}\n\n📚 **Source**: {source}"
        
#         return response, source
    
#     def create_gradio_interface(self):
#         """Create Gradio interface"""
        
#         with gr.Blocks(title="Pakistan History Chatbot", theme=gr.themes.Soft()) as interface:
#             gr.Markdown("# 🇵🇰 Pakistan History Question-Answering Chatbot")
#             gr.Markdown("Ask me anything about Pakistan's history!")
            
#             with gr.Row():
#                 with gr.Column(scale=3):
#                     chatbot = gr.Chatbot(
#                         height=500,
#                         bubble_full_width=False,
#                         show_copy_button=True
#                     )
                    
#                     query_input = gr.Textbox(
#                         label="Your Question",
#                         placeholder="Ask about Pakistan's history...",
#                         lines=2
#                     )
                    
#                     with gr.Row():
#                         submit_btn = gr.Button("Submit", variant="primary")
#                         clear_btn = gr.Button("Clear")
                    
#                     source_display = gr.Textbox(
#                         label="Answer Source",
#                         interactive=False
#                     )
                
#                 with gr.Column(scale=1):
#                     gr.Markdown("### ℹ️ Information")
#                     gr.Markdown("""
#                     **Supported Topics:**
#                     - Pakistan's independence and partition
#                     - Historical figures
#                     - Wars and conflicts
#                     - Political history
#                     - Cultural developments
                    
#                     **How it works:**
#                     1. Checks if query is about Pakistan history
#                     2. Searches knowledge base
#                     3. Falls back to web search if needed
#                     4. Generates answer using LLM
#                     """)
            
#             # Event handlers
#             submit_btn.click(
#                 fn=self.process_query,
#                 inputs=[query_input, chatbot],
#                 outputs=[chatbot, source_display]
#             ).then(
#                 lambda: "", None, query_input
#             )
            
#             clear_btn.click(lambda: None, None, chatbot, queue=False)
            
#             query_input.submit(
#                 fn=self.process_query,
#                 inputs=[query_input, chatbot],
#                 outputs=[chatbot, source_display]
#             ).then(
#                 lambda: "", None, query_input
#             )
        
#         return interface

# def main():
#     # Check for API keys
#     required_keys = ['GROQ_API_KEY', 'PINECONE_API_KEY', 'TAVILY_API_KEY']
#     missing_keys = [key for key in required_keys if not getattr(Config, key, None)]
    
#     if missing_keys:
#         print("⚠️ Missing API keys. Please set the following environment variables:")
#         for key in missing_keys:
#             print(f"   - {key}")
#         print("\nCreate a .env file with these keys or set them in your environment.")
#         return
    
#     # Initialize and run chatbot
#     chatbot = PakistanHistoryChatbot()
#     interface = chatbot.create_gradio_interface()
#     interface.launch(server_name="0.0.0.0", server_port=7860, share=False)

# if __name__ == "__main__":
#     main()

import gradio as gr
#from dataset_creation import PakistanHistoryDataset
from vector_store import VectorStoreManager
from utils import QueryClassifier, WebSearcher, AnswerGenerator, ContextFormatter
from config import Config
import os
import json
import time
import re
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

class EnhancedDataLoader:
    """Enhanced data loader that uses the structured data folder"""
    
    @staticmethod
    def load_all_data_from_folders():
        """Load data from all folders in the data directory"""
        all_data = []
        
        # Check if data directory exists
        if not os.path.exists(Config.DATA_DIR):
            print(f"⚠️ Data directory '{Config.DATA_DIR}' not found!")
            return all_data
        
        print(f"📂 Loading data from '{Config.DATA_DIR}'...")
        
        # 1. Load from topics directory
        topics_path = os.path.join(Config.DATA_DIR, "topics")
        if os.path.exists(topics_path):
            for category in os.listdir(topics_path):
                category_path = os.path.join(topics_path, category)
                if os.path.isdir(category_path):
                    for file in os.listdir(category_path):
                        if file.endswith('.txt'):
                            file_path = os.path.join(category_path, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Extract title
                                lines = content.split('\n')
                                title = lines[0] if lines else file.replace('.txt', '').replace('_', ' ').title()
                                
                                all_data.append({
                                    'text': content,
                                    'title': title,
                                    'category': category,
                                    'filename': file,
                                    'source': f'topics/{category}'
                                })
                            except Exception as e:
                                print(f"  ⚠️ Error loading {file_path}: {e}")
        
        # 2. Load from raw_sources directory
        raw_sources_path = os.path.join(Config.DATA_DIR, "raw_sources")
        if os.path.exists(raw_sources_path):
            for source_type in os.listdir(raw_sources_path):
                source_path = os.path.join(raw_sources_path, source_type)
                if os.path.isdir(source_path):
                    for file in os.listdir(source_path):
                        if file.endswith('.txt'):
                            file_path = os.path.join(source_path, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Extract title from first line
                                lines = content.split('\n')
                                title = lines[0] if lines else file.replace('.txt', '').replace('_', ' ').title()
                                
                                all_data.append({
                                    'text': content,
                                    'title': title,
                                    'category': f'raw_{source_type}',
                                    'filename': file,
                                    'source': f'raw_sources/{source_type}'
                                })
                            except Exception as e:
                                print(f"  ⚠️ Error loading {file_path}: {e}")
        
        # 3. Load main dataset file
        if os.path.exists(Config.DATASET_PATH):
            try:
                with open(Config.DATASET_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split into topics
                topic_sections = re.split(r'TOPIC #\d+: ', content)
                for i, section in enumerate(topic_sections[1:], 1):  # Skip first empty
                    if section.strip():
                        lines = section.split('\n')
                        title = lines[0].strip()
                        text = '\n'.join(lines[2:]).strip()  # Skip category line
                        
                        # Find category
                        category_match = re.search(r'CATEGORY: (\w+)', section)
                        category = category_match.group(1) if category_match else 'main_dataset'
                        
                        all_data.append({
                            'text': text[:3000],  # Limit size
                            'title': title,
                            'category': category,
                            'filename': f'topic_{i}.txt',
                            'source': 'main_dataset'
                        })
            except Exception as e:
                print(f"  ⚠️ Error loading main dataset: {e}")
        
        print(f"  ✅ Loaded {len(all_data)} data items from data folder")
        return all_data
    
    @staticmethod
    def chunk_data(data_items, chunk_size=400, overlap=50):
        """Chunk data into smaller pieces for vector storage"""
        chunks = []
        
        for item in data_items:
            text = item['text']
            # Split into sentences for better chunking
            sentences = re.split(r'[.!?]+', text)
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                sentence_length = len(sentence.split())
                
                if current_length + sentence_length > chunk_size and current_chunk:
                    # Save current chunk
                    chunk_text = ' '.join(current_chunk)
                    if len(chunk_text.split()) > 20:  # Only add chunks with enough content
                        chunks.append({
                            'text': chunk_text,
                            'title': item['title'],
                            'category': item['category'],
                            'source': item['source'],
                            'metadata': {
                                'filename': item['filename'],
                                'chunk_index': len(chunks),
                                'timestamp': time.strftime('%Y-%m-%d')
                            }
                        })
                    
                    # Start new chunk with overlap
                    overlap_sentences = int(len(current_chunk) * overlap / 100)
                    current_chunk = current_chunk[-overlap_sentences:] if overlap_sentences > 0 else []
                    current_length = sum(len(s.split()) for s in current_chunk)
                
                current_chunk.append(sentence)
                current_length += sentence_length
            
            # Add last chunk
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text.split()) > 20:
                    chunks.append({
                        'text': chunk_text,
                        'title': item['title'],
                        'category': item['category'],
                        'source': item['source'],
                        'metadata': {
                            'filename': item['filename'],
                            'chunk_index': len(chunks),
                            'timestamp': time.strftime('%Y-%m-%d')
                        }
                    })
        
        print(f"  ✅ Created {len(chunks)} chunks from data")
        return chunks

class EnhancedVectorStore(VectorStoreManager):
    """Enhanced vector store with additional functionality"""
    
    def __init__(self):
        super().__init__()
        self.initialize_with_data_if_needed()
    
    def initialize_with_data_if_needed(self):
        """Check if Pinecone has data, load if empty"""
        try:
            stats = self.get_index_stats()
            if stats.get("total_vectors", 0) == 0:
                print("📥 Pinecone index is empty. Loading data from folders...")
                self.load_data_to_pinecone()
            else:
                print(f"✅ Pinecone has {stats.get('total_vectors', 0)} vectors")
        except Exception as e:
            print(f"⚠️ Error checking Pinecone: {e}. Loading data...")
            self.load_data_to_pinecone()
    
    def load_data_to_pinecone(self):
        """Load data from folder and store in Pinecone"""
        print("🔄 Loading data from data folder into Pinecone...")
        
        # Load data
        documents = self.load_data_from_folder()
        print(f"  ✅ Loaded {len(documents)} data items from data folder")
        
        # Create chunks
        chunks = self.create_chunks(documents)
        print(f"  ✅ Created {len(chunks)} chunks from data")
        
        # Add topic field if missing
        for chunk in chunks:
            if "topic" not in chunk:
                chunk["topic"] = "general"
        
        # Store in Pinecone
        self.store_documents(chunks)
        print("✅ Data loaded into Pinecone successfully!")
    
    def load_data_from_folder(self, folder_path="data"):
        """Load documents from the data folder"""
        import os
        import json
        
        documents = []
        
        print(f"📂 Loading data from '{folder_path}'...")
        
        if not os.path.exists(folder_path):
            print(f"  ⚠️ Folder '{folder_path}' not found")
            return documents
        
        # Walk through all files in the data folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('.txt', '.json', '.md')):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Skip empty files
                        if not content.strip():
                            continue
                        
                        # Create document object
                        relative_path = os.path.relpath(file_path, folder_path)
                        document = {
                            "content": content[:5000],  # Limit content size
                            "source": relative_path,
                            "file": file,
                            "folder": os.path.basename(root),
                            "topic": os.path.basename(root),  # Use folder name as topic
                            "metadata": {
                                "path": relative_path,
                                "size": len(content)
                            }
                        }
                        
                        documents.append(document)
                        print(f"  📄 Loaded: {relative_path}")
                        
                    except Exception as e:
                        print(f"  ❌ Error loading {file_path}: {e}")
        
        return documents
    
    def create_chunks(self, documents, chunk_size=500):
        """Create text chunks from documents"""
        chunks = []
        
        for doc in documents:
            text = doc.get("content", "")
            if not text:
                continue
            
            # Split text into chunks
            words = text.split()
            for i in range(0, len(words), chunk_size):
                chunk_text = " ".join(words[i:i + chunk_size])
                
                chunks.append({
                    "text": chunk_text,
                    "source": doc.get("source", "data_folder"),
                    "topic": doc.get("topic", "general"),
                    "metadata": {
                        "original_length": len(text),
                        "chunk_index": i // chunk_size,
                        "file": doc.get("file", "unknown"),
                        "folder": doc.get("folder", "unknown")
                    }
                })
        
        return chunks
    
    def initialize_local_fallback(self):
        """Initialize local fallback vector store"""
        print("🔄 Initializing local vector store fallback...")
        # This would be ChromaDB or similar local store
        # For now, we'll just use Pinecone if available
        pass
    
    def create_sample_data(self):
        """Create sample data if no data exists"""
        return [{
            'text': """Pakistan was created on August 14, 1947, as a result of the partition of British India. 
            Muhammad Ali Jinnah became its first Governor-General. The Lahore Resolution of 1940 laid the 
            foundation for a separate Muslim state. Pakistan consists of four provinces: Punjab, Sindh, 
            Khyber Pakhtunkhwa, and Balochistan, along with territories like Gilgit-Baltistan and 
            Azad Jammu & Kashmir.""",
            'title': 'Creation of Pakistan',
            'category': 'basic_history',
            'filename': 'sample.txt',
            'source': 'sample'
        }]
    
    def search_enhanced(self, query, top_k=5, similarity_threshold=None):
        """Enhanced search with better filtering"""
        if similarity_threshold is None:
            similarity_threshold = Config.SIMILARITY_THRESHOLD
        
        try:
            # Search in Pinecone
            matches = self.search_similar(query, top_k)
            
            # Apply additional filtering
            filtered_matches = []
            for match in matches:
                # Check if match is relevant to Pakistan history
                if self.is_pakistan_related(match.get('text', '')):
                    # Adjust score based on relevance
                    adjusted_score = match.get('score', 0)
                    
                    # Boost score for recent history (post-1947)
                    if self.contains_recent_history(match.get('text', '')):
                        adjusted_score *= 1.1
                    
                    if adjusted_score >= similarity_threshold:
                        match['score'] = adjusted_score
                        filtered_matches.append(match)
            
            return filtered_matches
        
        except Exception as e:
            print(f"Enhanced search error: {e}")
            return []

    @staticmethod
    def is_pakistan_related(text):
        """Check if text is related to Pakistan"""
        pakistan_keywords = [
            'pakistan', 'pakistani', 'jinnah', 'quaid', 'islamabad',
            'karachi', 'lahore', 'partition', 'bangladesh', 'kashmir',
            'indus', 'pakistan history', 'pakistan historical', '1971',
            '1947', 'indo-pak', 'bhutto', 'zia', 'kargil'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in pakistan_keywords)
    
    @staticmethod
    def contains_recent_history(text):
        """Check if text contains recent history (post-1947)"""
        recent_years = [str(year) for year in range(1947, 2025)]
        text_lower = text.lower()
        return any(year in text_lower for year in recent_years)

class PakistanHistoryChatbot:
    def __init__(self):
        print("🚀 Initializing Pakistan History Chatbot...")
        
        # Initialize components
        print("📚 Loading knowledge base...")
        #self.dataset_manager = PakistanHistoryDataset()
        self.vector_store = EnhancedVectorStore()
        self.web_searcher = WebSearcher()
        self.query_classifier = QueryClassifier()
        
        # Check if dataset exists, if not use data folder
        if not os.path.exists(Config.DATASET_PATH):
            print("⚠️ Main dataset file not found. Using data folder instead...")
            print(f"   Data will be loaded from: {Config.DATA_DIR}")
        
        print("✅ Chatbot initialization complete!")
        print(f"📊 Knowledge base: {Config.DATA_DIR}")
        print(f"🔍 Similarity threshold: {Config.SIMILARITY_THRESHOLD}")
        print(f"🤖 LLM Model: {Config.LLM_MODEL}")
    
    def process_query(self, query, history):
        """Process user query and generate response"""
        
        print(f"\n🔍 Processing query: '{query}'")
        
        # Step 1: Classify query
        is_pakistan_history = self.query_classifier.classify_query(query)
        
        if not is_pakistan_history:
            rejection_msg = "I'm sorry, I only answer questions related to Pakistan's history. Please ask about Pakistan's historical events, figures, or developments."
            print("  ❌ Query rejected: Not Pakistan history")
            return rejection_msg, "Rejected", history
        
        # Step 2: Search in vector database
        print("  🔎 Searching knowledge base...")
        rag_results = self.vector_store.search_enhanced(query)
        
        if rag_results:
            # Use RAG context
            context = ContextFormatter.format_rag_context(rag_results)
            answer = AnswerGenerator.generate_answer(query, context, "RAG Database")
            source = "RAG (Local Knowledge Base)"
            print(f"  ✅ Found {len(rag_results)} relevant documents")
            
            # Log the search results
            print(f"  📊 Top match similarity: {rag_results[0].get('score', 0):.3f}")
        else:
            # Fallback to web search
            print("  🌐 No relevant local results. Searching web...")
            web_results = self.web_searcher.search(query)
            
            if web_results:
                context = ContextFormatter.format_web_context(web_results)
                answer = AnswerGenerator.generate_answer(query, context, "Web Search")
                source = "Web Search"
                print(f"  ✅ Found {len(web_results)} web results")
            else:
                answer = "I couldn't find sufficient information to answer your question about Pakistan's history in either my knowledge base or through web search."
                source = "No source found"
                print("  ⚠️ No information found")
        
        # Format final response
        response = f"{answer}\n\n📚 **Source**: {source}"
        
        # Update history
        history.append((query, response))
        
        return response, source, history
    
    def create_gradio_interface(self):
        """Create Gradio interface"""
        
        with gr.Blocks(title="Pakistan History Chatbot", theme=gr.themes.Soft()) as interface:
            gr.Markdown("""
            # 🇵🇰 Pakistan History Question-Answering Chatbot
            ### Intelligent Assistant for Pakistan's Historical Knowledge
            
            *Powered by RAG (Retrieval-Augmented Generation) + LLM + Web Search*
            """)
            
            with gr.Row():
                with gr.Column(scale=3):
                    # Chat display
                    chatbot = gr.Chatbot(
                        label="Conversation History",
                        height=500,
                        bubble_full_width=False,
                        show_copy_button=True
                        #avatar_images=(None, "🇵🇰")
                    )
                    
                    # Query input
                    with gr.Row():
                        query_input = gr.Textbox(
                            label="Ask about Pakistan's History",
                            placeholder="Example: Who was Muhammad Ali Jinnah and what was his role in Pakistan's creation?",
                            lines=3,
                            scale=9,
                            container=False
                        )
                        
                        submit_btn = gr.Button("Ask", variant="primary", scale=1, size="lg")
                    
                    # Source and status
                    with gr.Row():
                        source_display = gr.Textbox(
                            label="Information Source",
                            interactive=False,
                            scale=3
                        )
                        
                        clear_btn = gr.Button("Clear Chat", scale=1, variant="secondary")
                
                with gr.Column(scale=1):
                    # Information panel
                    gr.Markdown("### 📖 How It Works")
                    gr.Markdown("""
                    **1. Query Classification**  
                    Checks if your question is about Pakistan history
                    
                    **2. Knowledge Search**  
                    Searches through 100+ historical documents
                    
                    **3. Web Search (if needed)**  
                    Falls back to current information
                    
                    **4. Answer Generation**  
                    Uses AI to create comprehensive answers
                    """)
                    
                    # Data statistics
                    gr.Markdown("### 📊 Knowledge Base")
                    gr.Markdown(f"""
                    **Data Source:** {Config.DATA_DIR}
                    **Topics Covered:**
                    • Pre-Partition History
                    • Post-Independence Events
                    • Military Conflicts
                    • Political Figures
                    • Constitutional Development
                    • Economic History
                    """)
                    
                    # Example questions
                    gr.Markdown("### 💡 Example Questions")
                    examples = gr.Examples(
                        examples=[
                            ["Who founded Pakistan and when?"],
                            ["What was the Lahore Resolution?"],
                            ["Tell me about the 1971 Bangladesh Liberation War"],
                            ["Who was Pakistan's first female Prime Minister?"],
                            ["When did Pakistan conduct nuclear tests?"],
                            ["Explain the Kashmir conflict"],
                            ["What is the Two-Nation Theory?"],
                            ["Who was Allama Muhammad Iqbal?"],
                            ["Describe Pakistan's constitutional history"],
                            ["What were the major Indo-Pakistan wars?"]
                        ],
                        inputs=query_input,
                        label="Try these:",
                        examples_per_page=5
                    )
            
            # Event handlers
            def respond(query, history):
                if not query.strip():
                    return "", "No query", history
                
                response, source, new_history = self.process_query(query, history)
                return "", source, new_history
            
            # Button click
            submit_btn.click(
                fn=respond,
                inputs=[query_input, chatbot],
                outputs=[query_input, source_display, chatbot]
            )
            
            # Enter key
            query_input.submit(
                fn=respond,
                inputs=[query_input, chatbot],
                outputs=[query_input, source_display, chatbot]
            )
            
            # Clear button
            clear_btn.click(
                fn=lambda: ([], ""),
                outputs=[chatbot, source_display]
            )
            
            # Footer
            gr.Markdown("---")
            gr.Markdown("""
            <div style='text-align: center; color: #666; font-size: 0.9em;'>
            <p>This chatbot specializes in Pakistan's history using AI-powered retrieval and generation.</p>
            <p>Accuracy may vary. Verify important information from multiple sources.</p>
            </div>
            """)
        
        return interface

def check_api_keys():
    """Check if required API keys are available"""
    print("\n🔑 Checking API keys...")
    
    missing_keys = []
    
    if not Config.GROQ_API_KEY:
        missing_keys.append("GROQ_API_KEY")
        print("  ⚠️ GROQ_API_KEY not found")
    else:
        print("  ✅ GROQ_API_KEY: Found")
    
    if not Config.PINECONE_API_KEY:
        missing_keys.append("PINECONE_API_KEY")
        print("  ⚠️ PINECONE_API_KEY not found")
    else:
        print("  ✅ PINECONE_API_KEY: Found")
    
    if not Config.TAVILY_API_KEY:
        missing_keys.append("TAVILY_API_KEY")
        print("  ⚠️ TAVILY_API_KEY not found")
    else:
        print("  ✅ TAVILY_API_KEY: Found")
    
    if missing_keys:
        print(f"\n⚠️ Missing API keys: {', '.join(missing_keys)}")
        print("Some features may not work correctly.")
        print("Add missing keys to your .env file:")
        for key in missing_keys:
            print(f"   {key}=your_key_here")
        print("\nThe chatbot will attempt to run with available components.")
    
    return len(missing_keys)

def main():
    """Main function to run the chatbot"""
    
    print("\n" + "="*70)
    print("PAKISTAN HISTORY QUESTION-ANSWERING CHATBOT")
    print("="*70)
    
    # Check API keys
    api_check = check_api_keys()
    
    # Check data folder
    if not os.path.exists(Config.DATA_DIR):
        print(f"\n⚠️ Data directory '{Config.DATA_DIR}' not found!")
        print("Please run 'python create_datastructure.py' first to create the data folder.")
        print("Alternatively, the chatbot will use its internal dataset.")
        create_data = input("\nDo you want to create the data folder now? (y/n): ")
        if create_data.lower() == 'y':
            try:
                import create_datastructure
                create_datastructure.main()
            except ImportError:
                print("❌ Could not import create_datastructure.py")
                print("Make sure the file exists in the current directory.")
                return
    
    # Initialize and run chatbot
    try:
        chatbot = PakistanHistoryChatbot()
        interface = chatbot.create_gradio_interface()
        
        print("\n" + "="*70)
        print("✅ CHATBOT READY!")
        print("="*70)
        print("\n🌐 Opening web interface at: http://localhost:7860")
        print("📚 Knowledge base: data/ folder")
        print("🤖 LLM: Groq with LLaMA 3")
        print("🔍 Search: Pinecone + Tavily")
        print("\n💡 Try asking about Pakistan's history!")
        print("🛑 Press Ctrl+C to stop the server")
        print("="*70)
        
        # Launch interface
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            favicon_path=None,
            auth=None,
            auth_message=None,
            prevent_thread_lock=False,
            show_api=False
        )
    
    except Exception as e:
        print(f"\n❌ Error starting chatbot: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check if all API keys are set in .env file")
        print("2. Make sure dependencies are installed: pip install -r requirements.txt")
        print("3. Run 'python create_datastructure.py' to create data folder")
        print("4. Check internet connection (required for API calls)")
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()