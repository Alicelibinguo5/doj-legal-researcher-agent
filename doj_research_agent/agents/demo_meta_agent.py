"""Demo script for Meta-Agent controlled DOJ research system.

This script demonstrates the Meta-Agent that provides strategic oversight
and control over the Research Agent, Evaluation Agent, and Legal Intelligence Agent.
"""

import asyncio
import os
from datetime import datetime
from typing import Optional

from ..meta_orchestrator import MetaAgentOrchestrator
from ..core.multi_agent_models import AgentCoordinationConfig
from ..core.models import ScrapingConfig
from ..core.utils import setup_logger

logger = setup_logger(__name__)


async def demo_meta_agent_system(max_cases: int = 5, 
                                coordination_strategy: str = "adaptive") -> None:
    """Demonstrate the Meta-Agent controlled DOJ research system.
    
    Args:
        max_cases: Maximum number of cases to process
        coordination_strategy: Initial coordination strategy preference
    """
    
    print("=" * 80)
    print("DOJ META-AGENT RESEARCH SYSTEM DEMO")
    print("=" * 80)
    print(f"🤖 Meta-Agent will strategically control up to {max_cases} cases")
    print(f"📋 Initial coordination preference: {coordination_strategy}")
    print("🧠 Meta-Agent will dynamically optimize strategy based on performance")
    print()
    
    # Configure system
    scraping_config = ScrapingConfig(
        max_cases=max_cases,
        max_pages=2,
        delay_between_requests=1.0
    )
    
    coordination_config = AgentCoordinationConfig(
        coordination_strategy=coordination_strategy,
        max_processing_rounds=4,  # Allow Meta-Agent more rounds for optimization
        enable_parallel_processing=True
    )
    
    # LLM configuration
    llm_config = {
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.1,
        "api_key": os.getenv("OPENAI_API_KEY")
    }
    
    # Initialize Meta-Agent Orchestrator
    print("🎯 Initializing Meta-Agent Orchestrator...")
    orchestrator = MetaAgentOrchestrator(
        scraping_config=scraping_config,
        coordination_config=coordination_config,
        llm_config=llm_config
    )
    
    # Display system status
    status = orchestrator.get_system_status()
    print(f"✅ Meta-Agent system initialized:")
    print(f"   📊 Orchestrator Type: {status['orchestrator_type']}")
    print(f"   🤖 Total Agents: {status['agents_count']} (including Meta-Agent)")
    print(f"   🎮 Meta-Agent Active: {status['meta_agent_active']}")
    print(f"   🔧 Initial Strategy: {status['coordination_strategy']}")
    print()
    
    # Run Meta-Agent controlled system
    print("🚀 Meta-Agent taking strategic control...")
    print("   🧠 Meta-Agent will analyze, decide, and optimize throughout execution")
    print("   📈 Watch for strategic decisions and performance optimizations")
    print()
    
    start_time = datetime.now()
    
    try:
        results = await orchestrator.run(max_cases=max_cases)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print("✅ Meta-Agent controlled processing completed!")
        print()
        
        # Display Meta-Agent specific results
        display_meta_agent_results(results, processing_time, status)
        
        # Display strategic insights
        display_strategic_insights(results, orchestrator)
        
        # Display detailed performance analysis
        display_performance_analysis(results)
        
    except Exception as e:
        print(f"❌ Meta-Agent system failed: {e}")
        logger.error(f"Meta-Agent demo failed: {e}")


def display_meta_agent_results(results, processing_time: float, initial_status: dict) -> None:
    """Display Meta-Agent specific results and decisions.
    
    Args:
        results: MultiAgentResults instance
        processing_time: Total processing time in seconds
        initial_status: Initial system status
    """
    
    print("🎯 META-AGENT CONTROL RESULTS")
    print("-" * 50)
    
    # Meta-Agent oversight metrics
    coord_metrics = results.coordination_metrics
    meta_decisions = coord_metrics.get("meta_decisions", 0)
    final_strategy = coord_metrics.get("final_coordination_strategy", "unknown")
    
    print(f"⏱️  Processing Time: {processing_time:.2f} seconds")
    print(f"🔄 Processing Rounds: {results.processing_rounds}")
    print(f"🧠 Meta-Agent Decisions Made: {meta_decisions}")
    print(f"📊 Final Coordination Strategy: {final_strategy}")
    print(f"✅ Success: {'Yes' if results.success else 'No'}")
    
    if coord_metrics.get("meta_agent_controlled"):
        print(f"🎮 Meta-Agent Control: Active")
        system_performance = coord_metrics.get("system_performance_score", 0.0)
        print(f"📈 System Performance Score: {system_performance:.2f}/1.0")
        
        if coord_metrics.get("meta_agent_recommendations"):
            print(f"💡 Meta-Agent Recommendations:")
            for rec in coord_metrics["meta_agent_recommendations"][:3]:  # Show top 3
                print(f"   • {rec}")
    
    print()
    
    # Strategy evolution
    initial_strategy = initial_status.get("coordination_strategy", "unknown")
    if final_strategy != initial_strategy:
        print(f"🔄 STRATEGY EVOLUTION:")
        print(f"   Initial: {initial_strategy} → Final: {final_strategy}")
        print(f"   📊 Meta-Agent optimized coordination strategy during execution")
    else:
        print(f"🔧 STRATEGY STABILITY:")
        print(f"   Meta-Agent maintained {final_strategy} strategy throughout execution")
    
    print()


