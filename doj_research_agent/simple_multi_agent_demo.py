"""
Simplified Multi-Agent System Demo for DOJ Research
===================================================

This is a streamlined, interview-ready demonstration of a multi-agent system
that showcases key concepts without overwhelming complexity.

Core Concepts Demonstrated:
- Agent Specialization & Coordination
- Shared State Management
- Inter-Agent Communication
- Dynamic Task Allocation
- Performance Monitoring
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


# ================================
# 1. SIMPLE DATA MODELS
# ================================

@dataclass
class CaseData:
    """Simple case data structure."""
    url: str
    title: str
    fraud_detected: bool = False
    confidence: float = 0.0
    analysis_time: float = 0.0
    processed_by: str = ""


@dataclass
class AgentMessage:
    """Inter-agent communication message."""
    from_agent: str
    to_agent: str
    message_type: str
    data: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AgentStatus(Enum):
    """Agent status states."""
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SharedState:
    """Simplified shared state for all agents."""
    # Processing data
    pending_cases: List[str] = field(default_factory=list)
    processed_cases: List[CaseData] = field(default_factory=list)
    
    # Agent states
    agent_statuses: Dict[str, AgentStatus] = field(default_factory=dict)
    agent_performance: Dict[str, Dict] = field(default_factory=dict)
    
    # Communication
    message_queue: List[AgentMessage] = field(default_factory=list)
    
    # System metrics
    total_cases: int = 0
    fraud_detected: int = 0
    processing_time: float = 0.0
    
    def add_message(self, message: AgentMessage):
        """Add message to communication queue."""
        self.message_queue.append(message)
        # Keep only last 50 messages
        if len(self.message_queue) > 50:
            self.message_queue = self.message_queue[-50:]


# ================================
# 2. BASE AGENT CLASS
# ================================

class SimpleAgent:
    """Base class for all agents in the demo system."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.status = AgentStatus.IDLE
        self.processed_count = 0
        self.error_count = 0
        self.total_time = 0.0
    
    async def process_task(self, task_data: Any, shared_state: SharedState) -> Dict[str, Any]:
        """Process a task - to be implemented by subclasses."""
        raise NotImplementedError
    
    def send_message(self, shared_state: SharedState, to_agent: str, 
                    message_type: str, data: Any):
        """Send message to another agent."""
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            data=data
        )
        shared_state.add_message(message)
        print(f"📨 {self.agent_id} → {to_agent}: {message_type}")
    
    def get_messages(self, shared_state: SharedState, message_type: str = None) -> List[AgentMessage]:
        """Get messages sent to this agent."""
        messages = [
            msg for msg in shared_state.message_queue 
            if msg.to_agent == self.agent_id
        ]
        if message_type:
            messages = [msg for msg in messages if msg.message_type == message_type]
        return messages
    
    def update_performance(self, shared_state: SharedState, processing_time: float, success: bool):
        """Update agent performance metrics."""
        self.processed_count += 1
        self.total_time += processing_time
        if not success:
            self.error_count += 1
        
        # Update shared state
        shared_state.agent_performance[self.agent_id] = {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "avg_time": self.total_time / self.processed_count if self.processed_count > 0 else 0,
            "success_rate": (self.processed_count - self.error_count) / self.processed_count if self.processed_count > 0 else 0
        }


# ================================
# 3. SPECIALIZED AGENTS
# ================================

class ResearchAgent(SimpleAgent):
    """Agent specialized in case analysis and fraud detection."""
    
    def __init__(self):
        super().__init__("research_agent")
        self.fraud_patterns = ["scheme", "fraud", "deception", "embezzlement", "laundering"]
    
    async def process_task(self, case_url: str, shared_state: SharedState) -> Dict[str, Any]:
        """Analyze a case for fraud indicators."""
        start_time = time.time()
        self.status = AgentStatus.WORKING
        
        try:
            # Simulate case analysis
            print(f"🔍 Research Agent analyzing: {case_url}")
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Simple fraud detection simulation
            case_title = f"DOJ Case {case_url.split('/')[-1]}"
            fraud_detected = any(pattern in case_title.lower() for pattern in self.fraud_patterns)
            confidence = 0.85 if fraud_detected else 0.3
            
            # Create case data
            case_data = CaseData(
                url=case_url,
                title=case_title,
                fraud_detected=fraud_detected,
                confidence=confidence,
                analysis_time=time.time() - start_time,
                processed_by=self.agent_id
            )
            
            # Add to shared state
            shared_state.processed_cases.append(case_data)
            shared_state.total_cases += 1
            if fraud_detected:
                shared_state.fraud_detected += 1
            
            # Send results to other agents
            self.send_message(shared_state, "evaluation_agent", "case_analyzed", {
                "case_url": case_url,
                "fraud_detected": fraud_detected,
                "confidence": confidence
            })
            
            if fraud_detected:
                self.send_message(shared_state, "legal_agent", "fraud_case", {
                    "case_url": case_url,
                    "case_title": case_title,
                    "confidence": confidence
                })
            
            self.status = AgentStatus.COMPLETED
            self.update_performance(shared_state, time.time() - start_time, True)
            
            print(f"✅ Research Agent completed: {case_url} ({'FRAUD' if fraud_detected else 'CLEAN'})")
            
            return {"success": True, "case_data": case_data}
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.update_performance(shared_state, time.time() - start_time, False)
            print(f"❌ Research Agent error: {e}")
            return {"success": False, "error": str(e)}


