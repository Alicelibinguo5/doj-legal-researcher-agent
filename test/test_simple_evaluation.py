#!/usr/bin/env python3
"""
Simple test to check if evaluation works without FRAUD_KEYWORDS issue.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_evaluation():
    """Test simple evaluation without Langfuse."""
    print("Testing simple evaluation...")
    
    try:
        from doj_research_agent.evaluation.evaluate import FraudDetectionEvaluator
        
        # Create evaluator
        evaluator = FraudDetectionEvaluator(
            model_provider="openai",
            model_name="gpt-4o",
            model_api_key=os.getenv("OPENAI_API_KEY"),
            use_llm_judge=False  # Disable LLM judge to avoid complexity
        )
        
        print("✅ Evaluator created successfully")
        
        # Create a simple test case
        from doj_research_agent.evaluation.evaluation_types import TestCase
        
        test_case = TestCase(
            text="John Smith was sentenced to 5 years for wire fraud scheme that defrauded investors of $2 million through false investment promises.",
            expected_fraud_flag=True,
            expected_fraud_type="financial_fraud",
            expected_money_laundering_flag=False,
            title="Test Case",
            ground_truth_rationale="Clear wire fraud charges"
        )
        
        print("✅ Test case created successfully")
        
        # Evaluate single case
        result = evaluator.evaluate_single_case(test_case)
        
        print("✅ Single case evaluation completed")
        print(f"   Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_evaluation() 