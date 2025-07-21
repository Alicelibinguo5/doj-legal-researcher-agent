"""
Data types for evaluation system.

This module contains the data structures used by the evaluation system
to avoid circular imports between evaluate.py and langfuse_integration.py.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class EvaluationResult:
    """Result of an evaluation run."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: List[List[int]]
    detailed_results: List[Dict]
    ragas_scores: Optional[Dict] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class TestCase:
    """Individual test case for evaluation."""
    text: str
    expected_fraud_flag: bool
    expected_fraud_type: Optional[str] = None
    expected_money_laundering_flag: bool = False
    title: Optional[str] = None
    source_url: Optional[str] = None
    ground_truth_rationale: Optional[str] = None 