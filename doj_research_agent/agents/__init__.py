"""Multi-agent system for DOJ research with specialized agents.

This module contains specialized agents for different aspects of DOJ case analysis:
- BaseAgent: Abstract base class for all agents
- ResearchAgent: Specialized for case research and pattern analysis
- EvaluationAgent: Specialized for performance evaluation and quality assessment
- LegalIntelligenceAgent: Specialized for legal context and precedent analysis
- MetaAgent: Strategic controller that oversees and coordinates all subagents
"""

from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .evaluation_agent import EvaluationAgent
from .legal_intelligence_agent import LegalIntelligenceAgent
from .meta_agent import MetaAgent

__all__ = [
    "BaseAgent",
    "ResearchAgent", 
    "EvaluationAgent",
    "LegalIntelligenceAgent",
    "MetaAgent",
]