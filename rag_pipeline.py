"""
RAG Pipeline Module
Orchestrate retrieval and generation
"""
from typing import List, Dict, Optional
from openai import OpenAI
import logging
import requests
from sentence_transformers import SentenceTransformer
from vector_db import VectorDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGPipeline:
    """Retrieval Augmented Generation pipeline"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 db_path: str = "./data/chroma_db",
                 collection_name: str = "support_docs",
                 embedding_model: str = "text-embedding-ada-002",
                 llm_model: str = "gpt-3.5-turbo",
                 max_tokens: int = 500,
                 temperature: float = 0.7,
                 top_k: int = 3,
                 use_ollama: bool = False,
                 ollama_model: str = "llama3.2"):
        """
        Initialize RAG pipeline
        
        Args:
            api_key: OpenAI API key (optional if using Ollama)
            db_path: Path to vector database
            collection_name: Name of the collection
            embedding_model: Embedding model to use
            llm_model: LLM model for generation
            max_tokens: Maximum tokens for generation
            temperature: Temperature for generation
            top_k: Number of documents to retrieve
            use_ollama: Use local Ollama instead of OpenAI
            ollama_model: Ollama model name
        """
        self.vector_db = VectorDatabase(db_path, collection_name)
        self.llm_model = llm_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_k = top_k
        self.use_ollama = use_ollama
        self.ollama_model = ollama_model
        
        # Initialize embeddings
        if use_ollama or not api_key or api_key == "your_openai_api_key_here":
            logger.info("Using local sentence-transformers for embeddings")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_local_embeddings = True
        else:
            logger.info("Using OpenAI for embeddings")
            from embeddings import EmbeddingGenerator
            self.embedding_generator = EmbeddingGenerator(api_key, embedding_model)
            self.use_local_embeddings = False
        
        # Initialize LLM
        if use_ollama:
            logger.info(f"Using Ollama model: {ollama_model}")
            self.ollama_url = "http://localhost:11434/api/generate"
        else:
            if api_key and api_key != "your_openai_api_key_here":
                self.client = OpenAI(api_key=api_key)
            else:
                logger.warning("No valid OpenAI API key provided")
                self.client = None
    
    def retrieve_relevant_context(self, query: str) -> List[Dict[str, str]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query
            
        Returns:
            List of relevant documents
        """
        # Generate query embedding
        if self.use_local_embeddings:
            query_embedding = self.embedding_model.encode(query).tolist()
        else:
            query_embedding = self.embedding_generator.generate_query_embedding(query)
        
        # Retrieve relevant documents
        documents = self.vector_db.get_relevant_documents(query_embedding, self.top_k)
        
        return documents
    
    def generate_answer(self, query: str, context_documents: List[Dict[str, str]]) -> str:
        """
        Generate answer using retrieved context
        
        Args:
            query: User query
            context_documents: Retrieved context documents
            
        Returns:
            Generated answer
        """
        # Build context from retrieved documents
        context = "\n\n".join([
            f"Document {i+1} (Source: {doc['title']}):\n{doc['text']}"
            for i, doc in enumerate(context_documents)
        ])
        
        # Create prompt
        system_prompt = """You are a helpful support assistant. Answer the user's question based ONLY on the provided context. 
If the answer cannot be found in the context, say "I don't have enough information to answer that question based on the available documentation."
Always cite the source document title when providing information."""
        
        user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""
        
        # Generate response using Ollama or OpenAI
        try:
            if self.use_ollama:
                # Use Ollama
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = requests.post(
                    self.ollama_url,
                    json={
                        "model": self.ollama_model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": self.max_tokens
                        }
                    }
                )
                
                if response.status_code == 200:
                    answer = response.json()['response']
                    return answer
                else:
                    raise Exception(f"Ollama error: {response.status_code} - {response.text}")
            else:
                # Use OpenAI
                if not self.client:
                    raise Exception("No valid API key configured")
                    
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                answer = response.choices[0].message.content
                return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    def answer_question(self, query: str) -> Dict[str, any]:
        """
        Answer a question using RAG
        
        Args:
            query: User question
            
        Returns:
            Dictionary with answer and source documents
        """
        logger.info(f"Processing query: {query}")
        
        # Retrieve relevant context
        context_documents = self.retrieve_relevant_context(query)
        
        if not context_documents:
            return {
                "answer": "I don't have any relevant information to answer your question.",
                "sources": []
            }
        
        # Generate answer
        answer = self.generate_answer(query, context_documents)
        
        # Prepare sources
        sources = [
            {
                "title": doc['title'],
                "url": doc['url'],
                "snippet": doc['text'][:200] + "..." if len(doc['text']) > 200 else doc['text']
            }
            for doc in context_documents
        ]
        
        return {
            "answer": answer,
            "sources": sources
        }
