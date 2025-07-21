"""Data models for DOJ research agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class CaseType(Enum):
    """Enumeration of case types."""
    CRIMINAL = "criminal"
    CIVIL = "civil"
    PLEA = "plea"
    UNKNOWN = "unknown"


class Disposition(Enum):
    """Enumeration of case dispositions."""
    SENTENCED = "sentenced"
    CONVICTED = "convicted"
    INDICTED = "indicted"
    GUILTY_PLEA = "guilty_plea"
    ARRESTED = "arrested"
    UNKNOWN = "unknown"


class ChargeCategory(Enum):
    """Enumeration of charge categories based on DOJ press release topics."""
    ANTITRUST = "antitrust"
    ASSET_FORFEITURE = "asset_forfeiture"
    BANKRUPTCY = "bankruptcy"
    CIVIL_RIGHTS = "civil_rights"
    CONSUMER_PROTECTION = "consumer_protection"
    CYBERCRIME = "cybercrime"
    DISASTER_FRAUD = "disaster_fraud"
    DRUGS = "drugs"
    ENVIRONMENT = "environment"
    FALSE_CLAIMS_ACT = "false_claims_act"
    FINANCIAL_FRAUD = "financial_fraud"
    FIREARMS_OFFENSES = "firearms_offenses"
    FOREIGN_CORRUPTION = "foreign_corruption"
    HEALTH_CARE_FRAUD = "health_care_fraud"
    IMMIGRATION = "immigration"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    LABOR_EMPLOYMENT = "labor_employment"
    NATIONAL_SECURITY = "national_security"
    PUBLIC_CORRUPTION = "public_corruption"
    TAX = "tax"
    VIOLENT_CRIME = "violent_crime"
    VOTING_ELECTIONS = "voting_elections"
    OTHER = "other"


@dataclass
class CaseFraudInfo:
    """Indicates if a case is categorized as fraud, with evidence."""
    is_fraud: bool
    charge_categories: List[ChargeCategory] = field(default_factory=list)
    evidence: Optional[str] = None  # e.g., text snippet or rationale


@dataclass
class CaseInfo:
    """Data structure for storing case information."""
    title: str
    date: str
    url: str
    charges: List[str] = field(default_factory=list)
    case_type: CaseType = CaseType.UNKNOWN
    charge_categories: List[ChargeCategory] = field(default_factory=list)
    extraction_date: Optional[datetime] = None
    # --- Added for linter/static analysis compliance ---
    fraud_info: Optional["CaseFraudInfo"] = None
    money_laundering_flag: Optional[bool] = None
    money_laundering_evidence: Optional[str] = None
    gpt4o: Optional[dict] = None
    # ---------------------------------------------------
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.extraction_date is None:
            self.extraction_date = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "date": self.date,
            "url": self.url,
            "charges": self.charges,
            "case_type": self.case_type.value,
            "charge_categories": [cat.value for cat in self.charge_categories],
            "extraction_date": self.extraction_date.isoformat() if self.extraction_date else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CaseInfo":
        """Create instance from dictionary."""
        return cls(
            title=data.get("title", ""),
            date=data.get("date", ""),
            url=data.get("url", ""),
            charges=data.get("charges", []),
            case_type=CaseType(data.get("case_type", "unknown")),
            charge_categories=[ChargeCategory(cat) for cat in data.get("charge_categories", [])],
            extraction_date=datetime.fromisoformat(data["extraction_date"]) if data.get("extraction_date") else None
        )


@dataclass
class ScrapingConfig:
    """Configuration for web scraping."""
    base_url: str = "https://www.justice.gov"
    max_pages: int = 50
    max_cases: int = 100
    delay_between_requests: float = 1.0
    timeout: int = 10
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    filter_video_content: bool = True  # Enable video content filtering by default


@dataclass
class AnalysisResult:
    """Results of case analysis."""
    cases: List[CaseInfo]
    total_cases: int
    successful_extractions: int
    failed_extractions: int
    analysis_date: datetime = field(default_factory=datetime.now)
    
    def success_rate(self) -> float:
        """Calculate success rate of extractions."""
        if self.total_cases == 0:
            return 0.0
        return self.successful_extractions / self.total_cases
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "cases": [case.to_dict() for case in self.cases],
            "total_cases": self.total_cases,
            "successful_extractions": self.successful_extractions,
            "failed_extractions": self.failed_extractions,
            "success_rate": self.success_rate(),
            "analysis_date": self.analysis_date.isoformat()
        }


@dataclass
class FeedbackData:
    """Data structure for user feedback."""
    case_id: str
    url: str
    user_feedback: str  # "positive", "negative", or "neutral"
    feedback_text: Optional[str] = None  # Optional detailed feedback
    timestamp: Optional[datetime] = None
    model_prediction: Optional[dict] = None  # Store the original prediction
    confidence_score: Optional[float] = None

@dataclass
class FeedbackResult:
    """Result of feedback processing."""
    success: bool
    message: str
    feedback_id: Optional[str] = None
    training_data_updated: bool = False