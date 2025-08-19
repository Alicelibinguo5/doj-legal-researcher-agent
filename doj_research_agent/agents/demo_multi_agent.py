"""Demo script for multi-agent DOJ research system.

This script demonstrates how to use the multi-agent system with
Research Agent, Evaluation Agent, and Legal Intelligence Agent.
"""

import asyncio
import os
from datetime import datetime
from typing import Optional

from ..multi_agent_orchestrator import MultiAgentOrchestrator
from ..core.multi_agent_models import AgentCoordinationConfig
from ..core.models import ScrapingConfig
from ..core.utils import setup_logger

logger = setup_logger(__name__)


async def demo_multi_agent_system(max_cases: int = 5, 
                                coordination_strategy: str = "sequential") -> None:
    """Demonstrate the multi-agent DOJ research system.
    
    Args:
        max_cases: Maximum number of cases to process
        coordination_strategy: Agent coordination strategy ("sequential", "parallel", "adaptive")
    """
    
    print("=" * 80)
    print("DOJ MULTI-AGENT RESEARCH SYSTEM DEMO")
    print("=" * 80)
    print(f"Processing up to {max_cases} cases with {coordination_strategy} coordination")
    print()
    
    # Configure system
    scraping_config = ScrapingConfig(
        max_cases=max_cases,
        max_pages=2,
        delay_between_requests=1.0
    )
    
    coordination_config = AgentCoordinationConfig(
        coordination_strategy=coordination_strategy,
        max_processing_rounds=3,
        enable_parallel_processing=(coordination_strategy == "parallel")
    )
    
    # LLM configuration (optional)
    llm_config = {
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.1,
        "api_key": os.getenv("OPENAI_API_KEY")  # Make sure to set this
    }
    
    # Initialize orchestrator
    print("🤖 Initializing Multi-Agent Orchestrator...")
    orchestrator = MultiAgentOrchestrator(
        scraping_config=scraping_config,
        coordination_config=coordination_config,
        llm_config=llm_config
    )
    
    # Display system status
    status = orchestrator.get_system_status()
    print(f"✅ System initialized with {status['agents_count']} agents:")
    for agent in status['agents']:
        print(f"   - {agent.replace('_', ' ').title()}")
    print()
    
    # Run multi-agent system
    print("🚀 Starting multi-agent processing...")
    start_time = datetime.now()
    
    try:
        results = await orchestrator.run(max_cases=max_cases)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print("✅ Multi-agent processing completed!")
        print()
        
        # Display results summary
        display_results_summary(results, processing_time)
        
        # Display detailed insights
        display_detailed_insights(results)
        
    except Exception as e:
        print(f"❌ Multi-agent processing failed: {e}")
        logger.error(f"Demo failed: {e}")


def display_results_summary(results, processing_time: float) -> None:
    """Display summary of multi-agent results.
    
    Args:
        results: MultiAgentResults instance
        processing_time: Total processing time in seconds
    """
    
    print("📊 RESULTS SUMMARY")
    print("-" * 50)
    
    # Overall metrics
    print(f"Processing Time: {processing_time:.2f} seconds")
    print(f"Processing Rounds: {results.processing_rounds}")
    print(f"Success: {'✅ Yes' if results.success else '❌ No'}")
    
    if results.error_log:
        print(f"Errors: {len(results.error_log)}")
    
    print()
    
    # Agent-specific results
    print("🔍 AGENT PERFORMANCE")
    print("-" * 30)
    
    # Research Agent
    research = results.research_results
    if research:
        cases_analyzed = research.get("cases_analyzed", 0)
        patterns_found = len(research.get("patterns_discovered", {}).get("fraud_patterns", []))
        print(f"Research Agent:")
        print(f"  - Cases analyzed: {cases_analyzed}")
        print(f"  - Patterns discovered: {patterns_found}")
    
    # Legal Intelligence Agent
    legal = results.legal_intelligence_results
    if legal:
        precedents = legal.get("precedents_analyzed", 0)
        regulatory = legal.get("regulatory_updates_count", 0)
        print(f"Legal Intelligence Agent:")
        print(f"  - Precedents analyzed: {precedents}")
        print(f"  - Regulatory updates: {regulatory}")
    
    # Evaluation Agent
    evaluation = results.evaluation_results
    if evaluation:
        evaluations = evaluation.get("evaluations_completed", 0)
        trend = evaluation.get("accuracy_trend", "unknown")
        print(f"Evaluation Agent:")
        print(f"  - Evaluations completed: {evaluations}")
        print(f"  - Accuracy trend: {trend}")
    
    print()
    
    # Case processing results
    if results.final_result:
        final = results.final_result
        print("📋 CASE PROCESSING")
        print("-" * 25)
        print(f"Total cases: {final.total_cases}")
        print(f"Successful extractions: {final.successful_extractions}")
        print(f"Failed extractions: {final.failed_extractions}")
        print(f"Success rate: {final.success_rate():.1%}")
        print()
    
    # Evaluation metrics
    if results.evaluation_result:
        eval_result = results.evaluation_result
        print("🎯 FRAUD DETECTION PERFORMANCE")
        print("-" * 35)
        print(f"Accuracy: {eval_result.accuracy:.3f}")
        print(f"Precision: {eval_result.precision:.3f}")
        print(f"Recall: {eval_result.recall:.3f}")
        print(f"F1 Score: {eval_result.f1_score:.3f}")
        print()


