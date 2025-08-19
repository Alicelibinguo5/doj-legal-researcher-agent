"""Meta-Agent for controlling and supervising DOJ research subagents.

This Meta-Agent acts as a strategic controller that oversees the Research Agent,
Evaluation Agent, and Legal Intelligence Agent, providing high-level coordination,
task allocation, and performance optimization.
"""

import asyncio
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

from .base_agent import BaseAgent
from ..core.models import CaseInfo, ScrapingConfig
from ..core.utils import setup_logger

logger = setup_logger(__name__)


class AgentPriority(Enum):
    """Priority levels for agent task allocation."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class CoordinationStrategy(Enum):
    """Available coordination strategies for the meta-agent."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"
    HIERARCHICAL = "hierarchical"
    LOAD_BALANCED = "load_balanced"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent."""
    
    task_id: str
    agent_id: str
    task_type: str
    priority: AgentPriority
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None
    
    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """Check if task dependencies are satisfied."""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def is_overdue(self) -> bool:
        """Check if task is past its deadline."""
        return self.deadline is not None and datetime.now() > self.deadline


@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for individual agents."""
    
    agent_id: str
    task_completion_rate: float = 0.0
    average_processing_time: float = 0.0
    error_rate: float = 0.0
    quality_score: float = 0.0
    workload: int = 0
    specialization_score: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_metrics(self, completed_tasks: List[AgentTask]) -> None:
        """Update performance metrics based on completed tasks."""
        if not completed_tasks:
            return
        
        # Calculate completion rate
        total_tasks = len([t for t in completed_tasks if t.agent_id == self.agent_id])
        completed = len([t for t in completed_tasks if t.agent_id == self.agent_id and t.status == "completed"])
        self.task_completion_rate = completed / total_tasks if total_tasks > 0 else 0.0
        
        # Calculate average processing time
        processing_times = []
        for task in completed_tasks:
            if task.agent_id == self.agent_id and task.status == "completed" and task.result:
                start_time = task.created_at
                end_time = task.result.get("completion_time", datetime.now())
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time)
                processing_times.append((end_time - start_time).total_seconds())
        
        self.average_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        # Calculate error rate
        failed_tasks = len([t for t in completed_tasks if t.agent_id == self.agent_id and t.status == "failed"])
        self.error_rate = failed_tasks / total_tasks if total_tasks > 0 else 0.0
        
        self.last_updated = datetime.now()


@dataclass
class SystemState:
    """Represents the current state of the multi-agent system."""
    
    active_agents: Set[str] = field(default_factory=set)
    pending_tasks: List[AgentTask] = field(default_factory=list)
    in_progress_tasks: List[AgentTask] = field(default_factory=list)
    completed_tasks: List[AgentTask] = field(default_factory=list)
    failed_tasks: List[AgentTask] = field(default_factory=list)
    agent_metrics: Dict[str, AgentPerformanceMetrics] = field(default_factory=dict)
    system_load: float = 0.0
    coordination_strategy: CoordinationStrategy = CoordinationStrategy.ADAPTIVE
    processing_round: int = 0
    
    def get_workload_distribution(self) -> Dict[str, int]:
        """Get current workload distribution across agents."""
        workload = {}
        for task in self.in_progress_tasks:
            workload[task.agent_id] = workload.get(task.agent_id, 0) + 1
        return workload


