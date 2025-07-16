#!/usr/bin/env python3
"""Test script to demonstrate enhanced fraud detection capabilities."""

from doj_research_agent import CaseAnalyzer, ChargeCategorizer
from doj_research_agent.models import ChargeCategory, CaseFraudInfo

def test_fraud_detection():
    """Test the enhanced fraud detection with various fraud-related content."""
    
    analyzer = CaseAnalyzer()
    categorizer = ChargeCategorizer()
    
    # Test cases with different types of fraud
    test_cases = [
        {
            "title": "Financial Fraud Case",
            "content": "The defendant was charged with wire fraud and money laundering. He operated a ponzi scheme that defrauded investors of millions of dollars through false promises of high returns.",
            "expected_fraud": True
        },
        {
            "title": "Healthcare Fraud Case", 
            "content": "The medical provider was convicted of medicare fraud and billing fraud. They engaged in upcoding and submitted false billing for services never provided.",
            "expected_fraud": True
        },
        {
            "title": "Disaster Fraud Case",
            "content": "The individual was charged with covid fraud and ppp loan fraud. They submitted false applications for pandemic relief funds.",
            "expected_fraud": True
        },
        {
            "title": "Consumer Protection Case",
            "content": "The company engaged in telemarketing fraud and operated a phone scam targeting elderly victims with false investment opportunities.",
            "expected_fraud": True
        },
        {
            "title": "Immigration Fraud Case",
            "content": "The defendant was charged with visa fraud and document fraud. They submitted fake documents and made false statements to immigration officials.",
            "expected_fraud": True
        },
        {
            "title": "Tax Fraud Case",
            "content": "The individual was convicted of tax evasion and filing false tax returns. They concealed income in offshore accounts.",
            "expected_fraud": True
        },
        {
            "title": "Public Corruption Case",
            "content": "The public official was charged with bribery and official misconduct. They accepted kickbacks in exchange for government contracts.",
            "expected_fraud": True
        },
        {
            "title": "Intellectual Property Case",
            "content": "The defendant was charged with counterfeiting and trademark infringement. They sold fake designer goods and counterfeit products.",
            "expected_fraud": True
        },
        {
            "title": "Cybercrime Case",
            "content": "The hacker was charged with computer fraud and data breach. They used phishing schemes to steal personal information.",
            "expected_fraud": True
        },
        {
            "title": "Non-Fraud Case",
            "content": "The defendant was charged with drug trafficking and possession of controlled substances. No fraud-related activities were involved.",
            "expected_fraud": False
        }
    ]
    
    print("Testing Enhanced Fraud Detection Capabilities")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['title']}")
        print("-" * 40)
        
        # Test charge categorization
        charges = ["wire fraud", "money laundering"]  # Sample charges
        categories = categorizer.categorize_charges(charges, test_case['content'])
        
        # Test fraud detection
        fraud_info = analyzer._is_fraud_case(categories, test_case['content'])
        
        print(f"Content: {test_case['content'][:100]}...")
        print(f"Categories: {[cat.value for cat in categories]}")
        print(f"Fraud Detected: {fraud_info.is_fraud}")
        print(f"Expected Fraud: {test_case['expected_fraud']}")
        print(f"Match: {'✓' if fraud_info.is_fraud == test_case['expected_fraud'] else '✗'}")
        
        if fraud_info.evidence:
            print(f"Evidence: {fraud_info.evidence}")
    
    print(f"\n{'=' * 60}")
    print("Fraud Detection Test Complete!")

def test_fraud_keywords():
    """Test specific fraud keywords and synonyms."""
    
    categorizer = ChargeCategorizer()
    
    # Test various fraud-related terms
    fraud_terms = [
        "ponzi scheme", "embezzlement", "money laundering", "medicare fraud",
        "covid fraud", "telemarketing fraud", "visa fraud", "tax evasion",
        "bribery", "counterfeiting", "phishing", "identity theft",
        "kickback", "false claims", "document fraud", "election fraud"
    ]
    
    print("\nTesting Fraud Keywords and Categories")
    print("=" * 50)
    
    for term in fraud_terms:
        categories = categorizer.categorize_charge(term)
        fraud_categories = [cat for cat in categories if 'fraud' in cat.value or cat.value in ['tax', 'public_corruption', 'cybercrime', 'consumer_protection']]
        
        print(f"Term: '{term}'")
        print(f"  Categories: {[cat.value for cat in categories]}")
        print(f"  Fraud-related: {[cat.value for cat in fraud_categories]}")
        print()

if __name__ == "__main__":
    test_fraud_detection()
    test_fraud_keywords() 