"""Meta-Agent Orchestrator for DOJ research system.

This orchestrator integrates the Meta-Agent as a strategic controller that supervises
and coordinates the Research Agent, Evaluation Agent, and Legal Intelligence Agent.
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
from .agents.meta_agent import MetaAgent, CoordinationStrategy
from .core.utils import setup_logger

logger = setup_logger(__name__)


class MetaAgentOrchestrator:
    """Meta-Agent Orchestrator with strategic oversight and control.
    
    This orchestrator integrates a Meta-Agent that provides strategic oversight,
    dynamic coordination, and intelligent task allocation for the three specialized
    subagents: Research Agent, Evaluation Agent, and Legal Intelligence Agent.
    """
    
    def __init__(self, 
                 scraping_config: Optional[ScrapingConfig] = None,
                 coordination_config: Optional[AgentCoordinationConfig] = None,
                 llm_config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize meta-agent orchestrator.
        
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
        
        # Initialize Meta-Agent (the controller)
        self.meta_agent = MetaAgent(self.llm_config)
        
        # Initialize managed subagents
        self.research_agent = ResearchAgent(self.llm_config)
        self.evaluation_agent = EvaluationAgent(self.llm_config)
        self.legal_intelligence_agent = LegalIntelligenceAgent(self.llm_config)
        
        # Initialize all agents with shared memory
        self.meta_agent.initialize_memory(self.shared_memory)
        self.research_agent.initialize_memory(self.shared_memory)
        self.evaluation_agent.initialize_memory(self.shared_memory)
        self.legal_intelligence_agent.initialize_memory(self.shared_memory)
        
        # Build meta-controlled workflow graph
        self.graph = self._build_meta_graph()
        
        logger.info("Meta-Agent Orchestrator initialized with Meta-Agent control layer")
    
    def _build_meta_graph(self) -> StateGraph:
        """Build LangGraph with Meta-Agent strategic control.
        
        Returns:
            Compiled StateGraph for meta-agent controlled workflow
        """
        workflow = StateGraph(MultiAgentState)
        
        # Define nodes with Meta-Agent control
        workflow.add_node("initialize_system", self._initialize_system_node)
        workflow.add_node("meta_agent_control", self._meta_agent_control_node)
        workflow.add_node("execute_subagents", self._execute_subagents_node)
        workflow.add_node("meta_evaluation", self._meta_evaluation_node)
        workflow.add_node("meta_coordination", self._meta_coordination_node)
        workflow.add_node("finalize_results", self._finalize_results_node)
        
        # Set entry point
        workflow.set_entry_point("initialize_system")
        
        # Define meta-controlled workflow
        workflow.add_edge("initialize_system", "meta_agent_control")
        workflow.add_edge("meta_agent_control", "execute_subagents")
        workflow.add_edge("execute_subagents", "meta_evaluation")
        workflow.add_conditional_edges(
            "meta_evaluation",
            self._meta_should_continue,
            {
                "continue": "meta_coordination",
                "finalize": "finalize_results"
            }
        )
        workflow.add_edge("meta_coordination", "meta_agent_control")
        workflow.add_edge("finalize_results", END)
        
        return workflow.compile()
    
    async def _initialize_system_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Initialize the meta-agent controlled system.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Initialization updates
        """
        logger.info("Initializing Meta-Agent controlled system...")
        
        # Initialize system metrics in shared memory
        self.shared_memory.update_system_metric("meta_system_start_time", datetime.now())
        self.shared_memory.update_system_metric("meta_processing_round", 0)
        self.shared_memory.update_system_metric("meta_agent_active", True)
        
        # Perform initial URL fetching if needed
        from .scraping.scraper import DOJScraper
        
        if not state.get("urls_to_process"):
            logger.info("Meta-Agent directing initial URL fetching...")
            scraper = DOJScraper(state["scraping_config"])
            urls = scraper.get_press_release_urls()
            
            if state["scraping_config"].max_cases:
                urls = urls[:state["scraping_config"].max_cases]
            
            logger.info(f"Meta-Agent: Fetched {len(urls)} URLs for strategic processing")
            return {
                "urls_to_process": urls,
                "meta_system_initialized": True,
                "meta_agent_directives": ["initialize_strategic_oversight"]
            }
        
        return {
            "meta_system_initialized": True,
            "meta_agent_directives": ["begin_strategic_control"]
        }
    
    async def _meta_agent_control_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Execute Meta-Agent strategic control and planning.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Meta-Agent control directives and strategic decisions
        """
        logger.info("Meta-Agent executing strategic control...")
        
        start_time = time.time()
        
        try:
            # Execute Meta-Agent strategic oversight
            # Convert state to Dict for agent processing
            state_dict = dict(state)
            meta_updates = await self.meta_agent.process(state_dict)
            
            # Extract strategic decisions for subagent coordination
            strategy_decisions = meta_updates.get("strategy_decisions", {})
            task_allocation = meta_updates.get("task_allocation", {})
            coordination_optimization = meta_updates.get("coordination_optimization", {})
            
            # Update coordination strategy based on Meta-Agent decisions
            if strategy_decisions.get("coordination_strategy"):
                strategy_name = strategy_decisions["coordination_strategy"]
                try:
                    new_strategy = CoordinationStrategy(strategy_name)
                    self.meta_agent.system_state.coordination_strategy = new_strategy
                    logger.info(f"Meta-Agent updated coordination strategy to: {strategy_name}")
                except ValueError:
                    logger.warning(f"Invalid coordination strategy: {strategy_name}")
            
            # Generate subagent execution plan
            execution_plan = self._generate_execution_plan(strategy_decisions, task_allocation)
            
            # Log Meta-Agent performance
            processing_time = time.time() - start_time
            self.shared_memory.update_system_metric("meta_agent_control_time", processing_time)
            
            logger.info(f"Meta-Agent strategic control completed in {processing_time:.2f}s")
            
            return {
                **meta_updates,
                "meta_execution_plan": execution_plan,
                "meta_control_active": True,
                "meta_processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Meta-Agent control failed: {e}")
            return {
                "meta_agent_error": str(e),
                "meta_execution_plan": self._fallback_execution_plan(),
                "meta_control_active": False
            }
    
    def _generate_execution_plan(self, strategy_decisions: Dict[str, Any], 
                               task_allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate execution plan for subagents based on Meta-Agent decisions.
        
        Args:
            strategy_decisions: Strategic decisions from Meta-Agent
            task_allocation: Task allocation plan from Meta-Agent
            
        Returns:
            Execution plan for subagents
        """
        
        coordination_strategy = strategy_decisions.get("coordination_strategy", "adaptive")
        agent_assignments = task_allocation.get("agent_assignments", {})
        
        execution_plan = {
            "coordination_mode": coordination_strategy,
            "execution_order": [],
            "parallel_groups": [],
            "agent_priorities": strategy_decisions.get("priority_adjustments", {}),
            "resource_allocation": task_allocation.get("estimated_completion", {}),
            "meta_oversight": True
        }
        
        # Determine execution order based on coordination strategy
        if coordination_strategy == "sequential":
            execution_plan["execution_order"] = [
                "research_agent", 
                "legal_intelligence_agent", 
                "evaluation_agent"
            ]
        elif coordination_strategy == "parallel":
            execution_plan["parallel_groups"] = [
                ["research_agent", "legal_intelligence_agent"],
                ["evaluation_agent"]
            ]
        elif coordination_strategy == "load_balanced":
            # Balance based on current workload
            workload = self.meta_agent.system_state.get_workload_distribution()
            sorted_agents = sorted(workload.items(), key=lambda x: x[1])
            execution_plan["execution_order"] = [agent for agent, _ in sorted_agents]
        else:  # adaptive or hierarchical
            execution_plan["execution_order"] = [
                "research_agent",
                "legal_intelligence_agent", 
                "evaluation_agent"
            ]
            execution_plan["adaptive_control"] = True
        
        return execution_plan
    
    def _fallback_execution_plan(self) -> Dict[str, Any]:
        """Generate fallback execution plan when Meta-Agent control fails."""
        return {
            "coordination_mode": "sequential",
            "execution_order": ["research_agent", "legal_intelligence_agent", "evaluation_agent"],
            "parallel_groups": [],
            "agent_priorities": {},
            "resource_allocation": {},
            "meta_oversight": False,
            "fallback_mode": True
        }
    
    async def _execute_subagents_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Execute subagents according to Meta-Agent execution plan.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Subagent execution results
        """
        logger.info("Executing subagents under Meta-Agent control...")
        
        execution_plan = state.get("meta_execution_plan", self._fallback_execution_plan())
        coordination_mode = execution_plan["coordination_mode"]
        
        execution_results = {
            "subagent_results": {},
            "execution_summary": {},
            "coordination_effectiveness": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Convert state to Dict for agent processing
            state_dict = dict(state)
            
            if coordination_mode == "parallel" and execution_plan.get("parallel_groups"):
                # Execute parallel groups
                for group in execution_plan["parallel_groups"]:
                    await self._execute_agent_group_parallel(group, state_dict, execution_results)
            else:
                # Execute sequential or adaptive
                execution_order = execution_plan.get("execution_order", ["research_agent", "legal_intelligence_agent", "evaluation_agent"])
                await self._execute_agent_group_sequential(execution_order, state_dict, execution_results)
            
            # Calculate coordination effectiveness
            total_time = time.time() - start_time
            successful_agents = len([r for r in execution_results["subagent_results"].values() if not r.get("error")])
            execution_results["coordination_effectiveness"] = successful_agents / 3.0  # 3 total agents
            
            logger.info(f"Subagent execution completed in {total_time:.2f}s with {successful_agents}/3 agents successful")
            
        except Exception as e:
            logger.error(f"Subagent execution failed: {e}")
            execution_results["execution_error"] = str(e)
        
        return execution_results
    
    async def _execute_agent_group_parallel(self, agent_group: List[str], 
                                          state: Dict[str, Any], 
                                          execution_results: Dict[str, Any]) -> None:
        """Execute a group of agents in parallel.
        
        Args:
            agent_group: List of agent IDs to execute in parallel
            state: Current multi-agent state
            execution_results: Results dictionary to update
        """
        
        tasks = []
        for agent_id in agent_group:
            if agent_id == "research_agent":
                task = asyncio.create_task(self.research_agent.process(state))
            elif agent_id == "evaluation_agent":
                task = asyncio.create_task(self.evaluation_agent.process(state))
            elif agent_id == "legal_intelligence_agent":
                task = asyncio.create_task(self.legal_intelligence_agent.process(state))
            else:
                continue
            
            tasks.append((agent_id, task))
        
        # Execute tasks in parallel
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Process results
        for (agent_id, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                execution_results["subagent_results"][agent_id] = {"error": str(result)}
                logger.error(f"Parallel execution failed for {agent_id}: {result}")
            else:
                execution_results["subagent_results"][agent_id] = result
                # Update state with agent results
                if isinstance(result, dict):
                    state.update(result)
    
    async def _execute_agent_group_sequential(self, agent_order: List[str], 
                                            state: Dict[str, Any], 
                                            execution_results: Dict[str, Any]) -> None:
        """Execute agents sequentially according to specified order.
        
        Args:
            agent_order: Ordered list of agent IDs to execute
            state: Current multi-agent state
            execution_results: Results dictionary to update
        """
        
        for agent_id in agent_order:
            try:
                if agent_id == "research_agent":
                    result = await self.research_agent.process(state)
                elif agent_id == "evaluation_agent":
                    result = await self.evaluation_agent.process(state)
                elif agent_id == "legal_intelligence_agent":
                    result = await self.legal_intelligence_agent.process(state)
                else:
                    logger.warning(f"Unknown agent ID: {agent_id}")
                    continue
                
                execution_results["subagent_results"][agent_id] = result
                
                # Update state with agent results
                if isinstance(result, dict):
                    state.update(result)
                
                logger.info(f"Sequential execution completed for {agent_id}")
                
            except Exception as e:
                execution_results["subagent_results"][agent_id] = {"error": str(e)}
                logger.error(f"Sequential execution failed for {agent_id}: {e}")
    
    async def _meta_evaluation_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Meta-Agent evaluates subagent performance and system state.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Meta-evaluation results and decisions
        """
        logger.info("Meta-Agent performing system evaluation...")
        
        try:
            # Evaluate subagent performance
            performance_evaluation = await self._evaluate_subagent_performance(state)
            
            # Evaluate system convergence
            convergence_analysis = self._analyze_system_convergence(state)
            
            # Generate meta-level insights
            meta_insights = await self._generate_meta_system_insights(state)
            
            # Update Meta-Agent system state
            processing_round = state.get("processing_round", 0) + 1
            self.meta_agent.system_state.processing_round = processing_round
            
            evaluation_results = {
                "meta_evaluation_completed": True,
                "performance_evaluation": performance_evaluation,
                "convergence_analysis": convergence_analysis,
                "meta_insights": meta_insights,
                "processing_round": processing_round,
                "meta_recommendation": convergence_analysis.get("recommendation", "continue")
            }
            
            logger.info(f"Meta-evaluation completed for round {processing_round}")
            
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Meta-evaluation failed: {e}")
            return {
                "meta_evaluation_error": str(e),
                "meta_recommendation": "continue",  # Conservative approach
                "processing_round": state.get("processing_round", 0) + 1
            }
    
    async def _evaluate_subagent_performance(self, state: MultiAgentState) -> Dict[str, Any]:
        """Evaluate individual subagent performance under Meta-Agent oversight.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Performance evaluation for each subagent
        """
        
        performance_eval = {
            "timestamp": datetime.now().isoformat(),
            "agent_performance": {},
            "overall_system_performance": 0.0,
            "performance_alerts": [],
            "improvement_recommendations": []
        }
        
        # Evaluate Research Agent
        research_state = state.get("research_agent_state", {})
        if research_state:
            research_perf = {
                "agent_id": "research_agent",
                "cases_analyzed": research_state.get("cases_analyzed", 0),
                "patterns_discovered": len(research_state.get("patterns_discovered", {}).get("fraud_patterns", [])),
                "performance_score": 0.0
            }
            
            # Calculate performance score
            if research_perf["cases_analyzed"] > 0:
                research_perf["performance_score"] = min(1.0, research_perf["cases_analyzed"] / 10) * 0.7 + \
                                                   min(1.0, research_perf["patterns_discovered"] / 5) * 0.3
            
            performance_eval["agent_performance"]["research_agent"] = research_perf
        
        # Evaluate Evaluation Agent
        eval_state = state.get("evaluation_agent_state", {})
        if eval_state:
            eval_perf = {
                "agent_id": "evaluation_agent",
                "evaluations_completed": eval_state.get("evaluations_completed", 0),
                "accuracy_trend": eval_state.get("accuracy_trend", "unknown"),
                "performance_score": 0.0
            }
            
            # Calculate performance score based on evaluation quality
            if eval_perf["evaluations_completed"] > 0:
                trend_score = {"improving": 1.0, "stable": 0.8, "declining": 0.4, "unknown": 0.5}
                eval_perf["performance_score"] = min(1.0, eval_perf["evaluations_completed"] / 5) * 0.6 + \
                                                trend_score.get(eval_perf["accuracy_trend"], 0.5) * 0.4
            
            performance_eval["agent_performance"]["evaluation_agent"] = eval_perf
        
        # Evaluate Legal Intelligence Agent
        legal_state = state.get("legal_intelligence_agent_state", {})
        if legal_state:
            legal_perf = {
                "agent_id": "legal_intelligence_agent",
                "precedents_analyzed": legal_state.get("precedents_analyzed", 0),
                "regulatory_updates": legal_state.get("regulatory_updates_count", 0),
                "performance_score": 0.0
            }
            
            # Calculate performance score
            legal_perf["performance_score"] = min(1.0, legal_perf["precedents_analyzed"] / 3) * 0.6 + \
                                            min(1.0, legal_perf["regulatory_updates"] / 2) * 0.4
            
            performance_eval["agent_performance"]["legal_intelligence_agent"] = legal_perf
        
        # Calculate overall system performance
        agent_scores = [perf.get("performance_score", 0) for perf in performance_eval["agent_performance"].values()]
        performance_eval["overall_system_performance"] = sum(agent_scores) / len(agent_scores) if agent_scores else 0.0
        
        # Generate alerts and recommendations
        if performance_eval["overall_system_performance"] < 0.6:
            performance_eval["performance_alerts"].append("Overall system performance below threshold")
            performance_eval["improvement_recommendations"].append("Consider coordination strategy adjustment")
        
        return performance_eval
    
    def _analyze_system_convergence(self, state: MultiAgentState) -> Dict[str, Any]:
        """Analyze system convergence and completion criteria.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Convergence analysis and recommendations
        """
        
        convergence = {
            "timestamp": datetime.now().isoformat(),
            "convergence_criteria": {},
            "convergence_score": 0.0,
            "recommendation": "continue",
            "completion_factors": {}
        }
        
        # Check convergence criteria
        criteria = {
            "url_processing_complete": len(state.get("urls_to_process", [])) == 0,
            "sufficient_cases_analyzed": len(state.get("analyzed_cases", [])) >= 5,
            "evaluation_completed": state.get("evaluation_result") is not None,
            "meta_rounds_sufficient": state.get("processing_round", 0) >= 2,
            "system_stable": len(state.get("failed_urls", [])) <= len(state.get("analyzed_cases", [])) * 0.3
        }
        
        convergence["convergence_criteria"] = criteria
        
        # Calculate convergence score
        convergence_score = sum(criteria.values()) / len(criteria)
        convergence["convergence_score"] = convergence_score
        
        # Determine recommendation
        max_rounds = self.coordination_config.max_processing_rounds
        current_round = state.get("processing_round", 0)
        
        if convergence_score >= 0.8 or current_round >= max_rounds:
            convergence["recommendation"] = "finalize"
        elif convergence_score >= 0.6 and current_round >= max_rounds - 1:
            convergence["recommendation"] = "finalize"
        else:
            convergence["recommendation"] = "continue"
        
        # Completion factors
        convergence["completion_factors"] = {
            "cases_processed": len(state.get("analyzed_cases", [])),
            "processing_rounds": current_round,
            "system_health": "good" if convergence_score > 0.7 else "fair" if convergence_score > 0.5 else "poor",
            "meta_agent_confidence": convergence_score
        }
        
        return convergence
    
    async def _generate_meta_system_insights(self, state: MultiAgentState) -> Dict[str, Any]:
        """Generate meta-level insights about the entire system.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Meta-level system insights
        """
        
        insights = {
            "timestamp": datetime.now().isoformat(),
            "system_learning": {},
            "optimization_insights": {},
            "strategic_recommendations": [],
            "future_improvements": []
        }
        
        # System learning analysis
        total_cases = len(state.get("analyzed_cases", []))
        processing_rounds = state.get("processing_round", 0)
        
        insights["system_learning"] = {
            "cases_per_round": total_cases / max(1, processing_rounds),
            "learning_efficiency": total_cases / max(1, len(state.get("urls_to_process", [])) + total_cases),
            "coordination_maturity": min(1.0, processing_rounds / 3)
        }
        
        # Optimization insights from Meta-Agent
        if hasattr(self.meta_agent, 'optimization_insights') and self.meta_agent.optimization_insights:
            recent_insights = self.meta_agent.optimization_insights[-3:]
            insights["optimization_insights"] = {
                "recent_optimizations": len(recent_insights),
                "optimization_effectiveness": "improving" if len(recent_insights) > 1 else "stable"
            }
        
        # Strategic recommendations
        if insights["system_learning"]["learning_efficiency"] < 0.7:
            insights["strategic_recommendations"].append("Focus on improving case processing efficiency")
        
        if processing_rounds > 2 and total_cases < 10:
            insights["strategic_recommendations"].append("Increase parallelization to boost throughput")
        
        # Future improvements
        insights["future_improvements"] = [
            "Implement predictive task allocation",
            "Enhanced cross-agent knowledge sharing",
            "Automated performance optimization",
            "Real-time strategy adaptation"
        ]
        
        return insights
    
    def _meta_should_continue(self, state: MultiAgentState) -> str:
        """Meta-Agent decision on whether to continue processing.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            "continue" or "finalize"
        """
        
        meta_evaluation = state.get("meta_evaluation_completed", False)
        if not meta_evaluation:
            return "finalize"  # Safety fallback
        
        recommendation = state.get("meta_recommendation", "continue")
        convergence_score = state.get("convergence_analysis", {}).get("convergence_score", 0.0)
        processing_round = state.get("processing_round", 0)
        
        # Meta-Agent override logic
        if processing_round >= self.coordination_config.max_processing_rounds:
            logger.info(f"Meta-Agent: Maximum rounds ({self.coordination_config.max_processing_rounds}) reached")
            return "finalize"
        
        if convergence_score >= 0.85:
            logger.info(f"Meta-Agent: High convergence score ({convergence_score:.2f}) - finalizing")
            return "finalize"
        
        if recommendation == "finalize":
            logger.info("Meta-Agent: Recommending finalization based on analysis")
            return "finalize"
        
        logger.info(f"Meta-Agent: Continuing processing (round {processing_round}, convergence: {convergence_score:.2f})")
        return "continue"
    
    async def _meta_coordination_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Meta-Agent coordination and optimization between processing rounds.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Coordination updates and optimizations
        """
        logger.info("Meta-Agent performing inter-round coordination...")
        
        coordination_updates = {
            "meta_coordination_completed": True,
            "strategy_adjustments": {},
            "performance_optimizations": {},
            "next_round_preparation": {}
        }
        
        try:
            # Analyze performance trends
            performance_eval = state.get("performance_evaluation", {})
            overall_performance = performance_eval.get("overall_system_performance", 0.0)
            
            # Adjust strategy if needed
            if overall_performance < 0.6:
                coordination_updates["strategy_adjustments"]["performance_boost"] = True
                coordination_updates["strategy_adjustments"]["new_strategy"] = "sequential"  # More controlled
                self.meta_agent.system_state.coordination_strategy = CoordinationStrategy.SEQUENTIAL
            elif overall_performance > 0.85:
                coordination_updates["strategy_adjustments"]["efficiency_mode"] = True
                coordination_updates["strategy_adjustments"]["new_strategy"] = "parallel"  # More efficient
                self.meta_agent.system_state.coordination_strategy = CoordinationStrategy.PARALLEL
            
            # Prepare for next round
            next_round = state.get("processing_round", 0) + 1
            coordination_updates["next_round_preparation"] = {
                "round_number": next_round,
                "expected_strategy": self.meta_agent.system_state.coordination_strategy.value,
                "performance_targets": {
                    "min_cases": 5,
                    "min_accuracy": 0.8,
                    "coordination_quality": 0.75
                }
            }
            
            logger.info(f"Meta-Agent coordination prepared for round {next_round}")
            
        except Exception as e:
            logger.error(f"Meta-Agent coordination failed: {e}")
            coordination_updates["coordination_error"] = str(e)
        
        return coordination_updates
    
    async def _finalize_results_node(self, state: MultiAgentState) -> Dict[str, Any]:
        """Finalize results under Meta-Agent oversight.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Final results with Meta-Agent insights
        """
        logger.info("Meta-Agent finalizing system results...")
        
        # Compile comprehensive results
        results = MultiAgentResults()
        
        # Individual agent results
        results.research_results = state.get("research_agent_state", {})
        results.evaluation_results = state.get("evaluation_agent_state", {})
        results.legal_intelligence_results = state.get("legal_intelligence_agent_state", {})
        
        # Meta-Agent specific results
        meta_results = {
            "meta_agent_oversight": True,
            "strategic_decisions_made": len(self.meta_agent.decision_history),
            "optimization_insights": len(self.meta_agent.optimization_insights),
            "final_coordination_strategy": self.meta_agent.system_state.coordination_strategy.value,
            "system_performance_score": state.get("performance_evaluation", {}).get("overall_system_performance", 0.0),
            "meta_agent_recommendations": state.get("meta_insights", {}).get("strategic_recommendations", [])
        }
        
        # Coordination metrics
        results.coordination_metrics = state.get("agent_coordination", {})
        results.coordination_metrics.update(meta_results)
        
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
        start_time = self.shared_memory.system_metrics.get("meta_system_start_time", {}).get("value")
        if start_time:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            results.processing_time = (datetime.now() - start_time).total_seconds()
        
        # Meta-Agent final insights
        final_meta_insight = {
            "insight_type": "meta_agent_final_analysis",
            "total_cases": len(state.get("analyzed_cases", [])),
            "processing_rounds": results.processing_rounds,
            "meta_coordination_effectiveness": meta_results["system_performance_score"],
            "strategic_success": len(self.meta_agent.decision_history) > 0,
            "system_maturity": "mature" if results.processing_rounds > 2 else "developing"
        }
        self.shared_memory.add_global_insight(final_meta_insight)
        
        logger.info(f"Meta-Agent system completed in {results.processing_rounds} rounds")
        logger.info(f"Total processing time: {results.processing_time:.2f}s")
        logger.info(f"Meta-Agent strategic decisions: {len(self.meta_agent.decision_history)}")
        
        return {"multi_agent_results": results}
    
    async def run(self, max_cases: Optional[int] = None) -> MultiAgentResults:
        """Run the Meta-Agent controlled multi-agent system.
        
        Args:
            max_cases: Maximum number of cases to process
            
        Returns:
            Multi-agent processing results with Meta-Agent oversight
        """
        logger.info("Starting Meta-Agent controlled DOJ research system...")
        
        if max_cases:
            self.scraping_config.max_cases = max_cases
        
        # Initialize state for Meta-Agent control
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
            "current_active_agents": ["meta_agent", "research_agent", "evaluation_agent", "legal_intelligence_agent"],
            "agent_communication_queue": [],
            
            # Meta-Agent specific state
            "processing_round": 0,
            "coordination_metadata": {},
            "meta_agent_active": True,
            "meta_control_mode": True
        }
        
        try:
            # Execute Meta-Agent controlled workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            # Extract results
            results = final_state.get("multi_agent_results")
            if isinstance(results, MultiAgentResults):
                return results
            else:
                # Create results from final state if needed
                return self._create_results_from_state(final_state)
                
        except Exception as e:
            logger.error(f"Meta-Agent controlled execution failed: {e}")
            # Return error results
            error_results = MultiAgentResults()
            error_results.success = False
            error_results.error_log = [{"error": str(e), "timestamp": datetime.now().isoformat()}]
            return error_results
    
    def _create_results_from_state(self, final_state: Dict[str, Any]) -> MultiAgentResults:
        """Create MultiAgentResults from final state with Meta-Agent data.
        
        Args:
            final_state: Final state from graph execution
            
        Returns:
            MultiAgentResults instance with Meta-Agent oversight data
        """
        results = MultiAgentResults()
        
        # Extract results from state
        results.research_results = final_state.get("research_agent_state", {})
        results.evaluation_results = final_state.get("evaluation_agent_state", {})
        results.legal_intelligence_results = final_state.get("legal_intelligence_agent_state", {})
        
        # Add Meta-Agent coordination data
        results.coordination_metrics = final_state.get("agent_coordination", {})
        results.coordination_metrics["meta_agent_controlled"] = True
        results.coordination_metrics["meta_decisions"] = len(self.meta_agent.decision_history)
        
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
        """Get current Meta-Agent controlled system status.
        
        Returns:
            System status with Meta-Agent oversight information
        """
        return {
            "orchestrator_type": "Meta-Agent Controlled",
            "meta_agent_active": True,
            "agents_count": 4,  # Including Meta-Agent
            "agents": ["meta_agent", "research_agent", "evaluation_agent", "legal_intelligence_agent"],
            "coordination_strategy": self.meta_agent.system_state.coordination_strategy.value,
            "meta_agent_decisions": len(self.meta_agent.decision_history),
            "optimization_insights": len(self.meta_agent.optimization_insights),
            "shared_memory_status": {
                "agents_registered": len(self.shared_memory.agent_memories),
                "global_insights": len(self.shared_memory.global_insights),
                "communication_log_size": len(self.shared_memory.communication_log)
            },
            "coordination_config": {
                "strategy": self.coordination_config.coordination_strategy,
                "max_rounds": self.coordination_config.max_processing_rounds,
                "parallel_enabled": self.coordination_config.enable_parallel_processing,
                "meta_oversight": True
            }
        }
