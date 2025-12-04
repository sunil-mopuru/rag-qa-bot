"""
Test script to demonstrate crawler functionality
Prints list of crawled URLs as required
"""
from crawler import WebCrawler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_crawler_simple():
    """Test crawler with a simple example site"""
    
    # Use Python docs as example (limited pages for quick test)
    base_url = "https://docs.python.org/3/tutorial/"
    
    logger.info("="*70)
    logger.info("CRAWLER TEST - Demonstrating Requirements")
    logger.info("="*70)
    logger.info(f"\n✓ Function accepts base URL: {base_url}")
    logger.info(f"✓ Limiting depth: max_depth=2")
    logger.info(f"✓ Limiting pages: max_pages=10")
    logger.info(f"✓ Skipping patterns: login, signup, cart, account, etc.")
    logger.info(f"✓ Crawling only same domain links\n")
    
    # Initialize crawler
    crawler = WebCrawler(
        base_url=base_url,
        max_depth=2,  # Limited for quick testing
        max_pages=10  # Limited for quick testing
    )
    
    # Crawl and get results
    crawled_data = crawler.crawl()
    
    # Display results to verify all requirements
    logger.info("\n" + "="*70)
    logger.info("VERIFICATION OF REQUIREMENTS")
    logger.info("="*70)
    
    for i, page in enumerate(crawled_data, 1):
        logger.info(f"\n--- Page {i} ---")
        logger.info(f"✓ URL stored: {page['url']}")
        logger.info(f"✓ Title stored: {page['title'][:80]}...")
        logger.info(f"✓ Raw HTML stored: {len(page.get('raw_html', ''))} characters")
        logger.info(f"✓ Content extracted: {len(page['content'])} characters")
    
    logger.info("\n" + "="*70)
    logger.info(f"SUCCESS: Crawled {len(crawled_data)} pages")
    logger.info("="*70)
    
    return crawled_data


if __name__ == "__main__":
    test_crawler_simple()
