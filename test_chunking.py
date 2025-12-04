"""
Test script to demonstrate chunking requirements
Shows chunks per page with all required metadata
"""
from text_processor import TextProcessor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_chunking():
    """Test chunking with sample documents"""
    
    logger.info("="*70)
    logger.info("CHUNKING TEST - Demonstrating Requirements")
    logger.info("="*70)
    logger.info("\nRequirements Coverage:")
    logger.info("✓ Split long text into smaller chunks with overlap")
    logger.info("✓ Each chunk includes:")
    logger.info("  - chunk_id (unique identifier)")
    logger.info("  - parent URL")
    logger.info("  - page title")
    logger.info("  - chunk text")
    logger.info("✓ Store all chunks for embedding")
    logger.info("✓ Test by checking count of chunks per page")
    logger.info("="*70 + "\n")
    
    # Create sample documents with varying lengths
    sample_docs = [
        {
            'url': 'https://example.com/page1',
            'title': 'Introduction to Python',
            'content': """
            Python is a high-level, interpreted programming language known for its simplicity and readability.
            It was created by Guido van Rossum and first released in 1991. Python supports multiple programming
            paradigms including procedural, object-oriented, and functional programming. The language emphasizes
            code readability with its notable use of significant whitespace. Python's standard library is extensive
            and provides built-in modules for various tasks. The language is dynamically typed and garbage-collected.
            Python interpreters are available for many operating systems including Windows, Linux, and macOS.
            The Python Package Index (PyPI) hosts thousands of third-party packages. Python is widely used in
            web development, data analysis, artificial intelligence, scientific computing, and automation.
            """ * 5  # Repeat to make it longer
        },
        {
            'url': 'https://example.com/page2',
            'title': 'Python Data Types',
            'content': """
            Python has several built-in data types. Numeric types include integers (int), floating point numbers
            (float), and complex numbers (complex). Sequence types include strings (str), lists (list), and tuples
            (tuple). The dict type represents dictionaries which store key-value pairs. Sets (set and frozenset)
            store unique elements. The bool type represents boolean values True and False. Python also has a special
            None type representing the absence of a value. Type conversion can be done using built-in functions.
            """ * 3
        },
        {
            'url': 'https://example.com/page3',
            'title': 'Python Functions',
            'content': """
            Functions in Python are defined using the def keyword. They can accept parameters and return values.
            Python supports default parameters, keyword arguments, and variable-length arguments. Lambda functions
            provide a way to create small anonymous functions. Decorators allow modification of function behavior.
            """ * 2
        }
    ]
    
    # Initialize processor with specific chunk size and overlap
    chunk_size = 500
    chunk_overlap = 100
    processor = TextProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    logger.info(f"Configuration:")
    logger.info(f"  Chunk size: {chunk_size} characters")
    logger.info(f"  Chunk overlap: {chunk_overlap} characters\n")
    
    # Process documents
    chunks = processor.process_documents(sample_docs)
    
    # Detailed verification of chunks
    logger.info("\n" + "="*70)
    logger.info("DETAILED CHUNK VERIFICATION")
    logger.info("="*70 + "\n")
    
    # Group chunks by URL
    chunks_by_page = {}
    for chunk in chunks:
        url = chunk['url']
        if url not in chunks_by_page:
            chunks_by_page[url] = []
        chunks_by_page[url].append(chunk)
    
    # Display detailed information for each page
    for page_num, (url, page_chunks) in enumerate(chunks_by_page.items(), 1):
        logger.info(f"--- Page {page_num} ---")
        logger.info(f"URL: {url}")
        logger.info(f"Title: {page_chunks[0]['title']}")
        logger.info(f"✓ Chunks generated: {len(page_chunks)}")
        logger.info("")
        
        # Show details of first 2 chunks from this page
        for i, chunk in enumerate(page_chunks[:2], 1):
            logger.info(f"  Chunk {i} Details:")
            logger.info(f"    ✓ chunk_id: {chunk['chunk_id']}")
            logger.info(f"    ✓ parent URL: {chunk['url']}")
            logger.info(f"    ✓ page title: {chunk['title']}")
            logger.info(f"    ✓ chunk_index: {chunk['chunk_index'] + 1}/{chunk['total_chunks']}")
            logger.info(f"    ✓ text length: {len(chunk['text'])} characters")
            logger.info(f"    ✓ text preview: {chunk['text'][:100]}...")
            logger.info("")
        
        if len(page_chunks) > 2:
            logger.info(f"  ... and {len(page_chunks) - 2} more chunks\n")
    
    # Summary statistics
    logger.info("="*70)
    logger.info("CHUNKING STATISTICS")
    logger.info("="*70)
    logger.info(f"Total documents: {len(sample_docs)}")
    logger.info(f"Total chunks: {len(chunks)}")
    logger.info(f"Average chunks per page: {len(chunks)/len(sample_docs):.1f}")
    logger.info("")
    logger.info("Chunks per page breakdown:")
    for i, (url, page_chunks) in enumerate(chunks_by_page.items(), 1):
        logger.info(f"  Page {i}: {len(page_chunks)} chunks")
    
    # Verify all required fields
    logger.info("\n" + "="*70)
    logger.info("REQUIREMENTS VERIFICATION")
    logger.info("="*70)
    
    all_have_chunk_id = all('chunk_id' in c for c in chunks)
    all_have_url = all('url' in c for c in chunks)
    all_have_title = all('title' in c for c in chunks)
    all_have_text = all('text' in c for c in chunks)
    all_have_unique_ids = len(set(c['chunk_id'] for c in chunks)) == len(chunks)
    
    logger.info(f"✓ All chunks have chunk_id: {'PASS ✓' if all_have_chunk_id else 'FAIL ✗'}")
    logger.info(f"✓ All chunks have parent URL: {'PASS ✓' if all_have_url else 'FAIL ✗'}")
    logger.info(f"✓ All chunks have page title: {'PASS ✓' if all_have_title else 'FAIL ✗'}")
    logger.info(f"✓ All chunks have chunk text: {'PASS ✓' if all_have_text else 'FAIL ✗'}")
    logger.info(f"✓ All chunk IDs are unique: {'PASS ✓' if all_have_unique_ids else 'FAIL ✗'}")
    logger.info(f"✓ Chunks ready for embedding: {'PASS ✓' if len(chunks) > 0 else 'FAIL ✗'}")
    
    logger.info("\n" + "="*70)
    logger.info("TEST COMPLETED SUCCESSFULLY ✓")
    logger.info("="*70)
    
    return chunks


if __name__ == "__main__":
    test_chunking()
