"""
Simple Vector Database Module
Store and retrieve embeddings using in-memory numpy arrays
"""
import numpy as np
from typing import List, Dict, Optional
import logging
import json
import os
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleVectorDatabase:
    """Simple vector database for storing and retrieving embeddings"""
    
    def __init__(self, db_path: str = "./data/simple_db", collection_name: str = "support_docs"):
        """
        Initialize vector database
        
        Args:
            db_path: Path to store the database
            collection_name: Name of the collection
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.db_file = os.path.join(db_path, f"{collection_name}.pkl")
        
        # Create directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize or load data
        self.embeddings = []
        self.documents = []
        self.metadatas = []
        
        self.load()
        
        logger.info(f"Simple vector database initialized at {db_path}")
    
    def add_documents(self, chunks: List[Dict[str, any]]):
        """
        Add documents with embeddings to the database
        
        Args:
            chunks: List of chunks with 'text', 'embedding', and metadata
        """
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        for chunk in chunks:
            self.embeddings.append(chunk['embedding'])
            self.documents.append(chunk['text'])
            self.metadatas.append({
                'url': chunk.get('url', ''),
                'title': chunk.get('title', ''),
                'chunk_index': chunk.get('chunk_index', 0)
            })
        
        self.save()
        logger.info(f"Successfully added {len(chunks)} documents to vector database")
    
    def query(self, query_embedding: List[float], top_k: int = 3) -> Dict:
        """
        Query the database for similar documents using cosine similarity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            Dictionary with query results
        """
        if not self.embeddings:
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
        
        # Convert to numpy arrays
        query_vec = np.array(query_embedding).reshape(1, -1)
        db_vecs = np.array(self.embeddings)
        
        # Normalize vectors for cosine similarity
        query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
        db_norms = db_vecs / (np.linalg.norm(db_vecs, axis=1, keepdims=True) + 1e-10)
        
        # Calculate cosine similarity
        similarities = np.dot(db_norms, query_norm.T).flatten()
        
        # Convert to distances (1 - similarity)
        distances = 1 - similarities
        
        # Get top k indices
        top_k = min(top_k, len(distances))
        top_indices = np.argsort(distances)[:top_k]
        
        # Prepare results
        results = {
            'documents': [[self.documents[i] for i in top_indices]],
            'metadatas': [[self.metadatas[i] for i in top_indices]],
            'distances': [[float(distances[i]) for i in top_indices]]
        }
        
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
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'text': doc,
                    'url': results['metadatas'][0][i].get('url', ''),
                    'title': results['metadatas'][0][i].get('title', ''),
                    'distance': results['distances'][0][i]
                })
        
        return documents
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        self.embeddings = []
        self.documents = []
        self.metadatas = []
        self.save()
        logger.info(f"Collection '{self.collection_name}' cleared")
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection"""
        return len(self.documents)
    
    def save(self):
        """Save database to disk"""
        data = {
            'embeddings': self.embeddings,
            'documents': self.documents,
            'metadatas': self.metadatas
        }
        with open(self.db_file, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self):
        """Load database from disk"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'rb') as f:
                    data = pickle.load(f)
                self.embeddings = data.get('embeddings', [])
                self.documents = data.get('documents', [])
                self.metadatas = data.get('metadatas', [])
                logger.info(f"Loaded {len(self.documents)} documents from disk")
            except Exception as e:
                logger.warning(f"Could not load database: {e}")
                self.embeddings = []
                self.documents = []
                self.metadatas = []
