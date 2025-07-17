from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Any
from doj_research_agent import (
    DOJScraper, ScrapingConfig, CaseAnalyzer, ChargeCategory
)
import os
import uuid
import redis
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or explicitly your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)
# In-memory job store (for demo; use Redis/db for production)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def set_job(job_id, data):
    redis_client.set(f"job:{job_id}", json.dumps(data))

def get_job(job_id):
    data = redis_client.get(f"job:{job_id}")
    return json.loads(data) if data else None

class AnalysisRequest(BaseModel):
    query: Optional[str] = None  # Not used in this simple version, but could be for keyword search
    max_pages: int = 2
    max_cases: int = 5
    fraud_type: Optional[str] = None  # e.g., 'financial_fraud', 'cybercrime', etc.

class JobStatus(BaseModel):
    job_id: str
    status: str  # 'pending', 'running', 'done', 'error'
    result: Optional[Any] = None
    error: Optional[str] = None

@app.post("/analyze/")
def analyze(request: AnalysisRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    set_job(job_id, {"status": "pending", "result": None, "error": None})
    background_tasks.add_task(run_agent_job, job_id, request)
    return {"job_id": job_id}

@app.get("/job/{job_id}")
def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        return {"error": "Job not found", "status": "not_found"}
    return {"job_id": job_id, "status": job["status"], "result": job["result"], "error": job["error"]}

def run_agent_job(job_id: str, request: AnalysisRequest):
    set_job(job_id, {"status": "running", "result": None, "error": None})
    try:
        results = run_agent(request.query, request.max_pages, request.max_cases, request.fraud_type)
        set_job(job_id, {"status": "done", "result": results, "error": None})
    except Exception as e:
        set_job(job_id, {"status": "error", "result": None, "error": str(e)})

# Helper to ensure charge_categories are always strings

def case_to_clean_dict(case_info):
    d = case_info.to_dict() if hasattr(case_info, 'to_dict') else dict(case_info)
    # Convert charge_categories to string values if present
    if 'charge_categories' in d:
        d['charge_categories'] = [c if isinstance(c, str) else getattr(c, 'value', str(c)) for c in d['charge_categories']]
    return d

def clean_fraud_info(fraud_info):
    if not fraud_info:
        return None
    d = fraud_info.__dict__.copy()
    if 'charge_categories' in d:
        d['charge_categories'] = [c if isinstance(c, str) else getattr(c, 'value', str(c)) for c in d['charge_categories']]
    return d

# Minimal agent runner using your backend logic
def run_agent(query: Optional[str], max_pages: int, max_cases: int, fraud_type: Optional[str]) -> List[Any]:
    config = ScrapingConfig(max_pages=max_pages, max_cases=max_cases, delay_between_requests=1.0)
    scraper = DOJScraper(config)
    analyzer = CaseAnalyzer()
    # If fraud_type is specified, filter by category
    if fraud_type:
        try:
            category = ChargeCategory(fraud_type)
        except ValueError:
            return [{"error": f"Unknown fraud_type: {fraud_type}"}]
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
                        charge_cats = analyzer.categorizer.categorize_charge(charge)
                        if category in charge_cats:
                            has_target_category = True
                            break
                    if has_target_category:
                        case_dict = case_to_clean_dict(case_info)
                        # Attach classic fraud_info if present
                        if hasattr(case_info, 'fraud_info') and case_info.fraud_info:
                            case_dict['fraud_info'] = clean_fraud_info(case_info.fraud_info)
                        # Attach money laundering info if present
                        if hasattr(case_info, 'money_laundering_flag'):
                            case_dict['money_laundering_flag'] = case_info.money_laundering_flag
                        if hasattr(case_info, 'money_laundering_evidence'):
                            case_dict['money_laundering_evidence'] = case_info.money_laundering_evidence
                        # Attach gpt4o if present
                        if hasattr(case_info, 'gpt4o') and case_info.gpt4o:
                            case_dict['gpt4o'] = case_info.gpt4o
                        cases.append(case_dict)
                    if len(cases) >= max_cases:
                        break
        return cases
    else:
        # No fraud_type: just analyze up to max_cases
        urls = scraper.get_press_release_urls()
        cases = []
        for url in urls[:max_cases]:
            soup = scraper.fetch_press_release_content(url)
            if soup:
                case_info = analyzer.analyze_press_release(url, soup)
                if case_info:
                    case_dict = case_to_clean_dict(case_info)
                    # Attach classic fraud_info if present
                    if hasattr(case_info, 'fraud_info') and case_info.fraud_info:
                        case_dict['fraud_info'] = clean_fraud_info(case_info.fraud_info)
                    # Attach money laundering info if present
                    if hasattr(case_info, 'money_laundering_flag'):
                        case_dict['money_laundering_flag'] = case_info.money_laundering_flag
                    if hasattr(case_info, 'money_laundering_evidence'):
                        case_dict['money_laundering_evidence'] = case_info.money_laundering_evidence
                    # Attach gpt4o if present
                    if hasattr(case_info, 'gpt4o') and case_info.gpt4o:
                        case_dict['gpt4o'] = case_info.gpt4o
                    cases.append(case_dict)
        return cases 