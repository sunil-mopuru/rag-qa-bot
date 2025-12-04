"""
Text Processing Utilities
Clean and chunk text for embedding generation
"""
from typing import List, Dict
import re
import tiktoken
import uuid
import logging
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        Clean text by removing excessive whitespace, special characters, and noise
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove HTML entities that might have slipped through
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
        text = re.sub(r'&#\d+;', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive whitespace (multiple spaces, tabs, etc.)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'""]', '', text)
        
        # Remove lines with only numbers or symbols
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if line.strip() and not line.strip().isdigit()]
        text = '\n'.join(cleaned_lines)
        
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
        Process multiple documents into chunks with overlap
        
        Args:
            documents: List of documents with 'url', 'title', and 'content'
            
        Returns:
            List of processed chunks with complete metadata
        """
        processed_chunks = []
        
        logger.info(f"Processing {len(documents)} documents for chunking...")
        logger.info(f"Chunk size: {self.chunk_size}, Overlap: {self.chunk_overlap}\n")
        
        for doc_idx, doc in enumerate(documents, 1):
            # Clean the content
            cleaned_content = self.clean_text(doc['content'])
            
            # Skip if content is too short
            if len(cleaned_content) < 100:
                logger.debug(f"Skipping document {doc_idx} (too short): {doc['url']}")
                continue
            
            # Chunk the content with overlap
            chunks = self.chunk_text(cleaned_content)
            
            logger.info(f"Page {doc_idx}: {doc['title'][:50]}...")
            logger.info(f"  URL: {doc['url']}")
            logger.info(f"  Original content length: {len(doc['content'])} chars")
            logger.info(f"  Cleaned content length: {len(cleaned_content)} chars")
            logger.info(f"  ✓ Chunks generated: {len(chunks)}")
            
            # Add metadata to each chunk including unique chunk_id
            for i, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())  # Generate unique chunk ID
                processed_chunks.append({
                    'chunk_id': chunk_id,           # Unique chunk identifier
                    'text': chunk,                   # Chunk text
                    'url': doc['url'],               # Parent URL
                    'title': doc['title'],           # Page title
                    'chunk_index': i,                # Chunk position
                    'total_chunks': len(chunks)      # Total chunks from this page
                })
                
                logger.debug(f"    Chunk {i+1}/{len(chunks)}: {len(chunk)} chars, ID: {chunk_id[:8]}...")
            
            logger.info("")
        
        logger.info("="*70)
        logger.info(f"✓ CHUNKING COMPLETE")
        logger.info(f"  Total documents processed: {len(documents)}")
        logger.info(f"  Total chunks created: {len(processed_chunks)}")
        logger.info(f"  Average chunks per page: {len(processed_chunks)/len(documents):.1f}")
        logger.info("="*70 + "\n")
        
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