def display_strategic_insights(results, orchestrator: MetaAgentOrchestrator) -> None:
    """Display strategic insights from Meta-Agent decisions.
    
    Args:
        results: MultiAgentResults instance
        orchestrator: MetaAgentOrchestrator instance
    """
    
    print("🧠 META-AGENT STRATEGIC INSIGHTS")
    print("-" * 40)
    
    # Access Meta-Agent decision history
    meta_agent = orchestrator.meta_agent
    decision_history = meta_agent.decision_history
    optimization_insights = meta_agent.optimization_insights
    
    if decision_history:
        print(f"📋 Strategic Decisions Made: {len(decision_history)}")
        
        # Show recent decisions
        recent_decisions = decision_history[-3:] if len(decision_history) > 3 else decision_history
        for i, decision in enumerate(recent_decisions, 1):
            print(f"\n   Decision {i}:")
            print(f"   ⏰ Time: {decision.get('timestamp', 'Unknown')}")
            print(f"   🎯 Strategy: {decision.get('coordination_strategy', 'Unknown')}")
            
            strategic_focus = decision.get('strategic_focus', [])
            if strategic_focus:
                print(f"   🔍 Focus Areas:")
                for focus in strategic_focus[:2]:  # Show top 2
                    print(f"      • {focus}")
            
            priority_adjustments = decision.get('priority_adjustments', {})
            if priority_adjustments:
                print(f"   ⚡ Priority Adjustments:")
                for agent, priority in priority_adjustments.items():
                    print(f"      • {agent}: {priority}")
    
    if optimization_insights:
        print(f"\n🚀 Optimization Insights: {len(optimization_insights)}")
        latest_insight = optimization_insights[-1]
        insight_data = latest_insight.get("insights", {})
        
        system_maturity = insight_data.get("system_maturity", "unknown")
        print(f"   📊 System Maturity: {system_maturity}")
        
        optimization_opps = insight_data.get("optimization_opportunities", [])
        if optimization_opps:
            print(f"   💡 Optimization Opportunities:")
            for opp in optimization_opps[:3]:  # Show top 3
                print(f"      • {opp}")
        
        strategic_recs = insight_data.get("strategic_recommendations", [])
        if strategic_recs:
            print(f"   🎯 Strategic Recommendations:")
            for rec in strategic_recs[:2]:  # Show top 2
                print(f"      • {rec}")
    
    print()


