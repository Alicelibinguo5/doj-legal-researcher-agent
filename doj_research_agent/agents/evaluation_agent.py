"""Evaluation Agent for DOJ research multi-agent system."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent
from ..evaluation.evaluate import FraudDetectionEvaluator
from ..evaluation.evaluation_types import EvaluationResult, TestCase
from ..core.models import CaseInfo


class EvaluationAgent(BaseAgent):
    """Specialized agent for performance evaluation and quality assessment.
    
    This agent focuses on evaluating system performance, assessing quality
    of fraud detection, and providing feedback for continuous improvement.
    """
    
    def __init__(self, llm_config: Optional[Dict] = None) -> None:
        """Initialize Evaluation Agent.
        
        Args:
            llm_config: Configuration for LLM integration
        """
        super().__init__("evaluation_agent", llm_config)
        self.evaluator = FraudDetectionEvaluator()
        self.evaluation_history: List[Dict[str, Any]] = []
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process evaluation tasks and assess system performance.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Dictionary of evaluation updates
        """
        self.logger.info("Evaluation Agent starting processing...")
        
        # Initialize memory if not done
        if not self.memory:
            self.initialize_memory(state["shared_memory"])
        
        updates = {}
        
        # Evaluate current results if available
        if state.get("analyzed_cases"):
            evaluation_results = await self._evaluate_system_performance(state)
            updates.update(evaluation_results)
        
        # Process insights from other agents
        agent_insights = await self._process_agent_insights(state)
        if agent_insights:
            updates["agent_insights_evaluation"] = agent_insights
        
        # Evaluate cross-agent coordination effectiveness
        coordination_eval = self._evaluate_agent_coordination(state)
        updates["coordination_evaluation"] = coordination_eval
        
        # Update evaluation memory and history
        self._update_evaluation_memory(state, updates)
        
        # Share feedback with other agents
        await self._share_evaluation_feedback(state, updates)
        
        # Update agent state
        updates["evaluation_agent_state"] = {
            "last_evaluation": datetime.now().isoformat(),
            "evaluations_completed": len(self.evaluation_history),
            "accuracy_trend": self._calculate_accuracy_trend(),
            "performance_metrics": self._get_current_performance_metrics()
        }
        
        self.logger.info("Evaluation Agent completed processing")
        return updates
    
    async def _evaluate_system_performance(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate overall system performance.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            System performance evaluation results
        """
        
        # Create test cases from analyzed cases
        test_cases = self._create_test_cases_from_state(state)
        
        if not test_cases:
            return {"evaluation_skipped": "No test cases available"}
        
        try:
            # Run comprehensive evaluation
            evaluation_result = self.evaluator.evaluate_dataset(test_cases)
            
            # Analyze performance trends
            performance_analysis = await self._analyze_performance_trends(evaluation_result)
            
            # Evaluate specific fraud detection quality
            fraud_quality = self._evaluate_fraud_detection_quality(state["analyzed_cases"])
            
            # Store evaluation in history
            evaluation_record = {
                "timestamp": datetime.now().isoformat(),
                "accuracy": evaluation_result.accuracy,
                "precision": evaluation_result.precision,
                "recall": evaluation_result.recall,
                "f1_score": evaluation_result.f1_score,
                "test_cases_count": len(test_cases),
                "performance_analysis": performance_analysis
            }
            self.evaluation_history.append(evaluation_record)
            
            # Update memory
            self.update_memory("latest_evaluation", evaluation_record)
            
            # Log performance metrics
            self.log_performance_metric("system_accuracy", evaluation_result.accuracy)
            self.log_performance_metric("fraud_detection_precision", evaluation_result.precision)
            self.log_performance_metric("fraud_detection_recall", evaluation_result.recall)
            
            return {
                "evaluation_result": evaluation_result,
                "performance_analysis": performance_analysis,
                "fraud_quality_assessment": fraud_quality,
                "evaluation_summary": {
                    "accuracy": evaluation_result.accuracy,
                    "precision": evaluation_result.precision,
                    "recall": evaluation_result.recall,
                    "f1_score": evaluation_result.f1_score,
                    "test_cases": len(test_cases)
                }
            }
            
        except Exception as e:
            self.logger.error(f"System evaluation failed: {e}")
            return {
                "evaluation_error": str(e),
                "fallback_evaluation": self._fallback_evaluation(state["analyzed_cases"])
            }
    
    def _create_test_cases_from_state(self, state: Dict[str, Any]) -> List[TestCase]:
        """Create test cases from current analyzed cases.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            List of test cases for evaluation
        """
        test_cases = []
        
        # Use recent cases for evaluation (last 20 cases or all if fewer)
        recent_cases = state["analyzed_cases"][-20:] if len(state["analyzed_cases"]) > 20 else state["analyzed_cases"]
        
        for case in recent_cases:
            test_case = TestCase(
                text=case.title,
                expected_fraud_flag=case.fraud_info.is_fraud if case.fraud_info else False,
                expected_fraud_type=None,  # Could be enhanced with fraud type
                expected_money_laundering_flag=case.money_laundering_flag or False,
                title=case.title,
                source_url=case.url
            )
            test_cases.append(test_case)
        
        return test_cases
    
    async def _analyze_performance_trends(self, current_result: EvaluationResult) -> Dict[str, Any]:
        """Analyze performance trends using LLM.
        
        Args:
            current_result: Current evaluation result
            
        Returns:
            Performance trends analysis
        """
        
        # Get historical performance from memory
        historical_evaluations = self.get_memory("evaluation_history") or []
        
        # Prepare trend data
        recent_history = self.evaluation_history[-5:] if len(self.evaluation_history) >= 5 else self.evaluation_history
        
        trend_prompt = f"""
        Analyze system performance trends based on current and historical evaluations:
        
        Current Evaluation:
        - Accuracy: {current_result.accuracy:.3f}
        - Precision: {current_result.precision:.3f}
        - Recall: {current_result.recall:.3f}
        - F1 Score: {current_result.f1_score:.3f}
        
        Recent Historical Performance: {recent_history}
        
        Analyze:
        1. Performance trends (improving/declining/stable)
        2. Specific areas of strength and weakness
        3. Potential causes of performance changes
        4. Recommendations for improvement
        5. Quality assurance insights
        6. System reliability assessment
        
        Provide actionable recommendations for the research and legal intelligence agents.
        """
        
        try:
            response = await self.generate_llm_response(trend_prompt)
            analysis = self._parse_performance_analysis(response)
            return analysis
        except Exception as e:
            self.logger.error(f"Performance trend analysis failed: {e}")
            return self._fallback_trend_analysis(current_result)
    
    def _fallback_trend_analysis(self, current_result: EvaluationResult) -> Dict[str, Any]:
        """Provide fallback trend analysis when LLM fails.
        
        Args:
            current_result: Current evaluation result
            
        Returns:
            Basic trend analysis
        """
        
        trend_direction = "unknown"
        if len(self.evaluation_history) >= 2:
            recent_accuracy = current_result.accuracy
            previous_accuracy = self.evaluation_history[-2]["accuracy"]
            
            if recent_accuracy > previous_accuracy + 0.05:
                trend_direction = "improving"
            elif recent_accuracy < previous_accuracy - 0.05:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        
        return {
            "trend_direction": trend_direction,
            "current_accuracy": current_result.accuracy,
            "current_precision": current_result.precision,
            "current_recall": current_result.recall,
            "evaluations_count": len(self.evaluation_history),
            "analysis_type": "fallback"
        }
    
    def _evaluate_fraud_detection_quality(self, cases: List[CaseInfo]) -> Dict[str, Any]:
        """Evaluate quality of fraud detection specifically.
        
        Args:
            cases: List of analyzed cases
            
        Returns:
            Fraud detection quality assessment
        """
        
        fraud_cases = [c for c in cases if c.fraud_info and c.fraud_info.is_fraud]
        non_fraud_cases = [c for c in cases if not (c.fraud_info and c.fraud_info.is_fraud)]
        
        # Assess fraud evidence quality
        fraud_with_evidence = [c for c in fraud_cases if c.fraud_info and c.fraud_info.evidence]
        evidence_rate = len(fraud_with_evidence) / len(fraud_cases) if fraud_cases else 0
        
        # Assess charge alignment
        fraud_with_charges = [c for c in fraud_cases if c.charges]
        charge_alignment_rate = len(fraud_with_charges) / len(fraud_cases) if fraud_cases else 0
        
        # Assess categorization quality
        categorized_cases = [c for c in cases if c.charge_categories]
        categorization_rate = len(categorized_cases) / len(cases) if cases else 0
        
        quality_assessment = {
            "total_cases": len(cases),
            "fraud_cases": len(fraud_cases),
            "fraud_rate": len(fraud_cases) / len(cases) if cases else 0,
            "evidence_quality": {
                "cases_with_evidence": len(fraud_with_evidence),
                "evidence_rate": evidence_rate
            },
            "charge_alignment": {
                "fraud_with_charges": len(fraud_with_charges),
                "alignment_rate": charge_alignment_rate
            },
            "categorization": {
                "categorized_cases": len(categorized_cases),
                "categorization_rate": categorization_rate
            }
        }
        
        return quality_assessment
    
    async def _process_agent_insights(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process and evaluate insights from other agents.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Evaluation of agent insights
        """
        
        insights_evaluation = {}
        
        # Evaluate research agent insights
        research_messages = self.get_agent_messages(state, "research_agent")
        if research_messages:
            research_eval = await self._evaluate_research_insights(research_messages)
            insights_evaluation["research_agent"] = research_eval
        
        # Evaluate legal intelligence insights
        legal_messages = self.get_agent_messages(state, "legal_intelligence_agent")
        if legal_messages:
            legal_eval = await self._evaluate_legal_insights(legal_messages)
            insights_evaluation["legal_intelligence_agent"] = legal_eval
        
        return insights_evaluation
    
    async def _evaluate_research_insights(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate quality of research agent insights.
        
        Args:
            messages: Messages from research agent
            
        Returns:
            Research insights evaluation
        """
        
        pattern_insights = []
        for message in messages:
            if message["type"] == "pattern_insights":
                pattern_insights.append(message["data"])
        
        if not pattern_insights:
            return {"evaluation": "no_insights_available"}
        
        # Evaluate insight quality using LLM
        evaluation_prompt = f"""
        Evaluate the quality of these research insights from the Research Agent:
        
        Insights: {pattern_insights}
        
        Assess:
        1. Accuracy and relevance of identified patterns
        2. Actionability of the insights
        3. Novelty and value of discoveries
        4. Completeness of pattern analysis
        5. Potential for fraud prevention and detection
        
        Rate each aspect 1-10 and provide specific feedback for improvement.
        """
        
        try:
            response = await self.generate_llm_response(evaluation_prompt)
            return self._parse_insight_evaluation(response, "research")
        except Exception as e:
            self.logger.error(f"Research insight evaluation failed: {e}")
            return {"evaluation_error": str(e), "insight_count": len(pattern_insights)}
    
    async def _evaluate_legal_insights(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate quality of legal intelligence insights.
        
        Args:
            messages: Messages from legal intelligence agent
            
        Returns:
            Legal insights evaluation
        """
        
        legal_insights = []
        for message in messages:
            if message["type"] in ["legal_precedents", "regulatory_updates", "legal_accuracy_feedback"]:
                legal_insights.append({
                    "type": message["type"],
                    "data": message["data"]
                })
        
        if not legal_insights:
            return {"evaluation": "no_legal_insights_available"}
        
        # Evaluate legal insight quality
        evaluation_prompt = f"""
        Evaluate the quality of these legal intelligence insights:
        
        Legal Insights: {legal_insights}
        
        Assess:
        1. Legal accuracy and relevance
        2. Precedent analysis quality
        3. Regulatory compliance insights
        4. Jurisdictional analysis value
        5. Integration with fraud detection goals
        
        Rate each aspect 1-10 and provide recommendations for legal intelligence improvement.
        """
        
        try:
            response = await self.generate_llm_response(evaluation_prompt)
            return self._parse_insight_evaluation(response, "legal")
        except Exception as e:
            self.logger.error(f"Legal insight evaluation failed: {e}")
            return {"evaluation_error": str(e), "insight_count": len(legal_insights)}
    
    def _evaluate_agent_coordination(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate effectiveness of agent coordination.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Agent coordination evaluation
        """
        
        communication_queue = state.get("agent_communication_queue", [])
        shared_memory = state.get("shared_memory")
        
        coordination_metrics = {
            "total_messages": len(communication_queue),
            "active_agents": len(state.get("current_active_agents", [])),
            "message_types": {},
            "agent_interactions": {}
        }
        
        # Analyze message patterns
        for message in communication_queue:
            msg_type = message.get("type", "unknown")
            coordination_metrics["message_types"][msg_type] = (
                coordination_metrics["message_types"].get(msg_type, 0) + 1
            )
            
            # Track agent-to-agent interactions
            from_agent = message.get("from", "unknown")
            to_agent = message.get("to", "unknown")
            interaction_key = f"{from_agent}->{to_agent}"
            coordination_metrics["agent_interactions"][interaction_key] = (
                coordination_metrics["agent_interactions"].get(interaction_key, 0) + 1
            )
        
        # Evaluate shared memory usage
        if shared_memory and hasattr(shared_memory, 'get_communication_summary'):
            memory_summary = shared_memory.get_communication_summary()
            coordination_metrics["memory_utilization"] = memory_summary
        
        # Assess coordination effectiveness
        effectiveness_score = self._calculate_coordination_effectiveness(coordination_metrics)
        
        return {
            "coordination_metrics": coordination_metrics,
            "effectiveness_score": effectiveness_score,
            "recommendations": self._get_coordination_recommendations(coordination_metrics)
        }
    
    def _calculate_coordination_effectiveness(self, metrics: Dict[str, Any]) -> float:
        """Calculate coordination effectiveness score.
        
        Args:
            metrics: Coordination metrics
            
        Returns:
            Effectiveness score between 0.0 and 1.0
        """
        
        score = 0.0
        
        # Message volume score (normalized)
        message_count = metrics["total_messages"]
        if message_count > 0:
            score += min(message_count / 20, 1.0) * 0.3  # 30% weight
        
        # Agent interaction diversity score
        interactions = metrics["agent_interactions"]
        if interactions:
            unique_interactions = len(interactions)
            max_possible = 6  # 3 agents * 2 directions each
            score += (unique_interactions / max_possible) * 0.4  # 40% weight
        
        # Message type diversity score
        message_types = metrics["message_types"]
        if message_types:
            type_diversity = len(message_types)
            score += min(type_diversity / 10, 1.0) * 0.3  # 30% weight
        
        return min(score, 1.0)
    
    def _get_coordination_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Get recommendations for improving coordination.
        
        Args:
            metrics: Coordination metrics
            
        Returns:
            List of recommendations
        """
        
        recommendations = []
        
        if metrics["total_messages"] < 5:
            recommendations.append("Increase inter-agent communication frequency")
        
        if len(metrics["agent_interactions"]) < 3:
            recommendations.append("Improve agent-to-agent interaction patterns")
        
        if len(metrics["message_types"]) < 3:
            recommendations.append("Diversify types of information shared between agents")
        
        if not recommendations:
            recommendations.append("Agent coordination is functioning well")
        
        return recommendations
    
    def _update_evaluation_memory(self, state: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """Update evaluation memory with current state and results.
        
        Args:
            state: Current multi-agent state
            updates: Updates from this evaluation cycle
        """
        
        # Update system performance statistics
        current_stats = {
            "total_cases": len(state.get("analyzed_cases", [])),
            "failed_urls": len(state.get("failed_urls", [])),
            "success_rate": self._calculate_success_rate(state),
            "timestamp": datetime.now().isoformat()
        }
        
        self.update_memory("system_stats", current_stats)
        
        # Update evaluation history in memory (keep last 50 evaluations)
        if self.evaluation_history:
            self.update_memory("evaluation_history", self.evaluation_history[-50:])
        
        # Store agent coordination insights
        if "coordination_evaluation" in updates:
            self.update_memory("coordination_insights", updates["coordination_evaluation"])
    
    def _calculate_success_rate(self, state: Dict[str, Any]) -> float:
        """Calculate overall system success rate.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Success rate between 0.0 and 1.0
        """
        
        analyzed = len(state.get("analyzed_cases", []))
        failed = len(state.get("failed_urls", []))
        total = analyzed + failed
        
        return analyzed / total if total > 0 else 0.0
    
    def _calculate_accuracy_trend(self) -> str:
        """Calculate accuracy trend from evaluation history.
        
        Returns:
            Trend direction: "improving", "declining", "stable", or "insufficient_data"
        """
        
        if len(self.evaluation_history) < 3:
            return "insufficient_data"
        
        recent_evals = self.evaluation_history[-3:]
        accuracies = [eval_record["accuracy"] for eval_record in recent_evals]
        
        # Simple trend calculation
        if accuracies[-1] > accuracies[0] + 0.05:
            return "improving"
        elif accuracies[-1] < accuracies[0] - 0.05:
            return "declining"
        else:
            return "stable"
    
    def _get_current_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics summary.
        
        Returns:
            Performance metrics dictionary
        """
        
        if not self.evaluation_history:
            return {"status": "no_evaluations_completed"}
        
        latest = self.evaluation_history[-1]
        return {
            "latest_accuracy": latest["accuracy"],
            "latest_precision": latest["precision"],
            "latest_recall": latest["recall"],
            "latest_f1": latest["f1_score"],
            "evaluation_count": len(self.evaluation_history),
            "trend": self._calculate_accuracy_trend()
        }
    
    async def _share_evaluation_feedback(self, state: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """Share evaluation feedback with other agents.
        
        Args:
            state: Current multi-agent state
            updates: Updates from this evaluation cycle
        """
        
        # Share performance feedback with research agent
        if "evaluation_result" in updates:
            eval_result = updates["evaluation_result"]
            self.communicate_with_agent(
                state, "research_agent", "performance_feedback", {
                    "accuracy": eval_result.accuracy,
                    "precision": eval_result.precision,
                    "recall": eval_result.recall,
                    "recommendations": updates.get("performance_analysis", {}).get("recommendations", [])
                }
            )
        
        # Share legal accuracy feedback with legal intelligence agent
        if "fraud_quality_assessment" in updates:
            self.communicate_with_agent(
                state, "legal_intelligence_agent", "quality_feedback",
                updates["fraud_quality_assessment"]
            )
        
        # Share coordination insights with all agents
        if "coordination_evaluation" in updates:
            coordination_data = updates["coordination_evaluation"]
            for agent_id in ["research_agent", "legal_intelligence_agent"]:
                self.communicate_with_agent(
                    state, agent_id, "coordination_feedback", coordination_data
                )
    
    def _fallback_evaluation(self, cases: List[CaseInfo]) -> Dict[str, Any]:
        """Provide fallback evaluation when main evaluation fails.
        
        Args:
            cases: List of analyzed cases
            
        Returns:
            Basic evaluation results
        """
        
        fraud_cases = [c for c in cases if c.fraud_info and c.fraud_info.is_fraud]
        
        return {
            "total_cases": len(cases),
            "fraud_cases": len(fraud_cases),
            "fraud_rate": len(fraud_cases) / len(cases) if cases else 0,
            "evaluation_type": "fallback",
            "basic_metrics": {
                "cases_with_charges": len([c for c in cases if c.charges]),
                "cases_with_categories": len([c for c in cases if c.charge_categories]),
                "money_laundering_cases": len([c for c in cases if c.money_laundering_flag])
            }
        }
    
    def _parse_performance_analysis(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for performance analysis.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed performance analysis
        """
        
        # Simple parsing implementation
        analysis = {
            "raw_analysis": response,
            "trends": [],
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if "trend" in line.lower():
                analysis["trends"].append(line)
            elif "strength" in line.lower() or "strong" in line.lower():
                analysis["strengths"].append(line)
            elif "weakness" in line.lower() or "weak" in line.lower():
                analysis["weaknesses"].append(line)
            elif "recommend" in line.lower():
                analysis["recommendations"].append(line)
        
        return analysis
    
    def _parse_insight_evaluation(self, response: str, agent_type: str) -> Dict[str, Any]:
        """Parse LLM response for insight evaluation.
        
        Args:
            response: Raw LLM response
            agent_type: Type of agent being evaluated
            
        Returns:
            Parsed insight evaluation
        """
        
        evaluation = {
            "agent_type": agent_type,
            "raw_evaluation": response,
            "scores": {},
            "feedback": [],
            "overall_assessment": "unknown"
        }
        
        # Extract numerical scores (simplified)
        import re
        score_pattern = r'(\w+):\s*(\d+)\/10'
        scores = re.findall(score_pattern, response, re.IGNORECASE)
        
        for aspect, score in scores:
            evaluation["scores"][aspect.lower()] = int(score)
        
        # Calculate overall assessment
        if evaluation["scores"]:
            avg_score = sum(evaluation["scores"].values()) / len(evaluation["scores"])
            if avg_score >= 8:
                evaluation["overall_assessment"] = "excellent"
            elif avg_score >= 6:
                evaluation["overall_assessment"] = "good"
            elif avg_score >= 4:
                evaluation["overall_assessment"] = "fair"
            else:
                evaluation["overall_assessment"] = "needs_improvement"
        
        return evaluation
    
    def get_prompt_template(self) -> str:
        """Get evaluation agent prompt template.
        
        Returns:
            Prompt template for evaluation analysis
        """
        return """
        As a DOJ Evaluation Agent, assess system performance and quality:
        
        Current Performance Metrics: {performance_metrics}
        Historical Trends: {historical_trends}
        Agent Insights: {agent_insights}
        
        Evaluate:
        1. Accuracy and reliability of fraud detection
        2. Quality of case analysis and categorization
        3. Effectiveness of multi-agent coordination
        4. System performance trends and stability
        5. Areas requiring improvement or optimization
        6. Legal accuracy and compliance with standards
        7. Research insight quality and actionability
        
        Provide specific recommendations for enhancing:
        - Individual agent performance
        - Multi-agent coordination
        - Overall system effectiveness
        - Quality assurance processes
        
        Structure your analysis with clear metrics and actionable recommendations.
        """
