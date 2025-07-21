"""DOJ Research Agent - A Python tool for analyzing DOJ press releases."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .analyzer import CaseAnalyzer
from .categorizer import ChargeCategorizer
from .orchestrator import ResearchOrchestrator
from .models import (
    AnalysisResult,
    CaseInfo,
    CaseType,
    ChargeCategory,
    Disposition,
    ScrapingConfig,
)
from .scraper import DOJScraper
from .utils import (
    create_summary_report,
    export_to_csv,
    filter_cases_by_category,
    load_analysis_result,
    save_analysis_result,
    setup_logger,
)

__all__ = [
    # Main classes
    "CaseAnalyzer",
    "ChargeCategorizer",
    "DOJScraper",
    "ResearchOrchestrator",
    
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