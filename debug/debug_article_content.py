#!/usr/bin/env python3
"""
Extract the actual article content from the DOJ press release.
"""

import requests
from bs4 import BeautifulSoup
from doj_research_agent.scraper import DOJScraper, ScrapingConfig

def extract_article_content():
    """Extract the actual article content from the DOJ press release."""
    
    config = ScrapingConfig(
        max_pages=1,
        max_cases=1,
        delay_between_requests=1.0
    )
    
    scraper = DOJScraper(config)
    test_url = "https://www.justice.gov/opa/pr/seattle-businessman-convicted-tax-evasion-and-filing-false-tax-returns"
    
    print(f"Extracting article content from: {test_url}")
    print("=" * 80)
    
    try:
        # Fetch content
        soup = scraper.fetch_press_release_content(test_url)
        
        if not soup:
            print("Failed to fetch content")
            return
        
        # Try different content extraction strategies
        print("Trying different content extraction methods:")
        
        # Method 1: Look for article tag
        article = soup.find('article')
        if article:
            print("\nMethod 1 - Article tag content:")
            print("-" * 40)
            article_text = article.get_text().strip()
            print(article_text[:1000])
            print("-" * 40)
        
        # Method 2: Look for specific DOJ content areas
        content_areas = [
            '.field--name-body',
            '.field--type-text-with-summary',
            '.press-release-content',
            '.content',
            '.article-content'
        ]
        
        for selector in content_areas:
            elements = soup.select(selector)
            if elements:
                print(f"\nMethod 2 - {selector} content:")
                print("-" * 40)
                for elem in elements:
                    text = elem.get_text().strip()
                    if len(text) > 100:  # Only show substantial content
                        print(text[:1000])
                        print("-" * 40)
                        break
        
        # Method 3: Look for paragraphs after the title
        h1 = soup.find('h1')
        if h1:
            print("\nMethod 3 - Content after H1:")
            print("-" * 40)
            # Find all paragraphs that come after the h1
            paragraphs = []
            current = h1.find_next_sibling()
            while current:
                if current.name == 'p':
                    text = current.get_text().strip()
                    if text and len(text) > 20:
                        paragraphs.append(text)
                current = current.find_next_sibling()
            
            for i, p in enumerate(paragraphs[:10]):  # Show first 10 paragraphs
                print(f"Paragraph {i+1}: {p}")
                print()
        
        # Method 4: Extract main content area
        main_content = soup.find('main')
        if main_content:
            print("\nMethod 4 - Main content area:")
            print("-" * 40)
            # Remove navigation and other non-content elements
            for elem in main_content.find_all(['nav', 'aside', 'header', 'footer']):
                elem.decompose()
            
            main_text = main_content.get_text().strip()
            print(main_text[:1000])
            print("-" * 40)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_article_content() 