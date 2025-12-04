"""
Configuration module for RAG Q&A Support Bot
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str = "your_openai_api_key_here"
    
    # Vector Database Configuration
    chroma_db_path: str = "./data/chroma_db"
    collection_name: str = "support_docs"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Crawling Configuration
    max_crawl_depth: int = 3
    max_pages: int = 50
    base_url: Optional[str] = None
    
    # Embedding Configuration
    embedding_model: str = "text-embedding-ada-002"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # LLM Configuration
    use_ollama: bool = True  # Set to True to use free local Ollama
    ollama_model: str = "llama3.2"
    llm_model: str = "gpt-3.5-turbo"
    max_tokens: int = 500
    temperature: float = 0.7
    top_k_results: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
