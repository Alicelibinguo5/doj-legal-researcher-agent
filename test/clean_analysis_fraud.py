import json
from doj_research_agent import CaseAnalyzer, ChargeCategorizer

input_path = "output/complete_analysis_20250715_183409.json"
output_path = "output/complete_analysis_20250715_183409_fraud_cleaned.json"

with open(input_path, "r") as f:
    data = json.load(f)

analyzer = CaseAnalyzer()
categorizer = ChargeCategorizer()

cleaned_cases = []
for case in data["cases"]:
    # Remove unwanted fields
    case.pop("location", None)
    case.pop("case_type", None)
    case.pop("charge_categories", None)
    # Add charge_count
    charges = case.get("charges", [])
    case["charge_count"] = len(charges)
    # Add fraud_flag using analyzer
    content = case.get("description", "")
    categories = categorizer.categorize_charges(charges, content)
    fraud_info = analyzer._is_fraud_case(categories, content)
    case["fraud_flag"] = bool(fraud_info.is_fraud)
    cleaned_cases.append(case)

# Save new JSON
with open(output_path, "w") as f:
    json.dump({"cases": cleaned_cases}, f, indent=2)

print(f"Cleaned file saved to: {output_path}") 