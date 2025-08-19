"""
🚀 DOJ Multi-Agent Research System - Clean Demo
===============================================

A streamlined, interview-ready demonstration of a multi-agent system
showcasing key distributed AI concepts without overwhelming complexity.

Core Concepts:
- Agent Specialization & Coordination  
- Shared State Management
- Inter-Agent Communication
- Dynamic Performance Monitoring
- Multiple Coordination Strategies

Run: python multi_agent_demo.py
"""

import asyncio
import time
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


# ================================
# 📊 DATA MODELS
# ================================

@dataclass
class CaseData:
    """Fraud case data structure."""
    url: str
    title: str
    fraud_detected: bool = False
    confidence: float = 0.0
    processing_time: float = 0.0
    processed_by: str = ""


@dataclass
class AgentMessage:
    """Inter-agent communication message."""
    from_agent: str
    to_agent: str
    message_type: str
    data: Any
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


class AgentStatus(Enum):
    """Agent execution states."""
    IDLE = "idle"
    WORKING = "working" 
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SharedState:
    """System-wide shared state."""
    pending_cases: List[str] = field(default_factory=list)
    processed_cases: List[CaseData] = field(default_factory=list)
    agent_statuses: Dict[str, AgentStatus] = field(default_factory=dict)
    agent_performance: Dict[str, Dict] = field(default_factory=dict)
    message_queue: List[AgentMessage] = field(default_factory=list)
    
    # System metrics
    total_cases: int = 0
    fraud_detected: int = 0
    processing_time: float = 0.0
    
    def add_message(self, message: AgentMessage):
        """Add message to communication queue."""
        self.message_queue.append(message)
        # Keep last 20 messages for demo clarity
        if len(self.message_queue) > 20:
            self.message_queue = self.message_queue[-20:]


# ================================
# 🤖 BASE AGENT
# ================================

