#!/usr/bin/env python3
"""
Test GPT-4o and classic fraud logic consistency for a known problematic use case.
"""

import os
from doj_research_agent.analyzer import CaseAnalyzer

def main():
    # Example problematic content (telemarketing scheme, consumer fraud)
    content = (
        "Costa Rica Resident Sentenced for Orchestrating Multimillion-Dollar International Telemarketing Scheme. "
        "The press release describes a telemarketing scheme that defrauded victims in the United States. "
        "The defendant was convicted for orchestrating a scheme to defraud consumers through deceptive telemarketing practices."
    )
    print("Testing GPT-4o and classic fraud logic on telemarketing scheme use case...")
    print("=" * 80)
    analyzer = CaseAnalyzer()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        return
    # Run GPT-4o extraction (with consistency post-processing)
    result = analyzer.extract_structured_info_gpt4o(content, api_key)
    print("\nGPT-4o + Consistency Results:")
    print("-" * 40)
    for key, value in result.items():
        if key == 'charges' and isinstance(value, list):
            print(f"{key}: {len(value)} charges found")
            for i, charge in enumerate(value, 1):
                print(f"  {i}. {charge}")
        elif key == 'classic_fraud_categories' and isinstance(value, list):
            print(f"{key}: {', '.join(value)}")
        else:
            print(f"{key}: {value}")
    print("\nTest complete.")

if __name__ == "__main__":
    main() 