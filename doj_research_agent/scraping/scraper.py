"""Web scraping functionality for DOJ press releases."""

import logging
import time
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import re

import requests
from bs4 import BeautifulSoup
import warnings
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from ..core.models import ScrapingConfig
from ..core.utils import setup_logger

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
        from bs4 import Tag
        for link in press_releases:
            if not isinstance(link, Tag):
                continue
            href = link.get('href')
            if isinstance(href, str) and self._is_press_release_url(href):
                full_url = urljoin(self.config.base_url, href)
                urls.append(full_url)
        
        return urls
    
    def _is_press_release_url(self, url: str) -> bool:
        """
        Check if URL is a press release URL.
        Excludes DOJ video pages and video formats.
        Args:
            url: URL to check
        Returns:
            True if URL appears to be a press release
        """
        # Exclude DOJ video pages and video-related paths
        video_paths = [
            '/news/videos',
            '/video',
            '/videos',
            '/media/video',
            '/media/videos',
            '/multimedia/video',
            '/multimedia/videos'
        ]
        
        for video_path in video_paths:
            if video_path in url.lower():
                return False
        
        # Exclude common video file extensions
        video_extensions = [
            r'\.(mp4|mov|avi|wmv|flv|webm|mkv|m4v|3gp|ogv|ts|mts|m2ts)(\?|$)',
            r'\.(mp3|wav|aac|ogg|wma|flac)(\?|$)',
            r'\.(gif|webp)(\?|$)'
        ]
        
        for pattern in video_extensions:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Exclude video streaming and player URLs
        video_platforms = [
            'youtube.com',
            'vimeo.com',
            'dailymotion.com',
            'brightcove.com',
            'jwplayer.com',
            'video.js',
            'player'
        ]
        
        for platform in video_platforms:
            if platform in url.lower():
                return False
        
        # Common patterns for DOJ press release URLs
        patterns = ['/pr/', '/press-release/', '/news/', '/opa/pr/']
        return any(pattern in url for pattern in patterns)
    
    def _filter_video_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Remove video-related content from the page.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            BeautifulSoup object with video content removed
        """
        # Remove video elements
        video_selectors = [
            'video',
            'iframe[src*="youtube"]',
            'iframe[src*="vimeo"]',
            'iframe[src*="dailymotion"]',
            'iframe[src*="brightcove"]',
            'iframe[src*="jwplayer"]',
            '.video-player',
            '.video-container',
            '[class*="video"]',
            '[id*="video"]'
        ]
        
        for selector in video_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Remove video-related text content
        video_keywords = [
            'video', 'videos', 'multimedia', 'media player',
            'play video', 'watch video', 'video player'
        ]
        
        # Find and remove paragraphs or divs that contain only video-related text
        for element in soup.find_all(['p', 'div', 'span']):
            if element.get_text().strip().lower() in video_keywords:
                element.decompose()
        
        return soup

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
            
            # Filter out video content if enabled
            if self.config.filter_video_content:
                soup = self._filter_video_content(soup)
            
            return soup
            
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return None
    
    def extract_indictment_number_from_url(self, url: str) -> str:
        """Fetch a press release and extract the indictment number/details if present."""
        soup = self.fetch_press_release_content(url)
        if soup:
            from ..analysis.analyzer import CaseAnalyzer
            analyzer = CaseAnalyzer()
            content = analyzer._extract_content(soup)
            return analyzer.extract_indictment_number(content)
        return ""
    
    def extract_structured_info_from_url(self, url: str, api_key: str = None) -> dict:
        """
        Fetch a press release, extract the main text, and use GPT-4o to extract structured info.
        Returns a dict with both classic and GPT-4o fields.
        """
        from ..llm.llm import extract_structured_info
        soup = self.fetch_press_release_content(url)
        if soup:
            from ..analysis.analyzer import CaseAnalyzer
            analyzer = CaseAnalyzer()
            # Use classic extraction for structure
            case_info = analyzer.analyze_press_release(url, soup)
            # Use main article content for LLM
            content = analyzer.extract_main_article_content(soup)
            if not isinstance(content, str):
                content = str(content) if content is not None else ""
            gpt_result = extract_structured_info(content, api_key=api_key or "")
            # Merge classic and GPT-4o results
            result = case_info.to_dict() if case_info else {}
            result['gpt4o'] = gpt_result
            return result
        return {"error": "Could not fetch or parse content."}
    
    def extract_fraud_info_from_url(self, url: str) -> dict:
        """
        Fetch a press release, analyze it, and return fraud info and charge count.
        Returns a dict: {is_fraud, evidence, charge_count, charge_list}
        """
        from ..analysis.analyzer import CaseAnalyzer
        soup = self.fetch_press_release_content(url)
        if soup:
            analyzer = CaseAnalyzer()
            case_info = analyzer.analyze_press_release(url, soup)
            if case_info:
                fraud_info = getattr(case_info, 'fraud_info', None)
                is_fraud = fraud_info.is_fraud if fraud_info else False
                evidence = fraud_info.evidence if fraud_info else None
                charge_count = len(case_info.charges) if hasattr(case_info, 'charges') else 0
                charge_list = case_info.charges if hasattr(case_info, 'charges') else []
                return {
                    'is_fraud': is_fraud,
                    'evidence': evidence,
                    'charge_count': charge_count,
                    'charge_list': charge_list
                }
        return {
            'is_fraud': False,
            'evidence': None,
            'charge_count': 0,
            'charge_list': []
        }
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()