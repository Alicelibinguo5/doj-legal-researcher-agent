"""LLM module for DOJ Research Agent.

This module contains the LLM integration functionality for extracting
structured information from DOJ press releases.
"""

from .llm import LLMManager, extract_structured_info
from .llm_models import CaseAnalysisResponse

__all__ = [
    "LLMManager",
    "extract_structured_info",
    "CaseAnalysisResponse",
]
