"""
Text Processing Utilities
Clean and chunk text for embedding generation
"""
from typing import List, Dict
import re
import tiktoken
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter


class TextProcessor:
    """Process and chunk text for embeddings"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize text processor
        
        Args:
            chunk_size: Size of each text chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing excessive whitespace and special characters
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    def process_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Process multiple documents into chunks
        
        Args:
            documents: List of documents with 'url', 'title', and 'content'
            
        Returns:
            List of processed chunks with metadata
        """
        processed_chunks = []
        
        for doc in documents:
            # Clean the content
            cleaned_content = self.clean_text(doc['content'])
            
            # Skip if content is too short
            if len(cleaned_content) < 100:
                continue
            
            # Chunk the content
            chunks = self.chunk_text(cleaned_content)
            
            # Add metadata to each chunk
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    'text': chunk,
                    'url': doc['url'],
                    'title': doc['title'],
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
        
        return processed_chunks
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Count tokens in text
        
        Args:
            text: Text to count tokens for
            model: Model name for tokenizer
            
        Returns:
            Number of tokens
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except:
            # Fallback to approximate count
            return len(text) // 4


def process_crawled_data(crawled_data: List[Dict[str, str]], 
                        chunk_size: int = 1000, 
                        chunk_overlap: int = 200) -> List[Dict[str, str]]:
    """
    Convenience function to process crawled data
    
    Args:
        crawled_data: List of crawled documents
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of processed chunks
    """
    processor = TextProcessor(chunk_size, chunk_overlap)
    return processor.process_documents(crawled_data)
