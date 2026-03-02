# 🇵🇰 Pakistan History Question-Answering Chatbot

An intelligent NLP-powered chatbot that answers questions about **Pakistan's history** using a combination of **Retrieval-Augmented Generation (RAG)**, **LLM (LLaMA 3 via Groq)**, and **Web Search (Tavily)** with a clean **Gradio** web interface.

---

## 🧠 How It Works

```
User Query
    ↓
[1] Query Classifier (LLM) → Is it about Pakistan history?
    ↓ YES
[2] Vector Search (Pinecone RAG) → Found relevant docs?
    ↓ YES → Generate answer from local knowledge base
    ↓ NO  → Web Search (Tavily) → Generate answer from web
    ↓
[3] Answer Generation (Groq / LLaMA 3)
    ↓
Display with Source Attribution
```

---

## 📁 Project Structure

```
Abdul_BSCS22031_03/
│
├── chatbot.py              # Main chatbot application (Gradio UI + orchestration)
├── config.py               # API keys and global configuration (uses .env)
├── utils.py                # QueryClassifier, WebSearcher, AnswerGenerator, ContextFormatter
├── vector_store.py         # Pinecone vector DB management + embedding with SentenceTransformers
├── dataset_creation.py     # Script to build and organize the Pakistan history dataset
├── create_data_structure.py# Helper to create the data folder structure
├── requirements.txt        # Python dependencies
├── report.md               # Assignment report
└── data/                   # (Generated) Historical text files and chunks
    ├── topics/             # Curated topic files (pre-partition, conflicts, figures, etc.)
    ├── raw_sources/        # Wikipedia articles, history books, official docs
    ├── processed/          # Chunked text and JSON metadata
    ├── metadata/           # Timelines, important dates, bibliography
    └── pakistan_history_dataset.txt
```

---

## 🚀 Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/moiz200125/Pakistan-History-Chatbot.git
cd Pakistan-History-Chatbot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
TAVILY_API_KEY=your_tavily_api_key
```

> **Get your keys from:**
> - Groq: https://console.groq.com
> - Pinecone: https://app.pinecone.io
> - Tavily: https://tavily.com

### 4. Create the data folder (first-time only)
```bash
python dataset_creation.py
```

### 5. Run the chatbot
```bash
python chatbot.py
```

Then open your browser at **http://localhost:7860**

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | LLaMA 3.3 70B via [Groq](https://groq.com) |
| Embeddings | `all-MiniLM-L6-v2` (SentenceTransformers) |
| Vector Database | [Pinecone](https://pinecone.io) |
| Web Search | [Tavily](https://tavily.com) |
| UI Framework | [Gradio](https://gradio.app) |
| LLM Framework | [LangChain](https://langchain.com) |

---

## 💡 Example Questions

- *"Who founded Pakistan and when?"*
- *"What was the Lahore Resolution?"*
- *"Tell me about the 1971 Bangladesh Liberation War"*
- *"Who was Pakistan's first female Prime Minister?"*
- *"When did Pakistan conduct nuclear tests?"*
- *"Explain the Kashmir conflict"*

---

## 📝 Assignment Report

See [`report.md`](./report.md) for the detailed system documentation and evaluation.

---

## ⚠️ Notes

- The chatbot **only answers questions about Pakistan's history**. Off-topic queries are rejected.
- Make sure all 3 API keys are set before running.
- The `data/` folder is excluded from the repo (gitignored). Run `dataset_creation.py` to generate it locally.
