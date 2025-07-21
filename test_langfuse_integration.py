#!/usr/bin/env python3
"""
Test script for Langfuse integration with DOJ Research Agent.

This script tests the Langfuse integration to ensure it can:
1. Load environment variables from .env file
2. Initialize the Langfuse client
3. Create traces and scores
"""

import os
import logging
from doj_research_agent.langfuse_integration import LangfuseTracer, get_langfuse_tracer
from doj_research_agent.evaluate import quick_eval

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_langfuse_initialization():
    """Test Langfuse client initialization."""
    print("Testing Langfuse initialization...")
    
    # Check environment variables
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST")
    
    print(f"LANGFUSE_PUBLIC_KEY: {'Set' if public_key else 'Not set'}")
    print(f"LANGFUSE_SECRET_KEY: {'Set' if secret_key else 'Not set'}")
    print(f"LANGFUSE_HOST: {host}")
    
    # Create tracer
    tracer = LangfuseTracer()
    
    if tracer.enabled:
        print("✅ Langfuse tracer initialized successfully")
        return True
    else:
        print("❌ Langfuse tracer initialization failed")
        return False


def test_evaluation_with_langfuse():
    """Test evaluation with Langfuse tracing."""
    print("\nTesting evaluation with Langfuse tracing...")
    
    try:
        # Run a quick evaluation
        result = quick_eval(
            model_provider="openai",
            model_name="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            use_llm_judge=True,
            enable_langfuse_tracing=True
        )
        
        print(f"✅ Evaluation completed successfully")
        print(f"   Accuracy: {result.accuracy:.3f}")
        print(f"   Precision: {result.precision:.3f}")
        print(f"   Recall: {result.recall:.3f}")
        print(f"   F1 Score: {result.f1_score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return False


def main():
    """Main test function."""
    print("DOJ Research Agent - Langfuse Integration Test")
    print("=" * 50)
    
    # Test 1: Langfuse initialization
    init_success = test_langfuse_initialization()
    
    # Test 2: Evaluation with tracing
    if init_success:
        eval_success = test_evaluation_with_langfuse()
    else:
        eval_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Langfuse Initialization: {'✅ PASS' if init_success else '❌ FAIL'}")
    print(f"Evaluation with Tracing: {'✅ PASS' if eval_success else '❌ FAIL'}")
    
    if init_success and eval_success:
        print("\n🎉 All tests passed! Check your Langfuse dashboard for traces.")
        print("Dashboard URL: https://cloud.langfuse.com")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")
    
    # Clean up
    tracer = get_langfuse_tracer()
    if tracer:
        tracer.close()


if __name__ == "__main__":
    main() 