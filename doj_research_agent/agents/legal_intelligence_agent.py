"""Legal Intelligence Agent for DOJ research multi-agent system."""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import re
import json
from dataclasses import dataclass, field
from .base_agent import BaseAgent
from ..core.models import CaseInfo, ChargeCategory, CaseType, Disposition


@dataclass
class LegalPrecedent:
    """Represents a legal precedent case."""
    
    case_name: str
    citation: str
    year: int
    court: str
    charges: List[str]
    outcome: str
    sentence_range: Optional[str] = None
    key_holdings: List[str] = field(default_factory=list)
    relevance_score: float = 0.0


@dataclass
class RegulatoryUpdate:
    """Represents a regulatory change or update."""
    
    agency: str
    update_type: str  # "new_regulation", "amendment", "enforcement_guidance", etc.
    title: str
    date: datetime
    summary: str
    impact_areas: List[str] = field(default_factory=list)
    fraud_relevance: float = 0.0


@dataclass
class JurisdictionalPattern:
    """Represents patterns in jurisdictional prosecution."""
    
    district: str
    state: str
    fraud_types: List[str]
    case_count: int
    avg_sentence_months: Optional[float] = None
    prosecution_rate: float = 0.0
    specializations: List[str] = field(default_factory=list)


class LegalIntelligenceAgent(BaseAgent):
    """Specialized agent for legal context analysis and precedent tracking.
    
    This agent provides legal intelligence by analyzing precedents, tracking
    regulatory changes, and providing legal context for fraud cases.
    """
    
    def __init__(self, llm_config: Optional[Dict] = None) -> None:
        """Initialize Legal Intelligence Agent.
        
        Args:
            llm_config: Configuration for LLM integration
        """
        super().__init__("legal_intelligence_agent", llm_config)
        self.precedent_database: List[LegalPrecedent] = []
        self.regulatory_updates: List[RegulatoryUpdate] = []
        self.jurisdictional_patterns: Dict[str, JurisdictionalPattern] = {}
        self._initialize_legal_knowledge()
    
    def _initialize_legal_knowledge(self) -> None:
        """Initialize basic legal knowledge and precedent database."""
        
        # Sample precedents for demonstration (in real implementation, load from database)
        sample_precedents = [
            LegalPrecedent(
                case_name="United States v. Smith",
                citation="F.3d (2023)",
                year=2023,
                court="2nd Circuit",
                charges=["wire fraud", "money laundering"],
                outcome="conviction",
                sentence_range="24-36 months",
                key_holdings=["COVID-19 fraud enhancement applies", "Loss amount calculation clarified"],
                relevance_score=0.9
            ),
            LegalPrecedent(
                case_name="United States v. Johnson", 
                citation="F.3d (2022)",
                year=2022,
                court="9th Circuit",
                charges=["healthcare fraud", "kickback scheme"],
                outcome="plea agreement",
                sentence_range="18-24 months",
                key_holdings=["Telemedicine fraud patterns", "AKS violation standards"],
                relevance_score=0.85
            )
        ]
        
        self.precedent_database.extend(sample_precedents)
        self.logger.info(f"Initialized legal knowledge with {len(self.precedent_database)} precedents")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process legal intelligence analysis.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Dictionary of legal intelligence updates
        """
        self.logger.info("Legal Intelligence Agent starting processing...")
        
        # Initialize memory if not done
        if not self.memory:
            self.initialize_memory(state["shared_memory"])
        
        updates = {}
        
        # Analyze legal precedents for current cases
        if state.get("analyzed_cases"):
            precedent_analysis = await self._analyze_precedents(state["analyzed_cases"])
            updates["precedent_analysis"] = precedent_analysis
        
        # Check for regulatory updates
        regulatory_analysis = await self._check_regulatory_changes()
        if regulatory_analysis:
            updates["regulatory_analysis"] = regulatory_analysis
        
        # Validate legal classifications from other agents
        legal_validation = await self._validate_legal_accuracy(state)
        updates["legal_validation"] = legal_validation
        
        # Analyze jurisdictional patterns
        jurisdictional_analysis = self._analyze_jurisdictional_patterns(
            state.get("analyzed_cases", [])
        )
        updates["jurisdictional_analysis"] = jurisdictional_analysis
        
        # Process insights from other agents
        await self._process_agent_insights(state)
        
        # Update agent state
        updates["legal_intelligence_agent_state"] = {
            "last_analysis": datetime.now().isoformat(),
            "precedents_analyzed": len(self.precedent_database),
            "regulatory_updates_count": len(self.regulatory_updates),
            "jurisdictions_tracked": len(self.jurisdictional_patterns)
        }
        
        # Share insights with other agents
        await self._share_legal_insights(state, updates)
        
        self.logger.info("Legal Intelligence Agent completed processing")
        return updates
    
    async def _analyze_precedents(self, cases: List[CaseInfo]) -> Dict[str, Any]:
        """Analyze legal precedents relevant to current cases.
        
        Args:
            cases: List of analyzed cases
            
        Returns:
            Precedent analysis results
        """
        precedent_matches = []
        legal_trends = {}
        
        for case in cases[-10:]:  # Analyze last 10 cases
            
            # Find relevant precedents
            relevant_precedents = self._find_relevant_precedents(case)
            
            if relevant_precedents:
                precedent_matches.append({
                    "case_url": case.url,
                    "case_title": case.title,
                    "charges": case.charges,
                    "relevant_precedents": [
                        {
                            "case_name": p.case_name,
                            "citation": p.citation,
                            "relevance_score": p.relevance_score,
                            "key_holdings": p.key_holdings,
                            "sentence_range": p.sentence_range
                        }
                        for p in relevant_precedents[:3]  # Top 3 most relevant
                    ]
                })
        
        # Analyze legal trends using LLM
        if precedent_matches:
            trends_analysis = await self._analyze_legal_trends(precedent_matches)
            legal_trends = trends_analysis
        
        # Update memory
        self.update_memory("recent_precedent_analysis", {
            "matches": precedent_matches,
            "trends": legal_trends,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "precedent_matches": precedent_matches,
            "legal_trends": legal_trends,
            "analysis_summary": f"Found {len(precedent_matches)} cases with relevant precedents"
        }
    
    def _find_relevant_precedents(self, case: CaseInfo) -> List[LegalPrecedent]:
        """Find precedents relevant to a specific case.
        
        Args:
            case: Case to find precedents for
            
        Returns:
            List of relevant precedents, sorted by relevance
        """
        relevant_precedents = []
        
        for precedent in self.precedent_database:
            relevance_score = self._calculate_precedent_relevance(case, precedent)
            if relevance_score > 0.3:  # Minimum relevance threshold
                precedent.relevance_score = relevance_score
                relevant_precedents.append(precedent)
        
        # Sort by relevance score
        relevant_precedents.sort(key=lambda p: p.relevance_score, reverse=True)
        return relevant_precedents
    
    def _calculate_precedent_relevance(self, case: CaseInfo, precedent: LegalPrecedent) -> float:
        """Calculate relevance score between a case and precedent.
        
        Args:
            case: Current case
            precedent: Precedent case
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        
        # Charge similarity (40% weight)
        case_charges = [charge.lower() for charge in case.charges]
        precedent_charges = [charge.lower() for charge in precedent.charges]
        
        charge_overlap = len(set(case_charges) & set(precedent_charges))
        charge_similarity = charge_overlap / max(len(case_charges), len(precedent_charges), 1)
        score += charge_similarity * 0.4
        
        # Fraud type similarity (30% weight)
        if case.fraud_info and case.fraud_info.is_fraud:
            # Check if precedent involves similar fraud patterns
            case_title_lower = case.title.lower()
            precedent_name_lower = precedent.case_name.lower()
            
            fraud_keywords = ["fraud", "scheme", "conspiracy", "money laundering", "embezzlement"]
            case_fraud_words = [word for word in fraud_keywords if word in case_title_lower]
            precedent_fraud_words = [word for word in fraud_keywords if word in precedent_name_lower]
            
            if case_fraud_words and precedent_fraud_words:
                fraud_overlap = len(set(case_fraud_words) & set(precedent_fraud_words))
                fraud_similarity = fraud_overlap / max(len(case_fraud_words), len(precedent_fraud_words), 1)
                score += fraud_similarity * 0.3
        
        # Recency factor (20% weight)
        current_year = datetime.now().year
        years_old = current_year - precedent.year
        recency_score = max(0, 1 - (years_old / 10))  # Decay over 10 years
        score += recency_score * 0.2
        
        # Court authority (10% weight) 
        if "Circuit" in precedent.court or "Supreme" in precedent.court:
            score += 0.1
        
        return min(score, 1.0)
    
    async def _analyze_legal_trends(self, precedent_matches: List[Dict]) -> Dict[str, Any]:
        """Analyze legal trends from precedent matches using LLM.
        
        Args:
            precedent_matches: List of precedent match data
            
        Returns:
            Legal trends analysis
        """
        
        prompt = self.get_prompt_template().format(
            precedent_data=json.dumps(precedent_matches, indent=2),
            analysis_type="legal_trends"
        )
        
        try:
            response = await self.generate_llm_response(prompt)
            trends = self._parse_legal_trends_response(response)
            return trends
        except Exception as e:
            self.logger.error(f"Legal trends analysis failed: {e}")
            return {"error": str(e)}
    
    async def _check_regulatory_changes(self) -> Optional[Dict[str, Any]]:
        """Check for recent regulatory changes affecting fraud prosecution.
        
        Returns:
            Regulatory analysis or None if no significant updates
        """
        
        # In a real implementation, this would query regulatory databases
        # For now, simulate checking for recent updates
        
        recent_cutoff = datetime.now() - timedelta(days=90)
        recent_updates = [
            update for update in self.regulatory_updates 
            if update.date >= recent_cutoff
        ]
        
        if not recent_updates:
            # Simulate finding new regulatory guidance
            simulated_update = RegulatoryUpdate(
                agency="DOJ",
                update_type="enforcement_guidance",
                title="Updated Cryptocurrency Fraud Prosecution Guidelines",
                date=datetime.now(),
                summary="New guidelines for prosecuting cryptocurrency-related fraud schemes",
                impact_areas=["financial_fraud", "cybercrime"],
                fraud_relevance=0.8
            )
            self.regulatory_updates.append(simulated_update)
            recent_updates = [simulated_update]
        
        if recent_updates:
            analysis = await self._analyze_regulatory_impact(recent_updates)
            
            self.update_memory("recent_regulatory_updates", {
                "updates": [
                    {
                        "agency": u.agency,
                        "title": u.title,
                        "date": u.date.isoformat(),
                        "impact_areas": u.impact_areas,
                        "relevance": u.fraud_relevance
                    }
                    for u in recent_updates
                ],
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "recent_updates": recent_updates,
                "impact_analysis": analysis,
                "update_count": len(recent_updates)
            }
        
        return None
    
    async def _analyze_regulatory_impact(self, updates: List[RegulatoryUpdate]) -> Dict[str, Any]:
        """Analyze impact of regulatory updates.
        
        Args:
            updates: List of regulatory updates
            
        Returns:
            Impact analysis
        """
        
        updates_summary = []
        for update in updates:
            updates_summary.append({
                "agency": update.agency,
                "type": update.update_type,
                "title": update.title,
                "impact_areas": update.impact_areas,
                "summary": update.summary
            })
        
        prompt = f"""
        Analyze the impact of these regulatory updates on fraud prosecution:
        
        {json.dumps(updates_summary, indent=2)}
        
        Assess:
        1. Impact on current fraud detection and prosecution strategies
        2. New legal requirements or standards
        3. Enforcement priority changes
        4. Implications for specific fraud types
        5. Recommendations for compliance and detection
        
        Provide structured analysis with specific recommendations.
        """
        
        try:
            response = await self.generate_llm_response(prompt)
            return {"impact_analysis": response, "updates_analyzed": len(updates)}
        except Exception as e:
            self.logger.error(f"Regulatory impact analysis failed: {e}")
            return {"error": str(e)}
    
    async def _validate_legal_accuracy(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate legal accuracy of classifications from other agents.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Legal validation results
        """
        validation_results = {}
        
        # Get research agent insights
        research_messages = self.get_agent_messages(state, "research_agent")
        evaluation_messages = self.get_agent_messages(state, "evaluation_agent")
        
        # Validate fraud classifications
        if state.get("analyzed_cases"):
            fraud_validation = await self._validate_fraud_classifications(
                state["analyzed_cases"]
            )
            validation_results["fraud_classification_accuracy"] = fraud_validation
        
        # Validate charge categorizations
        if state.get("analyzed_cases"):
            charge_validation = self._validate_charge_categories(state["analyzed_cases"])
            validation_results["charge_categorization_accuracy"] = charge_validation
        
        # Validate against legal standards
        legal_standards_check = await self._check_legal_standards_compliance(state)
        validation_results["legal_standards_compliance"] = legal_standards_check
        
        return validation_results
    
    async def _validate_fraud_classifications(self, cases: List[CaseInfo]) -> Dict[str, Any]:
        """Validate fraud classifications against legal standards.
        
        Args:
            cases: List of cases to validate
            
        Returns:
            Validation results
        """
        validation_errors = []
        total_fraud_cases = 0
        correct_classifications = 0
        
        for case in cases:
            if case.fraud_info and case.fraud_info.is_fraud:
                total_fraud_cases += 1
                
                # Validate fraud classification using legal criteria
                is_valid = await self._check_fraud_legal_criteria(case)
                if is_valid:
                    correct_classifications += 1
                else:
                    validation_errors.append({
                        "case_url": case.url,
                        "case_title": case.title,
                        "issue": "Fraud classification doesn't meet legal criteria",
                        "evidence": case.fraud_info.evidence
                    })
        
        accuracy = correct_classifications / total_fraud_cases if total_fraud_cases > 0 else 1.0
        
        return {
            "total_fraud_cases": total_fraud_cases,
            "correct_classifications": correct_classifications,
            "legal_accuracy": accuracy,
            "validation_errors": validation_errors
        }
    
    async def _check_fraud_legal_criteria(self, case: CaseInfo) -> bool:
        """Check if a case meets legal criteria for fraud classification.
        
        Args:
            case: Case to validate
            
        Returns:
            True if case meets legal fraud criteria
        """
        
        # Legal elements of fraud: 
        # 1. Material misrepresentation or omission
        # 2. Intent to deceive
        # 3. Reasonable reliance by victim
        # 4. Resulting damages
        
        legal_fraud_indicators = [
            "false statement", "misrepresentation", "scheme to defraud", 
            "intent to deceive", "fraudulent", "deceptive practice",
            "wire fraud", "mail fraud", "bank fraud", "securities fraud"
        ]
        
        case_text = f"{case.title} {' '.join(case.charges)}".lower()
        
        # Check for legal fraud indicators
        fraud_indicators_found = [
            indicator for indicator in legal_fraud_indicators 
            if indicator in case_text
        ]
        
        # Must have at least one clear legal fraud indicator
        return len(fraud_indicators_found) > 0
    
    def _validate_charge_categories(self, cases: List[CaseInfo]) -> Dict[str, Any]:
        """Validate charge category assignments.
        
        Args:
            cases: List of cases to validate
            
        Returns:
            Charge validation results
        """
        
        category_accuracy = {}
        total_categorized = 0
        correct_categories = 0
        
        for case in cases:
            if case.charge_categories:
                total_categorized += 1
                
                # Validate categories against charges
                is_valid = self._check_charge_category_validity(case)
                if is_valid:
                    correct_categories += 1
                
                # Track category-specific accuracy
                for category in case.charge_categories:
                    if category.value not in category_accuracy:
                        category_accuracy[category.value] = {"correct": 0, "total": 0}
                    
                    category_accuracy[category.value]["total"] += 1
                    if is_valid:
                        category_accuracy[category.value]["correct"] += 1
        
        overall_accuracy = correct_categories / total_categorized if total_categorized > 0 else 1.0
        
        return {
            "overall_accuracy": overall_accuracy,
            "category_breakdown": category_accuracy,
            "total_categorized": total_categorized
        }
    
    def _check_charge_category_validity(self, case: CaseInfo) -> bool:
        """Check if charge categories are valid for the case.
        
        Args:
            case: Case to validate
            
        Returns:
            True if categories are valid
        """
        
        # Simple validation based on charge text
        charges_text = " ".join(case.charges).lower()
        
        category_keywords = {
            ChargeCategory.FINANCIAL_FRAUD: ["fraud", "embezzlement", "money laundering", "securities"],
            ChargeCategory.HEALTH_CARE_FRAUD: ["healthcare", "medicare", "medicaid", "medical"],
            ChargeCategory.CYBERCRIME: ["computer", "cyber", "hacking", "internet", "wire"],
            ChargeCategory.PUBLIC_CORRUPTION: ["corruption", "bribery", "kickback", "official"],
            ChargeCategory.TAX: ["tax", "evasion", "irs", "income"],
            ChargeCategory.DRUGS: ["drug", "narcotic", "controlled substance", "trafficking"],
            ChargeCategory.FIREARMS_OFFENSES: ["firearm", "weapon", "gun", "ammunition"],
        }
        
        for category in case.charge_categories:
            if category in category_keywords:
                keywords = category_keywords[category]
                if any(keyword in charges_text for keyword in keywords):
                    return True
        
        # If no keywords match, might be miscategorized
        return len(case.charge_categories) == 0  # Empty categories are technically valid
    
    async def _check_legal_standards_compliance(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with legal standards and best practices.
        
        Args:
            state: Current multi-agent state
            
        Returns:
            Legal standards compliance check
        """
        
        compliance_issues = []
        recommendations = []
        
        # Check if classifications follow legal definitions
        if state.get("analyzed_cases"):
            for case in state["analyzed_cases"][-5:]:  # Check last 5 cases
                
                # Check fraud definition compliance
                if case.fraud_info and case.fraud_info.is_fraud:
                    if not case.fraud_info.evidence:
                        compliance_issues.append({
                            "case": case.url,
                            "issue": "Fraud classification lacks supporting evidence",
                            "severity": "medium"
                        })
                
                # Check charge-category alignment
                if case.charges and not case.charge_categories:
                    compliance_issues.append({
                        "case": case.url,
                        "issue": "Case has charges but no categories assigned",
                        "severity": "low"
                    })
        
        # Generate recommendations
        if compliance_issues:
            recommendations.append("Ensure all fraud classifications include supporting evidence")
            recommendations.append("Review charge categorization logic for completeness")
        
        return {
            "compliance_score": 1.0 - (len(compliance_issues) / 10),  # Normalized score
            "issues_found": compliance_issues,
            "recommendations": recommendations,
            "total_issues": len(compliance_issues)
        }
    
    def _analyze_jurisdictional_patterns(self, cases: List[CaseInfo]) -> Dict[str, Any]:
        """Analyze jurisdictional patterns in fraud prosecution.
        
        Args:
            cases: List of cases to analyze
            
        Returns:
            Jurisdictional pattern analysis
        """
        
        # Extract jurisdiction info from case URLs or titles
        jurisdiction_data = {}
        
        for case in cases:
            # Extract jurisdiction from URL pattern (simplified)
            jurisdiction = self._extract_jurisdiction(case.url, case.title)
            
            if jurisdiction not in jurisdiction_data:
                jurisdiction_data[jurisdiction] = {
                    "cases": [],
                    "fraud_count": 0,
                    "charge_types": set()
                }
            
            jurisdiction_data[jurisdiction]["cases"].append(case)
            
            if case.fraud_info and case.fraud_info.is_fraud:
                jurisdiction_data[jurisdiction]["fraud_count"] += 1
            
            jurisdiction_data[jurisdiction]["charge_types"].update(case.charges)
        
        # Convert to analysis format
        patterns = []
        for jurisdiction, data in jurisdiction_data.items():
            if len(data["cases"]) >= 2:  # Only include jurisdictions with multiple cases
                patterns.append({
                    "jurisdiction": jurisdiction,
                    "total_cases": len(data["cases"]),
                    "fraud_cases": data["fraud_count"],
                    "fraud_rate": data["fraud_count"] / len(data["cases"]),
                    "common_charges": list(data["charge_types"])[:5]  # Top 5 charge types
                })
        
        return {
            "jurisdictional_patterns": patterns,
            "total_jurisdictions": len(jurisdiction_data),
            "analysis_summary": f"Analyzed {len(cases)} cases across {len(jurisdiction_data)} jurisdictions"
        }
    
    def _extract_jurisdiction(self, url: str, title: str) -> str:
        """Extract jurisdiction from case URL or title.
        
        Args:
            url: Case URL
            title: Case title
            
        Returns:
            Jurisdiction identifier
        """
        
        # Extract from URL patterns (simplified)
        district_patterns = [
            r"\.gov/([a-z]{2,4})/",  # State abbreviations
            r"usao-([a-z]{2,4})",    # USAO patterns
        ]
        
        for pattern in district_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1).upper()
        
        # Extract from title patterns
        district_keywords = [
            "Eastern District", "Western District", "Northern District", "Southern District",
            "Middle District", "District of"
        ]
        
        for keyword in district_keywords:
            if keyword in title:
                # Extract the state/jurisdiction after the keyword
                parts = title.split(keyword)
                if len(parts) > 1:
                    state_part = parts[1].split()[0:2]  # Get next 1-2 words
                    return f"{keyword} of {' '.join(state_part)}"
        
        return "Unknown"
    
    async def _process_agent_insights(self, state: Dict[str, Any]) -> None:
        """Process insights shared by other agents.
        
        Args:
            state: Current multi-agent state
        """
        
        # Process research agent insights
        research_messages = self.get_agent_messages(state, "research_agent")
        for message in research_messages:
            if message["type"] == "pattern_insights":
                await self._analyze_legal_implications_of_patterns(message["data"])
        
        # Process evaluation agent insights
        eval_messages = self.get_agent_messages(state, "evaluation_agent")
        for message in eval_messages:
            if message["type"] == "performance_feedback":
                self._incorporate_performance_feedback(message["data"])
    
    async def _analyze_legal_implications_of_patterns(self, pattern_data: Dict[str, Any]) -> None:
        """Analyze legal implications of patterns discovered by research agent.
        
        Args:
            pattern_data: Pattern data from research agent
        """
        
        # Find legal precedents related to the patterns
        relevant_precedents = []
        for precedent in self.precedent_database:
            # Check if precedent relates to discovered patterns
            pattern_keywords = str(pattern_data).lower()
            precedent_keywords = f"{precedent.case_name} {' '.join(precedent.charges)}".lower()
            
            if any(keyword in precedent_keywords for keyword in pattern_keywords.split()):
                relevant_precedents.append(precedent)
        
        if relevant_precedents:
            self.update_memory("pattern_precedents", {
                "pattern_data": pattern_data,
                "relevant_precedents": [p.case_name for p in relevant_precedents],
                "timestamp": datetime.now().isoformat()
            })
    
    def _incorporate_performance_feedback(self, feedback_data: Dict[str, Any]) -> None:
        """Incorporate performance feedback from evaluation agent.
        
        Args:
            feedback_data: Feedback data from evaluation agent
        """
        
        # Adjust legal validation criteria based on performance feedback
        accuracy = feedback_data.get("accuracy", 0.0)
        
        if accuracy < 0.8:
            # Lower accuracy suggests need for stricter legal validation
            self.update_memory("validation_strictness", "high")
        elif accuracy > 0.95:
            # High accuracy suggests validation might be too strict
            self.update_memory("validation_strictness", "moderate")
        
        self.log_performance_metric("legal_validation_accuracy", accuracy)
    
    async def _share_legal_insights(self, state: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """Share legal insights with other agents.
        
        Args:
            state: Current multi-agent state
            updates: Updates from this processing cycle
        """
        
        # Share precedent insights with research agent
        if "precedent_analysis" in updates:
            self.communicate_with_agent(
                state, "research_agent", "legal_precedents", 
                updates["precedent_analysis"]
            )
        
        # Share legal validation results with evaluation agent
        if "legal_validation" in updates:
            self.communicate_with_agent(
                state, "evaluation_agent", "legal_accuracy_feedback",
                updates["legal_validation"]
            )
        
        # Share regulatory updates with both agents
        if "regulatory_analysis" in updates:
            self.communicate_with_agent(
                state, "research_agent", "regulatory_updates",
                updates["regulatory_analysis"]
            )
            self.communicate_with_agent(
                state, "evaluation_agent", "regulatory_compliance",
                updates["regulatory_analysis"]
            )
    
    def _parse_legal_trends_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for legal trends analysis.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed legal trends data
        """
        
        # Simple parsing - in practice, would use more sophisticated extraction
        trends = {
            "raw_analysis": response,
            "key_trends": [],
            "legal_developments": [],
            "enforcement_patterns": []
        }
        
        # Extract key points (simplified)
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if "trend" in line.lower():
                trends["key_trends"].append(line)
            elif "enforcement" in line.lower():
                trends["enforcement_patterns"].append(line)
            elif "development" in line.lower():
                trends["legal_developments"].append(line)
        
        return trends
    
    def get_prompt_template(self) -> str:
        """Get legal intelligence agent prompt template.
        
        Returns:
            Prompt template for legal analysis
        """
        return """
        As a Legal Intelligence Agent specializing in DOJ fraud cases, analyze the following data:
        
        {precedent_data}
        
        Analysis Type: {analysis_type}
        
        Provide detailed legal analysis including:
        1. Relevant legal precedents and their implications
        2. Current enforcement trends and patterns
        3. Regulatory developments affecting fraud prosecution
        4. Jurisdictional considerations and venue patterns
        5. Sentencing trends and judicial patterns
        6. Legal strategy insights and prosecution approaches
        
        Focus on actionable legal intelligence that can inform fraud detection,
        case evaluation, and prosecution strategy recommendations.
        
        Structure your analysis with clear sections and specific legal citations where applicable.
        """
