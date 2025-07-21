#!/usr/bin/env python3
"""Test script for the feedback system."""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from doj_research_agent.core.feedback_manager import FeedbackManager
from doj_research_agent.core.models import FeedbackData

def test_feedback_system():
    """Test the feedback system functionality."""
    print("🧪 Testing Feedback System...")
    
    # Initialize feedback manager
    fm = FeedbackManager("test_feedback.json")
    
    # Test adding feedback
    test_feedback = FeedbackData(
        case_id="test_case_1",
        url="https://example.com/test",
        user_feedback="positive",
        feedback_text="Great analysis!",
        model_prediction={"fraud_flag": True, "money_laundering_flag": False}
    )
    
    result = fm.add_feedback(test_feedback)
    print(f"✅ Feedback added: {result.success}")
    print(f"   Message: {result.message}")
    print(f"   Feedback ID: {result.feedback_id}")
    
    # Test getting stats
    stats = fm.get_feedback_stats()
    print(f"📊 Feedback stats: {stats}")
    
    # Test getting feedback for case
    case_feedback = fm.get_feedback_for_case("test_case_1")
    print(f"📝 Case feedback count: {len(case_feedback)}")
    
    # Test export
    export_success = fm.export_training_data("test_training_data.json")
    print(f"📤 Export success: {export_success}")
    
    # Clean up test files
    if os.path.exists("test_feedback.json"):
        os.remove("test_feedback.json")
    if os.path.exists("test_training_data.json"):
        os.remove("test_training_data.json")
    
    print("🎉 Feedback system test completed successfully!")

if __name__ == "__main__":
    test_feedback_system() 