class EvaluationAgent(SimpleAgent):
    """Agent specialized in performance evaluation and quality assessment."""
    
    def __init__(self):
        super().__init__("evaluation_agent")
        self.evaluation_history = []
    
    async def process_task(self, trigger: str, shared_state: SharedState) -> Dict[str, Any]:
        """Evaluate system performance."""
        start_time = time.time()
        self.status = AgentStatus.WORKING
        
        try:
            print(f"📊 Evaluation Agent performing system evaluation...")
            await asyncio.sleep(0.3)  # Simulate evaluation time
            
            # Calculate system metrics
            total_cases = len(shared_state.processed_cases)
            if total_cases == 0:
                return {"success": True, "message": "No cases to evaluate"}
            
            fraud_cases = len([c for c in shared_state.processed_cases if c.fraud_detected])
            avg_confidence = sum(c.confidence for c in shared_state.processed_cases) / total_cases
            avg_processing_time = sum(c.analysis_time for c in shared_state.processed_cases) / total_cases
            
            # Performance evaluation
            evaluation = {
                "timestamp": datetime.now().isoformat(),
                "total_cases": total_cases,
                "fraud_detection_rate": fraud_cases / total_cases,
                "avg_confidence": avg_confidence,
                "avg_processing_time": avg_processing_time,
                "system_health": "good" if avg_confidence > 0.6 else "needs_improvement"
            }
            
            self.evaluation_history.append(evaluation)
            
            # Send feedback to research agent
            if avg_confidence < 0.7:
                self.send_message(shared_state, "research_agent", "improve_accuracy", {
                    "current_accuracy": avg_confidence,
                    "target_accuracy": 0.8,
                    "recommendation": "Enhance fraud detection patterns"
                })
            
            # Send performance summary to coordinator
            self.send_message(shared_state, "coordinator", "performance_report", evaluation)
            
            self.status = AgentStatus.COMPLETED
            self.update_performance(shared_state, time.time() - start_time, True)
            
            print(f"📈 Evaluation completed: {fraud_cases}/{total_cases} fraud cases, {avg_confidence:.2f} avg confidence")
            
            return {"success": True, "evaluation": evaluation}
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.update_performance(shared_state, time.time() - start_time, False)
            print(f"❌ Evaluation Agent error: {e}")
            return {"success": False, "error": str(e)}