def display_detailed_insights(results) -> None:
    """Display detailed insights from multi-agent processing.
    
    Args:
        results: MultiAgentResults instance
    """
    
    print("🧠 MULTI-AGENT INSIGHTS")
    print("-" * 30)
    
    # Communication summary
    comm = results.communication_summary
    if comm:
        print(f"Inter-agent messages: {comm.get('total_messages', 0)}")
        print(f"Agent interactions: {len(comm.get('agent_pairs', []))}")
        
        if comm.get('message_types'):
            print("Message types:")
            for msg_type, count in comm['message_types'].items():
                print(f"  - {msg_type}: {count}")
        print()
    
    # Shared insights
    if results.shared_insights:
        print(f"Global insights generated: {len(results.shared_insights)}")
        
        # Display last few insights
        recent_insights = results.shared_insights[-3:] if len(results.shared_insights) > 3 else results.shared_insights
        for i, insight in enumerate(recent_insights, 1):
            insight_type = insight.get("insight_type", "unknown")
            confidence = insight.get("confidence", 0)
            print(f"  {i}. {insight_type} (confidence: {confidence:.2f})")
        print()
    
    # Coordination metrics
    coord = results.coordination_metrics
    if coord:
        print("🤝 COORDINATION METRICS")
        print("-" * 25)
        print(f"Last coordination: {coord.get('last_coordination', 'N/A')}")
        print(f"System status: {coord.get('system_status', 'N/A')}")
        if coord.get('active_agents'):
            print(f"Active agents: {', '.join(coord['active_agents'])}")
        print()


async def run_demo_scenarios() -> None:
    """Run multiple demo scenarios to showcase different coordination strategies."""
    
    print("🎭 RUNNING DEMO SCENARIOS")
    print("=" * 80)
    
    scenarios = [
        {"strategy": "sequential", "cases": 3, "description": "Sequential processing"},
        {"strategy": "parallel", "cases": 3, "description": "Parallel processing"},
        {"strategy": "adaptive", "cases": 5, "description": "Adaptive coordination"}
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 SCENARIO {i}: {scenario['description']}")
        print("-" * 60)
        
        await demo_multi_agent_system(
            max_cases=scenario['cases'],
            coordination_strategy=scenario['strategy']
        )
        
        if i < len(scenarios):
            print("\n" + "⏸️ " * 20)
            await asyncio.sleep(2)  # Brief pause between scenarios
    
    print("\n🎉 All demo scenarios completed!")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. LLM features may not work properly.")
        print("   Set your API key: export OPENAI_API_KEY='your-key-here'")
        print()
    
    # Run demo
    print("🚀 Starting DOJ Multi-Agent Research System Demo...")
    print()
    
    # Choice: single demo or multiple scenarios
    choice = input("Run (1) single demo or (2) multiple scenarios? [1/2]: ").strip()
    
    if choice == "2":
        asyncio.run(run_demo_scenarios())
    else:
        # Single demo with user parameters
        try:
            max_cases = int(input("Max cases to process [5]: ") or "5")
            strategy = input("Coordination strategy (sequential/parallel/adaptive) [sequential]: ").strip() or "sequential"
            
            asyncio.run(demo_multi_agent_system(max_cases=max_cases, coordination_strategy=strategy))
            
        except ValueError:
            print("Invalid input, using defaults...")
            asyncio.run(demo_multi_agent_system())
        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")
        except Exception as e:
            print(f"❌ Demo failed: {e}")
    
    print("\n👋 Demo completed!")
