#!/usr/bin/env python3
"""
Test the merged classic + GPT-4o extraction for a real DOJ press release URL.
"""

import os
from doj_research_agent.scraper import DOJScraper, ScrapingConfig
import json

def main():
    url = "https://www.justice.gov/opa/pr/seattle-businessman-convicted-tax-evasion-and-filing-false-tax-returns"
    print(f"Testing extract_structured_info_gpt4o_from_url on: {url}")
    config = ScrapingConfig(max_pages=1, max_cases=1, delay_between_requests=1.0)
    scraper = DOJScraper(config)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        return
    result = scraper.extract_structured_info_gpt4o_from_url(url, api_key=api_key)
    print("\nClassic Extraction:")
    for k, v in result.items():
        if k == 'gpt4o':
            continue
        print(f"{k}: {v}")
    print("\nGPT-4o Extraction:")
    for k, v in result.get('gpt4o', {}).items():
        print(f"{k}: {v}")
    # Save output for inspection
    import datetime
    output_file = f"output/test_gpt4o_scraper_merge_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main() 