#!/usr/bin/env python3
"""
Debug script to test Langfuse integration and see if scores are being pushed.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_langfuse_connection():
    """Test basic Langfuse connection."""
    print("=" * 60)
    print("TESTING LANGFUSE CONNECTION")
    print("=" * 60)
    
    # Check environment variables
    print(f"LANGFUSE_PUBLIC_KEY: {'Set' if os.getenv('LANGFUSE_PUBLIC_KEY') else 'Not set'}")
    print(f"LANGFUSE_SECRET_KEY: {'Set' if os.getenv('LANGFUSE_SECRET_KEY') else 'Not set'}")
    print(f"LANGFUSE_HOST: {os.getenv('LANGFUSE_HOST', 'Not set')}")
    print(f"ENABLE_LANGFUSE_TRACING: {os.getenv('ENABLE_LANGFUSE_TRACING', 'Not set')}")
    
    try:
        from doj_research_agent.evaluation.langfuse_integration import get_langfuse_tracer, LangfuseTracer
        
        # Test tracer initialization
        tracer = get_langfuse_tracer()
        if tracer:
            print("✅ Langfuse tracer initialized successfully")
            print(f"   Enabled: {tracer.enabled}")
            print(f"   Host: {tracer.host}")
        else:
            print("❌ Langfuse tracer initialization failed")
            
    except Exception as e:
        print(f"❌ Error initializing Langfuse tracer: {e}")
        import traceback
        traceback.print_exc()

def test_evaluation_tracing():
    """Test evaluation tracing functionality."""
    print("\n" + "=" * 60)
    print("TESTING EVALUATION TRACING")
    print("=" * 60)
    
    try:
        from doj_research_agent.evaluation.evaluate import quick_eval
        from doj_research_agent.evaluation.langfuse_integration import get_langfuse_tracer
        
        # Check if tracer is available
        tracer = get_langfuse_tracer()
        if not tracer or not tracer.enabled:
            print("❌ Langfuse tracer not available or disabled")
            return
        
        print("Running quick evaluation with Langfuse tracing...")
        
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
        
        # Check if trace was created
        if hasattr(result, 'trace_id') and result.trace_id:
            print(f"✅ Trace ID: {result.trace_id}")
        else:
            print("⚠️  No trace ID found in result")
            
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()

def test_direct_langfuse_api():
    """Test direct Langfuse API calls."""
    print("\n" + "=" * 60)
    print("TESTING DIRECT LANGFUSE API")
    print("=" * 60)
    
    try:
        import langfuse
        
        # Initialize client directly
        client = langfuse.Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        
        print("✅ Langfuse client created successfully")
        
        # Try to create a simple trace
        trace = client.trace(
            name="test-trace",
            metadata={"test": True, "source": "debug-script"}
        )
        
        print("✅ Trace created successfully")
        print(f"   Trace ID: {trace.id}")
        
        # Add a score
        trace.score(
            name="test-score",
            value=0.85,
            comment="Test score from debug script"
        )
        
        print("✅ Score added successfully")
        
        # Close the trace
        trace.update(end_time=langfuse.now())
        
        print("✅ Trace closed successfully")
        
        # Close client
        client.close()
        
    except Exception as e:
        print(f"❌ Error with direct Langfuse API: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("Starting Langfuse integration debug tests...")
    
    test_langfuse_connection()
    test_direct_langfuse_api()
    test_evaluation_tracing()
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)
    print("Check your Langfuse dashboard to see if traces and scores appear.")
    print("If not, check the error messages above for issues.")

if __name__ == "__main__":
    main() 