"""
Tests for the ResearchOrchestrator to ensure the graph can be generated and executed.
"""

import pytest
from unittest.mock import MagicMock

from doj_research_agent.orchestrator import ResearchOrchestrator
from doj_research_agent.models import CaseInfo, CaseType
from doj_research_agent.evaluate import EvaluationResult


@pytest.fixture
def mock_scraper(mocker):
    """Fixture to mock the DOJScraper."""
    mock = MagicMock()
    mock.get_press_release_urls.return_value = ["http://example.com/pr1", "http://example.com/pr2"]
    mock.fetch_press_release_content.return_value = "<html><body>Mock content</body></html>"
    return mock


@pytest.fixture
def mock_analyzer(mocker):
    """Fixture to mock the CaseAnalyzer."""
    mock = MagicMock()
    mock.analyze_press_release.return_value = CaseInfo(
        title="Mock Case",
        date="2025-07-21",
        url="http://example.com/pr1",
        case_type=CaseType.CRIMINAL,
    )
    return mock


@pytest.fixture
def mock_evaluator(mocker):
    """Fixture to mock the FraudDetectionEvaluator."""
    mock = MagicMock()
    mock.evaluate_dataset.return_value = EvaluationResult(
        accuracy=1.0, precision=1.0, recall=1.0, f1_score=1.0, confusion_matrix=[[1, 0], [0, 1]], detailed_results=[]
    )
    return mock


def test_generate_graph_definition():
    """
    Tests that the orchestrator's graph can be generated and visualized.
    """
    orchestrator = ResearchOrchestrator()
    mermaid_definition = orchestrator.graph.get_graph().draw_mermaid()

    print("--- Mermaid Graph Definition ---")
    print(mermaid_definition)
    print("--------------------------------")

    assert mermaid_definition
    assert "fetch_urls" in mermaid_definition
    assert "analyze_url" in mermaid_definition
    assert "compile_results" in mermaid_definition
    assert "evaluate_results" in mermaid_definition
    assert "fetch_urls --> analyze_url" in mermaid_definition
    assert "analyze_url -. &nbsp;finish&nbsp; .-> compile_results" in mermaid_definition
    assert "compile_results --> evaluate_results" in mermaid_definition


def test_orchestrator_run(mocker, mock_scraper, mock_analyzer, mock_evaluator):
    """
    Tests the full execution of the orchestrator with mocked components.
    """
    mocker.patch("doj_research_agent.orchestrator.DOJScraper", return_value=mock_scraper)
    mocker.patch("doj_research_agent.orchestrator.CaseAnalyzer", return_value=mock_analyzer)
    mocker.patch("doj_research_agent.orchestrator.FraudDetectionEvaluator", return_value=mock_evaluator)

    orchestrator = ResearchOrchestrator()
    result = orchestrator.run(max_cases=2)

    assert result.total_cases == 2
    assert result.successful_extractions == 2
    assert len(result.cases) == 2
    assert result.cases[0].title == "Mock Case"
