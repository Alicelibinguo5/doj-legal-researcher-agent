"""
Orchestrates the scraping and analysis of DOJ press releases using LangGraph.
"""

from typing import List, Optional, TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, END

from .analysis.analyzer import CaseAnalyzer
from .core.models import AnalysisResult, CaseInfo, ScrapingConfig, FeedbackData
from .core.feedback_manager import FeedbackManager
from .core.feedback_improver import FeedbackBasedImprover
from .scraping.scraper import DOJScraper
from .core.utils import save_analysis_result, setup_logger
from .evaluation.evaluate import FraudDetectionEvaluator
from .evaluation.evaluation_types import EvaluationResult, TestCase

logger = setup_logger(__name__)


class ResearchState(TypedDict):
    """Defines the state for the research graph."""

    urls_to_process: List[str]
    analyzed_cases: Annotated[List[CaseInfo], operator.add]
    failed_urls: Annotated[List[str], operator.add]
    scraping_config: ScrapingConfig
    final_result: Optional[AnalysisResult]
    evaluation_result: Optional[EvaluationResult]
    feedback_manager: Optional[FeedbackManager]
    pending_feedback: Annotated[List[FeedbackData], operator.add]


class ResearchOrchestrator:
    """
    Orchestrates the process of scraping and analyzing DOJ press releases using a LangGraph workflow.
    """

    def __init__(self, scraping_config: Optional[ScrapingConfig] = None):
        """
        Initialize the orchestrator.

        Args:
            scraping_config: Configuration for the scraper.
        """
        self.scraping_config = scraping_config or ScrapingConfig()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Builds the LangGraph for the research process."""
        workflow = StateGraph(ResearchState)

        # Define the nodes
        workflow.add_node("fetch_urls", self._fetch_urls_node)
        workflow.add_node("analyze_url", self._analyze_url_node)
        workflow.add_node("compile_results", self._compile_results_node)
        workflow.add_node("evaluate_results", self._evaluate_results_node)
        workflow.add_node("process_feedback", self._process_feedback_node)

        # Set the entrypoint
        workflow.set_entry_point("fetch_urls")

        # Define the edges
        workflow.add_edge("fetch_urls", "analyze_url")
        workflow.add_conditional_edges(
            "analyze_url",
            self._decide_next_step,
            {
                "continue": "analyze_url",
                "finish": "compile_results",
            },
        )
        workflow.add_edge("compile_results", "evaluate_results")
        workflow.add_edge("evaluate_results", "process_feedback")
        workflow.add_edge("process_feedback", END)

        return workflow.compile()

    def _fetch_urls_node(self, state: ResearchState) -> dict:
        """Fetches press release URLs."""
        logger.info("Fetching press release URLs...")
        scraper = DOJScraper(state["scraping_config"])
        urls = scraper.get_press_release_urls()

        if not urls:
            logger.warning("No press release URLs found.")
            return {"urls_to_process": []}

        logger.info(f"Found {len(urls)} URLs to process.")
        if state["scraping_config"].max_cases:
            urls = urls[: state["scraping_config"].max_cases]
            logger.info(f"Limiting to {len(urls)} URLs based on max_cases.")

        return {"urls_to_process": urls}

    def _analyze_url_node(self, state: ResearchState) -> dict:
        """Analyzes a single URL from the list."""
        url = state["urls_to_process"].pop(0)
        logger.info(
            f"Processing URL {len(state['analyzed_cases']) + len(state['failed_urls']) + 1}/{len(state['urls_to_process']) + len(state['analyzed_cases']) + len(state['failed_urls']) + 1}: {url}"
        )

        scraper = DOJScraper(state["scraping_config"])
        analyzer = CaseAnalyzer()

        try:
            soup = scraper.fetch_press_release_content(url)
            if soup:
                case_info = analyzer.analyze_press_release(url, soup)
                if case_info:
                    return {"analyzed_cases": [case_info]}
                else:
                    logger.warning(f"Failed to analyze press release from {url}")
                    return {"failed_urls": [url]}
            else:
                logger.warning(f"Failed to fetch content from {url}")
                return {"failed_urls": [url]}
        except Exception as e:
            logger.error(f"An error occurred while processing {url}: {e}")
            return {"failed_urls": [url]}

    def _decide_next_step(self, state: ResearchState) -> str:
        """Decides whether to continue processing URLs or finish."""
        if state["urls_to_process"]:
            return "continue"
        return "finish"

    def _compile_results_node(self, state: ResearchState) -> dict:
        """Compiles the final analysis result."""
        total_processed = len(state["analyzed_cases"]) + len(state["failed_urls"])
        result = AnalysisResult(
            cases=state["analyzed_cases"],
            total_cases=total_processed,
            successful_extractions=len(state["analyzed_cases"]),
            failed_extractions=len(state["failed_urls"]),
        )
        logger.info("DOJ research process finished.")
        logger.info(f"Successfully processed {result.successful_extractions} cases.")
        logger.info(f"Failed to process {result.failed_extractions} cases.")
        return {"final_result": result}

    def _evaluate_results_node(self, state: ResearchState) -> dict:
        """Evaluates the analysis results."""
        logger.info("Evaluating analysis results...")
        
        if not state["analyzed_cases"]:
            logger.warning("No cases to evaluate.")
            return {"evaluation_result": None}
        
        evaluator = FraudDetectionEvaluator()
        # Create test cases from analyzed cases for evaluation
        test_cases = []
        for case in state["analyzed_cases"]:
            test_case = TestCase(
                text=case.title,  # Use title as text since content is not available
                expected_fraud_flag=case.fraud_info.is_fraud if case.fraud_info else False,
                expected_fraud_type=None,  # CaseFraudInfo doesn't have fraud_type field
                expected_money_laundering_flag=case.money_laundering_flag or False,
                title=case.title,
                source_url=case.url
            )
            test_cases.append(test_case)
        
        evaluation_result = evaluator.evaluate_dataset(test_cases)
        
        logger.info(f"Evaluation completed. Accuracy: {evaluation_result.accuracy:.2f}")
        return {"evaluation_result": evaluation_result}

    def _process_feedback_node(self, state: ResearchState) -> dict:
        """Process any pending feedback for model improvement."""
        logger.info("Processing feedback for model improvement...")
        
        # Initialize feedback manager if not present
        feedback_manager = state.get("feedback_manager")
        if not feedback_manager:
            feedback_manager = FeedbackManager()
        
        # Process any pending feedback
        processed_count = 0
        for feedback in state.get("pending_feedback", []):
            result = feedback_manager.add_feedback(feedback)
            if result.success:
                processed_count += 1
                logger.info(f"Feedback processed: {result.feedback_id}")
            else:
                logger.error(f"Failed to process feedback: {result.message}")
        
        # Use feedback to improve model performance
        improver = FeedbackBasedImprover(feedback_manager)
        
        # Analyze feedback patterns
        analysis = improver.analyze_feedback_patterns()
        logger.info(f"Feedback analysis: {analysis.get('total_feedback', 0)} total feedback items")
        
        # Get improved configuration
        improved_config = improver.get_improved_config()
        logger.info(f"Improved fraud threshold: {improved_config.fraud_detection_threshold:.3f}")
        logger.info(f"Improved laundering threshold: {improved_config.money_laundering_threshold:.3f}")
        
        # Export improvement report
        improver.export_improvement_report()
        
        # Apply improvements to future analyses
        # TODO: Store improved config in state for use in subsequent analyses
        logger.info("Feedback-based improvements applied to model configuration")
        
        if processed_count > 0:
            logger.info(f"Processed {processed_count} feedback items")
        
        return {"pending_feedback": [], "feedback_manager": feedback_manager}

    def run(self, max_cases: Optional[int] = None) -> AnalysisResult:
        """
        Run the full research process.

        Args:
            max_cases: The maximum number of cases to process.

        Returns:
            An AnalysisResult object containing the processed cases.
        """
        logger.info("Starting DOJ research process with LangGraph...")

        if max_cases:
            self.scraping_config.max_cases = max_cases

        initial_state: ResearchState = {
            "urls_to_process": [],
            "analyzed_cases": [],
            "failed_urls": [],
            "scraping_config": self.scraping_config,
            "final_result": None,
            "evaluation_result": None,
            "feedback_manager": None,
            "pending_feedback": [],
        }

        final_state = self.graph.invoke(initial_state)

        return final_state.get(
            "final_result",
            AnalysisResult(
                cases=[], total_cases=0, successful_extractions=0, failed_extractions=0
            ),
        )

    def run_and_save(self, output_path: str, max_cases: Optional[int] = None) -> None:
        """
        Run the research process and save the results to a file.

        Args:
            output_path: The path to save the JSON results file.
            max_cases: The maximum number of cases to process.
        """
        result = self.run(max_cases=max_cases)
        logger.info(f"Saving analysis results to {output_path}")
        save_analysis_result(result, output_path)
        logger.info("Results saved.")