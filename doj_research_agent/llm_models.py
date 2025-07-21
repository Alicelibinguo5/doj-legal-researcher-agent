"""Pydantic models for structured LLM output using instructor."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from enum import Enum


class FraudType(str, Enum):
    """Fraud type enumeration."""
    FINANCIAL_FRAUD = "financial_fraud"
    HEALTHCARE_FRAUD = "healthcare_fraud"
    DISASTER_FRAUD = "disaster_fraud"
    CONSUMER_FRAUD = "consumer_fraud"
    GOVERNMENT_FRAUD = "government_fraud"
    BUSINESS_FRAUD = "business_fraud"
    IMMIGRATION_FRAUD = "immigration_fraud"
    INTELLECTUAL_PROPERTY_FRAUD = "intellectual_property_fraud"
    GENERAL_FRAUD = "general_fraud"


class CaseAnalysisResponse(BaseModel):
    """Structured response for DOJ case analysis."""
    
    fraud_flag: bool = Field(
        description="True if this is a fraud case, false otherwise. This is the key field.",
        example=True
    )
    
    fraud_type: Optional[FraudType] = Field(
        default=None,
        description="Category of fraud if fraud_flag is true, otherwise null"
    )
    
    fraud_evidence: Optional[str] = Field(
        default=None,
        description="Brief snippet of evidence if fraud_flag is true, otherwise null",
        max_length=500
    )
    
    fraud_rationale: Optional[str] = Field(
        default=None,
        description="1-2 sentences explaining why this was classified as fraud or not",
        max_length=1000
    )
    
    money_laundering_flag: bool = Field(
        default=False,
        description="True if this is a money laundering case, false otherwise"
    )
    
    money_laundering_evidence: Optional[str] = Field(
        default=None,
        description="Brief snippet of evidence if money_laundering_flag is true, otherwise null",
        max_length=500
    )
    
    title: str = Field(
        description="The title of the press release",
        example="Former Bank President Sentenced for Fraud"
    )
    
    date: Optional[str] = Field(
        default=None,
        description="The date of the press release",
        example="2024-01-15"
    )
    
    charges: List[str] = Field(
        default_factory=list,
        description="List of all charges mentioned in the press release",
        example=["wire fraud", "bank fraud", "money laundering"]
    )
    
    indictment_number: Optional[str] = Field(
        default=None,
        description="Indictment number if present, otherwise null",
        example="CR-24-001"
    )
    
    charge_count: int = Field(
        default=0,
        description="Number of charges found",
        ge=0
    )
    
    @validator('fraud_type', always=True)
    def validate_fraud_type_consistency(cls, v, values):
        """Ensure fraud_type is consistent with fraud_flag."""
        fraud_flag = values.get('fraud_flag', False)
        if fraud_flag and v is None:
            # If fraud is detected but no type specified, default to general
            return FraudType.GENERAL_FRAUD
        elif not fraud_flag and v is not None:
            # If no fraud detected, type should be None
            return None
        return v
    
    @validator('fraud_evidence', always=True)
    def validate_fraud_evidence_consistency(cls, v, values):
        """Ensure fraud_evidence is consistent with fraud_flag."""
        fraud_flag = values.get('fraud_flag', False)
        if not fraud_flag:
            return None
        return v
    
    @validator('fraud_rationale', always=True)
    def validate_fraud_rationale_consistency(cls, v, values):
        """Ensure fraud_rationale is consistent with fraud_flag."""
        fraud_flag = values.get('fraud_flag', False)
        if not fraud_flag:
            return None
        return v
    
    @validator('money_laundering_evidence', always=True)
    def validate_money_laundering_evidence_consistency(cls, v, values):
        """Ensure money_laundering_evidence is consistent with money_laundering_flag."""
        money_laundering_flag = values.get('money_laundering_flag', False)
        if not money_laundering_flag:
            return None
        return v
    
    @validator('charge_count', always=True)
    def validate_charge_count_consistency(cls, v, values):
        """Ensure charge_count matches the length of charges list."""
        charges = values.get('charges', [])
        return len(charges) if charges else 0
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"


class SimpleCaseResponse(BaseModel):
    """Simplified response model for basic case information."""
    
    is_fraud: bool = Field(description="Whether this case involves fraud")
    title: str = Field(description="Case title")
    charges: List[str] = Field(default_factory=list, description="List of charges")
    summary: Optional[str] = Field(default=None, description="Brief case summary")


class MoneyLaunderingResponse(BaseModel):
    """Response model specifically for money laundering detection."""
    
    is_money_laundering: bool = Field(description="Whether this case involves money laundering")
    evidence: Optional[str] = Field(default=None, description="Evidence of money laundering")
    methods: List[str] = Field(default_factory=list, description="Money laundering methods identified")
    amount: Optional[str] = Field(default=None, description="Amount involved if mentioned")