class LegalAgent(SimpleAgent):
    """Agent specialized in legal analysis and precedent matching."""
    
    def __init__(self):
        super().__init__("legal_agent")
        self.precedent_database = {
            "wire_fraud": {"severity": "high", "typical_sentence": "2-5 years"},
            "embezzlement": {"severity": "medium", "typical_sentence": "1-3 years"},
            "money_laundering": {"severity": "high", "typical_sentence": "3-7 years"}
        }
    
    async def process_task(self, fraud_case_data: Dict, shared_state: SharedState) -> Dict[str, Any]:
        """Analyze legal aspects of fraud cases."""
        start_time = time.time()
        self.status = AgentStatus.WORKING
        
        try:
            case_url = fraud_case_data["case_url"]
            print(f"⚖️  Legal Agent analyzing: {case_url}")
            await asyncio.sleep(0.4)  # Simulate legal analysis time
            
            # Simple legal analysis
            case_title = fraud_case_data.get("case_title", "").lower()
            relevant_precedents = []
            
            for fraud_type, details in self.precedent_database.items():
                if fraud_type.replace("_", " ") in case_title:
                    relevant_precedents.append({
                        "type": fraud_type,
                        "severity": details["severity"],
                        "typical_sentence": details["typical_sentence"]
                    })
            
            legal_analysis = {
                "case_url": case_url,
                "relevant_precedents": relevant_precedents,
                "legal_complexity": "high" if len(relevant_precedents) > 1 else "medium",
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # Send analysis to evaluation agent
            self.send_message(shared_state, "evaluation_agent", "legal_analysis", legal_analysis)
            
            self.status = AgentStatus.COMPLETED
            self.update_performance(shared_state, time.time() - start_time, True)
            
            print(f"⚖️  Legal analysis completed: {len(relevant_precedents)} precedents found")
            
            return {"success": True, "legal_analysis": legal_analysis}
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.update_performance(shared_state, time.time() - start_time, False)
            print(f"❌ Legal Agent error: {e}")
            return {"success": False, "error": str(e)}


# ================================
# 4. SIMPLE COORDINATOR
# ================================

class SimpleCoordinator:
    """Simplified coordinator for the multi-agent system."""
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.evaluation_agent = EvaluationAgent()
        self.legal_agent = LegalAgent()
        
        # Coordination strategy
        self.coordination_mode = "sequential"  # sequential, parallel, adaptive
    
    async def run_demo(self, case_urls: List[str]) -> Dict[str, Any]:
        """Run the multi-agent demo on given case URLs."""
        print("🚀 Starting Simplified Multi-Agent Demo")
        print(f"📋 Processing {len(case_urls)} cases with {self.coordination_mode} coordination")
        print("=" * 60)
        
        # Initialize shared state
        shared_state = SharedState()
        shared_state.pending_cases = case_urls.copy()
        
        # Set initial agent statuses
        for agent_id in ["research_agent", "evaluation_agent", "legal_agent"]:
            shared_state.agent_statuses[agent_id] = AgentStatus.IDLE
        
        start_time = time.time()
        
        try:
            if self.coordination_mode == "sequential":
                await self._run_sequential(shared_state)
            elif self.coordination_mode == "parallel":
                await self._run_parallel(shared_state)
            else:  # adaptive
                await self._run_adaptive(shared_state)
            
            # Final evaluation
            await self.evaluation_agent.process_task("final_evaluation", shared_state)
            
            # Calculate final metrics
            total_time = time.time() - start_time
            shared_state.processing_time = total_time
            
            # Generate summary
            summary = self._generate_summary(shared_state)
            
            print("=" * 60)
            print("✅ Multi-Agent Demo Completed!")
            self._display_results(summary)
            
            return summary
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _run_sequential(self, shared_state: SharedState):
        """Run agents sequentially."""
        print("🔄 Sequential Processing Mode")
        
        # Process each case through research agent
        for case_url in shared_state.pending_cases:
            await self.research_agent.process_task(case_url, shared_state)
        
        # Process fraud cases through legal agent
        fraud_messages = self.legal_agent.get_messages(shared_state, "fraud_case")
        for message in fraud_messages:
            await self.legal_agent.process_task(message.data, shared_state)
        
        # Periodic evaluations
        if len(shared_state.processed_cases) > 0:
            await self.evaluation_agent.process_task("periodic_evaluation", shared_state)
    
    async def _run_parallel(self, shared_state: SharedState):
        """Run agents in parallel where possible."""
        print("⚡ Parallel Processing Mode")
        
        # Create tasks for parallel execution
        research_tasks = [
            self.research_agent.process_task(case_url, shared_state)
            for case_url in shared_state.pending_cases
        ]
        
        # Execute research tasks in parallel (with limit)
        batch_size = 3
        for i in range(0, len(research_tasks), batch_size):
            batch = research_tasks[i:i + batch_size]
            await asyncio.gather(*batch)
            
            # Parallel legal analysis for completed fraud cases
            fraud_messages = self.legal_agent.get_messages(shared_state, "fraud_case")
            if fraud_messages:
                legal_tasks = [
                    self.legal_agent.process_task(msg.data, shared_state)
                    for msg in fraud_messages[-batch_size:]  # Process recent messages
                ]
                await asyncio.gather(*legal_tasks)
            
            # Evaluation after each batch
            await self.evaluation_agent.process_task("batch_evaluation", shared_state)
    
    async def _run_adaptive(self, shared_state: SharedState):
        """Run with adaptive coordination based on performance."""
        print("🧠 Adaptive Processing Mode")
        
        # Start with sequential
        processed = 0
        for case_url in shared_state.pending_cases:
            await self.research_agent.process_task(case_url, shared_state)
            processed += 1
            
            # Adapt strategy based on performance
            if processed == 2:  # After 2 cases, evaluate performance
                await self.evaluation_agent.process_task("adaptation_check", shared_state)
                
                # Check if we should switch to parallel
                performance = shared_state.agent_performance.get("research_agent", {})
                if performance.get("success_rate", 0) > 0.8:
                    print("🔄 Adapting to parallel mode based on good performance")
                    
                    # Process remaining cases in parallel
                    remaining = shared_state.pending_cases[processed:]
                    remaining_tasks = [
                        self.research_agent.process_task(url, shared_state)
                        for url in remaining
                    ]
                    await asyncio.gather(*remaining_tasks)
                    break
        
        # Process legal analysis for all fraud cases
        fraud_messages = self.legal_agent.get_messages(shared_state, "fraud_case")
        for message in fraud_messages:
            await self.legal_agent.process_task(message.data, shared_state)
    
    def _generate_summary(self, shared_state: SharedState) -> Dict[str, Any]:
        """Generate comprehensive summary of the demo run."""
        return {
            "success": True,
            "coordination_mode": self.coordination_mode,
            "processing_time": shared_state.processing_time,
            "cases_processed": shared_state.total_cases,
            "fraud_detected": shared_state.fraud_detected,
            "fraud_rate": shared_state.fraud_detected / shared_state.total_cases if shared_state.total_cases > 0 else 0,
            "agent_performance": shared_state.agent_performance,
            "messages_exchanged": len(shared_state.message_queue),
            "evaluation_history": self.evaluation_agent.evaluation_history,
            "processed_cases": [
                {
                    "url": case.url,
                    "fraud_detected": case.fraud_detected,
                    "confidence": case.confidence,
                    "processing_time": case.analysis_time
                }
                for case in shared_state.processed_cases
            ]
        }
    
    def _display_results(self, summary: Dict[str, Any]):
        """Display demo results in a clear format."""
        print(f"⏱️  Total Processing Time: {summary['processing_time']:.2f}s")
        print(f"📊 Cases Processed: {summary['cases_processed']}")
        print(f"🚨 Fraud Cases Detected: {summary['fraud_detected']} ({summary['fraud_rate']:.1%})")
        print(f"📨 Messages Exchanged: {summary['messages_exchanged']}")
        
        print("\n📈 Agent Performance:")
        for agent_id, perf in summary['agent_performance'].items():
            print(f"  {agent_id}:")
            print(f"    - Processed: {perf['processed_count']} cases")
            print(f"    - Success Rate: {perf['success_rate']:.1%}")
            print(f"    - Avg Time: {perf['avg_time']:.2f}s")


# ================================
# 5. DEMO RUNNER
# ================================

async def run_interview_demo():
    """Run the interview-ready multi-agent demo."""
    
    print("🎯 SIMPLIFIED MULTI-AGENT SYSTEM DEMO")
    print("=====================================")
    print("Showcasing: Agent Specialization, Coordination, Communication & Performance Monitoring")
    print()
    
    # Sample case URLs for demo
    demo_cases = [
        "https://justice.gov/case/fraud-scheme-1",
        "https://justice.gov/case/embezzlement-2", 
        "https://justice.gov/case/clean-case-3",
        "https://justice.gov/case/money-laundering-4",
        "https://justice.gov/case/regular-case-5"
    ]
    
    # Test different coordination strategies
    strategies = ["sequential", "parallel", "adaptive"]
    
    print("🔄 Testing Multiple Coordination Strategies:")
    print()
    
    results = {}
    
    for strategy in strategies:
        print(f"\n{'='*20} {strategy.upper()} MODE {'='*20}")
        
        coordinator = SimpleCoordinator()
        coordinator.coordination_mode = strategy
        
        result = await coordinator.run_demo(demo_cases)
        results[strategy] = result
        
        await asyncio.sleep(1)  # Brief pause between strategies
    
    # Comparison summary
    print("\n" + "="*60)
    print("📊 STRATEGY COMPARISON")
    print("="*60)
    
    for strategy, result in results.items():
        if result.get("success"):
            print(f"{strategy.capitalize():12} | "
                  f"Time: {result['processing_time']:5.2f}s | "
                  f"Messages: {result['messages_exchanged']:2d} | "
                  f"Fraud Rate: {result['fraud_rate']:5.1%}")
    
    print("\n✅ Demo completed! Key concepts demonstrated:")
    print("   🤖 Agent Specialization (Research, Evaluation, Legal)")
    print("   🔄 Multi-Strategy Coordination (Sequential, Parallel, Adaptive)")
    print("   📨 Inter-Agent Communication & Message Passing")
    print("   📊 Shared State Management")
    print("   📈 Performance Monitoring & Adaptation")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(run_interview_demo())
