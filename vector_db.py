"""
Vector Database Module
Store and retrieve embeddings using ChromaDB or fallback to SimpleVectorDatabase
"""
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import chromadb
    from typing import List, Dict, Optional
    import uuid


    class VectorDatabase:
        """Vector database for storing and retrieving embeddings"""
        
        def __init__(self, db_path: str = "./data/chroma_db", collection_name: str = "support_docs"):
            """
            Initialize vector database
            
            Args:
                db_path: Path to store the database
                collection_name: Name of the collection
            """
            self.db_path = db_path
            self.collection_name = collection_name
            
            # Create directory if it doesn't exist
            os.makedirs(db_path, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Vector database initialized at {db_path}")
    
    def add_documents(self, chunks: List[Dict[str, any]]):
        """
        Add documents with embeddings to the database
        
        Args:
            chunks: List of chunks with 'text', 'embedding', and metadata
        """
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        # Get current count to generate unique IDs
        current_count = self.collection.count()
        
        # Prepare data for ChromaDB
        ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
        embeddings = [chunk['embedding'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [
            {
                'url': chunk.get('url', ''),
                'title': chunk.get('title', ''),
                'chunk_index': chunk.get('chunk_index', 0)
            }
            for chunk in chunks
        ]
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_documents = documents[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            
            self.collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_documents,
                metadatas=batch_metadatas
            )
            
            logger.info(f"Added batch {i // batch_size + 1}/{(len(ids) - 1) // batch_size + 1}")
        
        logger.info(f"Successfully added {len(chunks)} documents to vector database")
    
    def query(self, query_embedding: List[float], top_k: int = 3) -> Dict:
        """
        Query the database for similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            Dictionary with query results
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return results
    
    def get_relevant_documents(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, str]]:
        """
        Get relevant documents for a query
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        results = self.query(query_embedding, top_k)
        
        documents = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'text': doc,
                    'url': results['metadatas'][0][i].get('url', ''),
                    'title': results['metadatas'][0][i].get('title', ''),
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        
        return documents
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Collection '{self.collection_name}' cleared")
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection"""
        return self.collection.count()

except Exception as e:
    # Fallback to SimpleVectorDatabase if ChromaDB fails
    logger.warning(f"ChromaDB not available ({str(e)[:100]}), using SimpleVectorDatabase as fallback")
    from simple_vector_db import SimpleVectorDatabase as VectorDatabase
