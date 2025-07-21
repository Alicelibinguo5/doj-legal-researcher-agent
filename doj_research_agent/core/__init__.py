"""Core module for DOJ Research Agent.

This module contains the fundamental data models, constants, and utilities
used throughout the application.
"""

from .models import (
    AnalysisResult,
    CaseInfo,
    CaseType,
    ChargeCategory,
    Disposition,
    ScrapingConfig,
)
from .utils import (
    create_summary_report,
    export_to_csv,
    filter_cases_by_category,
    load_analysis_result,
    save_analysis_result,
    setup_logger,
)

__all__ = [
    # Models
    "AnalysisResult",
    "CaseInfo", 
    "CaseType",
    "ChargeCategory",
    "Disposition",
    "ScrapingConfig",
    
    # Utilities
    "create_summary_report",
    "export_to_csv",
    "filter_cases_by_category",
    "load_analysis_result",
    "save_analysis_result",
    "setup_logger",
]