class MetaAgent(BaseAgent):
    """Meta-Agent that controls and supervises all subagents.
    
    The Meta-Agent provides strategic oversight, task allocation, performance
    optimization, and dynamic coordination of the Research Agent, Evaluation Agent,
    and Legal Intelligence Agent.
    """
    
    def __init__(self, llm_config: Optional[Dict] = None) -> None:
        """Initialize Meta-Agent.
        
        Args:
            llm_config: Configuration for LLM integration
        """
        super().__init__("meta_agent", llm_config)
        
        # Initialize subagent management
        self.managed_agents = ["research_agent", "evaluation_agent", "legal_intelligence_agent"]
        self.system_state = SystemState()
        self.task_counter = 0
        
        # Performance tracking
        for agent_id in self.managed_agents:
            self.system_state.agent_metrics[agent_id] = AgentPerformanceMetrics(agent_id=agent_id)
        
        # Strategic decision history
        self.decision_history: List[Dict[str, Any]] = []
        self.optimization_insights: List[Dict[str, Any]] = []
        
        logger.info("Meta-Agent initialized with oversight of 3 subagents")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process meta-agent coordination and control.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Meta-agent control updates
        """
        self.logger.info("Meta-Agent starting strategic oversight...")
        
        # Initialize memory if not done
        if not self.memory:
            self.initialize_memory(state["shared_memory"])
        
        updates = {}
        
        # 1. Analyze current system state
        system_analysis = await self._analyze_system_state(state)
        updates["system_analysis"] = system_analysis
        
        # 2. Make strategic decisions
        strategy_decisions = await self._make_strategic_decisions(state, system_analysis)
        updates["strategy_decisions"] = strategy_decisions
        
        # 3. Allocate tasks dynamically
        task_allocation = await self._allocate_tasks(state, strategy_decisions)
        updates["task_allocation"] = task_allocation
        
        # 4. Optimize coordination strategy
        coordination_optimization = await self._optimize_coordination(state)
        updates["coordination_optimization"] = coordination_optimization
        
        # 5. Monitor and adjust agent performance
        performance_adjustments = await self._monitor_agent_performance(state)
        updates["performance_adjustments"] = performance_adjustments
        
        # 6. Generate meta-insights
        meta_insights = await self._generate_meta_insights(state)
        updates["meta_insights"] = meta_insights
        
        # Update meta-agent state
        updates["meta_agent_state"] = {
            "last_oversight": datetime.now().isoformat(),
            "managed_agents": self.managed_agents,
            "coordination_strategy": self.system_state.coordination_strategy.value,
            "system_load": self.system_state.system_load,
            "processing_round": self.system_state.processing_round,
            "decisions_made": len(self.decision_history),
            "optimization_insights": len(self.optimization_insights)
        }
        
        # Share meta-level guidance with subagents
        await self._share_meta_guidance(state, updates)
        
        self.logger.info("Meta-Agent completed strategic oversight")
        return updates
    
    async def _analyze_system_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current system state and performance.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            System state analysis
        """
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "system_health": "unknown",
            "bottlenecks": [],
            "performance_summary": {},
            "resource_utilization": {},
            "coordination_effectiveness": 0.0
        }
        
        # Analyze agent performance
        agent_states = {
            "research": state.get("research_agent_state", {}),
            "evaluation": state.get("evaluation_agent_state", {}),
            "legal": state.get("legal_intelligence_agent_state", {})
        }
        
        active_agents = len([s for s in agent_states.values() if s])
        analysis["active_agents"] = active_agents
        
        # Detect bottlenecks
        if state.get("urls_to_process") and len(state["urls_to_process"]) > 20:
            analysis["bottlenecks"].append("URL processing backlog")
        
        if len(state.get("failed_urls", [])) > len(state.get("analyzed_cases", [])) * 0.2:
            analysis["bottlenecks"].append("High failure rate in case processing")
        
        # Assess communication effectiveness
        comm_queue = state.get("agent_communication_queue", [])
        recent_messages = len([m for m in comm_queue if self._is_recent_message(m)])
        analysis["communication_activity"] = recent_messages
        
        # Calculate coordination effectiveness
        if comm_queue:
            unique_interactions = len(set(f"{m.get('from')}->{m.get('to')}" for m in comm_queue))
            max_interactions = len(self.managed_agents) * (len(self.managed_agents) - 1)
            analysis["coordination_effectiveness"] = unique_interactions / max_interactions
        
        # Determine system health
        if analysis["coordination_effectiveness"] > 0.7 and not analysis["bottlenecks"]:
            analysis["system_health"] = "excellent"
        elif analysis["coordination_effectiveness"] > 0.5 and len(analysis["bottlenecks"]) <= 1:
            analysis["system_health"] = "good"
        elif analysis["coordination_effectiveness"] > 0.3:
            analysis["system_health"] = "fair"
        else:
            analysis["system_health"] = "poor"
        
        return analysis
    
    def _is_recent_message(self, message: Dict[str, Any]) -> bool:
        """Check if message is recent (within last 5 minutes)."""
        try:
            msg_time = datetime.fromisoformat(message.get("timestamp", ""))
            return datetime.now() - msg_time < timedelta(minutes=5)
        except:
            return False
    
    async def _make_strategic_decisions(self, state: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Make high-level strategic decisions for the system.
        
        Args:
            state: Current multi-agent state
            analysis: System state analysis
            
        Returns:
            Strategic decisions
        """
        
        decisions = {
            "timestamp": datetime.now().isoformat(),
            "coordination_strategy": self.system_state.coordination_strategy.value,
            "priority_adjustments": {},
            "resource_reallocation": {},
            "strategic_focus": []
        }
        
        # Decide coordination strategy based on system state
        current_strategy = self.system_state.coordination_strategy
        
        if analysis["system_health"] == "poor":
            # Switch to sequential for better control
            decisions["coordination_strategy"] = CoordinationStrategy.SEQUENTIAL.value
            decisions["strategic_focus"].append("Stabilize system performance")
            
        elif analysis["system_health"] == "excellent" and len(state.get("urls_to_process", [])) > 10:
            # Switch to parallel for efficiency
            decisions["coordination_strategy"] = CoordinationStrategy.PARALLEL.value
            decisions["strategic_focus"].append("Maximize processing throughput")
            
        elif len(analysis["bottlenecks"]) > 0:
            # Use load balancing to address bottlenecks
            decisions["coordination_strategy"] = CoordinationStrategy.LOAD_BALANCED.value
            decisions["strategic_focus"].append("Address system bottlenecks")
            
        else:
            # Use adaptive strategy for balanced performance
            decisions["coordination_strategy"] = CoordinationStrategy.ADAPTIVE.value
            decisions["strategic_focus"].append("Maintain adaptive coordination")
        
        # Make priority adjustments based on case analysis
        cases_analyzed = len(state.get("analyzed_cases", []))
        evaluation_result = state.get("evaluation_result")
        
        if evaluation_result and evaluation_result.accuracy < 0.8:
            decisions["priority_adjustments"]["evaluation_agent"] = AgentPriority.HIGH.value
            decisions["strategic_focus"].append("Improve detection accuracy")
        
        if cases_analyzed < 5:
            decisions["priority_adjustments"]["research_agent"] = AgentPriority.HIGH.value
            decisions["strategic_focus"].append("Increase case processing")
        
        # Resource reallocation decisions
        workload = self.system_state.get_workload_distribution()
        if workload:
            max_load = max(workload.values())
            min_load = min(workload.values())
            if max_load - min_load > 2:  # Significant imbalance
                decisions["resource_reallocation"]["rebalance_needed"] = True
                decisions["strategic_focus"].append("Rebalance agent workloads")
        
        # Store decision in history
        self.decision_history.append(decisions)
        if len(self.decision_history) > 50:  # Keep last 50 decisions
            self.decision_history = self.decision_history[-50:]
        
        # Use LLM for advanced strategic analysis
        strategic_prompt = await self._generate_strategic_analysis_prompt(state, analysis)
        try:
            llm_insights = await self.generate_llm_response(strategic_prompt)
            decisions["llm_strategic_insights"] = llm_insights
        except Exception as e:
            self.logger.error(f"LLM strategic analysis failed: {e}")
        
        return decisions
    
    async def _generate_strategic_analysis_prompt(self, state: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate prompt for LLM strategic analysis."""
        
        prompt = f"""
        As a Meta-Agent overseeing a DOJ fraud research system, analyze the current situation and provide strategic recommendations:
        
        CURRENT SYSTEM STATE:
        - System Health: {analysis['system_health']}
        - Active Agents: {analysis['active_agents']}/3
        - Coordination Effectiveness: {analysis['coordination_effectiveness']:.2f}
        - Bottlenecks: {analysis['bottlenecks']}
        - Cases Processed: {len(state.get('analyzed_cases', []))}
        - Failed Cases: {len(state.get('failed_urls', []))}
        - Pending URLs: {len(state.get('urls_to_process', []))}
        
        AGENT PERFORMANCE:
        - Research Agent: {state.get('research_agent_state', {}).get('cases_analyzed', 0)} cases analyzed
        - Evaluation Agent: {state.get('evaluation_agent_state', {}).get('evaluations_completed', 0)} evaluations
        - Legal Intelligence: {state.get('legal_intelligence_agent_state', {}).get('precedents_analyzed', 0)} precedents
        
        RECENT DECISION HISTORY:
        {self.decision_history[-3:] if self.decision_history else 'No recent decisions'}
        
        Provide strategic recommendations for:
        1. Optimal coordination strategy for current conditions
        2. Agent priority adjustments needed
        3. Resource allocation optimization
        4. Performance improvement opportunities
        5. Risk mitigation strategies
        
        Focus on maximizing fraud detection accuracy while maintaining system efficiency.
        """
        
        return prompt
    
    async def _allocate_tasks(self, state: Dict[str, Any], decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically allocate tasks to agents based on strategic decisions.
        
        Args:
            state: Current multi-agent state
            decisions: Strategic decisions from meta-agent
            
        Returns:
            Task allocation plan
        """
        
        allocation = {
            "timestamp": datetime.now().isoformat(),
            "strategy": decisions["coordination_strategy"],
            "agent_assignments": {},
            "task_priorities": {},
            "estimated_completion": {}
        }
        
        # Create tasks based on current state
        tasks_to_allocate = []
        
        # URL processing tasks
        urls_to_process = state.get("urls_to_process", [])
        if urls_to_process:
            batch_size = self._calculate_optimal_batch_size(decisions["coordination_strategy"])
            for i in range(0, min(len(urls_to_process), batch_size)):
                task = AgentTask(
                    task_id=f"url_process_{self.task_counter}",
                    agent_id="research_agent",
                    task_type="url_processing",
                    priority=AgentPriority.MEDIUM,
                    data={"url": urls_to_process[i]}
                )
                tasks_to_allocate.append(task)
                self.task_counter += 1
        
        # Evaluation tasks
        if len(state.get("analyzed_cases", [])) >= 5:
            task = AgentTask(
                task_id=f"evaluation_{self.task_counter}",
                agent_id="evaluation_agent",
                task_type="performance_evaluation",
                priority=AgentPriority.HIGH if decisions.get("priority_adjustments", {}).get("evaluation_agent") == AgentPriority.HIGH.value else AgentPriority.MEDIUM,
                data={"cases": state["analyzed_cases"][-10:]},  # Last 10 cases
                dependencies=[t.task_id for t in tasks_to_allocate if t.task_type == "url_processing"]
            )
            tasks_to_allocate.append(task)
            self.task_counter += 1
        
        # Legal intelligence tasks
        if state.get("analyzed_cases"):
            task = AgentTask(
                task_id=f"legal_analysis_{self.task_counter}",
                agent_id="legal_intelligence_agent",
                task_type="legal_intelligence",
                priority=AgentPriority.MEDIUM,
                data={"cases": state["analyzed_cases"][-5:]},  # Last 5 cases
                dependencies=[]
            )
            tasks_to_allocate.append(task)
            self.task_counter += 1
        
        # Assign tasks to agents
        for task in tasks_to_allocate:
            agent_id = task.agent_id
            if agent_id not in allocation["agent_assignments"]:
                allocation["agent_assignments"][agent_id] = []
            
            allocation["agent_assignments"][agent_id].append({
                "task_id": task.task_id,
                "task_type": task.task_type,
                "priority": task.priority.value,
                "estimated_duration": self._estimate_task_duration(task),
                "dependencies": task.dependencies
            })
            
            allocation["task_priorities"][task.task_id] = task.priority.value
        
        # Calculate estimated completion times
        for agent_id, tasks in allocation["agent_assignments"].items():
            total_duration = sum(t["estimated_duration"] for t in tasks)
            allocation["estimated_completion"][agent_id] = (
                datetime.now() + timedelta(seconds=total_duration)
            ).isoformat()
        
        # Store tasks in system state
        self.system_state.pending_tasks.extend(tasks_to_allocate)
        
        return allocation
    
    def _calculate_optimal_batch_size(self, strategy: str) -> int:
        """Calculate optimal batch size based on coordination strategy."""
        strategy_batch_sizes = {
            CoordinationStrategy.SEQUENTIAL.value: 3,
            CoordinationStrategy.PARALLEL.value: 8,
            CoordinationStrategy.ADAPTIVE.value: 5,
            CoordinationStrategy.LOAD_BALANCED.value: 6,
            CoordinationStrategy.HIERARCHICAL.value: 4
        }
        return strategy_batch_sizes.get(strategy, 5)
    
    def _estimate_task_duration(self, task: AgentTask) -> float:
        """Estimate task duration in seconds based on task type and agent performance."""
        
        base_durations = {
            "url_processing": 30.0,
            "performance_evaluation": 45.0,
            "legal_intelligence": 60.0,
            "pattern_analysis": 40.0,
            "coordination": 20.0
        }
        
        base_duration = base_durations.get(task.task_type, 30.0)
        
        # Adjust based on agent performance
        agent_metrics = self.system_state.agent_metrics.get(task.agent_id)
        if agent_metrics and agent_metrics.average_processing_time > 0:
            performance_factor = agent_metrics.average_processing_time / base_duration
            base_duration *= min(performance_factor, 2.0)  # Cap at 2x base duration
        
        # Adjust based on priority
        priority_multipliers = {
            AgentPriority.LOW: 1.2,
            AgentPriority.MEDIUM: 1.0,
            AgentPriority.HIGH: 0.8,
            AgentPriority.CRITICAL: 0.6
        }
        
        return base_duration * priority_multipliers.get(task.priority, 1.0)
    
    async def _optimize_coordination(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize coordination strategy based on current performance.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Coordination optimization recommendations
        """
        
        optimization = {
            "timestamp": datetime.now().isoformat(),
            "current_strategy": self.system_state.coordination_strategy.value,
            "recommended_strategy": None,
            "optimization_reasons": [],
            "performance_predictions": {},
            "resource_recommendations": {}
        }
        
        # Analyze current strategy effectiveness
        current_performance = self._calculate_strategy_performance(state)
        optimization["current_performance"] = current_performance
        
        # Test different strategies
        strategy_scores = {}
        for strategy in CoordinationStrategy:
            score = await self._evaluate_strategy_fitness(strategy, state)
            strategy_scores[strategy.value] = score
        
        # Recommend best strategy
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])
        optimization["recommended_strategy"] = best_strategy[0]
        optimization["strategy_scores"] = strategy_scores
        
        # Generate optimization reasons
        if best_strategy[0] != self.system_state.coordination_strategy.value:
            optimization["optimization_reasons"].append(
                f"Strategy change from {self.system_state.coordination_strategy.value} to {best_strategy[0]} "
                f"could improve performance by {(best_strategy[1] - current_performance) * 100:.1f}%"
            )
        
        # Resource optimization recommendations
        workload = self.system_state.get_workload_distribution()
        if workload:
            overloaded_agents = [agent for agent, load in workload.items() if load > 3]
            underloaded_agents = [agent for agent, load in workload.items() if load < 1]
            
            if overloaded_agents and underloaded_agents:
                optimization["resource_recommendations"]["rebalance"] = {
                    "overloaded": overloaded_agents,
                    "underloaded": underloaded_agents,
                    "action": "Redistribute tasks to balance workload"
                }
        
        return optimization
    
    def _calculate_strategy_performance(self, state: Dict[str, Any]) -> float:
        """Calculate performance score for current coordination strategy."""
        
        # Factors: throughput, accuracy, efficiency, coordination quality
        throughput_score = len(state.get("analyzed_cases", [])) / max(1, len(state.get("urls_to_process", [])) + len(state.get("analyzed_cases", [])))
        
        accuracy_score = 0.0
        if state.get("evaluation_result"):
            accuracy_score = state["evaluation_result"].accuracy
        
        efficiency_score = 1.0 - (len(state.get("failed_urls", [])) / max(1, len(state.get("analyzed_cases", [])) + len(state.get("failed_urls", []))))
        
        coordination_score = len(state.get("agent_communication_queue", [])) / max(1, 20)  # Normalize to expected message count
        
        # Weighted average
        performance = (throughput_score * 0.3 + accuracy_score * 0.4 + efficiency_score * 0.2 + coordination_score * 0.1)
        return min(performance, 1.0)
    
    async def _evaluate_strategy_fitness(self, strategy: CoordinationStrategy, state: Dict[str, Any]) -> float:
        """Evaluate fitness of a coordination strategy for current state."""
        
        # Base scores for each strategy
        base_scores = {
            CoordinationStrategy.SEQUENTIAL: 0.7,
            CoordinationStrategy.PARALLEL: 0.8,
            CoordinationStrategy.ADAPTIVE: 0.85,
            CoordinationStrategy.LOAD_BALANCED: 0.75,
            CoordinationStrategy.HIERARCHICAL: 0.72
        }
        
        base_score = base_scores[strategy]
        
        # Adjust based on current conditions
        cases_to_process = len(state.get("urls_to_process", []))
        system_load = len(state.get("agent_communication_queue", [])) / 20  # Normalize
        
        # Parallel works better with high load
        if strategy == CoordinationStrategy.PARALLEL and cases_to_process > 10:
            base_score += 0.1
        elif strategy == CoordinationStrategy.PARALLEL and cases_to_process < 3:
            base_score -= 0.1
        
        # Sequential works better with low load or high failure rate
        failure_rate = len(state.get("failed_urls", [])) / max(1, len(state.get("analyzed_cases", [])) + len(state.get("failed_urls", [])))
        if strategy == CoordinationStrategy.SEQUENTIAL and failure_rate > 0.2:
            base_score += 0.15
        
        # Adaptive is generally good but needs stable conditions
        if strategy == CoordinationStrategy.ADAPTIVE and system_load < 0.8:
            base_score += 0.05
        
        return min(base_score, 1.0)
    
    async def _monitor_agent_performance(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and adjust individual agent performance.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Performance monitoring results and adjustments
        """
        
        monitoring = {
            "timestamp": datetime.now().isoformat(),
            "agent_performance": {},
            "performance_alerts": [],
            "recommended_adjustments": {},
            "intervention_needed": False
        }
        
        # Monitor each agent
        for agent_id in self.managed_agents:
            agent_state = state.get(f"{agent_id}_state", {})
            
            performance_analysis = {
                "agent_id": agent_id,
                "active": bool(agent_state),
                "last_activity": agent_state.get("last_analysis", "unknown"),
                "performance_trend": "stable"
            }
            
            # Analyze specific metrics per agent
            if agent_id == "research_agent":
                cases_analyzed = agent_state.get("cases_analyzed", 0)
                patterns_found = len(agent_state.get("patterns_discovered", {}).get("fraud_patterns", []))
                
                performance_analysis.update({
                    "cases_analyzed": cases_analyzed,
                    "patterns_discovered": patterns_found,
                    "productivity": cases_analyzed / max(1, self.system_state.processing_round)
                })
                
                if cases_analyzed < 2 and self.system_state.processing_round > 1:
                    monitoring["performance_alerts"].append(f"{agent_id}: Low case analysis productivity")
                    monitoring["recommended_adjustments"][agent_id] = "Increase processing focus"
            
            elif agent_id == "evaluation_agent":
                evaluations_completed = agent_state.get("evaluations_completed", 0)
                accuracy_trend = agent_state.get("accuracy_trend", "unknown")
                
                performance_analysis.update({
                    "evaluations_completed": evaluations_completed,
                    "accuracy_trend": accuracy_trend
                })
                
                if accuracy_trend == "declining":
                    monitoring["performance_alerts"].append(f"{agent_id}: Declining accuracy trend")
                    monitoring["recommended_adjustments"][agent_id] = "Review evaluation criteria"
            
            elif agent_id == "legal_intelligence_agent":
                precedents_analyzed = agent_state.get("precedents_analyzed", 0)
                regulatory_updates = agent_state.get("regulatory_updates_count", 0)
                
                performance_analysis.update({
                    "precedents_analyzed": precedents_analyzed,
                    "regulatory_updates": regulatory_updates
                })
                
                if precedents_analyzed == 0 and len(state.get("analyzed_cases", [])) > 5:
                    monitoring["performance_alerts"].append(f"{agent_id}: No precedent analysis completed")
                    monitoring["recommended_adjustments"][agent_id] = "Activate precedent analysis"
            
            monitoring["agent_performance"][agent_id] = performance_analysis
        
        # Determine if intervention is needed
        if len(monitoring["performance_alerts"]) > 1:
            monitoring["intervention_needed"] = True
            monitoring["recommended_adjustments"]["meta_action"] = "Consider coordination strategy change"
        
        return monitoring
    
    async def _generate_meta_insights(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level insights about system performance and optimization.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Meta-level insights and recommendations
        """
        
        insights = {
            "timestamp": datetime.now().isoformat(),
            "system_maturity": "developing",
            "optimization_opportunities": [],
            "strategic_recommendations": [],
            "performance_forecast": {},
            "risk_assessment": {}
        }
        
        # Assess system maturity
        total_cases = len(state.get("analyzed_cases", []))
        processing_rounds = self.system_state.processing_round
        
        if total_cases > 20 and processing_rounds > 3:
            insights["system_maturity"] = "mature"
        elif total_cases > 10 and processing_rounds > 2:
            insights["system_maturity"] = "developing"
        else:
            insights["system_maturity"] = "nascent"
        
        # Identify optimization opportunities
        if len(state.get("failed_urls", [])) > 0:
            insights["optimization_opportunities"].append("Improve URL processing reliability")
        
        if state.get("evaluation_result") and state["evaluation_result"].accuracy < 0.9:
            insights["optimization_opportunities"].append("Enhance fraud detection accuracy")
        
        comm_effectiveness = len(state.get("agent_communication_queue", [])) / max(1, 15)
        if comm_effectiveness < 0.5:
            insights["optimization_opportunities"].append("Increase inter-agent communication")
        
        # Strategic recommendations
        if insights["system_maturity"] == "mature":
            insights["strategic_recommendations"].append("Focus on fine-tuning and optimization")
        else:
            insights["strategic_recommendations"].append("Prioritize system stabilization and learning")
        
        # Performance forecast using trend analysis
        if len(self.decision_history) >= 3:
            recent_decisions = self.decision_history[-3:]
            strategy_changes = len(set(d["coordination_strategy"] for d in recent_decisions))
            
            if strategy_changes > 2:
                insights["performance_forecast"]["stability"] = "unstable - frequent strategy changes"
            else:
                insights["performance_forecast"]["stability"] = "stable"
        
        # Risk assessment
        failure_rate = len(state.get("failed_urls", [])) / max(1, total_cases + len(state.get("failed_urls", [])))
        if failure_rate > 0.3:
            insights["risk_assessment"]["high_failure_rate"] = True
            insights["strategic_recommendations"].append("Address failure rate issues immediately")
        
        # Store insights
        insight_record = {
            "timestamp": datetime.now().isoformat(),
            "insights": insights,
            "system_snapshot": {
                "cases_processed": total_cases,
                "active_agents": len([s for s in [
                    state.get("research_agent_state"),
                    state.get("evaluation_agent_state"),
                    state.get("legal_intelligence_agent_state")
                ] if s])
            }
        }
        self.optimization_insights.append(insight_record)
        
        # Keep last 20 insights
        if len(self.optimization_insights) > 20:
            self.optimization_insights = self.optimization_insights[-20:]
        
        return insights
    
    async def _share_meta_guidance(self, state: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """Share meta-level guidance and directives with subagents.
        
        Args:
            state: Current multi-agent state
            updates: Updates from meta-agent processing
        """
        
        # Share strategic guidance with all agents
        strategic_guidance = {
            "meta_directive": "system_optimization",
            "coordination_strategy": updates.get("strategy_decisions", {}).get("coordination_strategy"),
            "system_priorities": updates.get("strategy_decisions", {}).get("strategic_focus", []),
            "performance_targets": {
                "accuracy_threshold": 0.85,
                "processing_efficiency": 0.9,
                "coordination_quality": 0.8
            }
        }
        
        for agent_id in self.managed_agents:
            self.communicate_with_agent(
                state, agent_id, "meta_guidance", strategic_guidance
            )
        
        # Share specific performance adjustments
        performance_adjustments = updates.get("performance_adjustments", {})
        if performance_adjustments.get("recommended_adjustments"):
            for agent_id, adjustment in performance_adjustments["recommended_adjustments"].items():
                if agent_id in self.managed_agents:
                    self.communicate_with_agent(
                        state, agent_id, "performance_adjustment", {
                            "adjustment_type": adjustment,
                            "priority": "high",
                            "meta_analysis": performance_adjustments.get("agent_performance", {}).get(agent_id, {})
                        }
                    )
        
        # Share resource allocation guidance
        task_allocation = updates.get("task_allocation", {})
        if task_allocation.get("agent_assignments"):
            for agent_id, tasks in task_allocation["agent_assignments"].items():
                self.communicate_with_agent(
                    state, agent_id, "task_assignment", {
                        "assigned_tasks": tasks,
                        "coordination_strategy": task_allocation["strategy"],
                        "expected_completion": task_allocation.get("estimated_completion", {}).get(agent_id)
                    }
                )
    
    def get_prompt_template(self) -> str:
        """Get meta-agent prompt template for strategic analysis.
        
        Returns:
            Prompt template for meta-agent LLM interactions
        """
        return """
        As a Meta-Agent overseeing a multi-agent DOJ fraud research system, provide strategic analysis and recommendations:
        
        SYSTEM OVERVIEW:
        Managed Agents: Research Agent, Evaluation Agent, Legal Intelligence Agent
        Current Strategy: {coordination_strategy}
        Processing Round: {processing_round}
        System Health: {system_health}
        
        PERFORMANCE METRICS:
        {performance_metrics}
        
        CURRENT CHALLENGES:
        {challenges}
        
        DECISION HISTORY:
        {recent_decisions}
        
        Provide strategic recommendations for:
        1. Optimal coordination strategy for current conditions
        2. Agent priority adjustments and task allocation
        3. Performance optimization opportunities
        4. Risk mitigation and system stability
        5. Resource allocation and workload balancing
        6. Long-term strategic planning
        
        Focus on maximizing fraud detection effectiveness while maintaining system efficiency and stability.
        Consider both immediate tactical decisions and long-term strategic objectives.
        """
