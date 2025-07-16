"""Utility functions for DOJ research agent."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from rich.console import Console
from rich.table import Table

from .models import AnalysisResult, CaseInfo, ChargeCategory


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def save_to_json(data: Any, filepath: str, indent: int = 2) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        filepath: Path to save file
        indent: JSON indentation
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)


def load_from_json(filepath: str) -> Any:
    """
    Load data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_analysis_result(result: AnalysisResult, filepath: str) -> None:
    """
    Save analysis result to JSON file.
    
    Args:
        result: Analysis result to save
        filepath: Path to save file
    """
    save_to_json(result.to_dict(), filepath)


def load_analysis_result(filepath: str) -> AnalysisResult:
    """
    Load analysis result from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded analysis result
    """
    data = load_from_json(filepath)
    
    cases = [CaseInfo.from_dict(case_data) for case_data in data['cases']]
    
    return AnalysisResult(
        cases=cases,
        total_cases=data['total_cases'],
        successful_extractions=data['successful_extractions'],
        failed_extractions=data['failed_extractions'],
        analysis_date=datetime.fromisoformat(data['analysis_date'])
    )


def create_summary_report(cases: List[Any]) -> Dict[str, Any]:
    """
    Create summary statistics from cases, focusing on fraud and charge counts.
    """
    if not cases:
        return {
            'total_cases': 0,
            'fraud_cases': 0,
            'fraud_evidence': [],
            'total_charges': 0,
            'top_charges': {},
        }
    # Count all charges
    all_charges = []
    for case in cases:
        if hasattr(case, 'charges'):
            all_charges.extend(case.charges)
        elif 'charges' in case:
            all_charges.extend(case['charges'])
    total_charges = len(all_charges)
    # Top charges
    if all_charges:
        charge_counts = pd.Series(all_charges).value_counts()
        top_charges = charge_counts.head(10).to_dict()
    else:
        top_charges = {}
    # Fraud summary
    fraud_cases = 0
    fraud_evidence = []
    for case in cases:
        fraud_info = getattr(case, 'fraud_info', None)
        if fraud_info and getattr(fraud_info, 'is_fraud', False):
            fraud_cases += 1
            if fraud_info.evidence:
                fraud_evidence.append(fraud_info.evidence)
        elif isinstance(case, dict) and 'is_fraud' in case:
            if case['is_fraud']:
                fraud_cases += 1
                if 'fraud_evidence' in case and case['fraud_evidence']:
                    fraud_evidence.append(case['fraud_evidence'])
    return {
        'total_cases': len(cases),
        'fraud_cases': fraud_cases,
        'fraud_evidence': fraud_evidence[:10],
        'total_charges': total_charges,
        'top_charges': top_charges,
    }


def export_to_csv(cases: List[CaseInfo], filepath: str) -> None:
    """
    Export cases to CSV file.
    
    Args:
        cases: List of case information
        filepath: Path to save CSV file
    """
    if not cases:
        return
    
    # Convert to DataFrame
    df = pd.DataFrame([case.to_dict() for case in cases])
    
    # Flatten list columns
    df['charges'] = df['charges'].apply(lambda x: '; '.join(x) if isinstance(x, list) else x)
    df['charge_categories'] = df['charge_categories'].apply(lambda x: '; '.join(x) if isinstance(x, list) else x)
    
    # Save to CSV
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)


def display_summary_table(summary: Dict[str, Any]) -> None:
    """
    Display summary statistics in a formatted table.
    
    Args:
        summary: Summary statistics dictionary
    """
    console = Console()
    
    # Overall statistics
    console.print("\n[bold]Overall Statistics[/bold]")
    console.print(f"Total cases: {summary['total_cases']}")
    
    # Disposition breakdown
    if summary['disposition_breakdown']:
        console.print("\n[bold]Disposition Breakdown[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Disposition")
        table.add_column("Count", justify="right")
        
        for disposition, count in summary['disposition_breakdown'].items():
            table.add_row(disposition, str(count))
        
        console.print(table)
    
    # Case type breakdown
    if summary['case_type_breakdown']:
        console.print("\n[bold]Case Type Breakdown[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Case Type")
        table.add_column("Count", justify="right")
        
        for case_type, count in summary['case_type_breakdown'].items():
            table.add_row(case_type, str(count))
        
        console.print(table)
    
    # Charge categories
    if summary['charge_categories']:
        console.print("\n[bold]Charge Categories[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Category")
        table.add_column("Count", justify="right")
        
        for category, count in summary['charge_categories'].items():
            table.add_row(category, str(count))
        
        console.print(table)
    
    # Top locations
    if summary['locations']:
        console.print("\n[bold]Top Locations[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Location")
        table.add_column("Count", justify="right")
        
        for location, count in summary['locations'].items():
            table.add_row(location, str(count))
        
        console.print(table)


def filter_cases_by_category(cases: List[CaseInfo], category: ChargeCategory) -> List[CaseInfo]:
    """
    Filter cases by charge category.
    
    Args:
        cases: List of case information
        category: Charge category to filter by
        
    Returns:
        Filtered list of cases
    """
    return [case for case in cases if category in case.charge_categories]


def filter_cases_by_date_range(cases: List[CaseInfo], start_date: str, end_date: str) -> List[CaseInfo]:
    """
    Filter cases by date range.
    
    Args:
        cases: List of case information
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Filtered list of cases
    """
    # This is a simplified implementation
    # In practice, you'd want to properly parse the date field
    return [case for case in cases if start_date <= case.date <= end_date]


def get_unique_charges(cases: List[CaseInfo]) -> List[str]:
    """
    Get unique charges from all cases.
    
    Args:
        cases: List of case information
        
    Returns:
        List of unique charges
    """
    all_charges = set()
    for case in cases:
        all_charges.update(case.charges)
    return sorted(list(all_charges))


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['base_url', 'max_pages', 'max_cases']
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Type validations
    if 'max_pages' in config and not isinstance(config['max_pages'], int):
        errors.append("max_pages must be an integer")
    
    if 'max_cases' in config and not isinstance(config['max_cases'], int):
        errors.append("max_cases must be an integer")
    
    if 'delay_between_requests' in config and not isinstance(config['delay_between_requests'], (int, float)):
        errors.append("delay_between_requests must be a number")
    
    return errors