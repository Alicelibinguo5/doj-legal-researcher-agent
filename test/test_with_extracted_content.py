#!/usr/bin/env python3
"""
Test GPT-4o analysis with properly extracted article content.
"""

import os
import json
from datetime import datetime
from doj_research_agent.scraper import DOJScraper, ScrapingConfig
from doj_research_agent.analyzer import CaseAnalyzer

def test_with_extracted_content():
    """Test fraud detection with properly extracted content."""
    
    config = ScrapingConfig(
        max_pages=1,
        max_cases=1,
        delay_between_requests=1.0
    )
    
    scraper = DOJScraper(config)
    analyzer = CaseAnalyzer()
    
    test_url = "https://www.justice.gov/opa/pr/seattle-businessman-convicted-tax-evasion-and-filing-false-tax-returns"
    
    print(f"Testing with extracted content from: {test_url}")
    print("=" * 80)
    
    try:
        # Fetch the page content
        soup = scraper.fetch_press_release_content(test_url)
        
        if not soup:
            print("Failed to fetch content")
            return
        
        # Extract the actual article content
        article = soup.find('article')
        if article:
            # Get the text content from the article
            article_text = article.get_text().strip()
            
            # Clean up the text (remove extra whitespace, etc.)
            import re
            article_text = re.sub(r'\s+', ' ', article_text)
            
            print("Extracted Article Content:")
            print("-" * 40)
            print(article_text[:1000] + "..." if len(article_text) > 1000 else article_text)
            print("-" * 40)
            
            # Test GPT-4o analysis on the extracted content
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("ERROR: OPENAI_API_KEY environment variable not set")
                return
            
            print("\nRunning GPT-4o analysis on extracted content...")
            result = analyzer.extract_structured_info_gpt4o(article_text, api_key)
            
            print("\nGPT-4o Analysis Results:")
            print("-" * 40)
            
            # Pretty print the results
            for key, value in result.items():
                if key == 'charges' and isinstance(value, list):
                    print(f"{key}: {len(value)} charges found")
                    for i, charge in enumerate(value, 1):
                        print(f"  {i}. {charge}")
                else:
                    print(f"{key}: {value}")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, f"extracted_content_analysis_{timestamp}.json")
            with open(output_file, "w") as f:
                json.dump({
                    "url": test_url,
                    "extracted_content": article_text,
                    "gpt4o_analysis": result
                }, f, indent=2)
            
            print(f"\nResults saved to: {output_file}")
            
        else:
            print("No article tag found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_extracted_content() 