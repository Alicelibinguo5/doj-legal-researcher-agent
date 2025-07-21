"""DOJ Research Agent - A Python tool for analyzing DOJ press releases."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core imports
from .core.models import (
    AnalysisResult,
    CaseInfo,
    CaseType,
    ChargeCategory,
    Disposition,
    ScrapingConfig,
)
from .core.utils import (
    create_summary_report,
    export_to_csv,
    filter_cases_by_category,
    load_analysis_result,
    save_analysis_result,
    setup_logger,
)

# Analysis imports
from .analysis.analyzer import CaseAnalyzer
from .analysis.categorizer import ChargeCategorizer

# Scraping imports
from .scraping.scraper import DOJScraper

# Orchestration imports
from .orchestrator import ResearchOrchestrator

# Evaluation imports
from .evaluation.evaluate import (
    FraudDetectionEvaluator,
    quick_eval,
    quick_eval_real_data,
)
from .evaluation.evaluation_types import EvaluationResult, TestCase

# LLM imports
from .llm.llm import LLMManager, extract_structured_info
from .llm.llm_models import CaseAnalysisResponse

__all__ = [
    # Main classes
    "CaseAnalyzer",
    "ChargeCategorizer",
    "DOJScraper",
    "ResearchOrchestrator",
    "FraudDetectionEvaluator",
    "LLMManager",
    
    # Models
    "AnalysisResult",
    "CaseInfo",
    "CaseType",
    "ChargeCategory",
    "Disposition",
    "ScrapingConfig",
    "EvaluationResult",
    "TestCase",
    "CaseAnalysisResponse",
    
    # Utilities
    "create_summary_report",
    "export_to_csv",
    "filter_cases_by_category",
    "load_analysis_result",
    "save_analysis_result",
    "setup_logger",
    
    # Evaluation functions
    "quick_eval",
    "quick_eval_real_data",
    "extract_structured_info",
]