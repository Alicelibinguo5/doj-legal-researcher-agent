
"""
Tests for the CaseAnalyzer class.
"""

import pytest
from bs4 import BeautifulSoup

from doj_research_agent.analyzer import CaseAnalyzer
from doj_research_agent.models import CaseType, ChargeCategory


@pytest.fixture
def mock_soup():
    """Fixture to create a mock BeautifulSoup object for a press release."""
    html = """
    <html>
        <head>
            <title>Test Press Release</title>
        </head>
        <body>
            <article>
                <h1>Man Sentenced for Wire Fraud</h1>
                <p class="date">July 21, 2025</p>
                <div class="field--name-body">
                    <p>A man was sentenced to 5 years in prison for a wire fraud scheme.</p>
                    <p>He was charged with conspiracy to commit wire fraud.</p>
                </div>
            </article>
        </body>
    </html>
    """
    return BeautifulSoup(html, "html.parser")


def test_analyze_press_release(mock_soup):
    """
    Tests the analysis of a mock press release.
    """
    analyzer = CaseAnalyzer()
    case_info = analyzer.analyze_press_release("http://example.com/pr1", mock_soup)

    assert case_info is not None
    assert case_info.title == "Man Sentenced for Wire Fraud"
    assert case_info.date == "July 21, 2025"
    assert case_info.case_type == CaseType.CRIMINAL
    assert "conspiracy to commit wire fraud" in case_info.charges
    assert ChargeCategory.FINANCIAL_FRAUD in case_info.charge_categories
