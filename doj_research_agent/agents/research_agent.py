"""Research Agent for DOJ research multi-agent system."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent
from ..analysis.analyzer import CaseAnalyzer
from ..scraping.scraper import DOJScraper
from ..core.models import CaseInfo, ScrapingConfig


class ResearchAgent(BaseAgent):
    """Specialized agent for DOJ case research and analysis.
    
    This agent focuses on discovering patterns in fraud cases, conducting
    research on DOJ press releases, and generating insights about fraud
    trends and methodologies.
    """
    
    def __init__(self, llm_config: Optional[Dict] = None) -> None:
        """Initialize Research Agent.
        
        Args:
            llm_config: Configuration for LLM integration
        """
        super().__init__("research_agent", llm_config)
        self.case_analyzer = CaseAnalyzer()
        self.research_patterns: List[Dict[str, Any]] = []
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process research tasks and analyze cases.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Dictionary of research updates
        """
        self.logger.info("Research Agent starting processing...")
        
        # Initialize memory if not done
        if not self.memory:
            self.initialize_memory(state["shared_memory"])
        
        updates = {}
        
        # Process URLs for research if available
        if state.get("urls_to_process"):
            research_results = await self._conduct_research(state)
            updates.update(research_results)
        
        # Analyze patterns from existing cases
        if state.get("analyzed_cases"):
            pattern_analysis = await self._analyze_case_patterns(state["analyzed_cases"])
            updates["research_agent_state"] = {
                "patterns_discovered": pattern_analysis,
                "last_analysis": datetime.now().isoformat(),
                "cases_analyzed": len(state["analyzed_cases"]),
                "research_insights_count": len(self.research_patterns)
            }
            
            # Share insights with other agents
            self.communicate_with_agent(
                state, "evaluation_agent", "pattern_insights", pattern_analysis
            )
            self.communicate_with_agent(
                state, "legal_intelligence_agent", "pattern_insights", pattern_analysis
            )
        
        # Process insights from other agents
        await self._process_agent_insights(state)
        
        # Update memory with new findings
        self._update_research_memory(state.get("analyzed_cases", []))
        
        self.logger.info("Research Agent completed processing")
        return updates
    
    async def _conduct_research(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct research on pending URLs.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Research results and insights
        """
        scraper = DOJScraper(state["scraping_config"])
        research_insights = []
        processed_urls = []
        
        # Process a batch of URLs
        batch_size = min(5, len(state["urls_to_process"]))
        urls_to_process = state["urls_to_process"][:batch_size]
        
        for url in urls_to_process:
            try:
                soup = scraper.fetch_press_release_content(url)
                if soup:
                    case_info = self.case_analyzer.analyze_press_release(url, soup)
                    if case_info:
                        # Extract research insights
                        insights = await self._extract_research_insights(case_info)
                        research_insights.append(insights)
                        processed_urls.append(url)
                        
            except Exception as e:
                self.logger.error(f"Research failed for {url}: {e}")
        
        # Update URLs to process
        remaining_urls = [url for url in state["urls_to_process"] if url not in processed_urls]
        
        return {
            "research_insights": research_insights,
            "urls_to_process": remaining_urls,
            "processed_urls_count": len(processed_urls)
        }
    
    async def _analyze_case_patterns(self, cases: List[CaseInfo]) -> Dict[str, Any]:
        """Analyze patterns across cases using LLM.
        
        Args:
            cases: List of cases to analyze
            
        Returns:
            Pattern analysis results
        """
        
        # Prepare cases data for analysis (analyze last 10 cases)
        recent_cases = cases[-10:] if len(cases) > 10 else cases
        cases_summary = []
        
        for case in recent_cases:
            case_summary = {
                "title": case.title,
                "date": case.date,
                "charges": case.charges,
                "fraud_info": {
                    "is_fraud": case.fraud_info.is_fraud if case.fraud_info else False,
                    "evidence": case.fraud_info.evidence if case.fraud_info else None
                },
                "categories": [cat.value for cat in case.charge_categories],
                "money_laundering": case.money_laundering_flag or False
            }
            cases_summary.append(case_summary)
        
        # Get historical patterns from memory
        historical_patterns = self.get_memory("historical_patterns") or []
        
        # Generate pattern analysis using LLM
        prompt = self.get_prompt_template().format(
            cases_data=cases_summary,
            historical_patterns=historical_patterns,
            analysis_focus="fraud_patterns"
        )
        
        try:
            response = await self.generate_llm_response(prompt)
            pattern_analysis = self._parse_pattern_response(response)
            
            # Store patterns in memory
            self.update_memory("latest_patterns", pattern_analysis)
            self.research_patterns.append({
                "analysis": pattern_analysis,
                "timestamp": datetime.now().isoformat(),
                "cases_count": len(recent_cases)
            })
            
            return pattern_analysis
            
        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {e}")
            return {"error": str(e), "fallback_analysis": self._fallback_pattern_analysis(recent_cases)}
    
    def _fallback_pattern_analysis(self, cases: List[CaseInfo]) -> Dict[str, Any]:
        """Provide fallback pattern analysis when LLM fails.
        
        Args:
            cases: List of cases to analyze
            
        Returns:
            Basic pattern analysis
        """
        
        fraud_cases = [c for c in cases if c.fraud_info and c.fraud_info.is_fraud]
        charge_frequency = {}
        category_frequency = {}
        
        for case in cases:
            # Count charge types
            for charge in case.charges:
                charge_frequency[charge] = charge_frequency.get(charge, 0) + 1
            
            # Count categories
            for category in case.charge_categories:
                category_frequency[category.value] = category_frequency.get(category.value, 0) + 1
        
        return {
            "total_cases": len(cases),
            "fraud_cases": len(fraud_cases),
            "fraud_rate": len(fraud_cases) / len(cases) if cases else 0,
            "top_charges": sorted(charge_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_categories": sorted(category_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "analysis_type": "fallback"
        }
    
    async def _extract_research_insights(self, case_info: CaseInfo) -> Dict[str, Any]:
        """Extract deeper research insights from a case.
        
        Args:
            case_info: Case information to analyze
            
        Returns:
            Research insights for the case
        """
        
        insights_prompt = f"""
        Analyze this DOJ case for research insights:
        
        Title: {case_info.title}
        Date: {case_info.date}
        Charges: {case_info.charges}
        Fraud Info: {case_info.fraud_info.evidence if case_info.fraud_info else 'None'}
        Money Laundering: {case_info.money_laundering_flag}
        
        Extract insights about:
        1. Novel fraud techniques or methodologies
        2. Victim targeting patterns or demographics
        3. Geographic or temporal trends
        4. Technology or tools used in the scheme
        5. Investigation methods that led to prosecution
        6. Cooperation patterns or plea agreements
        
        Provide structured insights that could help identify similar future cases.
        """
        
        try:
            response = await self.generate_llm_response(insights_prompt)
            return {
                "case_url": case_info.url,
                "case_title": case_info.title,
                "insights": response,
                "extraction_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Insight extraction failed for {case_info.url}: {e}")
            return {
                "case_url": case_info.url,
                "case_title": case_info.title,
                "error": str(e),
                "fallback_insights": self._generate_fallback_insights(case_info)
            }
    
    def _generate_fallback_insights(self, case_info: CaseInfo) -> Dict[str, Any]:
        """Generate basic insights when LLM extraction fails.
        
        Args:
            case_info: Case information
            
        Returns:
            Basic insights about the case
        """
        
        insights = {
            "charge_analysis": {
                "total_charges": len(case_info.charges),
                "charge_types": case_info.charges,
                "categories": [cat.value for cat in case_info.charge_categories]
            },
            "fraud_indicators": {
                "is_fraud": case_info.fraud_info.is_fraud if case_info.fraud_info else False,
                "has_money_laundering": case_info.money_laundering_flag or False
            },
            "temporal_info": {
                "case_date": case_info.date,
                "extraction_date": case_info.extraction_date.isoformat() if case_info.extraction_date else None
            }
        }
        
        return insights
    
    def _update_research_memory(self, cases: List[CaseInfo]) -> None:
        """Update research memory with case analysis.
        
        Args:
            cases: List of analyzed cases
        """
        if not cases:
            return
        
        # Update basic statistics
        fraud_cases = [c for c in cases if c.fraud_info and c.fraud_info.is_fraud]
        ml_cases = [c for c in cases if c.money_laundering_flag]
        
        self.update_memory("total_cases_analyzed", len(cases))
        self.update_memory("fraud_cases_found", len(fraud_cases))
        self.update_memory("money_laundering_cases", len(ml_cases))
        self.update_memory("last_research_date", datetime.now().isoformat())
        
        # Update charge patterns
        all_charges = []
        for case in cases:
            all_charges.extend(case.charges)
        
        charge_frequency = {}
        for charge in all_charges:
            charge_frequency[charge] = charge_frequency.get(charge, 0) + 1
        
        self.update_memory("charge_patterns", dict(sorted(
            charge_frequency.items(), key=lambda x: x[1], reverse=True
        )[:20]))  # Keep top 20 charges
        
        # Update category patterns
        all_categories = []
        for case in cases:
            all_categories.extend([cat.value for cat in case.charge_categories])
        
        category_frequency = {}
        for category in all_categories:
            category_frequency[category] = category_frequency.get(category, 0) + 1
        
        self.update_memory("category_patterns", category_frequency)
        
        # Log performance metrics
        self.log_performance_metric("fraud_detection_rate", len(fraud_cases) / len(cases) if cases else 0)
        self.log_performance_metric("cases_processed", len(cases))
    
    async def _process_agent_insights(self, state: Dict[str, Any]) -> None:
        """Process insights shared by other agents.
        
        Args:
            state: Current multi-agent state
        """
        
        # Process legal intelligence insights
        legal_messages = self.get_agent_messages(state, "legal_intelligence_agent")
        for message in legal_messages:
            if message["type"] == "legal_precedents":
                await self._incorporate_legal_precedents(message["data"])
            elif message["type"] == "regulatory_updates":
                self._incorporate_regulatory_updates(message["data"])
        
        # Process evaluation agent feedback
        eval_messages = self.get_agent_messages(state, "evaluation_agent")
        for message in eval_messages:
            if message["type"] == "performance_feedback":
                self._adjust_research_focus(message["data"])
    
    async def _incorporate_legal_precedents(self, precedent_data: Dict[str, Any]) -> None:
        """Incorporate legal precedent information into research.
        
        Args:
            precedent_data: Legal precedent data from legal intelligence agent
        """
        
        # Use precedent information to refine pattern analysis
        self.update_memory("legal_precedents", {
            "precedent_data": precedent_data,
            "incorporated_timestamp": datetime.now().isoformat()
        })
        
        # Adjust research focus based on precedent trends
        if "legal_trends" in precedent_data:
            trends = precedent_data["legal_trends"]
            self.update_memory("legal_trend_focus", trends.get("key_trends", []))
    
    def _incorporate_regulatory_updates(self, regulatory_data: Dict[str, Any]) -> None:
        """Incorporate regulatory update information.
        
        Args:
            regulatory_data: Regulatory update data
        """
        
        self.update_memory("regulatory_updates", {
            "update_data": regulatory_data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Adjust research patterns based on new regulations
        if "recent_updates" in regulatory_data:
            updates = regulatory_data["recent_updates"]
            focus_areas = []
            for update in updates:
                if hasattr(update, 'impact_areas'):
                    focus_areas.extend(update.impact_areas)
            
            if focus_areas:
                self.update_memory("regulatory_focus_areas", list(set(focus_areas)))
    
    def _adjust_research_focus(self, performance_data: Dict[str, Any]) -> None:
        """Adjust research focus based on performance feedback.
        
        Args:
            performance_data: Performance data from evaluation agent
        """
        
        accuracy = performance_data.get("accuracy", 0.0)
        
        # Adjust pattern detection sensitivity based on accuracy
        if accuracy < 0.8:
            # Lower accuracy suggests need for more conservative pattern detection
            self.update_memory("pattern_sensitivity", "conservative")
        elif accuracy > 0.95:
            # High accuracy suggests we can be more aggressive in pattern detection
            self.update_memory("pattern_sensitivity", "aggressive")
        else:
            self.update_memory("pattern_sensitivity", "balanced")
        
        self.log_performance_metric("evaluation_feedback_accuracy", accuracy)
    
    def _parse_pattern_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for pattern analysis.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed pattern analysis
        """
        
        # Simple parsing implementation - in practice would use more sophisticated extraction
        patterns = {
            "raw_analysis": response,
            "fraud_patterns": [],
            "emerging_trends": [],
            "risk_indicators": [],
            "recommendations": []
        }
        
        # Extract patterns from response (simplified)
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if "pattern" in line.lower():
                patterns["fraud_patterns"].append(line)
            elif "trend" in line.lower():
                patterns["emerging_trends"].append(line)
            elif "risk" in line.lower() or "indicator" in line.lower():
                patterns["risk_indicators"].append(line)
            elif "recommend" in line.lower():
                patterns["recommendations"].append(line)
        
        return patterns
    
    def get_prompt_template(self) -> str:
        """Get research agent prompt template.
        
        Returns:
            Prompt template for research analysis
        """
        return """
        As a DOJ Research Agent, analyze the following cases for patterns and insights:
        
        Cases Data: {cases_data}
        
        Historical Patterns from Memory: {historical_patterns}
        
        Analysis Focus: {analysis_focus}
        
        Identify and analyze:
        1. Emerging fraud trends and evolving schemes
        2. Common charge combinations and legal strategies  
        3. Geographic, temporal, or demographic patterns
        4. Evolution of fraud techniques over time
        5. Relationships between different case types and fraud methodologies
        6. Technology usage patterns in fraud schemes
        7. Victim targeting strategies and vulnerabilities
        8. Investigation and prosecution patterns
        
        Provide detailed analysis with specific examples and actionable insights.
        Focus on patterns that could help predict, prevent, or detect future fraud cases.
        
        Structure your response with clear sections:
        - Fraud Patterns: Specific patterns observed in the data
        - Emerging Trends: New or evolving trends in fraud
        - Risk Indicators: Key indicators that suggest fraud
        - Recommendations: Actionable recommendations for detection and prevention
        """
