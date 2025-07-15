"""Web scraping functionality for DOJ press releases."""

import logging
import time
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .models import ScrapingConfig
from .utils import setup_logger

logger = setup_logger(__name__)


class DOJScraper:
    """Web scraper for DOJ press releases."""
    
    def __init__(self, config: ScrapingConfig):
        """Initialize scraper with configuration."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
    
    def get_press_release_urls(self) -> List[str]:
        """
        Fetch URLs of DOJ press releases.
        
        Returns:
            List of press release URLs
        """
        urls = []
        
        for page in range(1, self.config.max_pages + 1):
            try:
                page_urls = self._scrape_page(page)
                
                if not page_urls:
                    logger.info(f"No more press releases found on page {page}")
                    break
                
                urls.extend(page_urls)
                logger.info(f"Found {len(page_urls)} press releases on page {page}")
                
                # Rate limiting
                time.sleep(self.config.delay_between_requests)
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
        
        return list(set(urls))  # Remove duplicates
    
    def _scrape_page(self, page_num: int) -> List[str]:
        """
        Scrape a single page for press release URLs.
        
        Args:
            page_num: Page number to scrape
            
        Returns:
            List of URLs found on the page
        """
        page_url = f"{self.config.base_url}/news?page={page_num}"
        response = self.session.get(page_url, timeout=self.config.timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find press release links (adjust selector based on actual DOJ site structure)
        press_releases = soup.find_all('a', href=True)
        
        urls = []
        for link in press_releases:
            href = link.get('href')
            if href and self._is_press_release_url(href):
                full_url = urljoin(self.config.base_url, href)
                urls.append(full_url)
        
        return urls
    
    def _is_press_release_url(self, url: str) -> bool:
        """
        Check if URL is a press release URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL appears to be a press release
        """
        # Common patterns for DOJ press release URLs
        patterns = ['/pr/', '/press-release/', '/news/', '/opa/pr/']
        return any(pattern in url for pattern in patterns)
    
    def fetch_press_release_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch content of a single press release.
        
        Args:
            url: URL of the press release
            
        Returns:
            BeautifulSoup object or None if fetch fails
        """
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return None
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()