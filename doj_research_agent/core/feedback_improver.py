"""Feedback-based model improvement system."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .feedback_manager import FeedbackManager
from .models import FeedbackData
from .utils import setup_logger

logger = setup_logger(__name__)


@dataclass
class ModelImprovementConfig:
    """Configuration for model improvement based on feedback."""
    fraud_detection_threshold: float = 0.7
    money_laundering_threshold: float = 0.6
    confidence_boost_factor: float = 1.1
    prompt_adjustment_factor: float = 0.1


class FeedbackBasedImprover:
    """Uses feedback data to improve model performance."""
    
    def __init__(self, feedback_manager: FeedbackManager):
        """
        Initialize the feedback-based improver.
        
        Args:
            feedback_manager: Manager to access feedback data
        """
        self.feedback_manager = feedback_manager
        self.config = ModelImprovementConfig()
    
    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """
        Analyze feedback patterns to identify improvement opportunities.
        
        Returns:
            Dictionary with feedback analysis insights
        """
        all_feedback = self.feedback_manager.get_all_feedback()
        
        if not all_feedback:
            return {"message": "No feedback data available"}
        
        # Categorize feedback
        positive_feedback = [f for f in all_feedback if f.user_feedback == "positive"]
        negative_feedback = [f for f in all_feedback if f.user_feedback == "negative"]
        neutral_feedback = [f for f in all_feedback if f.user_feedback == "neutral"]
        
        # Analyze model predictions vs feedback
        prediction_accuracy = self._analyze_prediction_accuracy(all_feedback)
        
        # Analyze fraud detection patterns
        fraud_patterns = self._analyze_fraud_patterns(all_feedback)
        
        # Analyze money laundering patterns
        laundering_patterns = self._analyze_laundering_patterns(all_feedback)
        
        return {
            "total_feedback": len(all_feedback),
            "positive_count": len(positive_feedback),
            "negative_count": len(negative_feedback),
            "neutral_count": len(neutral_feedback),
            "positive_rate": len(positive_feedback) / len(all_feedback) if all_feedback else 0,
            "prediction_accuracy": prediction_accuracy,
            "fraud_patterns": fraud_patterns,
            "laundering_patterns": laundering_patterns,
            "improvement_suggestions": self._generate_improvement_suggestions(
                positive_feedback, negative_feedback, prediction_accuracy
            )
        }
    
    def _analyze_prediction_accuracy(self, feedback: List[FeedbackData]) -> Dict[str, float]:
        """Analyze how well model predictions align with user feedback."""
        if not feedback:
            return {"overall_accuracy": 0.0}
        
        correct_predictions = 0
        total_predictions = 0
        
        for f in feedback:
            if f.model_prediction and f.user_feedback in ["positive", "negative"]:
                total_predictions += 1
                # Consider positive feedback as agreement with model prediction
                if f.user_feedback == "positive":
                    correct_predictions += 1
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        
        return {
            "overall_accuracy": accuracy,
            "correct_predictions": correct_predictions,
            "total_predictions": total_predictions
        }
    
    def _analyze_fraud_patterns(self, feedback: List[FeedbackData]) -> Dict[str, Any]:
        """Analyze fraud detection patterns in feedback."""
        fraud_feedback = [f for f in feedback if f.model_prediction and f.model_prediction.get("fraud_flag")]
        non_fraud_feedback = [f for f in feedback if f.model_prediction and not f.model_prediction.get("fraud_flag")]
        
        fraud_accuracy = self._calculate_category_accuracy(fraud_feedback)
        non_fraud_accuracy = self._calculate_category_accuracy(non_fraud_feedback)
        
        return {
            "fraud_detection_accuracy": fraud_accuracy,
            "non_fraud_accuracy": non_fraud_accuracy,
            "fraud_feedback_count": len(fraud_feedback),
            "non_fraud_feedback_count": len(non_fraud_feedback)
        }
    
    def _analyze_laundering_patterns(self, feedback: List[FeedbackData]) -> Dict[str, Any]:
        """Analyze money laundering detection patterns in feedback."""
        laundering_feedback = [f for f in feedback if f.model_prediction and f.model_prediction.get("money_laundering_flag")]
        non_laundering_feedback = [f for f in feedback if f.model_prediction and not f.model_prediction.get("money_laundering_flag")]
        
        laundering_accuracy = self._calculate_category_accuracy(laundering_feedback)
        non_laundering_accuracy = self._calculate_category_accuracy(non_laundering_feedback)
        
        return {
            "laundering_detection_accuracy": laundering_accuracy,
            "non_laundering_accuracy": non_laundering_accuracy,
            "laundering_feedback_count": len(laundering_feedback),
            "non_laundering_feedback_count": len(non_laundering_feedback)
        }
    
    def _calculate_category_accuracy(self, feedback: List[FeedbackData]) -> float:
        """Calculate accuracy for a specific category of feedback."""
        if not feedback:
            return 0.0
        
        positive_count = sum(1 for f in feedback if f.user_feedback == "positive")
        return positive_count / len(feedback)
    
    def _generate_improvement_suggestions(self, positive_feedback: List[FeedbackData], 
                                        negative_feedback: List[FeedbackData],
                                        prediction_accuracy: Dict[str, float]) -> List[str]:
        """Generate improvement suggestions based on feedback analysis."""
        suggestions = []
        
        # Overall accuracy suggestions
        if prediction_accuracy.get("overall_accuracy", 0) < 0.7:
            suggestions.append("Consider adjusting fraud detection thresholds - low overall accuracy detected")
        
        # Fraud detection suggestions
        if len(positive_feedback) > len(negative_feedback):
            suggestions.append("Model performing well - consider maintaining current parameters")
        else:
            suggestions.append("High negative feedback - consider retraining with more diverse data")
        
        # Threshold suggestions
        if len(negative_feedback) > 10:
            suggestions.append("Significant negative feedback - recommend threshold adjustment")
        
        return suggestions
    
    def get_improved_config(self) -> ModelImprovementConfig:
        """
        Get improved configuration based on feedback analysis.
        
        Returns:
            Updated configuration with improved parameters
        """
        analysis = self.analyze_feedback_patterns()
        
        # Adjust thresholds based on feedback
        if analysis.get("prediction_accuracy", {}).get("overall_accuracy", 0) < 0.7:
            # Lower thresholds if accuracy is poor
            self.config.fraud_detection_threshold *= 0.9
            self.config.money_laundering_threshold *= 0.9
            logger.info("Lowering detection thresholds due to poor feedback accuracy")
        
        if analysis.get("positive_rate", 0) > 0.8:
            # Increase thresholds if performance is good
            self.config.fraud_detection_threshold *= 1.1
            self.config.money_laundering_threshold *= 1.1
            logger.info("Increasing detection thresholds due to good feedback performance")
        
        return self.config
    
    def export_improvement_report(self, output_file: str = "model_improvement_report.json") -> bool:
        """
        Export a comprehensive improvement report.
        
        Args:
            output_file: Path to save the report
            
        Returns:
            True if export successful
        """
        try:
            import json
            from datetime import datetime
            
            analysis = self.analyze_feedback_patterns()
            improved_config = self.get_improved_config()
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "feedback_analysis": analysis,
                "improved_config": {
                    "fraud_detection_threshold": improved_config.fraud_detection_threshold,
                    "money_laundering_threshold": improved_config.money_laundering_threshold,
                    "confidence_boost_factor": improved_config.confidence_boost_factor,
                    "prompt_adjustment_factor": improved_config.prompt_adjustment_factor
                },
                "recommendations": analysis.get("improvement_suggestions", [])
            }
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Model improvement report exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting improvement report: {e}")
            return False 