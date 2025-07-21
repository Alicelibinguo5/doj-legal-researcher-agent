#!/usr/bin/env python3
"""Test script for feedback-based model improvement."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from doj_research_agent.core.feedback_manager import FeedbackManager
from doj_research_agent.core.feedback_improver import FeedbackBasedImprover
from doj_research_agent.core.models import FeedbackData

def test_feedback_improvement():
    """Test feedback-based model improvement functionality."""
    print("🧪 Testing Feedback-Based Model Improvement...")
    
    # Initialize feedback manager
    fm = FeedbackManager("test_feedback_improvement.json")
    
    # Add some test feedback
    test_feedback = [
        FeedbackData(
            case_id="case_1",
            url="https://example.com/case1",
            user_feedback="positive",
            model_prediction={"fraud_flag": True, "money_laundering_flag": False}
        ),
        FeedbackData(
            case_id="case_2", 
            url="https://example.com/case2",
            user_feedback="negative",
            model_prediction={"fraud_flag": True, "money_laundering_flag": True}
        ),
        FeedbackData(
            case_id="case_3",
            url="https://example.com/case3", 
            user_feedback="positive",
            model_prediction={"fraud_flag": False, "money_laundering_flag": False}
        ),
        FeedbackData(
            case_id="case_4",
            url="https://example.com/case4",
            user_feedback="negative", 
            model_prediction={"fraud_flag": False, "money_laundering_flag": True}
        )
    ]
    
    # Add feedback
    for feedback in test_feedback:
        result = fm.add_feedback(feedback)
        print(f"✅ Added feedback for {feedback.case_id}: {result.success}")
    
    # Test feedback-based improvement
    improver = FeedbackBasedImprover(fm)
    
    # Analyze feedback patterns
    analysis = improver.analyze_feedback_patterns()
    print(f"\n📊 Feedback Analysis:")
    print(f"  Total feedback: {analysis.get('total_feedback', 0)}")
    print(f"  Positive rate: {analysis.get('positive_rate', 0):.2%}")
    print(f"  Prediction accuracy: {analysis.get('prediction_accuracy', {}).get('overall_accuracy', 0):.2%}")
    
    # Get improved configuration
    improved_config = improver.get_improved_config()
    print(f"\n🔧 Improved Configuration:")
    print(f"  Fraud detection threshold: {improved_config.fraud_detection_threshold:.3f}")
    print(f"  Money laundering threshold: {improved_config.money_laundering_threshold:.3f}")
    
    # Export improvement report
    success = improver.export_improvement_report("test_improvement_report.json")
    print(f"\n📤 Improvement report exported: {success}")
    
    # Show improvement suggestions
    suggestions = analysis.get('improvement_suggestions', [])
    if suggestions:
        print(f"\n💡 Improvement Suggestions:")
        for suggestion in suggestions:
            print(f"  • {suggestion}")
    
    # Clean up test files
    if os.path.exists("test_feedback_improvement.json"):
        os.remove("test_feedback_improvement.json")
    if os.path.exists("test_improvement_report.json"):
        os.remove("test_improvement_report.json")
    
    print("\n🎉 Feedback-based model improvement test completed!")

if __name__ == "__main__":
    test_feedback_improvement() 