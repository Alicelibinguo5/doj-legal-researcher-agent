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
    """Enumeration of charge categories."""
    FINANCIAL_CRIMES = "financial_crimes"
    DRUG_CRIMES = "drug_crimes"
    VIOLENT_CRIMES = "violent_crimes"
    CYBERCRIME = "cybercrime"
    PUBLIC_CORRUPTION = "public_corruption"
    IMMIGRATION = "immigration"
    CIVIL_RIGHTS = "civil_rights"
    OTHER = "other"


@dataclass
class CaseInfo:
    """Data structure for storing case information."""
    title: str
    date: str
    url: str
    charges: List[str] = field(default_factory=list)
    case_type: CaseType = CaseType.UNKNOWN
    defendant_name: str = "Unknown"
    location: str = "Unknown"
    disposition: Disposition = Disposition.UNKNOWN
    description: str = ""
    charge_categories: List[ChargeCategory] = field(default_factory=list)
    extraction_date: Optional[datetime] = None
    
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
            "defendant_name": self.defendant_name,
            "location": self.location,
            "disposition": self.disposition.value,
            "description": self.description,
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
            defendant_name=data.get("defendant_name", "Unknown"),
            location=data.get("location", "Unknown"),
            disposition=Disposition(data.get("disposition", "unknown")),
            description=data.get("description", ""),
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