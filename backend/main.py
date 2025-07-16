from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Any
from doj_research_agent import (
    DOJScraper, ScrapingConfig, CaseAnalyzer, ChargeCategory
)
import os
import uuid
from threading import Lock

app = FastAPI()

# In-memory job store (for demo; use Redis/db for production)
jobs = {}
jobs_lock = Lock()

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
    with jobs_lock:
        jobs[job_id] = {"status": "pending", "result": None, "error": None}
    background_tasks.add_task(run_agent_job, job_id, request)
    return {"job_id": job_id}

@app.get("/job/{job_id}")
def get_job(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return {"error": "Job not found", "status": "not_found"}
        return {"job_id": job_id, "status": job["status"], "result": job["result"], "error": job["error"]}

def run_agent_job(job_id: str, request: AnalysisRequest):
    with jobs_lock:
        jobs[job_id]["status"] = "running"
    try:
        results = run_agent(request.query, request.max_pages, request.max_cases, request.fraud_type)
        with jobs_lock:
            jobs[job_id]["status"] = "done"
            jobs[job_id]["result"] = results
    except Exception as e:
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)

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
                        case_dict = case_info.to_dict()
                        # Attach classic fraud_info if present
                        if hasattr(case_info, 'fraud_info') and case_info.fraud_info:
                            case_dict['fraud_info'] = case_info.fraud_info.__dict__
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
                    case_dict = case_info.to_dict()
                    # Attach classic fraud_info if present
                    if hasattr(case_info, 'fraud_info') and case_info.fraud_info:
                        case_dict['fraud_info'] = case_info.fraud_info.__dict__
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