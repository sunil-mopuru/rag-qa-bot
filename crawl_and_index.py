"""
Example script to crawl a website and populate the vector database
"""
import sys
import logging
from crawler import crawl_website
from text_processor import process_crawled_data
from embeddings import generate_embeddings_for_chunks
from vector_db import VectorDatabase
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main function to crawl and index a website"""
    
    # Get base URL from command line or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        if settings.base_url:
            base_url = settings.base_url
        else:
            logger.error("Please provide a base URL as command line argument or set BASE_URL in .env")
            logger.info("Usage: python crawl_and_index.py <base_url>")
            sys.exit(1)
    
    logger.info(f"Starting crawl and index process for: {base_url}")
    
    # Step 1: Crawl the website
    logger.info("Step 1: Crawling website...")
    crawled_data = crawl_website(
        base_url=base_url,
        max_depth=settings.max_crawl_depth,
        max_pages=settings.max_pages
    )
    
    if not crawled_data:
        logger.error("No data was crawled. Exiting.")
        sys.exit(1)
    
    logger.info(f"Crawled {len(crawled_data)} pages")
    
    # Step 2: Process and chunk the text
    logger.info("Step 2: Processing and chunking text...")
    chunks = process_crawled_data(
        crawled_data,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    logger.info(f"Created {len(chunks)} text chunks")
    
    if not chunks:
        logger.error("No chunks were created. Exiting.")
        sys.exit(1)
    
    # Step 3: Generate embeddings
    logger.info("Step 3: Generating embeddings...")
    chunks_with_embeddings = generate_embeddings_for_chunks(
        chunks,
        api_key=settings.openai_api_key,
        model=settings.embedding_model
    )
    
    logger.info("Embeddings generated successfully")
    
    # Step 4: Store in vector database
    logger.info("Step 4: Storing in vector database...")
    vector_db = VectorDatabase(
        db_path=settings.chroma_db_path,
        collection_name=settings.collection_name
    )
    
    # Clear existing collection (optional)
    logger.info("Clearing existing collection...")
    vector_db.clear_collection()
    
    # Add documents
    vector_db.add_documents(chunks_with_embeddings)
    
    # Verify
    count = vector_db.get_collection_count()
    logger.info(f"Successfully indexed {count} documents in vector database")
    
    logger.info("Crawl and index process completed successfully!")
    logger.info(f"You can now start the API server with: python main.py")


if __name__ == "__main__":
    main()
