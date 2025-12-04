"""
Web Crawler Module
Crawls websites and extracts text content from web pages
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebCrawler:
    """Web crawler to extract content from websites"""
    
    def __init__(self, base_url: str, max_depth: int = 3, max_pages: int = 50):
        """
        Initialize the web crawler
        
        Args:
            base_url: Starting URL for crawling
            max_depth: Maximum depth to crawl
            max_pages: Maximum number of pages to crawl
        """
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.crawled_data: List[Dict[str, str]] = []
        
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to the same domain"""
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)
        return (
            parsed_url.scheme in ['http', 'https'] and
            parsed_url.netloc == parsed_base.netloc
        )
    
    def extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator='\n')
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all valid links from the page"""
        links = []
        for link in soup.find_all('a', href=True):
            url = urljoin(current_url, link['href'])
            # Remove fragments
            url = url.split('#')[0]
            if self.is_valid_url(url) and url not in self.visited_urls:
                links.append(url)
        return links
    
    def crawl_page(self, url: str) -> Dict[str, str]:
        """Crawl a single page and extract content"""
        try:
            logger.info(f"Crawling: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else url
            
            # Extract main content
            content = self.extract_text(soup)
            
            return {
                'url': url,
                'title': title_text,
                'content': content
            }
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return None
    
    def crawl(self) -> List[Dict[str, str]]:
        """
        Crawl the website starting from base_url
        
        Returns:
            List of dictionaries containing crawled data
        """
        # Queue: (url, depth)
        queue = [(self.base_url, 0)]
        
        while queue and len(self.visited_urls) < self.max_pages:
            current_url, depth = queue.pop(0)
            
            if current_url in self.visited_urls or depth > self.max_depth:
                continue
            
            self.visited_urls.add(current_url)
            
            # Crawl the page
            page_data = self.crawl_page(current_url)
            if page_data:
                self.crawled_data.append(page_data)
                
                # If not at max depth, add links to queue
                if depth < self.max_depth:
                    try:
                        response = requests.get(current_url, timeout=10)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        links = self.extract_links(soup, current_url)
                        
                        for link in links:
                            if len(self.visited_urls) + len(queue) < self.max_pages:
                                queue.append((link, depth + 1))
                    except Exception as e:
                        logger.error(f"Error extracting links from {current_url}: {str(e)}")
            
            # Be respectful - add delay
            time.sleep(0.5)
        
        logger.info(f"Crawling completed. Total pages crawled: {len(self.crawled_data)}")
        return self.crawled_data


def crawl_website(base_url: str, max_depth: int = 3, max_pages: int = 50) -> List[Dict[str, str]]:
    """
    Convenience function to crawl a website
    
    Args:
        base_url: Starting URL
        max_depth: Maximum crawl depth
        max_pages: Maximum pages to crawl
        
    Returns:
        List of crawled page data
    """
    crawler = WebCrawler(base_url, max_depth, max_pages)
    return crawler.crawl()
