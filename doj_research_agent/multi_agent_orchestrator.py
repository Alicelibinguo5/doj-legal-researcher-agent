"""Multi-Agent Orchestrator for DOJ research system.

This module coordinates the Research Agent, Evaluation Agent, and Legal Intelligence Agent
in a unified workflow with shared state and memory management.
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import time
from langgraph.graph import StateGraph, END

from .core.multi_agent_models import (
    MultiAgentState, SharedMemoryStore, AgentCoordinationConfig, MultiAgentResults
)
from .core.models import ScrapingConfig, AnalysisResult
from .agents import ResearchAgent, EvaluationAgent, LegalIntelligenceAgent
from .core.utils import setup_logger

logger = setup_logger(__name__)


class MultiAgentOrchestrator:
    """Orchestrates research, evaluation, and legal intelligence agents.
    
    This orchestrator manages the coordination of three specialized agents:
    - Research Agent: Pattern analysis and fraud research
    - Evaluation Agent: Performance evaluation and quality assessment  
    - Legal Intelligence Agent: Legal context and precedent analysis
    
    The agents share state and memory to provide comprehensive DOJ case analysis.
    """
    
    def __init__(self, 
                 scraping_config: Optional[ScrapingConfig] = None,
                 coordination_config: Optional[AgentCoordinationConfig] = None,
                 llm_config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize multi-agent orchestrator.
        
        Args:
            scraping_config: Configuration for DOJ scraping
            coordination_config: Configuration for agent coordination
            llm_config: Configuration for LLM integration
        """
        self.scraping_config = scraping_config or ScrapingConfig()
        self.coordination_config = coordination_config or AgentCoordinationConfig()
        self.llm_config = llm_config or {}
        
        # Initialize shared memory
        self.shared_memory = SharedMemoryStore()
        
        # Initialize agents
        self.research_agent = ResearchAgent(self.llm_config)
        self.evaluation_agent = EvaluationAgent(self.llm_config)
        self.legal_intelligence_agent = LegalIntelligenceAgent(self.llm_config)
        
        # Initialize agents with shared memory
        self.research_agent.initialize_memory(self.shared_memory)
        self.evaluation_agent.initialize_memory(self.shared_memory)
        self.legal_intelligence_agent.initialize_memory(self.shared_memory)
        
        # Build coordination graph
        self.graph = self._build_graph()
        
        logger.info("Multi-Agent Orchestrator initialized with 3 agents")
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph for multi-agent coordination.
        
        Returns:
            Compiled StateGraph for multi-agent workflow
        """
        workflow = StateGraph(MultiAgentState)
        
        # Define agent nodes
        workflow.add_node("initialize_system", self._initialize_system_node)
        workflow.add_node("research_agent", self._research_agent_node)
        workflow.add_node("legal_intelligence_agent", self._legal_intelligence_agent_node)
        workflow.add_node("evaluation_agent", self._evaluation_agent_node)
        workflow.add_node("coordinate_agents", self._coordinate_agents_node)
        workflow.add_node("finalize_results", self._finalize_results_node)
        
        # Set entry point
        workflow.set_entry_point("initialize_system")
        
        # Define workflow based on coordination strategy
        if self.coordination_config.coordination_strategy == "parallel":
            # Parallel execution of agents
            workflow.add_edge("initialize_system", ["research_agent", "legal_intelligence_agent"])
            workflow.add_edge(["research_agent", "legal_intelligence_agent"], "evaluation_agent")
            workflow.add_edge("evaluation_agent", "coordinate_agents")
        elif self.coordination_config.coordination_strategy == "sequential":
            # Sequential execution
            workflow.add_edge("initialize_system", "research_agent")
            workflow.add_edge("research_agent", "legal_intelligence_agent")
            workflow.add_edge("legal_intelligence_agent", "evaluation_agent")
            workflow.add_edge("evaluation_agent", "coordinate_agents")
        else:  # adaptive strategy
            # Adaptive execution with conditional edges
            workflow.add_edge("initialize_system", "research_agent")
            workflow.add_conditional_edges(
                "research_agent",
                self._decide_next_agent,
                {
                    "legal_intelligence": "legal_intelligence_agent",
                    "evaluation": "evaluation_agent",
                    "coordinate": "coordinate_agents"
                }
            )
            workflow.add_edge("legal_intelligence_agent", "evaluation_agent")
            workflow.add_edge("evaluation_agent", "coordinate_agents")
        
        # Coordination and finalization
        workflow.add_conditional_edges(
            "coordinate_agents",
            self._should_continue_processing,
            {
                "continue": "research_agent",
                "finalize": "finalize_results"
            }
        )
        workflow.add_edge("finalize_results", END)
        
        return workflow.compile()
    
    async def _initialize_system_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Initialize the multi-agent system.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Initialization updates
        """
        logger.info("Initializing multi-agent system...")
        
        # Initialize system metrics
        self.shared_memory.update_system_metric("system_start_time", datetime.now())
        self.shared_memory.update_system_metric("processing_round", 0)
        
        # Perform initial URL fetching if needed
        from .scraping.scraper import DOJScraper
        
        if not state.get("urls_to_process"):
            logger.info("Fetching initial URLs...")
            scraper = DOJScraper(state["scraping_config"])
            urls = scraper.get_press_release_urls()
            
            if state["scraping_config"].max_cases:
                urls = urls[:state["scraping_config"].max_cases]
            
            logger.info(f"Fetched {len(urls)} URLs for processing")
            return {"urls_to_process": urls}
        
        return {"system_initialized": True}
    
    async def _research_agent_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Execute research agent processing.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Research agent updates
        """
        logger.info("Executing Research Agent node...")
        
        start_time = time.time()
        
        try:
            # Execute research agent
            updates = await self.research_agent.process(state)
            
            # Log performance
            processing_time = time.time() - start_time
            self.shared_memory.update_system_metric("research_agent_time", processing_time)
            
            logger.info(f"Research Agent completed in {processing_time:.2f}s")
            return updates
            
        except Exception as e:
            logger.error(f"Research Agent failed: {e}")
            return {"research_agent_error": str(e)}
    
    async def _legal_intelligence_agent_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Execute legal intelligence agent processing.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Legal intelligence agent updates
        """
        logger.info("Executing Legal Intelligence Agent node...")
        
        start_time = time.time()
        
        try:
            # Execute legal intelligence agent
            updates = await self.legal_intelligence_agent.process(state)
            
            # Log performance
            processing_time = time.time() - start_time
            self.shared_memory.update_system_metric("legal_intelligence_agent_time", processing_time)
            
            logger.info(f"Legal Intelligence Agent completed in {processing_time:.2f}s")
            return updates
            
        except Exception as e:
            logger.error(f"Legal Intelligence Agent failed: {e}")
            return {"legal_intelligence_agent_error": str(e)}
    
    async def _evaluation_agent_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Execute evaluation agent processing.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Evaluation agent updates
        """
        logger.info("Executing Evaluation Agent node...")
        
        start_time = time.time()
        
        try:
            # Execute evaluation agent
            updates = await self.evaluation_agent.process(state)
            
            # Log performance
            processing_time = time.time() - start_time
            self.shared_memory.update_system_metric("evaluation_agent_time", processing_time)
            
            logger.info(f"Evaluation Agent completed in {processing_time:.2f}s")
            return updates
            
        except Exception as e:
            logger.error(f"Evaluation Agent failed: {e}")
            return {"evaluation_agent_error": str(e)}
    
    async def _coordinate_agents_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Coordinate between agents and manage shared state.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Coordination updates
        """
        logger.info("Coordinating agents...")
        
        coordination_updates = {}
        
        # Process inter-agent communications
        message_count = len(state.get("agent_communication_queue", []))
        if message_count > 0:
            logger.info(f"Processing {message_count} inter-agent messages")
            
            # Analyze communication patterns
            communication_analysis = self._analyze_communications(state["agent_communication_queue"])
            coordination_updates["communication_analysis"] = communication_analysis
        
        # Update processing round
        current_round = state.get("processing_round", 0) + 1
        coordination_updates["processing_round"] = current_round
        
        # Check for convergence or completion criteria
        convergence_check = self._check_convergence(state)
        coordination_updates["convergence_status"] = convergence_check
        
        # Update coordination metadata
        coordination_updates["agent_coordination"] = {
            "last_coordination": datetime.now().isoformat(),
            "messages_processed": message_count,
            "active_agents": state.get("current_active_agents", []),
            "coordination_round": current_round,
            "system_status": "coordinating"
        }
        
        # Clear processed messages (keep recent ones for analysis)
        recent_messages = state.get("agent_communication_queue", [])[-50:]  # Keep last 50
        coordination_updates["agent_communication_queue"] = recent_messages
        
        # Generate global insights from agent coordination
        global_insights = self._generate_global_insights(state)
        if global_insights:
            self.shared_memory.add_global_insight(global_insights)
            coordination_updates["global_insights_generated"] = True
        
        logger.info(f"Agent coordination completed for round {current_round}")
        return coordination_updates
    
    def _analyze_communications(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze inter-agent communication patterns.
        
        Args:
            messages: List of messages between agents
            
        Returns:
            Communication analysis
        """
        
        if not messages:
            return {"status": "no_communications"}
        
        # Analyze message patterns
        message_types = {}
        agent_pairs = {}
        temporal_patterns = []
        
        for message in messages:
            # Count message types
            msg_type = message.get("type", "unknown")
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
            
            # Count agent interactions
            from_agent = message.get("from", "unknown")
            to_agent = message.get("to", "unknown")
            pair_key = f"{from_agent}->{to_agent}"
            agent_pairs[pair_key] = agent_pairs.get(pair_key, 0) + 1
            
            # Track temporal patterns
            temporal_patterns.append({
                "timestamp": message.get("timestamp"),
                "type": msg_type,
                "agents": pair_key
            })
        
        return {
            "total_messages": len(messages),
            "message_types": message_types,
            "agent_interactions": agent_pairs,
            "communication_density": len(messages) / max(len(set(m.get("from") for m in messages)), 1),
            "most_common_type": max(message_types.items(), key=lambda x: x[1])[0] if message_types else None
        }
    
    def _check_convergence(self, state: MultiAgentState) -> Dict[str, Any]:
        """Check if agents have converged on results.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Convergence status and metrics
        """
        
        convergence_criteria = {
            "url_processing_complete": len(state.get("urls_to_process", [])) == 0,
            "sufficient_cases_analyzed": len(state.get("analyzed_cases", [])) >= 5,
            "evaluation_completed": state.get("evaluation_result") is not None,
            "max_rounds_reached": state.get("processing_round", 0) >= self.coordination_config.max_processing_rounds
        }
        
        convergence_score = sum(convergence_criteria.values()) / len(convergence_criteria)
        
        return {
            "criteria": convergence_criteria,
            "convergence_score": convergence_score,
            "should_continue": convergence_score < 0.8,  # Continue if less than 80% criteria met
            "recommendation": "continue" if convergence_score < 0.8 else "finalize"
        }
    
    def _generate_global_insights(self, state: MultiAgentState) -> Optional[Dict[str, Any]]:
        """Generate global insights from multi-agent coordination.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Global insights or None if insufficient data
        """
        
        # Collect insights from all agents
        research_state = state.get("research_agent_state", {})
        eval_state = state.get("evaluation_agent_state", {})
        legal_state = state.get("legal_intelligence_agent_state", {})
        
        if not any([research_state, eval_state, legal_state]):
            return None
        
        # Generate cross-agent insights
        insights = {
            "insight_type": "multi_agent_synthesis",
            "contributing_agents": [],
            "synthesis": {},
            "confidence": 0.0
        }
        
        # Research agent contributions
        if research_state:
            insights["contributing_agents"].append("research_agent")
            insights["synthesis"]["research_patterns"] = research_state.get("patterns_discovered", {})
        
        # Legal intelligence contributions
        if legal_state:
            insights["contributing_agents"].append("legal_intelligence_agent")
            insights["synthesis"]["legal_context"] = {
                "precedents_analyzed": legal_state.get("precedents_analyzed", 0),
                "regulatory_updates": legal_state.get("regulatory_updates_count", 0)
            }
        
        # Evaluation contributions
        if eval_state:
            insights["contributing_agents"].append("evaluation_agent")
            insights["synthesis"]["performance_metrics"] = {
                "accuracy_trend": eval_state.get("accuracy_trend", "unknown"),
                "evaluations_completed": eval_state.get("evaluations_completed", 0)
            }
        
        # Calculate confidence based on agent participation
        insights["confidence"] = len(insights["contributing_agents"]) / 3.0
        
        return insights if insights["confidence"] > 0.5 else None
    
    def _decide_next_agent(self, state: MultiAgentState) -> str:
        """Decide which agent to execute next in adaptive mode.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Next agent to execute
        """
        
        # Simple adaptive logic - in practice could be more sophisticated
        research_state = state.get("research_agent_state", {})
        
        if not research_state:
            return "legal_intelligence"
        
        if len(state.get("analyzed_cases", [])) > 5:
            return "evaluation"
        
        return "coordinate"
    
    def _should_continue_processing(self, state: MultiAgentState) -> str:
        """Determine if agents should continue processing.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            "continue" or "finalize"
        """
        
        convergence = self._check_convergence(state)
        
        # Continue if convergence criteria not met and within round limits
        if (convergence["should_continue"] and 
            state.get("processing_round", 0) < self.coordination_config.max_processing_rounds):
            return "continue"
        
        return "finalize"
    
    async def _finalize_results_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Finalize multi-agent processing results.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Final results
        """
        logger.info("Finalizing multi-agent results...")
        
        # Compile comprehensive results
        results = MultiAgentResults()
        
        # Individual agent results
        results.research_results = state.get("research_agent_state", {})
        results.evaluation_results = state.get("evaluation_agent_state", {})
        results.legal_intelligence_results = state.get("legal_intelligence_agent_state", {})
        
        # Coordination metrics
        results.coordination_metrics = state.get("agent_coordination", {})
        results.communication_summary = self.shared_memory.get_communication_summary()
        results.shared_insights = self.shared_memory.global_insights
        
        # Processing metrics
        results.processing_rounds = state.get("processing_round", 0)
        results.success = True
        
        # Traditional results
        if state.get("analyzed_cases"):
            results.final_result = AnalysisResult(
                cases=state["analyzed_cases"],
                total_cases=len(state.get("analyzed_cases", [])) + len(state.get("failed_urls", [])),
                successful_extractions=len(state["analyzed_cases"]),
                failed_extractions=len(state.get("failed_urls", []))
            )
        
        results.evaluation_result = state.get("evaluation_result")
        
        # Calculate total processing time
        start_time = self.shared_memory.system_metrics.get("system_start_time", {}).get("value")
        if start_time:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            results.processing_time = (datetime.now() - start_time).total_seconds()
        
        # Store final insights
        final_insight = {
            "insight_type": "final_synthesis",
            "total_cases": len(state.get("analyzed_cases", [])),
            "processing_rounds": results.processing_rounds,
            "agent_coordination_score": self._calculate_final_coordination_score(state),
            "system_performance": self._calculate_system_performance(state)
        }
        self.shared_memory.add_global_insight(final_insight)
        
        logger.info(f"Multi-agent processing completed in {results.processing_rounds} rounds")
        logger.info(f"Total processing time: {results.processing_time:.2f}s")
        
        return {"multi_agent_results": results}
    
    def _calculate_final_coordination_score(self, state: MultiAgentState) -> float:
        """Calculate final coordination effectiveness score.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Coordination score between 0.0 and 1.0
        """
        
        score = 0.0
        
        # Message exchange score
        messages = len(state.get("agent_communication_queue", []))
        if messages > 0:
            score += min(messages / 20, 1.0) * 0.4
        
        # Agent participation score
        agent_states = [
            state.get("research_agent_state"),
            state.get("evaluation_agent_state"), 
            state.get("legal_intelligence_agent_state")
        ]
        active_agents = sum(1 for s in agent_states if s)
        score += (active_agents / 3.0) * 0.4
        
        # Processing efficiency score
        rounds = state.get("processing_round", 0)
        if rounds > 0:
            efficiency = max(0, 1 - (rounds / self.coordination_config.max_processing_rounds))
            score += efficiency * 0.2
        
        return min(score, 1.0)
    
    def _calculate_system_performance(self, state: MultiAgentState) -> Dict[str, Any]:
        """Calculate overall system performance metrics.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            System performance metrics
        """
        
        total_cases = len(state.get("analyzed_cases", []))
        failed_cases = len(state.get("failed_urls", []))
        
        performance = {
            "cases_processed": total_cases,
            "case_failure_rate": failed_cases / (total_cases + failed_cases) if (total_cases + failed_cases) > 0 else 0,
            "processing_rounds": state.get("processing_round", 0),
            "agents_active": len([s for s in [
                state.get("research_agent_state"),
                state.get("evaluation_agent_state"),
                state.get("legal_intelligence_agent_state")
            ] if s]),
            "communication_effectiveness": self._calculate_final_coordination_score(state)
        }
        
        if state.get("evaluation_result"):
            eval_result = state["evaluation_result"]
            performance["fraud_detection_accuracy"] = eval_result.accuracy
            performance["fraud_detection_precision"] = eval_result.precision
            performance["fraud_detection_recall"] = eval_result.recall
        
        return performance
    
    async def run(self, max_cases: Optional[int] = None) -> MultiAgentResults:
        """Run the multi-agent system.
        
        Args:
            max_cases: Maximum number of cases to process
            
        Returns:
            Multi-agent processing results
        """
        logger.info("Starting multi-agent DOJ research system...")
        
        if max_cases:
            self.scraping_config.max_cases = max_cases
        
        # Initialize state
        initial_state: MultiAgentState = {
            # Standard state
            "urls_to_process": [],
            "analyzed_cases": [],
            "failed_urls": [],
            "scraping_config": self.scraping_config,
            "final_result": None,
            "evaluation_result": None,
            "feedback_manager": None,
            "pending_feedback": [],
            
            # Multi-agent state
            "shared_memory": self.shared_memory,
            "research_agent_state": {},
            "evaluation_agent_state": {},
            "legal_intelligence_agent_state": {},
            "agent_coordination": {},
            "current_active_agents": ["research_agent", "evaluation_agent", "legal_intelligence_agent"],
            "agent_communication_queue": [],
            
            # Coordination state
            "processing_round": 0,
            "coordination_metadata": {}
        }
        
        try:
            # Execute multi-agent workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            # Extract results
            results = final_state.get("multi_agent_results")
            if isinstance(results, MultiAgentResults):
                return results
            else:
                # Create results from final state if needed
                return self._create_results_from_state(final_state)
                
        except Exception as e:
            logger.error(f"Multi-agent execution failed: {e}")
            # Return error results
            error_results = MultiAgentResults()
            error_results.success = False
            error_results.error_log = [{"error": str(e), "timestamp": datetime.now().isoformat()}]
            return error_results
    
    def _create_results_from_state(self, final_state: Dict[str, Any]) -> MultiAgentResults:
        """Create MultiAgentResults from final state.
        
        Args:
            final_state: Final state from graph execution
            
        Returns:
            MultiAgentResults instance
        """
        results = MultiAgentResults()
        
        # Extract results from state
        results.research_results = final_state.get("research_agent_state", {})
        results.evaluation_results = final_state.get("evaluation_agent_state", {})
        results.legal_intelligence_results = final_state.get("legal_intelligence_agent_state", {})
        
        results.coordination_metrics = final_state.get("agent_coordination", {})
        results.processing_rounds = final_state.get("processing_round", 0)
        results.success = True
        
        # Create final result if cases were analyzed
        if final_state.get("analyzed_cases"):
            results.final_result = AnalysisResult(
                cases=final_state["analyzed_cases"],
                total_cases=len(final_state.get("analyzed_cases", [])) + len(final_state.get("failed_urls", [])),
                successful_extractions=len(final_state["analyzed_cases"]),
                failed_extractions=len(final_state.get("failed_urls", []))
            )
        
        results.evaluation_result = final_state.get("evaluation_result")
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics.
        
        Returns:
            System status information
        """
        return {
            "orchestrator_initialized": True,
            "agents_count": 3,
            "agents": ["research_agent", "evaluation_agent", "legal_intelligence_agent"],
            "shared_memory_status": {
                "agents_registered": len(self.shared_memory.agent_memories),
                "global_insights": len(self.shared_memory.global_insights),
                "communication_log_size": len(self.shared_memory.communication_log)
            },
            "coordination_config": {
                "strategy": self.coordination_config.coordination_strategy,
                "max_rounds": self.coordination_config.max_processing_rounds,
                "parallel_enabled": self.coordination_config.enable_parallel_processing
            }
        }
