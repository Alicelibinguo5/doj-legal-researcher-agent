#!/usr/bin/env python3
"""Test script to demonstrate enhanced GPT-4o fraud detection capabilities."""

from doj_research_agent import CaseAnalyzer
import json

def test_gpt4o_fraud_detection():
    """Test the enhanced GPT-4o fraud detection with various fraud-related content."""
    
    analyzer = CaseAnalyzer()
    
    # Test cases with different types of fraud
    test_cases = [
        {
            "title": "Financial Fraud Case",
            "content": """
            Department of Justice Press Release
            Date: July 15, 2024
            
            John Smith was charged with wire fraud and money laundering. He operated a ponzi scheme that defrauded investors of millions of dollars through false promises of high returns. The defendant used shell companies to launder the proceeds and concealed the fraud from investors.
            """,
            "expected_fraud": True,
            "expected_type": "financial_fraud"
        },
        {
            "title": "Healthcare Fraud Case", 
            "content": """
            Department of Justice Press Release
            Date: July 15, 2024
            
            Medical provider ABC Healthcare was convicted of medicare fraud and billing fraud. They engaged in upcoding and submitted false billing for services never provided. The company received kickbacks from pharmaceutical companies and engaged in phantom billing practices.
            """,
            "expected_fraud": True,
            "expected_type": "healthcare_fraud"
        },
        {
            "title": "Disaster Fraud Case",
            "content": """
            Department of Justice Press Release
            Date: July 15, 2024
            
            The individual was charged with covid fraud and ppp loan fraud. They submitted false applications for pandemic relief funds, claiming to have employees and business operations that did not exist. The defendant received over $500,000 in fraudulent SBA loans.
            """,
            "expected_fraud": True,
            "expected_type": "disaster_fraud"
        },
        {
            "title": "Consumer Protection Case",
            "content": """
            Department of Justice Press Release
            Date: July 15, 2024
            
            The company engaged in telemarketing fraud and operated a phone scam targeting elderly victims with false investment opportunities. They used deceptive advertising and bait-and-switch tactics to defraud consumers of their retirement savings.
            """,
            "expected_fraud": True,
            "expected_type": "consumer_fraud"
        },
        {
            "title": "Government Corruption Case",
            "content": """
            Department of Justice Press Release
            Date: July 15, 2024
            
            Public official was charged with bribery and official misconduct. They accepted kickbacks in exchange for government contracts and engaged in corruption schemes. The defendant used their position for personal gain and violated public trust.
            """,
            "expected_fraud": True,
            "expected_type": "government_fraud"
        },
        {
            "title": "Non-Fraud Case",
            "content": """
            Department of Justice Press Release
            Date: July 15, 2024
            
            The defendant was charged with drug trafficking and possession of controlled substances. No fraud-related activities were involved. The case involved the distribution of narcotics and illegal drug manufacturing.
            """,
            "expected_fraud": False,
            "expected_type": None
        }
    ]
    
    print("Testing Enhanced GPT-4o Fraud Detection Capabilities")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['title']}")
        print("-" * 50)
        
        # Test GPT-4o extraction
        try:
            result = analyzer.extract_structured_info_gpt4o(test_case['content'])
            
            print(f"Content: {test_case['content'][:100]}...")
            print(f"GPT-4o Result:")
            print(f"  - Title: {result.get('title', 'N/A')}")
            print(f"  - Date: {result.get('date', 'N/A')}")
            print(f"  - Charges: {result.get('charges', [])}")
            print(f"  - Fraud Flag: {result.get('fraud_flag', False)}")
            print(f"  - Fraud Type: {result.get('fraud_type', 'N/A')}")
            print(f"  - Fraud Evidence: {result.get('fraud_evidence', 'N/A')}")
            print(f"  - Charge Count: {result.get('charge_count', 0)}")
            
            # Check if fraud detection matches expectation
            fraud_detected = result.get('fraud_flag', False)
            expected_fraud = test_case['expected_fraud']
            fraud_match = fraud_detected == expected_fraud
            
            print(f"Expected Fraud: {expected_fraud}")
            print(f"Fraud Detection Match: {'✓' if fraud_match else '✗'}")
            
            if fraud_detected and test_case['expected_type']:
                type_match = result.get('fraud_type') == test_case['expected_type']
                print(f"Fraud Type Match: {'✓' if type_match else '✗'}")
            
        except Exception as e:
            print(f"Error testing GPT-4o: {e}")
    
    print(f"\n{'=' * 70}")
    print("GPT-4o Fraud Detection Test Complete!")

def test_fraud_keywords_in_prompt():
    """Test that fraud keywords are properly included in the GPT-4o prompt."""
    
    analyzer = CaseAnalyzer()
    
    # Create a simple test case
    test_content = "This is a test case with wire fraud and money laundering."
    
    print("\nTesting Fraud Keywords in GPT-4o Prompt")
    print("=" * 50)
    
    try:
        result = analyzer.extract_structured_info_gpt4o(test_content)
        
        print(f"Test Content: {test_content}")
        print(f"Result:")
        print(f"  - Fraud Flag: {result.get('fraud_flag', False)}")
        print(f"  - Fraud Type: {result.get('fraud_type', 'N/A')}")
        print(f"  - Fraud Evidence: {result.get('fraud_evidence', 'N/A')}")
        
        if result.get('fraud_flag'):
            print("✓ Successfully detected fraud using keywords")
        else:
            print("✗ Failed to detect fraud")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Note: This requires an OpenAI API key to run
    print("Note: This test requires an OpenAI API key to be set.")
    print("Set OPENAI_API_KEY environment variable or provide it in the code.")
    
    # Uncomment the following lines to run the tests
    # test_gpt4o_fraud_detection()
    # test_fraud_keywords_in_prompt()
    
    print("\nTo run the tests, uncomment the test function calls above.") 