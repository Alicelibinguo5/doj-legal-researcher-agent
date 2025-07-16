#!/usr/bin/env python3
"""
Debug script to check what content is being retrieved from a URL.
"""

import requests
from bs4 import BeautifulSoup
from doj_research_agent.scraper import DOJScraper, ScrapingConfig

def debug_url_content():
    """Debug what content is being retrieved from the URL."""
    
    config = ScrapingConfig(
        max_pages=1,
        max_cases=1,
        delay_between_requests=1.0
    )
    
    scraper = DOJScraper(config)
    test_url = "https://www.justice.gov/opa/pr/seattle-businessman-convicted-tax-evasion-and-filing-false-tax-returns"
    
    print(f"Debugging URL: {test_url}")
    print("=" * 80)
    
    try:
        # Fetch raw content
        response = scraper.session.get(test_url, timeout=config.timeout)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check title
        title = soup.find('title')
        print(f"\nPage title: {title.get_text() if title else 'No title found'}")
        
        # Check for h1 tags
        h1_tags = soup.find_all('h1')
        print(f"\nH1 tags found: {len(h1_tags)}")
        for i, h1 in enumerate(h1_tags):
            print(f"  H1 {i+1}: {h1.get_text().strip()}")
        
        # Check for content areas
        content_selectors = [
            '.content', '.article-content', '.body', '.press-release-content',
            'article', 'main', '.field--name-body', '.field--type-text-with-summary'
        ]
        
        print(f"\nChecking content areas:")
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  {selector}: {len(elements)} elements found")
                for i, elem in enumerate(elements[:2]):  # Show first 2
                    text = elem.get_text().strip()[:200]
                    print(f"    Element {i+1}: {text}...")
        
        # Check for any text containing "tax evasion" or "fraud"
        full_text = soup.get_text()
        print(f"\nFull text length: {len(full_text)} characters")
        
        # Look for specific keywords
        keywords = ['tax evasion', 'fraud', 'convicted', 'seattle', 'businessman']
        print(f"\nKeyword search:")
        for keyword in keywords:
            if keyword.lower() in full_text.lower():
                print(f"  '{keyword}' found in content")
            else:
                print(f"  '{keyword}' NOT found in content")
        
        # Show first 500 characters of text
        print(f"\nFirst 500 characters of content:")
        print("-" * 40)
        print(full_text[:500])
        print("-" * 40)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_url_content() 