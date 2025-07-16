#!/usr/bin/env python3
"""
Test script to analyze a specific DOJ press release for fraud detection.
"""

import os
import json
from datetime import datetime
from doj_research_agent.scraper import DOJScraper, ScrapingConfig
from doj_research_agent.analyzer import CaseAnalyzer

def test_specific_case():
    """Test fraud detection on a specific DOJ press release."""
    
    # Configuration
    config = ScrapingConfig(
        max_pages=1,
        max_cases=1,
        delay_between_requests=1.0
    )
    
    # Initialize components
    scraper = DOJScraper(config)
    analyzer = CaseAnalyzer()
    
    # Specific URL to test
    test_url = "https://www.justice.gov/opa/pr/seattle-businessman-convicted-tax-evasion-and-filing-false-tax-returns"
    
    print(f"Analyzing specific case: {test_url}")
    print("=" * 80)
    
    try:
        # Extract content using GPT-4o
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("ERROR: OPENAI_API_KEY environment variable not set")
            return
        
        print("Using GPT-4o for structured extraction...")
        result = scraper.extract_structured_info_gpt4o_from_url(test_url, api_key=api_key)
        
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
        
        print("\n" + "=" * 80)
        
        # Also test the fraud info extraction method
        print("Testing fraud info extraction...")
        fraud_info = scraper.extract_fraud_info_from_url(test_url)
        
        print("\nFraud Info Results:")
        print("-" * 40)
        for key, value in fraud_info.items():
            if key == 'charge_list' and isinstance(value, list):
                print(f"{key}: {len(value)} charges")
                for i, charge in enumerate(value, 1):
                    print(f"  {i}. {charge}")
            else:
                print(f"{key}: {value}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"specific_case_analysis_{timestamp}.json")
        with open(output_file, "w") as f:
            json.dump({
                "url": test_url,
                "gpt4o_analysis": result,
                "fraud_info": fraud_info
            }, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"Error analyzing case: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_case() 