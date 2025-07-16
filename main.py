"""Basic usage example for DOJ Research Agent."""
import os
from datetime import datetime
import json
from doj_research_agent import (
    CaseAnalyzer,
    ChargeCategorizer,
    DOJScraper,
    ScrapingConfig,
    ChargeCategory,
    create_summary_report,
    save_analysis_result,
    AnalysisResult,
    filter_cases_by_category,
)

USE_GPT4O = True  # Set to True to use GPT-4o for scraping structured data
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Or set to your key, or use env var

def main():
    """Basic usage example."""
    
    # Configure scraping
    config = ScrapingConfig(
        max_pages=2,
        max_cases=5,
        delay_between_requests=1.0
    )
    
    # Initialize components
    scraper = DOJScraper(config)
    analyzer = CaseAnalyzer()
    categorizer = ChargeCategorizer()
    
    print("Starting DOJ press release analysis...")
    
    # Scrape URLs
    urls = scraper.get_press_release_urls()
    print(f"Found {len(urls)} press release URLs")
    
    # Analyze cases
    cases = []
    total_cases = 0
    successful_extractions = 0
    failed_extractions = 0
    
    for i, url in enumerate(urls[:config.max_cases]):
        print(f"Analyzing case {i+1}/{min(len(urls), config.max_cases)}")
        total_cases += 1
        try:
            if USE_GPT4O:
                result = scraper.extract_structured_info_gpt4o_from_url(url, api_key=OPENAI_API_KEY)
                print(f"  - GPT-4o extracted: {result}")
                cases.append(result)
                successful_extractions += 1 if 'error' not in result else 0
                failed_extractions += 1 if 'error' in result else 0
            else:
                soup = scraper.fetch_press_release_content(url)
                if soup:
                    case_info = analyzer.analyze_press_release(url, soup)
                    if case_info:
                        successful_extractions += 1
                        # Categorize charges
                        charges_with_categories = []
                        for charge in case_info.charges:
                            categories = categorizer.categorize_charge(charge)
                            charges_with_categories.append({
                                'charge': charge,
                                'categories': categories
                            })
                        # Store charges with categories in case_info if needed
                        case_info.charges_with_categories = charges_with_categories
                        cases.append(case_info)
                        print(f"  - Successfully extracted case")
                        print(f"  - Charges found: {len(case_info.charges)}")
                    else:
                        failed_extractions += 1
                        print(f"  - Failed to extract case information from {url}")
                else:
                    failed_extractions += 1
                    print(f"  - Failed to fetch content from {url}")
        except Exception as e:
            failed_extractions += 1
            print(f"  - Error analyzing {url}: {e}")
    
    print(f"\nAnalysis complete!")
    print(f"Total cases processed: {total_cases}")
    print(f"Successful extractions: {successful_extractions}")
    print(f"Failed extractions: {failed_extractions}")
    if total_cases > 0:
        print(f"Success rate: {successful_extractions/total_cases*100:.1f}%")

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if USE_GPT4O:
        output_path = os.path.join(output_dir, f"gpt4o_results_{timestamp}.json")
    else:
        output_path = os.path.join(output_dir, f"complete_analysis_{timestamp}.json")
    
    if USE_GPT4O and cases:
        # Save with fraud info and charge count, and clean output format
        def case_to_clean_dict(case):
            d = case.to_dict() if hasattr(case, 'to_dict') else dict(case)
            # Remove unwanted fields
            d.pop('location', None)
            d.pop('case_type', None)
            d.pop('charge_categories', None)
            # Add charge_count
            d['charge_count'] = len(d.get('charges', []))
            # Add fraud_flag
            fraud_info = getattr(case, 'fraud_info', None)
            d['fraud_flag'] = bool(fraud_info.is_fraud) if fraud_info else False
            return d
        with open(output_path, "w") as f:
            json.dump([case_to_clean_dict(c) for c in cases], f, indent=2)
        # Save summary report with matching prefix
        summary_report_path = output_path.replace('.json', '_summary.json')
        summary_report = create_summary_report(cases)
        with open(summary_report_path, "w") as f:
            json.dump(summary_report, f, indent=2)
        print(f"\nGPT-4o results saved: {output_path}")
        print(f"Summary report saved: {summary_report_path}")

    if not USE_GPT4O and cases:
        # Save the complete analysis result in cleaned format
        def case_to_clean_dict(case):
            d = case.to_dict() if hasattr(case, 'to_dict') else dict(case)
            d.pop('location', None)
            d.pop('case_type', None)
            d.pop('charge_categories', None)
            d['charge_count'] = len(d.get('charges', []))
            fraud_info = getattr(case, 'fraud_info', None)
            d['fraud_flag'] = bool(fraud_info.is_fraud) if fraud_info else False
            return d
        cleaned_cases = [case_to_clean_dict(c) for c in cases]
        with open(output_path, "w") as f:
            json.dump({"cases": cleaned_cases}, f, indent=2)
        summary_report_path = output_path.replace('.json', '_summary.json')
        summary_report = create_summary_report(cases)
        with open(summary_report_path, "w") as f:
            json.dump(summary_report, f, indent=2)
        print(f"\nResults saved:")
        print(f"  - Complete analysis: {output_path}")
        print(f"  - Summary report: {summary_report_path}")
    
    return cases

