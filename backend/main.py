from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Any
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from doj_research_agent import (
    DOJScraper, ScrapingConfig, CaseAnalyzer, ChargeCategory
)
from doj_research_agent.core.feedback_manager import FeedbackManager
from doj_research_agent.core.models import FeedbackData
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

# Initialize feedback manager
feedback_manager = FeedbackManager()

def set_job(job_id, data):
    redis_client.set(f"job:{job_id}", json.dumps(data))

def get_job(job_id) -> Optional[dict]:
    data = redis_client.get(f"job:{job_id}")
    return json.loads(data) if data else None

class AnalysisRequest(BaseModel):
    query: Optional[str] = None  # Not used in this simple version, but could be for keyword search
    max_pages: int = 100  # Raised from 10 to 100
    max_cases: int = 1000  # Raised from 10 to 1000
    fraud_type: Optional[str] = None  # e.g., 'financial_fraud', 'cybercrime', etc.

class FeedbackRequest(BaseModel):
    case_id: str
    url: str
    user_feedback: str  # "positive", "negative", or "neutral"
    feedback_text: Optional[str] = None
    model_prediction: Optional[dict] = None
    confidence_score: Optional[float] = None

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

@app.get("/")
def root():
    return {"message": "DOJ Research Agent API is running."}

@app.post("/feedback/")
def submit_feedback(feedback: FeedbackRequest):
    """Submit user feedback for a case."""
    try:
        feedback_data = FeedbackData(
            case_id=feedback.case_id,
            url=feedback.url,
            user_feedback=feedback.user_feedback,
            feedback_text=feedback.feedback_text,
            model_prediction=feedback.model_prediction,
            confidence_score=feedback.confidence_score
        )
        
        result = feedback_manager.add_feedback(feedback_data)
        
        return {
            "success": result.success,
            "message": result.message,
            "feedback_id": result.feedback_id
        }
    except Exception as e:
        return {"success": False, "message": f"Error processing feedback: {str(e)}"}

@app.get("/feedback/stats")
def get_feedback_stats():
    """Get feedback statistics."""
    try:
        stats = feedback_manager.get_feedback_stats()
        return stats
    except Exception as e:
        return {"error": f"Error getting feedback stats: {str(e)}"}

@app.get("/feedback/case/{case_id}")
def get_case_feedback(case_id: str):
    """Get all feedback for a specific case."""
    try:
        feedback_list = feedback_manager.get_feedback_for_case(case_id)
        return {
            "case_id": case_id,
            "feedback_count": len(feedback_list),
            "feedback": [{
                "user_feedback": f.user_feedback,
                "feedback_text": f.feedback_text,
                "timestamp": f.timestamp.isoformat() if f.timestamp else None
            } for f in feedback_list]
        }
    except Exception as e:
        return {"error": f"Error getting case feedback: {str(e)}"}

@app.post("/feedback/export")
def export_training_data():
    """Export feedback data for model training."""
    try:
        success = feedback_manager.export_training_data()
        return {
            "success": success,
            "message": "Training data exported successfully" if success else "Failed to export training data"
        }
    except Exception as e:
        return {"success": False, "message": f"Error exporting training data: {str(e)}"}

@app.get("/feedback/improvements")
def get_model_improvements():
    """Get feedback-based model improvement insights."""
    try:
        from doj_research_agent.core.feedback_improver import FeedbackBasedImprover
        
        improver = FeedbackBasedImprover(feedback_manager)
        analysis = improver.analyze_feedback_patterns()
        improved_config = improver.get_improved_config()
        
        return {
            "success": True,
            "feedback_analysis": analysis,
            "improved_config": {
                "fraud_detection_threshold": improved_config.fraud_detection_threshold,
                "money_laundering_threshold": improved_config.money_laundering_threshold,
                "confidence_boost_factor": improved_config.confidence_boost_factor,
                "prompt_adjustment_factor": improved_config.prompt_adjustment_factor
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Error getting model improvements: {str(e)}"}

@app.post("/feedback/improvements/export")
def export_improvement_report():
    """Export a comprehensive model improvement report."""
    try:
        from doj_research_agent.core.feedback_improver import FeedbackBasedImprover
        
        improver = FeedbackBasedImprover(feedback_manager)
        success = improver.export_improvement_report()
        
        return {
            "success": success,
            "message": "Improvement report exported successfully" if success else "Failed to export improvement report"
        }
    except Exception as e:
        return {"success": False, "message": f"Error exporting improvement report: {str(e)}"}

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
    print(f"🔍 Starting analysis with max_pages={max_pages}, max_cases={max_cases}, fraud_type={fraud_type}")
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
        print(f"📄 Found {len(urls)} URLs to process for fraud_type={fraud_type}")
        cases = []
        for url in urls:
            if len(cases) >= max_cases:
                print(f"✅ Reached max_cases limit ({max_cases}), stopping analysis")
                break
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
                        print(f"✅ Added case {len(cases)}/{max_cases}: {case_info.title[:50]}...")
        print(f"🎯 Analysis complete: {len(cases)} cases found matching fraud_type={fraud_type}")
        return cases
    else:
        # No fraud_type: just analyze up to max_cases
        urls = scraper.get_press_release_urls()
        print(f"📄 Found {len(urls)} URLs to process")
        cases = []
        for url in urls:  # Process all URLs, not just first max_cases
            if len(cases) >= max_cases:  # Stop when we reach max_cases
                print(f"✅ Reached max_cases limit ({max_cases}), stopping analysis")
                break
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
                    print(f"✅ Added case {len(cases)}/{max_cases}: {case_info.title[:50]}...")
        print(f"🎯 Analysis complete: {len(cases)} cases processed")
        return cases 