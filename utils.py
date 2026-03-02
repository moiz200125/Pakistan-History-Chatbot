from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate  # CHANGED THIS LINE
from tavily import TavilyClient
from config import Config
import re

class QueryClassifier:
    """Classify if query is about Pakistan history"""
    
    @staticmethod
    def classify_query(query):
        """Use LLM to determine if query is about Pakistan history"""
        
        classification_prompt = PromptTemplate(
            input_variables=["query"],
            template="""
            Analyze the following query and determine if it is about Pakistan's history.
            Consider topics related to:
            - Pakistan's creation, partition, independence
            - Historical figures of Pakistan (Jinnah, Bhutto, etc.)
            - Wars involving Pakistan (1965, 1971, Kargil)
            - Political history of Pakistan
            - Cultural and social history of Pakistan
            - Historical events in Pakistan
            
            Query: {query}
            
            Respond with ONLY one word: "YES" or "NO"
            
            Answer: """
        )
        
        llm = ChatGroq(
            groq_api_key=Config.GROQ_API_KEY,
            model_name=Config.LLM_MODEL,
            temperature=0
        )
        
        try:
            response = llm.invoke(
                classification_prompt.format(query=query)
            )
            result = response.content.strip().upper()
            return result == "YES"
        except Exception as e:
            print(f"Classification error: {e}")
            # Fallback: check for keywords
            return QueryClassifier.keyword_check(query)
    
    @staticmethod
    def keyword_check(query):
        """Fallback keyword-based classification"""
        pakistan_keywords = [
            'pakistan', 'pakistani', 'jinnah', 'quaid', 'islamabad', 'karachi',
            'lahore', 'partition 1947', 'bangladesh war', 'kashmir',
            'indus', 'pakistan history', 'pakistan historical'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in pakistan_keywords)


class WebSearcher:
    """Handle web search using Tavily"""
    
    def __init__(self):
        self.client = TavilyClient(api_key=Config.TAVILY_API_KEY)
    
    def search(self, query, max_results=3):
        """Search the web for Pakistan history information"""
        try:
            search_results = self.client.search(
                query=f"Pakistan history {query}",
                max_results=max_results,
                search_depth="advanced"
            )
            
            # Extract and format results
            formatted_results = []
            if 'results' in search_results:
                for result in search_results['results']:
                    formatted_results.append({
                        "content": result.get('content', ''),
                        "title": result.get('title', ''),
                        "url": result.get('url', ''),
                        "source": "Web Search"
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Web search error: {e}")
            return []


class AnswerGenerator:
    """Generate answers using LLM"""
    
    @staticmethod
    def generate_answer(query, context, source="RAG"):
        """Generate answer using LLM with context"""
        
        prompt_template = PromptTemplate(
            input_variables=["query", "context", "source"],
            template="""
            You are a helpful assistant specialized in Pakistan's history.
            Answer the question based on the provided context.
            If the context doesn't contain relevant information, say so.
            
            Context Source: {source}
            
            Context:
            {context}
            
            Question: {query}
            
            Provide a comprehensive, accurate answer about Pakistan's history.
            Include relevant dates, figures, and events when applicable.
            
            Answer: """
        )
        
        llm = ChatGroq(
            groq_api_key=Config.GROQ_API_KEY,
            model_name=Config.LLM_MODEL,
            temperature=0.3
        )
        
        try:
            response = llm.invoke(
                prompt_template.format(
                    query=query,
                    context=context,
                    source=source
                )
            )
            return response.content
        except Exception as e:
            print(f"Answer generation error: {e}")
            return "I apologize, but I encountered an error generating the answer."


class ContextFormatter:
    """Format context for LLM"""
    
    @staticmethod
    def format_rag_context(matches):
        """Format RAG search results as context"""
        if not matches:
            return "No relevant context found in knowledge base."
        
        context_parts = []
        for i, match in enumerate(matches, 1):
            context_parts.append(f"[Source {i} - RAG Database]:\n{match['text']}")
        
        return "\n\n".join(context_parts)
    
    @staticmethod
    def format_web_context(web_results):
        """Format web search results as context"""
        if not web_results:
            return "No relevant information found through web search."
        
        context_parts = []
        for i, result in enumerate(web_results, 1):
            context_parts.append(
                f"[Source {i} - Web: {result.get('title', 'Unknown')}]:\n"
                f"{result.get('content', 'No content')}"
            )
        
        return "\n\n".join(context_parts)