def analyze_specific_category(category: ChargeCategory):
    """Analyze cases for a specific charge category."""
    config = ScrapingConfig(max_pages=3, max_cases=10, delay_between_requests=1.0)
    
    scraper = DOJScraper(config)
    analyzer = CaseAnalyzer()
    categorizer = ChargeCategorizer()
    
    print(f"Analyzing cases for category: {category.value}")
    
    urls = scraper.get_press_release_urls()
    cases = []
    
    for url in urls:
        try:
            soup = scraper.fetch_press_release_content(url)
            if soup:
                case_info = analyzer.analyze_press_release(url, soup)
                if case_info:
                    # Check if any charges match the target category
                    has_target_category = False
                    for charge in case_info.charges:
                        # categorize_charge may return a list now, so check for membership
                        charge_cats = categorizer.categorize_charge(charge)
                        if category in charge_cats:
                            has_target_category = True
                            break
                    if has_target_category:
                        cases.append(case_info)
                        print(f"Found relevant case: {case_info.title}")
        except Exception as e:
            print(f"Error analyzing {url}: {e}")
    
    print(f"Found {len(cases)} cases in category {category.value}")
    return cases

if __name__ == "__main__":
    try:
        analysis_result = main()
        
        # Optional: Analyze specific categories
        print("\n" + "="*50)
        print("Analyzing specific categories...")
        
        # Example: Focus on drug crimes
        drug_cases = analyze_specific_category(ChargeCategory.DRUGS)
        
        # Example: Focus on financial fraud
        financial_cases = analyze_specific_category(ChargeCategory.FINANCIAL_FRAUD)
        
        # Example: Focus on cybercrime
        cyber_cases = analyze_specific_category(ChargeCategory.CYBERCRIME)
        
        # Save category analysis results
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        category_results = {
            "drug_cases": [case.to_dict() for case in drug_cases],
            "financial_fraud_cases": [case.to_dict() for case in financial_cases],
            "cybercrime_cases": [case.to_dict() for case in cyber_cases],
            "summary": {
                "drug_cases_count": len(drug_cases),
                "financial_fraud_cases_count": len(financial_cases),
                "cybercrime_cases_count": len(cyber_cases)
            }
        }
        
        category_output_path = os.path.join(output_dir, f"category_analysis_{timestamp}.json")
        with open(category_output_path, "w") as f:
            json.dump(category_results, f, indent=2)
        
        print(f"\nCategory analysis results saved: {category_output_path}")
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()