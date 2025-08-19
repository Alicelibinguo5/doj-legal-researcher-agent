"""Enhanced data models for multi-agent DOJ research system."""

from typing import Dict, List, Optional, Any, TypedDict, Annotated
from dataclasses import dataclass, field
from datetime import datetime
import operator
from .models import AnalysisResult, CaseInfo, ScrapingConfig, FeedbackData, EvaluationResult


@dataclass
class AgentMemory:
    """Persistent memory for agents with knowledge accumulation.
    
    This class manages the persistent memory for individual agents,
    storing learned patterns, performance history, and knowledge base
    that persists across processing sessions.
    """
    
    agent_id: str
    knowledge_base: Dict[str, Any] = field(default_factory=dict)
    learned_patterns: List[Dict[str, Any]] = field(default_factory=list)
    performance_history: List[Dict[str, Any]] = field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_knowledge(self, key: str, value: Any) -> None:
        """Update knowledge base with new information.
        
        Args:
            key: Knowledge key to update
            value: Value to store
        """
        self.knowledge_base[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "source": self.agent_id
        }
        self.last_updated = datetime.now()
    
    def add_pattern(self, pattern: Dict[str, Any]) -> None:
        """Add learned pattern to memory.
        
        Args:
            pattern: Pattern data to store
        """
        pattern["timestamp"] = datetime.now().isoformat()
        pattern["agent_id"] = self.agent_id
        self.learned_patterns.append(pattern)
        self.last_updated = datetime.now()
        
        # Keep only the most recent 100 patterns
        if len(self.learned_patterns) > 100:
            self.learned_patterns = self.learned_patterns[-100:]
    
    def add_interaction(self, interaction: Dict[str, Any]) -> None:
        """Add interaction record to memory.
        
        Args:
            interaction: Interaction data to store
        """
        interaction["timestamp"] = datetime.now().isoformat()
        interaction["agent_id"] = self.agent_id
        self.interaction_history.append(interaction)
        
        # Keep only the most recent 200 interactions
        if len(self.interaction_history) > 200:
            self.interaction_history = self.interaction_history[-200:]
    
    def get_recent_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent learned patterns.
        
        Args:
            limit: Maximum number of patterns to return
            
        Returns:
            List of recent patterns
        """
        return self.learned_patterns[-limit:]
    
    def get_knowledge(self, key: str) -> Optional[Any]:
        """Retrieve knowledge by key.
        
        Args:
            key: Knowledge key to retrieve
            
        Returns:
            Knowledge value or None if not found
        """
        if key in self.knowledge_base:
            return self.knowledge_base[key]["value"]
        return None


@dataclass 
class SharedMemoryStore:
    """Centralized memory store shared between agents.
    
    This class manages the shared memory system that allows agents
    to communicate, share knowledge, and maintain global insights
    across the multi-agent system.
    """
    
    agent_memories: Dict[str, AgentMemory] = field(default_factory=dict)
    cross_agent_knowledge: Dict[str, Any] = field(default_factory=dict)
    communication_log: List[Dict[str, Any]] = field(default_factory=list)
    global_insights: List[Dict[str, Any]] = field(default_factory=list)
    system_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def get_agent_memory(self, agent_id: str) -> AgentMemory:
        """Get or create agent memory.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            AgentMemory instance for the agent
        """
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = AgentMemory(agent_id=agent_id)
        return self.agent_memories[agent_id]
    
    def share_knowledge(self, source_agent: str, target_agent: str, key: str, value: Any) -> None:
        """Share knowledge between agents.
        
        Args:
            source_agent: ID of source agent
            target_agent: ID of target agent
            key: Knowledge key
            value: Knowledge value
        """
        knowledge_key = f"{source_agent}_to_{target_agent}_{key}"
        self.cross_agent_knowledge[knowledge_key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "source": source_agent,
            "target": target_agent
        }
        
        # Log communication
        self.communication_log.append({
            "source": source_agent,
            "target": target_agent,
            "key": key,
            "timestamp": datetime.now().isoformat(),
            "message_id": len(self.communication_log)
        })
        
        # Keep communication log manageable
        if len(self.communication_log) > 1000:
            self.communication_log = self.communication_log[-1000:]
    
    def get_shared_knowledge(self, source_agent: str, target_agent: str, key: str) -> Optional[Any]:
        """Retrieve shared knowledge between specific agents.
        
        Args:
            source_agent: ID of source agent
            target_agent: ID of target agent  
            key: Knowledge key
            
        Returns:
            Shared knowledge value or None if not found
        """
        knowledge_key = f"{source_agent}_to_{target_agent}_{key}"
        if knowledge_key in self.cross_agent_knowledge:
            return self.cross_agent_knowledge[knowledge_key]["value"]
        return None
    
    def add_global_insight(self, insight: Dict[str, Any]) -> None:
        """Add insight to global knowledge base.
        
        Args:
            insight: Insight data to store
        """
        insight["timestamp"] = datetime.now().isoformat()
        insight["insight_id"] = len(self.global_insights)
        self.global_insights.append(insight)
        
        # Keep only the most recent 500 insights
        if len(self.global_insights) > 500:
            self.global_insights = self.global_insights[-500:]
    
    def update_system_metric(self, metric_name: str, value: Any) -> None:
        """Update system-wide metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        self.system_metrics[metric_name] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "last_updated": datetime.now()
        }
    
    def get_communication_summary(self) -> Dict[str, Any]:
        """Get summary of inter-agent communications.
        
        Returns:
            Communication summary statistics
        """
        if not self.communication_log:
            return {"total_messages": 0, "agent_pairs": []}
        
        agent_pairs = set()
        message_types = {}
        
        for comm in self.communication_log:
            pair = f"{comm['source']}->{comm['target']}"
            agent_pairs.add(pair)
            
            key = comm.get('key', 'unknown')
            message_types[key] = message_types.get(key, 0) + 1
        
        return {
            "total_messages": len(self.communication_log),
            "agent_pairs": list(agent_pairs),
            "message_types": message_types,
            "recent_activity": self.communication_log[-10:]  # Last 10 messages
        }