class Agent:
    """Base agent class with common functionality."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.status = AgentStatus.IDLE
        self.processed_count = 0
        self.error_count = 0
        self.total_time = 0.0
    
    async def process_task(self, task_data: Any, shared_state: SharedState) -> Dict[str, Any]:
        """Process task - implemented by each agent type."""
        raise NotImplementedError
    
    def send_message(self, shared_state: SharedState, to_agent: str, message_type: str, data: Any):
        """Send message to another agent."""
        message = AgentMessage(self.agent_id, to_agent, message_type, data)
        shared_state.add_message(message)
        print(f"📨 {self.agent_id} → {to_agent}: {message_type}")
    
    def get_messages(self, shared_state: SharedState, message_type: str = None) -> List[AgentMessage]:
        """Get messages sent to this agent."""
        messages = [m for m in shared_state.message_queue if m.to_agent == self.agent_id]
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        return messages
    
    def update_performance(self, shared_state: SharedState, processing_time: float, success: bool):
        """Update performance metrics."""
        self.processed_count += 1
        self.total_time += processing_time
        if not success:
            self.error_count += 1
        
        shared_state.agent_performance[self.agent_id] = {
            "processed": self.processed_count,
            "errors": self.error_count,
            "avg_time": self.total_time / self.processed_count,
            "success_rate": (self.processed_count - self.error_count) / self.processed_count
        }


# ================================
# 🔍 RESEARCH AGENT
# ================================

class ResearchAgent(Agent):
    """Specialized agent for fraud detection and analysis."""
    
    def __init__(self):
        super().__init__("research_agent")
        self.fraud_patterns = ["fraud", "scheme", "embezzlement", "laundering", "scam"]
    
    async def process_task(self, case_url: str, shared_state: SharedState) -> Dict[str, Any]:
        """Analyze case for fraud indicators."""
        start_time = time.time()
        self.status = AgentStatus.WORKING
        
        try:
            # Simulate fraud analysis
            print(f"🔍 Research Agent analyzing: {case_url.split('/')[-1]}")
            await asyncio.sleep(0.5)  # Simulate processing
            
            # Simple fraud detection
            case_title = f"DOJ Case {case_url.split('/')[-1]}"
            fraud_detected = any(pattern in case_url.lower() for pattern in self.fraud_patterns)
            confidence = 0.85 if fraud_detected else 0.3
            
            # Create case data
            case_data = CaseData(
                url=case_url,
                title=case_title,
                fraud_detected=fraud_detected,
                confidence=confidence,
                processing_time=time.time() - start_time,
                processed_by=self.agent_id
            )
            
            # Update shared state
            shared_state.processed_cases.append(case_data)
            shared_state.total_cases += 1
            if fraud_detected:
                shared_state.fraud_detected += 1
            
            # Notify other agents
            self.send_message(shared_state, "evaluation_agent", "case_analyzed", {
                "case_url": case_url,
                "fraud_detected": fraud_detected,
                "confidence": confidence
            })
            
            if fraud_detected:
                self.send_message(shared_state, "legal_agent", "fraud_case", {
                    "case_url": case_url,
                    "confidence": confidence
                })
            
            self.status = AgentStatus.COMPLETED
            self.update_performance(shared_state, time.time() - start_time, True)
            
            print(f"✅ Research completed: {'🚨 FRAUD' if fraud_detected else '✅ CLEAN'} ({confidence:.2f})")
            return {"success": True, "case_data": case_data}
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.update_performance(shared_state, time.time() - start_time, False)
            print(f"❌ Research error: {e}")
            return {"success": False, "error": str(e)}


# ================================
# 📊 EVALUATION AGENT  
# ================================

class EvaluationAgent(Agent):
    """Performance evaluation and quality monitoring."""
    
    def __init__(self):
        super().__init__("evaluation_agent")
        self.evaluations = []
    
    async def process_task(self, trigger: str, shared_state: SharedState) -> Dict[str, Any]:
        """Evaluate system performance."""
        start_time = time.time()
        self.status = AgentStatus.WORKING
        
        try:
            print(f"📊 Evaluation Agent performing assessment...")
            await asyncio.sleep(0.3)
            
            # Calculate metrics
            total_cases = len(shared_state.processed_cases)
            if total_cases == 0:
                return {"success": True, "message": "No cases to evaluate"}
            
            fraud_cases = len([c for c in shared_state.processed_cases if c.fraud_detected])
            avg_confidence = sum(c.confidence for c in shared_state.processed_cases) / total_cases
            avg_time = sum(c.processing_time for c in shared_state.processed_cases) / total_cases
            
            evaluation = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "total_cases": total_cases,
                "fraud_rate": fraud_cases / total_cases,
                "avg_confidence": avg_confidence,
                "avg_processing_time": avg_time,
                "system_health": "good" if avg_confidence > 0.6 else "needs_improvement"
            }
            
            self.evaluations.append(evaluation)
            
            # Send feedback if performance is low
            if avg_confidence < 0.7:
                self.send_message(shared_state, "research_agent", "improve_accuracy", {
                    "current_accuracy": avg_confidence,
                    "recommendation": "Enhance detection patterns"
                })
            
            self.status = AgentStatus.COMPLETED
            self.update_performance(shared_state, time.time() - start_time, True)
            
            print(f"📈 Evaluation: {fraud_cases}/{total_cases} fraud, {avg_confidence:.2f} confidence")
            return {"success": True, "evaluation": evaluation}
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.update_performance(shared_state, time.time() - start_time, False)
            print(f"❌ Evaluation error: {e}")
            return {"success": False, "error": str(e)}


# ================================
# ⚖️ LEGAL AGENT
# ================================

class LegalAgent(Agent):
    """Legal analysis and precedent matching."""
    
    def __init__(self):
        super().__init__("legal_agent")
        self.precedents = {
            "wire_fraud": {"severity": "high", "sentence": "2-5 years"},
            "embezzlement": {"severity": "medium", "sentence": "1-3 years"},
            "money_laundering": {"severity": "high", "sentence": "3-7 years"}
        }
    
    async def process_task(self, fraud_data: Dict, shared_state: SharedState) -> Dict[str, Any]:
        """Analyze legal aspects of fraud cases."""
        start_time = time.time()
        self.status = AgentStatus.WORKING
        
        try:
            case_url = fraud_data["case_url"]
            print(f"⚖️  Legal Agent analyzing: {case_url.split('/')[-1]}")
            await asyncio.sleep(0.4)
            
            # Simple precedent matching
            case_text = case_url.lower()
            relevant_precedents = []
            
            for fraud_type, details in self.precedents.items():
                if fraud_type.replace("_", " ") in case_text:
                    relevant_precedents.append({
                        "type": fraud_type,
                        "severity": details["severity"],
                        "sentence": details["sentence"]
                    })
            
            legal_analysis = {
                "case_url": case_url,
                "precedents": relevant_precedents,
                "complexity": "high" if len(relevant_precedents) > 1 else "medium"
            }
            
            # Send analysis to evaluation
            self.send_message(shared_state, "evaluation_agent", "legal_analysis", legal_analysis)
            
            self.status = AgentStatus.COMPLETED
            self.update_performance(shared_state, time.time() - start_time, True)
            
            print(f"⚖️  Legal analysis: {len(relevant_precedents)} precedents found")
            return {"success": True, "analysis": legal_analysis}
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.update_performance(shared_state, time.time() - start_time, False)
            print(f"❌ Legal error: {e}")
            return {"success": False, "error": str(e)}


# ================================
# 🎯 COORDINATOR
# ================================

class MultiAgentCoordinator:
    """Coordinates the multi-agent system with different strategies."""
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.evaluation_agent = EvaluationAgent()
        self.legal_agent = LegalAgent()
    
    async def run_demo(self, case_urls: List[str], strategy: str = "sequential") -> Dict[str, Any]:
        """Run multi-agent demo with specified coordination strategy."""
        print(f"🚀 Multi-Agent Demo: {strategy.upper()} Mode")
        print(f"📋 Processing {len(case_urls)} cases")
        print("=" * 50)
        
        # Initialize shared state
        shared_state = SharedState()
        shared_state.pending_cases = case_urls.copy()
        
        start_time = time.time()
        
        try:
            # Execute based on strategy
            if strategy == "sequential":
                await self._run_sequential(shared_state)
            elif strategy == "parallel":
                await self._run_parallel(shared_state)
            elif strategy == "adaptive":
                await self._run_adaptive(shared_state)
            
            # Final evaluation
            await self.evaluation_agent.process_task("final", shared_state)
            
            # Calculate results
            total_time = time.time() - start_time
            shared_state.processing_time = total_time
            
            result = self._generate_summary(shared_state, strategy)
            self._display_results(result)
            
            return result
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _run_sequential(self, shared_state: SharedState):
        """Sequential processing: Research → Legal → Evaluation."""
        # Process all cases through research
        for case_url in shared_state.pending_cases:
            await self.research_agent.process_task(case_url, shared_state)
        
        # Process fraud cases through legal
        fraud_messages = self.legal_agent.get_messages(shared_state, "fraud_case")
        for message in fraud_messages:
            await self.legal_agent.process_task(message.data, shared_state)
        
        # Periodic evaluation
        if shared_state.processed_cases:
            await self.evaluation_agent.process_task("periodic", shared_state)
    
    async def _run_parallel(self, shared_state: SharedState):
        """Parallel processing: concurrent execution where possible."""
        # Parallel research tasks
        research_tasks = [
            self.research_agent.process_task(url, shared_state)
            for url in shared_state.pending_cases
        ]
        
        # Execute in batches
        batch_size = 3
        for i in range(0, len(research_tasks), batch_size):
            batch = research_tasks[i:i + batch_size]
            await asyncio.gather(*batch)
            
            # Parallel legal analysis for new fraud cases
            fraud_messages = self.legal_agent.get_messages(shared_state, "fraud_case")
            recent_fraud = fraud_messages[-(len(batch)):]  # Recent fraud cases
            
            if recent_fraud:
                legal_tasks = [
                    self.legal_agent.process_task(msg.data, shared_state)
                    for msg in recent_fraud
                ]
                await asyncio.gather(*legal_tasks)
            
            # Batch evaluation
            await self.evaluation_agent.process_task(f"batch_{i//batch_size}", shared_state)
    
    async def _run_adaptive(self, shared_state: SharedState):
        """Adaptive: Start sequential, switch to parallel based on performance."""
        processed = 0
        
        # Start with sequential
        for case_url in shared_state.pending_cases:
            await self.research_agent.process_task(case_url, shared_state)
            processed += 1
            
            # Adapt after 2 cases
            if processed == 2:
                await self.evaluation_agent.process_task("adaptation_check", shared_state)
                
                # Check performance
                performance = shared_state.agent_performance.get("research_agent", {})
                if performance.get("success_rate", 0) > 0.8:
                    print("🔄 Adapting to parallel mode - good performance detected")
                    
                    # Switch to parallel for remaining cases
                    remaining = shared_state.pending_cases[processed:]
                    if remaining:
                        remaining_tasks = [
                            self.research_agent.process_task(url, shared_state)
                            for url in remaining
                        ]
                        await asyncio.gather(*remaining_tasks)
                    break
        
        # Process all legal cases
        fraud_messages = self.legal_agent.get_messages(shared_state, "fraud_case")
        for message in fraud_messages:
            await self.legal_agent.process_task(message.data, shared_state)
    
    def _generate_summary(self, shared_state: SharedState, strategy: str) -> Dict[str, Any]:
        """Generate comprehensive summary."""
        return {
            "success": True,
            "strategy": strategy,
            "processing_time": shared_state.processing_time,
            "cases_processed": shared_state.total_cases,
            "fraud_detected": shared_state.fraud_detected,
            "fraud_rate": shared_state.fraud_detected / shared_state.total_cases if shared_state.total_cases > 0 else 0,
            "messages_exchanged": len(shared_state.message_queue),
            "agent_performance": shared_state.agent_performance
        }
    
    def _display_results(self, result: Dict[str, Any]):
        """Display clean results."""
        print("=" * 50)
        print("✅ Demo Completed!")
        print(f"⏱️  Time: {result['processing_time']:.2f}s")
        print(f"📊 Cases: {result['cases_processed']}")
        print(f"🚨 Fraud: {result['fraud_detected']} ({result['fraud_rate']:.1%})")
        print(f"📨 Messages: {result['messages_exchanged']}")
        
        print("\n📈 Agent Performance:")
        for agent_id, perf in result['agent_performance'].items():
            print(f"  {agent_id}: {perf['processed']} tasks, {perf['success_rate']:.1%} success")


# ================================
# 🎭 DEMO RUNNER
# ================================

async def main():
    """Main demo function showcasing multiple coordination strategies."""
    
    print("🎯 DOJ MULTI-AGENT RESEARCH SYSTEM")
    print("==================================")
    print("Demonstrating: Agent Coordination, Communication & Performance Monitoring")
    print()
    
    # Demo cases
    demo_cases = [
        "https://justice.gov/case/fraud-scheme-1",
        "https://justice.gov/case/embezzlement-case-2", 
        "https://justice.gov/case/clean-investigation-3",
        "https://justice.gov/case/money-laundering-4",
        "https://justice.gov/case/tax-evasion-5"
    ]
    
    # Test coordination strategies
    strategies = ["sequential", "parallel", "adaptive"]
    results = {}
    
    for strategy in strategies:
        print(f"\n{'='*15} {strategy.upper()} STRATEGY {'='*15}")
        
        coordinator = MultiAgentCoordinator()
        result = await coordinator.run_demo(demo_cases, strategy)
        results[strategy] = result
        
        await asyncio.sleep(0.5)  # Brief pause
    
    # Strategy comparison
    print("\n" + "="*50)
    print("📊 STRATEGY COMPARISON")
    print("="*50)
    
    for strategy, result in results.items():
        if result.get("success"):
            print(f"{strategy.capitalize():10} | "
                  f"Time: {result['processing_time']:5.2f}s | "
                  f"Messages: {result['messages_exchanged']:2d} | "
                  f"Fraud: {result['fraud_rate']:5.1%}")
    
    print("\n🎉 Key Concepts Demonstrated:")
    print("   🤖 Agent Specialization & Single Responsibility")
    print("   🔄 Multiple Coordination Strategies")
    print("   📨 Inter-Agent Message Passing")
    print("   📊 Shared State Management")
    print("   📈 Real-time Performance Monitoring")
    print("   🧠 Adaptive System Behavior")


if __name__ == "__main__":
    asyncio.run(main())
