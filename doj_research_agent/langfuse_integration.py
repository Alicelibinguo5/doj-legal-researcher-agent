"""
Langfuse integration for DOJ Research Agent evaluation and tracing.

This module provides functionality to trace evaluation runs and push scores
to Langfuse for monitoring and analysis.
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not available, continue without it
    pass

try:
    import langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False

from .evaluation_types import EvaluationResult, TestCase

logger = logging.getLogger(__name__)


class LangfuseTracer:
    """Langfuse integration for tracing evaluation runs and pushing scores."""
    
    def __init__(self, 
                 public_key: Optional[str] = None,
                 secret_key: Optional[str] = None,
                 host: Optional[str] = None,
                 enabled: Optional[bool] = None):
        """
        Initialize Langfuse tracer.
        
        Args:
            public_key: Langfuse public key (from env var LANGFUSE_PUBLIC_KEY)
            secret_key: Langfuse secret key (from env var LANGFUSE_SECRET_KEY)
            host: Langfuse host URL (from env var LANGFUSE_HOST)
            enabled: Whether tracing is enabled (from env var ENABLE_LANGFUSE_TRACING)
        """
        # Check if enabled from environment or parameter
        if enabled is None:
            enabled = os.getenv("ENABLE_LANGFUSE_TRACING", "true").lower() == "true"
        
        self.enabled = enabled and LANGFUSE_AVAILABLE
        
        if not self.enabled:
            logger.info("Langfuse tracing disabled or not available")
            return
            
        # Get credentials from environment or parameters
        self.public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        self.host = host or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if not self.public_key or not self.secret_key:
            logger.warning("Langfuse credentials not found. Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables.")
            self.enabled = False
            return
        
        try:
            # Initialize Langfuse client
            self.client = langfuse.Langfuse(
                public_key=self.public_key,
                secret_key=self.secret_key,
                host=self.host
            )
            logger.info(f"Langfuse client initialized successfully with host: {self.host}")
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse client: {e}")
            self.enabled = False
    
    def trace_evaluation_run(self, 
                           evaluation_result: EvaluationResult,
                           model_name: str,
                           model_provider: str,
                           test_cases: List[TestCase],
                           metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Create a trace for an evaluation run and push scores.
        
        Args:
            evaluation_result: Results from evaluation
            model_name: Name of the model being evaluated
            model_provider: Provider of the model
            test_cases: List of test cases used
            metadata: Additional metadata for the trace
            
        Returns:
            Trace ID if successful, None otherwise
        """
        if not self.enabled:
            return None
            
        try:
            # Create trace
            trace_metadata = {
                "model_name": model_name,
                "model_provider": model_provider,
                "evaluation_timestamp": evaluation_result.timestamp,
                "test_cases_count": len(test_cases),
                "evaluation_type": "fraud_detection",
                **(metadata or {})
            }
            
            trace = self.client.trace(
                name=f"fraud_detection_evaluation_{model_name}",
                metadata=trace_metadata
            )
            trace_id = trace.id if hasattr(trace, 'id') else str(trace)
            
            # Push overall scores
            self._push_overall_scores(trace_id, evaluation_result, model_name)
            
            # Push individual case scores
            self._push_case_scores(trace_id, evaluation_result, test_cases)
            
            # Push RAGAS scores if available
            if evaluation_result.ragas_scores:
                self._push_ragas_scores(trace_id, evaluation_result.ragas_scores)
            
            logger.info(f"Evaluation trace created with ID: {trace_id}")
            return trace_id
            
        except Exception as e:
            logger.error(f"Failed to create evaluation trace: {e}")
            return None
    
    def _push_overall_scores(self, trace_id: str, evaluation_result: EvaluationResult, model_name: str):
        """Push overall evaluation scores to Langfuse."""
        if not self.enabled:
            return
            
        try:
            # Main accuracy score
            self.client.score(
                trace_id=trace_id,
                name="fraud_detection_accuracy",
                value=evaluation_result.accuracy,
                comment=f"Overall fraud detection accuracy for {model_name}"
            )
            
            # Precision score
            self.client.score(
                trace_id=trace_id,
                name="fraud_detection_precision",
                value=evaluation_result.precision,
                comment=f"Fraud detection precision for {model_name}"
            )
            
            # Recall score
            self.client.score(
                trace_id=trace_id,
                name="fraud_detection_recall",
                value=evaluation_result.recall,
                comment=f"Fraud detection recall for {model_name}"
            )
            
            # F1 score
            self.client.score(
                trace_id=trace_id,
                name="fraud_detection_f1",
                value=evaluation_result.f1_score,
                comment=f"Fraud detection F1 score for {model_name}"
            )
            
            # Overall quality score (average of all metrics)
            overall_quality = (evaluation_result.accuracy + evaluation_result.precision + 
                             evaluation_result.recall + evaluation_result.f1_score) / 4
            self.client.score(
                trace_id=trace_id,
                name="fraud_detection_overall_quality",
                value=overall_quality,
                comment=f"Overall quality score for {model_name}"
            )
            
        except Exception as e:
            logger.error(f"Failed to push overall scores: {e}")
    
    def _push_case_scores(self, trace_id: str, evaluation_result: EvaluationResult, test_cases: List[TestCase]):
        """Push individual case scores to Langfuse."""
        if not self.enabled:
            return
            
        try:
            for i, (result, test_case) in enumerate(zip(evaluation_result.detailed_results, test_cases)):
                # Case-level accuracy
                case_correct = result.get('overall_correct', False)
                self.client.score(
                    trace_id=trace_id,
                    name=f"case_{i+1}_accuracy",
                    value=1.0 if case_correct else 0.0,
                    comment=f"Case {i+1}: {test_case.title}"
                )
                
                # Fraud flag accuracy
                fraud_correct = result.get('fraud_flag_correct', False)
                self.client.score(
                    trace_id=trace_id,
                    name=f"case_{i+1}_fraud_flag_accuracy",
                    value=1.0 if fraud_correct else 0.0,
                    comment=f"Case {i+1} fraud flag accuracy"
                )
                
                # Money laundering accuracy
                ml_correct = result.get('money_laundering_correct', False)
                self.client.score(
                    trace_id=trace_id,
                    name=f"case_{i+1}_money_laundering_accuracy",
                    value=1.0 if ml_correct else 0.0,
                    comment=f"Case {i+1} money laundering accuracy"
                )
                
                # LLM judge scores if available
                if 'llm_judgment' in result:
                    judgment = result['llm_judgment']
                    for score_name in ['fraud_accuracy', 'type_accuracy', 'evidence_quality', 
                                     'legal_reasoning', 'overall_quality']:
                        if score_name in judgment:
                            self.client.score(
                                trace_id=trace_id,
                                name=f"case_{i+1}_llm_judge_{score_name}",
                                value=judgment[score_name] / 10.0,  # Normalize to 0-1
                                comment=f"Case {i+1} LLM judge {score_name}"
                            )
                            
        except Exception as e:
            logger.error(f"Failed to push case scores: {e}")
    
    def _push_ragas_scores(self, trace_id: str, ragas_scores: Dict):
        """Push RAGAS evaluation scores to Langfuse."""
        if not self.enabled:
            return
            
        try:
            for metric_name, score in ragas_scores.items():
                if isinstance(score, (int, float)):
                    self.client.score(
                        trace_id=trace_id,
                        name=f"ragas_{metric_name}",
                        value=float(score),
                        comment=f"RAGAS {metric_name} score"
                    )
                    
        except Exception as e:
            logger.error(f"Failed to push RAGAS scores: {e}")
    
    def trace_single_case_evaluation(self,
                                   test_case: TestCase,
                                   prediction: Dict,
                                   model_name: str,
                                   metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Create a trace for a single case evaluation.
        
        Args:
            test_case: The test case being evaluated
            prediction: Model's prediction
            model_name: Name of the model
            metadata: Additional metadata
            
        Returns:
            Trace ID if successful, None otherwise
        """
        if not self.enabled:
            return None
            
        try:
            # Create trace for single case
            trace_metadata = {
                "model_name": model_name,
                "test_case_title": test_case.title,
                "expected_fraud": test_case.expected_fraud_flag,
                "predicted_fraud": prediction.get('fraud_flag', False),
                "case_type": "single_evaluation",
                **(metadata or {})
            }
            
            trace = self.client.trace(
                name=f"single_case_evaluation_{model_name}",
                metadata=trace_metadata
            )
            trace_id = trace.id if hasattr(trace, 'id') else str(trace)
            
            # Push case-specific scores
            fraud_correct = prediction.get('fraud_flag', False) == test_case.expected_fraud_flag
            self.client.score(
                trace_id=trace_id,
                name="fraud_detection_accuracy",
                value=1.0 if fraud_correct else 0.0,
                comment=f"Fraud detection accuracy for case: {test_case.title}"
            )
            
            logger.info(f"Single case trace created with ID: {trace_id}")
            return trace_id
            
        except Exception as e:
            logger.error(f"Failed to create single case trace: {e}")
            return None
    
    def close(self):
        """Close the Langfuse client."""
        if self.enabled and hasattr(self, 'client'):
            try:
                self.client.flush()
                logger.info("Langfuse client flushed and closed")
            except Exception as e:
                logger.error(f"Error closing Langfuse client: {e}")


# Global tracer instance
_global_tracer: Optional[LangfuseTracer] = None


def get_langfuse_tracer() -> Optional[LangfuseTracer]:
    """Get the global Langfuse tracer instance."""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = LangfuseTracer()
    return _global_tracer


def set_langfuse_tracer(tracer: LangfuseTracer):
    """Set the global Langfuse tracer instance."""
    global _global_tracer
    _global_tracer = tracer


def trace_evaluation(evaluation_result: EvaluationResult,
                    model_name: str,
                    model_provider: str,
                    test_cases: List[TestCase],
                    metadata: Optional[Dict] = None) -> Optional[str]:
    """
    Convenience function to trace an evaluation run.
    
    Args:
        evaluation_result: Results from evaluation
        model_name: Name of the model being evaluated
        model_provider: Provider of the model
        test_cases: List of test cases used
        metadata: Additional metadata for the trace
        
    Returns:
        Trace ID if successful, None otherwise
    """
    tracer = get_langfuse_tracer()
    if tracer:
        return tracer.trace_evaluation_run(
            evaluation_result=evaluation_result,
            model_name=model_name,
            model_provider=model_provider,
            test_cases=test_cases,
            metadata=metadata
        )
    return None 