class MultiAgentState(TypedDict):
    """Enhanced state for multi-agent coordination with shared memory.
    
    This extends the basic ResearchState to include multi-agent
    coordination capabilities, shared memory, and inter-agent
    communication mechanisms.
    """
    
    # Existing state fields from ResearchState
    urls_to_process: List[str]
    analyzed_cases: Annotated[List[CaseInfo], operator.add]
    failed_urls: Annotated[List[str], operator.add]
    scraping_config: ScrapingConfig
    final_result: Optional[AnalysisResult]
    evaluation_result: Optional[EvaluationResult]
    feedback_manager: Optional[Any]
    pending_feedback: Annotated[List[FeedbackData], operator.add]
    
    # Multi-agent specific state
    shared_memory: SharedMemoryStore
    research_agent_state: Dict[str, Any]
    evaluation_agent_state: Dict[str, Any]
    legal_intelligence_agent_state: Dict[str, Any]
    agent_coordination: Dict[str, Any]
    current_active_agents: List[str]
    agent_communication_queue: Annotated[List[Dict[str, Any]], operator.add]
    
    # Additional coordination fields
    processing_round: int
    coordination_metadata: Dict[str, Any]
    
    # Meta-agent specific fields
    meta_agent_active: Optional[bool]
    meta_control_mode: Optional[bool]


@dataclass
class AgentCoordinationConfig:
    """Configuration for multi-agent coordination.
    
    This class defines configuration parameters for how agents
    coordinate, communicate, and share resources in the system.
    """
    
    max_processing_rounds: int = 3
    agent_timeout_seconds: int = 300
    enable_parallel_processing: bool = True
    communication_queue_size: int = 1000
    memory_retention_days: int = 30
    coordination_strategy: str = "sequential"  # "sequential", "parallel", "adaptive"
    
    # Agent-specific configurations
    research_agent_config: Dict[str, Any] = field(default_factory=dict)
    evaluation_agent_config: Dict[str, Any] = field(default_factory=dict)
    legal_intelligence_agent_config: Dict[str, Any] = field(default_factory=dict)
    
    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """Get configuration for specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent-specific configuration
        """
        config_map = {
            "research_agent": self.research_agent_config,
            "evaluation_agent": self.evaluation_agent_config, 
            "legal_intelligence_agent": self.legal_intelligence_agent_config
        }
        return config_map.get(agent_id, {})


@dataclass
class MultiAgentResults:
    """Results from multi-agent processing.
    
    This class encapsulates the comprehensive results from running
    the multi-agent system, including individual agent outputs,
    coordination metrics, and shared insights.
    """
    
    # Individual agent results
    research_results: Dict[str, Any] = field(default_factory=dict)
    evaluation_results: Dict[str, Any] = field(default_factory=dict)
    legal_intelligence_results: Dict[str, Any] = field(default_factory=dict)
    
    # Coordination and communication results
    coordination_metrics: Dict[str, Any] = field(default_factory=dict)
    communication_summary: Dict[str, Any] = field(default_factory=dict)
    shared_insights: List[Dict[str, Any]] = field(default_factory=list)
    
    # Overall system results
    processing_time: float = 0.0
    processing_rounds: int = 0
    success: bool = True
    error_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Traditional DOJ research results
    final_result: Optional[AnalysisResult] = None
    evaluation_result: Optional[EvaluationResult] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary format.
        
        Returns:
            Dictionary representation of results
        """
        return {
            "research_results": self.research_results,
            "evaluation_results": self.evaluation_results,
            "legal_intelligence_results": self.legal_intelligence_results,
            "coordination_metrics": self.coordination_metrics,
            "communication_summary": self.communication_summary,
            "shared_insights": self.shared_insights,
            "processing_time": self.processing_time,
            "processing_rounds": self.processing_rounds,
            "success": self.success,
            "error_count": len(self.error_log),
            "final_result": self.final_result.to_dict() if self.final_result else None,
            "evaluation_result": self.evaluation_result.__dict__ if self.evaluation_result else None
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of multi-agent results.
        
        Returns:
            Summary of key results and metrics
        """
        return {
            "success": self.success,
            "processing_rounds": self.processing_rounds,
            "processing_time": self.processing_time,
            "agents_active": [
                agent for agent in ["research", "evaluation", "legal_intelligence"]
                if getattr(self, f"{agent}_results")
            ],
            "total_insights": len(self.shared_insights),
            "communication_messages": self.communication_summary.get("total_messages", 0),
            "errors": len(self.error_log),
            "cases_analyzed": (
                self.final_result.successful_extractions 
                if self.final_result else 0
            ),
            "evaluation_accuracy": (
                self.evaluation_result.accuracy 
                if self.evaluation_result else None
            )
        }