def display_performance_analysis(results) -> None:
    """Display detailed performance analysis from Meta-Agent oversight.
    
    Args:
        results: MultiAgentResults instance
    """
    
    print("📊 AGENT PERFORMANCE UNDER META-AGENT CONTROL")
    print("-" * 55)
    
    # Research Agent Performance
    research = results.research_results
    if research:
        print("🔍 Research Agent:")
        cases_analyzed = research.get("cases_analyzed", 0)
        patterns_found = len(research.get("patterns_discovered", {}).get("fraud_patterns", []))
        insights_count = research.get("research_insights_count", 0)
        
        print(f"   📋 Cases Analyzed: {cases_analyzed}")
        print(f"   🔬 Patterns Discovered: {patterns_found}")
        print(f"   💡 Insights Generated: {insights_count}")
        
        # Performance rating
        if cases_analyzed >= 5 and patterns_found >= 2:
            print(f"   ⭐ Performance: Excellent")
        elif cases_analyzed >= 3:
            print(f"   ⭐ Performance: Good")
        else:
            print(f"   ⭐ Performance: Developing")
    
    # Legal Intelligence Agent Performance
    legal = results.legal_intelligence_results
    if legal:
        print("\n⚖️  Legal Intelligence Agent:")
        precedents = legal.get("precedents_analyzed", 0)
        regulatory = legal.get("regulatory_updates_count", 0)
        jurisdictions = legal.get("jurisdictions_tracked", 0)
        
        print(f"   📚 Precedents Analyzed: {precedents}")
        print(f"   📋 Regulatory Updates: {regulatory}")
        print(f"   🏛️  Jurisdictions Tracked: {jurisdictions}")
        
        # Performance rating
        if precedents >= 2 and regulatory >= 1:
            print(f"   ⭐ Performance: Excellent")
        elif precedents >= 1:
            print(f"   ⭐ Performance: Good")
        else:
            print(f"   ⭐ Performance: Developing")
    
    # Evaluation Agent Performance
    evaluation = results.evaluation_results
    if evaluation:
        print("\n📈 Evaluation Agent:")
        evaluations = evaluation.get("evaluations_completed", 0)
        accuracy_trend = evaluation.get("accuracy_trend", "unknown")
        
        print(f"   🔍 Evaluations Completed: {evaluations}")
        print(f"   📊 Accuracy Trend: {accuracy_trend}")
        
        # Performance rating
        if evaluations >= 2 and accuracy_trend in ["improving", "stable"]:
            print(f"   ⭐ Performance: Excellent")
        elif evaluations >= 1:
            print(f"   ⭐ Performance: Good")
        else:
            print(f"   ⭐ Performance: Developing")
    
    print()
    
    # Overall system assessment
    if results.final_result:
        final = results.final_result
        success_rate = final.success_rate()
        
        print("🎯 OVERALL SYSTEM PERFORMANCE")
        print("-" * 35)
        print(f"📊 Total Cases Processed: {final.total_cases}")
        print(f"✅ Successful Extractions: {final.successful_extractions}")
        print(f"❌ Failed Extractions: {final.failed_extractions}")
        print(f"📈 Success Rate: {success_rate:.1%}")
        
        if success_rate >= 0.9:
            print(f"🏆 Meta-Agent Effectiveness: Outstanding")
        elif success_rate >= 0.8:
            print(f"🏆 Meta-Agent Effectiveness: Excellent")
        elif success_rate >= 0.7:
            print(f"🏆 Meta-Agent Effectiveness: Good")
        else:
            print(f"🏆 Meta-Agent Effectiveness: Developing")
    
    # Fraud detection performance
    if results.evaluation_result:
        eval_result = results.evaluation_result
        print(f"\n🎯 FRAUD DETECTION PERFORMANCE")
        print("-" * 35)
        print(f"🎯 Accuracy: {eval_result.accuracy:.3f}")
        print(f"🔍 Precision: {eval_result.precision:.3f}")
        print(f"📡 Recall: {eval_result.recall:.3f}")
        print(f"⚖️  F1 Score: {eval_result.f1_score:.3f}")
        
        if eval_result.accuracy >= 0.9:
            print(f"🌟 Detection Quality: Outstanding")
        elif eval_result.accuracy >= 0.8:
            print(f"🌟 Detection Quality: Excellent")
        elif eval_result.accuracy >= 0.7:
            print(f"🌟 Detection Quality: Good")
        else:
            print(f"🌟 Detection Quality: Developing")
    
    print()


async def run_meta_agent_scenarios() -> None:
    """Run multiple scenarios to showcase Meta-Agent capabilities."""
    
    print("🎭 META-AGENT DEMONSTRATION SCENARIOS")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "Strategic Optimization",
            "cases": 3, 
            "strategy": "adaptive",
            "description": "Meta-Agent dynamically optimizes strategy"
        },
        {
            "name": "High-Performance Mode", 
            "cases": 5,
            "strategy": "parallel",
            "description": "Meta-Agent manages high-throughput processing"
        },
        {
            "name": "Quality Control Mode",
            "cases": 4,
            "strategy": "sequential", 
            "description": "Meta-Agent ensures quality over speed"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 SCENARIO {i}: {scenario['name']}")
        print(f"📝 Description: {scenario['description']}")
        print("-" * 60)
        
        await demo_meta_agent_system(
            max_cases=scenario['cases'],
            coordination_strategy=scenario['strategy']
        )
        
        if i < len(scenarios):
            print("\n" + "⏸️ " * 20)
            print("Meta-Agent scenario completed. Next scenario starting...")
            await asyncio.sleep(3)  # Pause between scenarios
    
    print("\n🎉 All Meta-Agent scenarios completed!")
    print("🧠 Meta-Agent demonstrated strategic control, optimization, and adaptation")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Meta-Agent strategic features may not work properly.")
        print("   Set your API key: export OPENAI_API_KEY='your-key-here'")
        print()
    
    # Run demo
    print("🚀 Starting DOJ Meta-Agent Research System Demo...")
    print("🧠 Meta-Agent will provide strategic oversight and control")
    print()
    
    # Choice: single demo or multiple scenarios
    choice = input("Run (1) single Meta-Agent demo or (2) multiple scenarios? [1/2]: ").strip()
    
    if choice == "2":
        asyncio.run(run_meta_agent_scenarios())
    else:
        # Single demo with user parameters
        try:
            max_cases = int(input("Max cases for Meta-Agent to process [5]: ") or "5")
            strategy = input("Initial coordination preference (adaptive/parallel/sequential) [adaptive]: ").strip() or "adaptive"
            
            print(f"\n🧠 Meta-Agent will start with {strategy} strategy but may optimize during execution")
            print("📊 Watch for strategic decisions and performance optimizations!")
            print()
            
            asyncio.run(demo_meta_agent_system(max_cases=max_cases, coordination_strategy=strategy))
            
        except ValueError:
            print("Invalid input, using defaults...")
            asyncio.run(demo_meta_agent_system())
        except KeyboardInterrupt:
            print("\n🛑 Meta-Agent demo interrupted by user")
        except Exception as e:
            print(f"❌ Meta-Agent demo failed: {e}")
    
    print("\n👋 Meta-Agent demonstration completed!")
