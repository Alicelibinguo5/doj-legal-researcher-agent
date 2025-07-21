"""Evaluation module for DOJ Research Agent.

This module contains the evaluation functionality for assessing
fraud detection performance with Langfuse integration.
"""

from .evaluate import FraudDetectionEvaluator, quick_eval, quick_eval_real_data
from .evaluation_types import EvaluationResult, TestCase
from .langfuse_integration import LangfuseTracer, get_langfuse_tracer, trace_evaluation

__all__ = [
    "FraudDetectionEvaluator",
    "quick_eval",
    "quick_eval_real_data",
    "EvaluationResult",
    "TestCase",
    "LangfuseTracer",
    "get_langfuse_tracer",
    "trace_evaluation",
]
