"""
Simple test to add some sample data to the vector database
"""
import logging
from sentence_transformers import SentenceTransformer
from vector_db import VectorDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Add sample data to test the system"""
    
    # Sample Python documentation text
    sample_data = [
        {
            'text': "Python is an easy to learn, powerful programming language. It has efficient high-level data structures and a simple but effective approach to object-oriented programming.",
            'url': 'https://docs.python.org/3/tutorial/introduction.html',
            'title': 'Python Introduction'
        },
        {
            'text': "Python has several built-in data types including integers (int), floating point numbers (float), strings (str), lists, tuples, and dictionaries.",
            'url': 'https://docs.python.org/3/tutorial/introduction.html',
            'title': 'Python Data Types'
        },
        {
            'text': "Functions in Python are defined using the def keyword. A function can take parameters and return values. Functions help organize code and make it reusable.",
            'url': 'https://docs.python.org/3/tutorial/controlflow.html',
            'title': 'Python Functions'
        },
        {
            'text': "Lists are mutable sequences in Python. You can create a list using square brackets. Lists can contain items of different types and can be modified after creation.",
            'url': 'https://docs.python.org/3/tutorial/datastructures.html',
            'title': 'Python Lists'
        },
        {
            'text': "For loops in Python iterate over the items of any sequence. The syntax is: for item in sequence: The loop variable takes each value in the sequence.",
            'url': 'https://docs.python.org/3/tutorial/controlflow.html',
            'title': 'Python For Loops'
        }
    ]
    
    logger.info("Initializing embedding model (this may download the model first time)...")
    # Use sentence-transformers (free, local)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    logger.info("Generating embeddings for sample data...")
    chunks_with_embeddings = []
    for i, item in enumerate(sample_data):
        embedding = model.encode(item['text']).tolist()
        chunks_with_embeddings.append({
            'text': item['text'],
            'embedding': embedding,
            'url': item['url'],
            'title': item['title'],
            'chunk_index': i
        })
    
    logger.info(f"Generated {len(chunks_with_embeddings)} embeddings")
    
    logger.info("Initializing vector database...")
    db = VectorDatabase()
    
    logger.info("Adding documents to vector database...")
    db.add_documents(chunks_with_embeddings)
    
    count = db.get_collection_count()
    logger.info(f"✓ Successfully added {count} documents to vector database")
    logger.info("✓ You can now start the API server with: python main.py")
    logger.info("✓ Then test with: python test_bot.py 'What are Python data types?'")

if __name__ == "__main__":
    main()
