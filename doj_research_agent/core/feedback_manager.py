"""Feedback management system for human-in-the-loop learning."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from .models import FeedbackData, FeedbackResult
from .utils import setup_logger

logger = setup_logger(__name__)


class FeedbackManager:
    """Manages user feedback collection and processing for model improvement."""
    
    def __init__(self, feedback_file: str = "feedback_data.json"):
        """
        Initialize the feedback manager.
        
        Args:
            feedback_file: Path to store feedback data
        """
        self.feedback_file = Path(feedback_file)
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_feedback_data()
    
    def _load_feedback_data(self) -> None:
        """Load existing feedback data from file."""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    self.feedback_data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading feedback data: {e}")
                self.feedback_data = []
        else:
            self.feedback_data = []
    
    def _save_feedback_data(self) -> None:
        """Save feedback data to file."""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving feedback data: {e}")
    
    def add_feedback(self, feedback: FeedbackData) -> FeedbackResult:
        """
        Add new user feedback.
        
        Args:
            feedback: Feedback data to add
            
        Returns:
            FeedbackResult with success status and message
        """
        try:
            # Generate unique feedback ID
            feedback_id = str(uuid.uuid4())
            
            # Add timestamp if not provided
            if not feedback.timestamp:
                feedback.timestamp = datetime.now()
            
            # Convert to dict for storage
            feedback_dict = {
                "feedback_id": feedback_id,
                "case_id": feedback.case_id,
                "url": feedback.url,
                "user_feedback": feedback.user_feedback,
                "feedback_text": feedback.feedback_text,
                "timestamp": feedback.timestamp.isoformat(),
                "model_prediction": feedback.model_prediction,
                "confidence_score": feedback.confidence_score
            }
            
            self.feedback_data.append(feedback_dict)
            self._save_feedback_data()
            
            logger.info(f"Feedback added successfully: {feedback_id}")
            
            return FeedbackResult(
                success=True,
                message="Feedback recorded successfully",
                feedback_id=feedback_id,
                training_data_updated=True
            )
            
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            return FeedbackResult(
                success=False,
                message=f"Error recording feedback: {str(e)}"
            )
    
    def get_feedback_for_case(self, case_id: str) -> List[FeedbackData]:
        """
        Get all feedback for a specific case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of feedback data for the case
        """
        feedback_list = []
        for item in self.feedback_data:
            if item.get("case_id") == case_id:
                feedback = FeedbackData(
                    case_id=item["case_id"],
                    url=item["url"],
                    user_feedback=item["user_feedback"],
                    feedback_text=item.get("feedback_text"),
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    model_prediction=item.get("model_prediction"),
                    confidence_score=item.get("confidence_score")
                )
                feedback_list.append(feedback)
        
        return feedback_list
    
    def get_all_feedback(self) -> List[FeedbackData]:
        """
        Get all feedback data.
        
        Returns:
            List of all feedback data
        """
        feedback_list = []
        for item in self.feedback_data:
            feedback = FeedbackData(
                case_id=item["case_id"],
                url=item["url"],
                user_feedback=item["user_feedback"],
                feedback_text=item.get("feedback_text"),
                timestamp=datetime.fromisoformat(item["timestamp"]),
                model_prediction=item.get("model_prediction"),
                confidence_score=item.get("confidence_score")
            )
            feedback_list.append(feedback)
        
        return feedback_list
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get feedback statistics.
        
        Returns:
            Dictionary with feedback statistics
        """
        if not self.feedback_data:
            return {
                "total_feedback": 0,
                "positive_feedback": 0,
                "negative_feedback": 0,
                "neutral_feedback": 0
            }
        
        total = len(self.feedback_data)
        positive = sum(1 for item in self.feedback_data if item["user_feedback"] == "positive")
        negative = sum(1 for item in self.feedback_data if item["user_feedback"] == "negative")
        neutral = sum(1 for item in self.feedback_data if item["user_feedback"] == "neutral")
        
        return {
            "total_feedback": total,
            "positive_feedback": positive,
            "negative_feedback": negative,
            "neutral_feedback": neutral,
            "positive_rate": positive / total if total > 0 else 0,
            "negative_rate": negative / total if total > 0 else 0
        }
    
    def export_training_data(self, output_file: str = "training_data.json") -> bool:
        """
        Export feedback data for model training.
        
        Args:
            output_file: Output file path
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            training_data = {
                "feedback_data": self.feedback_data,
                "stats": self.get_feedback_stats(),
                "export_timestamp": datetime.now().isoformat()
            }
            
            with open(output_file, 'w') as f:
                json.dump(training_data, f, indent=2, default=str)
            
            logger.info(f"Training data exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting training data: {e}")
            return False 