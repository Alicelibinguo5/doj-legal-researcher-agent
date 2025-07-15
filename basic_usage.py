"""Basic usage example for DOJ Research Agent."""
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

def main():
    """Basic usage example."""
    
    # Configure scraping
    config = ScrapingConfig(
        max_pages=5,
        max_cases=20,
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
    
    for i, url in enumerate(urls[:config.max_cases]):
        print(f"Analyzing case {i+1}/{min(len(urls), config.max_cases)}")
        
        total_cases += 1
        soup = scraper.fetch_press_release_content(url)
        
        if soup:
            case_info = analyzer.analyze_press_release(url, soup)
            if case_info:
                successful_extractions += 1
                
                # Categorize charges
                charges_with_categories = []
                for charge in case_info.charges:
                    category = categorizer.categorize_charge(charge)
                    charges_with_categories.append({
                        'charge': charge,
                        'category': category
                    })
                
                # Create analysis result
                analysis_result = AnalysisResult(
                    case_info=case_info,
                    charges_with_categories=charges_with_categories,
                    analysis_date=analyzer.get_current_date()
                )
                
                cases.append(analysis_result)
                print(f"  - Successfully extracted: {case_info.defendant_name}")
                print(f"  - Charges found: {len(case_info.charges)}")
                print(f"  - Jurisdiction: {case_info.jurisdiction}")
            else:
                print(f"  - Failed to extract case information from {url}")
        else:
            print(f"  - Failed to fetch content from {url}")
    
    print(f"\nAnalysis complete!")
    print(f"Total cases processed: {total_cases}")
    print(f"Successful extractions: {successful_extractions}")
    print(f"Success rate: {successful_extractions/total_cases*100:.1f}%")
    
    # Generate category breakdown
    if cases:
        print("\nCharge Category Breakdown:")
        category_counts = {}
        for case in cases:
            for charge_info in case.charges_with_categories:
                category = charge_info['category']
                category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {category.value}: {count} charges")
    
    # Filter cases by category (example: white collar crimes)
    white_collar_cases = filter_cases_by_category(cases, ChargeCategory.WHITE_COLLAR)
    print(f"\nWhite collar cases found: {len(white_collar_cases)}")
    
    # Save results
    if cases:
        # Save individual case analyses
        for i, case in enumerate(cases):
            filename = f"case_analysis_{i+1}.json"
            save_analysis_result(case, filename)
        
        # Create summary report
        summary_report = create_summary_report(cases)
        with open("doj_analysis_summary.txt", "w") as f:
            f.write(summary_report)
        
        print(f"\nResults saved:")
        print(f"  - Individual case files: case_analysis_1.json to case_analysis_{len(cases)}.json")
        print(f"  - Summary report: doj_analysis_summary.txt")
    
    # Display sample case information
    if cases:
        print("\nSample Case Information:")
        sample_case = cases[0]
        print(f"  Defendant: {sample_case.case_info.defendant_name}")
        print(f"  Date: {sample_case.case_info.date}")
        print(f"  Jurisdiction: {sample_case.case_info.jurisdiction}")
        print(f"  Charges: {len(sample_case.case_info.charges)}")
        if sample_case.case_info.charges:
            print(f"  First charge: {sample_case.case_info.charges[0]}")
        if sample_case.case_info.sentence:
            print(f"  Sentence: {sample_case.case_info.sentence}")

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
        soup = scraper.fetch_press_release_content(url)
        if soup:
            case_info = analyzer.analyze_press_release(url, soup)
            if case_info:
                # Check if any charges match the target category
                has_target_category = False
                for charge in case_info.charges:
                    if categorizer.categorize_charge(charge) == category:
                        has_target_category = True
                        break
                
                if has_target_category:
                    cases.append(case_info)
                    print(f"Found relevant case: {case_info.defendant_name}")
    
    print(f"Found {len(cases)} cases in category {category.value}")
    return cases

if __name__ == "__main__":
    try:
        main()
        
        # Optional: Analyze specific categories
        print("\n" + "="*50)
        print("Analyzing specific categories...")
        
        # Example: Focus on drug trafficking cases
        drug_cases = analyze_specific_category(ChargeCategory.DRUG_TRAFFICKING)
        
        # Example: Focus on fraud cases
        fraud_cases = analyze_specific_category(ChargeCategory.FRAUD)
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()