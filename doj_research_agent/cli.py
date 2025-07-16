"""Command-line interface for DOJ research agent."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .analyzer import CaseAnalyzer
from .categorizer import ChargeCategorizer
from .models import AnalysisResult, ScrapingConfig, ChargeCategory
from .scraper import DOJScraper
from .utils import (
    create_summary_report,
    display_summary_table,
    export_to_csv,
    filter_cases_by_category,
    load_analysis_result,
    save_analysis_result,
    setup_logger,
    validate_config,
)

console = Console()
logger = setup_logger(__name__)


@click.group()
@click.version_option()
def cli():
    """DOJ Research Agent - Analyze DOJ press releases for indictments and convictions."""
    pass


@cli.command()
@click.option('--max-pages', default=20, help='Maximum number of pages to scrape')
@click.option('--max-cases', default=100, help='Maximum number of cases to analyze')
@click.option('--delay', default=1.0, help='Delay between requests (seconds)')
@click.option('--output', default='doj_analysis.json', help='Output file path')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def analyze(max_pages: int, max_cases: int, delay: float, output: str, 
           start_date: Optional[str], end_date: Optional[str], verbose: bool):
    """Analyze DOJ press releases and extract case information."""
    
    if verbose:
        logger.setLevel('DEBUG')
    
    console.print("[bold]Starting DOJ Press Release Analysis[/bold]")
    
    # Create configuration
    config = ScrapingConfig(
        max_pages=max_pages,
        max_cases=max_cases,
        delay_between_requests=delay,
        start_date=start_date,
        end_date=end_date
    )
    
    total_cases = 0
    successful_extractions = 0
    failed_extractions = 0
    cases = []
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Initialize components
            scraper = DOJScraper(config)
            analyzer = CaseAnalyzer()
            
            # Scrape URLs
            task = progress.add_task("Fetching press release URLs...", total=None)
            urls = scraper.get_press_release_urls()
            progress.update(task, description=f"Found {len(urls)} press release URLs")
            
            # Analyze cases
            task = progress.add_task("Analyzing cases...", total=min(len(urls), max_cases))
            
            for i, url in enumerate(urls[:max_cases]):
                progress.update(task, description=f"Analyzing case {i+1}/{min(len(urls), max_cases)}")
                
                total_cases += 1
                soup = scraper.fetch_press_release_content(url)
                
                if soup:
                    case_info = analyzer.analyze_press_release(url, soup)
                    if case_info:
                        cases.append(case_info)
                        successful_extractions += 1
                    else:
                        failed_extractions += 1
                else:
                    failed_extractions += 1
                
                progress.advance(task)
        
        # Create results
        result = AnalysisResult(
            cases=cases,
            total_cases=total_cases,
            successful_extractions=successful_extractions,
            failed_extractions=failed_extractions
        )
        
        # Save results
        save_analysis_result(result, output)
        console.print(f"\n[green]Analysis complete![/green]")
        console.print(f"Results saved to: {output}")
        console.print(f"Success rate: {result.success_rate():.1%}")
        
        # Display summary
        summary = create_summary_report(cases)
        display_summary_table(summary)
        
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('input_file')
@click.option('--format', 'output_format', type=click.Choice(['json', 'csv']), default='json')
@click.option('--output', help='Output file path')
@click.option('--category', type=click.Choice([cat.value for cat in ChargeCategory]), help='Filter by charge category')
def export(input_file: str, output_format: str, output: Optional[str], category: Optional[str]):
    """Export analysis results to different formats."""
    
    try:
        # Load results
        result = load_analysis_result(input_file)
        cases = result.cases
        
        # Filter by category if specified
        if category:
            cat_enum = ChargeCategory(category)
            cases = filter_cases_by_category(cases, cat_enum)
            console.print(f"Filtered to {len(cases)} cases in category: {category}")
        
        # Determine output path
        if not output:
            input_path = Path(input_file)
            output = str(input_path.with_suffix(f'.{output_format}'))
        
        # Export based on format
        if output_format == 'csv':
            export_to_csv(cases, output)
        else:
            data = [case.to_dict() for case in cases]
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        console.print(f"[green]Exported {len(cases)} cases to: {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error during export: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('input_file')
@click.option('--category', type=click.Choice([cat.value for cat in ChargeCategory]), help='Filter by charge category')
def summary(input_file: str, category: Optional[str]):
    """Display summary statistics from analysis results."""
    
    try:
        # Load results
        result = load_analysis_result(input_file)
        cases = result.cases
        
        # Filter by category if specified
        if category:
            cat_enum = ChargeCategory(category)
            cases = filter_cases_by_category(cases, cat_enum)
            console.print(f"[bold]Summary for category: {category}[/bold]")
        
        # Create and display summary
        summary_data = create_summary_report(cases)
        display_summary_table(summary_data)
        
    except Exception as e:
        console.print(f"[red]Error displaying summary: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('input_file')
@click.option('--category', type=click.Choice([cat.value for cat in ChargeCategory]), help='Filter by charge category')
@click.option('--limit', default=10, help='Number of cases to display')
def list_cases(input_file: str, category: Optional[str], limit: int):
    """List individual cases from analysis results."""
    
    try:
        # Load results
        result = load_analysis_result(input_file)
        cases = result.cases
        
        # Filter by category if specified
        if category:
            cat_enum = ChargeCategory(category)
            cases = filter_cases_by_category(cases, cat_enum)
        
        # Display cases
        console.print(f"[bold]Displaying {min(len(cases), limit)} cases[/bold]")
        
        for i, case in enumerate(cases[:limit]):
            console.print(f"\n[bold]{i+1}. {case.title}[/bold]")
            console.print(f"Date: {case.date}")
            # Removed Disposition, Defendant, Location
            console.print(f"Categories: {', '.join([cat.value for cat in case.charge_categories])}")
            if case.charges:
                console.print(f"Charges: {'; '.join(case.charges[:3])}{'...' if len(case.charges) > 3 else ''}")
            console.print(f"URL: {case.url}")
        
    except Exception as e:
        console.print(f"[red]Error listing cases: {e}[/red]")
        sys.exit(1)


@cli.command()
def categories():
    """List all available charge categories."""
    
    categorizer = ChargeCategorizer()
    
    console.print("[bold]Available Charge Categories[/bold]")
    
    for category in categorizer.get_all_categories():
        description = categorizer.get_category_description(category)
        keywords = categorizer.get_keywords_for_category(category)
        
        console.print(f"\n[bold]{category.value}[/bold]")
        console.print(f"Description: {description}")
        console.print(f"Keywords: {', '.join(list(keywords)[:10])}{'...' if len(keywords) > 10 else ''}")


@cli.command()
@click.argument('config_file')
def validate_config_file(config_file: str):
    """Validate a configuration file."""
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        errors = validate_config(config)
        
        if errors:
            console.print("[red]Configuration validation failed:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            sys.exit(1)
        else:
            console.print("[green]Configuration is valid![/green]")
            
    except Exception as e:
        console.print(f"[red]Error validating config: {e}[/red]")
        sys.exit(1)


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()