"""
LLM Judge evaluation system for DOJ fraud detection accuracy using RAGAS.

This module provides functionality to evaluate the performance of fraud detection
models using LLM-as-a-Judge techniques with RAGAS framework.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        answer_correctness
    )
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False

try:
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from ..llm.llm import LLMManager, extract_structured_info
from ..llm.llm_models import CaseAnalysisResponse
from .evaluation_types import EvaluationResult, TestCase
from .langfuse_integration import trace_evaluation, get_langfuse_tracer
from ..core.constants import FRAUD_KEYWORDS

logger = logging.getLogger(__name__)





class LLMJudge:
    """LLM-as-a-Judge evaluator for fraud detection accuracy."""
    
    def __init__(self, 
                 judge_provider: str = "openai",
                 judge_model: str = "gpt-4o",
                 judge_api_key: Optional[str] = None):
        """
        Initialize LLM Judge.
        
        Args:
            judge_provider: LLM provider for the judge model
            judge_model: Model to use for evaluation
            judge_api_key: API key for judge model
        """
        self.judge_llm = LLMManager(
            provider=judge_provider,
            model=judge_model,
            api_key=judge_api_key,
            temperature=0.1,
            use_instructor=True
        )
        
    def judge_fraud_classification(self, 
                                 text: str, 
                                 predicted_result: Dict, 
                                 expected_result: TestCase) -> Dict:
        """
        Use LLM to judge the quality of fraud classification.
        
        Args:
            text: Original press release text
            predicted_result: Model's prediction
            expected_result: Ground truth test case
            
        Returns:
            Dict with judgment scores and reasoning
        """
        judgment_prompt = f"""
        You are an expert legal evaluator specializing in fraud detection accuracy.
        
        Evaluate how well the predicted fraud classification matches the expected result for this DOJ press release.
        
        ORIGINAL TEXT:
        {text[:1000]}{"..." if len(text) > 1000 else ""}
        
        PREDICTED RESULT:
        - Fraud Flag: {predicted_result.get('fraud_flag', False)}
        - Fraud Type: {predicted_result.get('fraud_type', 'None')}
        - Money Laundering Flag: {predicted_result.get('money_laundering_flag', False)}
        - Rationale: {predicted_result.get('fraud_rationale', 'None')}
        
        EXPECTED RESULT:
        - Fraud Flag: {expected_result.expected_fraud_flag}
        - Fraud Type: {expected_result.expected_fraud_type or 'None'}
        - Money Laundering Flag: {expected_result.expected_money_laundering_flag}
        - Ground Truth Rationale: {expected_result.ground_truth_rationale or 'None'}
        
        Rate the prediction on the following criteria (0-10 scale):
        1. FRAUD_ACCURACY: How accurate is the fraud flag classification?
        2. TYPE_ACCURACY: How accurate is the fraud type classification (if applicable)?
        3. EVIDENCE_QUALITY: How well does the evidence support the classification?
        4. LEGAL_REASONING: How sound is the legal reasoning provided?
        5. OVERALL_QUALITY: Overall quality of the classification
        
        Provide your evaluation in this JSON format:
        {{
            "fraud_accuracy": <score>,
            "type_accuracy": <score>,
            "evidence_quality": <score>,
            "legal_reasoning": <score>,
            "overall_quality": <score>,
            "judgment_explanation": "<brief explanation of your evaluation>",
            "critical_errors": ["<list any critical classification errors>"],
            "recommendations": ["<suggestions for improvement>"]
        }}
        """
        
        try:
            response = self.judge_llm.generate_response(
                system_prompt="You are a precise legal evaluation expert. Always provide scores and detailed analysis.",
                user_prompt=judgment_prompt
            )
            
            # Parse JSON response
            judgment = json.loads(response)
            return judgment
            
        except Exception as e:
            logger.error(f"Error in LLM judge evaluation: {e}")
            return {
                "fraud_accuracy": 0,
                "type_accuracy": 0,
                "evidence_quality": 0,
                "legal_reasoning": 0,
                "overall_quality": 0,
                "judgment_explanation": f"Error in evaluation: {str(e)}",
                "critical_errors": ["Evaluation failed"],
                "recommendations": ["Review evaluation system"]
            }


class FraudDetectionEvaluator:
    """Main evaluator for fraud detection system."""
    
    def __init__(self, 
                 model_provider: str = "openai",
                 model_name: str = "gpt-4o",
                 model_api_key: Optional[str] = None,
                 use_llm_judge: bool = True,
                 judge_provider: str = "openai",
                 judge_model: str = "gpt-4o",
                 judge_api_key: Optional[str] = None):
        """
        Initialize the evaluator.
        
        Args:
            model_provider: Provider for model being evaluated
            model_name: Model being evaluated
            model_api_key: API key for model being evaluated
            use_llm_judge: Whether to use LLM judge for qualitative evaluation
            judge_provider: Provider for judge model
            judge_model: Judge model name
            judge_api_key: API key for judge model
        """
        self.model_provider = model_provider
        self.model_name = model_name
        self.model_api_key = model_api_key
        
        self.use_llm_judge = use_llm_judge
        if use_llm_judge:
            self.llm_judge = LLMJudge(
                judge_provider=judge_provider,
                judge_model=judge_model,
                judge_api_key=judge_api_key
            )
        
    def create_test_dataset(self) -> List[TestCase]:
        """Create a test dataset with known fraud and non-fraud cases."""
        return [
            TestCase(
                text="John Smith was sentenced to 5 years for wire fraud scheme that defrauded investors of $2 million through false investment promises.",
                expected_fraud_flag=True,
                expected_fraud_type="financial_fraud",
                expected_money_laundering_flag=False,
                title="Investment Fraud Sentencing",
                ground_truth_rationale="Clear wire fraud charges with deceptive investment scheme"
            ),
            TestCase(
                text="The Department of Justice announced new cybersecurity initiatives to protect against fraud. This is part of our ongoing commitment to preventing financial crimes.",
                expected_fraud_flag=False,
                expected_fraud_type=None,
                expected_money_laundering_flag=False,
                title="DOJ Cybersecurity Announcement",
                ground_truth_rationale="Generic mention of fraud prevention, not a fraud case"
            ),
            TestCase(
                text="Maria Lopez pleaded guilty to healthcare fraud charges for submitting false Medicare billing claims totaling $500,000 over two years.",
                expected_fraud_flag=True,
                expected_fraud_type="healthcare_fraud",
                expected_money_laundering_flag=False,
                title="Healthcare Fraud Guilty Plea",
                ground_truth_rationale="Clear healthcare fraud with false Medicare billing"
            ),
            TestCase(
                text="Robert Chen was convicted of money laundering $3 million in drug proceeds through multiple shell companies and offshore accounts.",
                expected_fraud_flag=False,
                expected_fraud_type=None,
                expected_money_laundering_flag=True,
                title="Money Laundering Conviction",
                ground_truth_rationale="Pure money laundering case without fraud charges"
            ),
            TestCase(
                text="A Ponzi scheme operator was sentenced for wire fraud and money laundering after stealing $10 million from investors and concealing the proceeds.",
                expected_fraud_flag=True,
                expected_fraud_type="financial_fraud",
                expected_money_laundering_flag=True,
                title="Ponzi Scheme with Money Laundering",
                ground_truth_rationale="Both fraud (Ponzi scheme) and money laundering charges present"
            )
        ]
    
    def create_test_dataset_from_real_data(self, 
                                          scraper,
                                          max_cases: int = 10,
                                          api_key: Optional[str] = None) -> List[TestCase]:
        """
        Create test dataset from real DOJ press releases.
        
        Args:
            scraper: DOJScraper instance to fetch real press releases
            max_cases: Maximum number of cases to include
            api_key: API key for LLM evaluation
            
        Returns:
            List of TestCase objects from real press releases
        """
        from ..scraping.scraper import DOJScraper
        from ..analysis.analyzer import CaseAnalyzer
        
        test_cases = []
        urls = scraper.get_press_release_urls()
        
        analyzer = CaseAnalyzer()
        
        for i, url in enumerate(urls[:max_cases]):
            try:
                # Fetch and analyze real press release
                soup = scraper.fetch_press_release_content(url)
                if not soup:
                    continue
                    
                # Get classic analysis
                case_info = analyzer.analyze_press_release(url, soup)
                if not case_info:
                    continue
                
                # Get LLM analysis for ground truth comparison
                content = analyzer.extract_main_article_content(soup)
                if not content:
                    continue
                
                llm_result = extract_structured_info(
                    text_or_soup=content,
                    provider=self.model_provider,
                    model=self.model_name,
                    api_key=api_key or ""
                )
                
                # Create test case with real data
                test_case = TestCase(
                    text=content[:1000] + "..." if len(content) > 1000 else content,
                    expected_fraud_flag=llm_result.get('fraud_flag', False),
                    expected_fraud_type=llm_result.get('fraud_type'),
                    expected_money_laundering_flag=llm_result.get('money_laundering_flag', False),
                    title=case_info.title or f"Real Case {i+1}",
                    source_url=url,
                    ground_truth_rationale=llm_result.get('fraud_rationale')
                )
                
                test_cases.append(test_case)
                logger.info(f"Created test case {i+1}: {test_case.title}")
                
            except Exception as e:
                logger.error(f"Error creating test case from {url}: {e}")
                continue
        
        return test_cases

    def evaluate_single_case(self, test_case: TestCase) -> Dict:
        """Evaluate a single test case."""
        try:
            # Get model prediction
            prediction = extract_structured_info(
                text_or_soup=test_case.text,
                provider=self.model_provider,
                model=self.model_name,
                api_key=self.model_api_key
            )
            
            # Calculate basic metrics
            fraud_correct = prediction.get('fraud_flag', False) == test_case.expected_fraud_flag
            ml_correct = prediction.get('money_laundering_flag', False) == test_case.expected_money_laundering_flag
            
            type_correct = True
            if test_case.expected_fraud_flag:
                predicted_type = prediction.get('fraud_type')
                type_correct = predicted_type == test_case.expected_fraud_type
            
            result = {
                'test_case': test_case,
                'prediction': prediction,
                'fraud_flag_correct': fraud_correct,
                'money_laundering_correct': ml_correct,
                'fraud_type_correct': type_correct,
                'overall_correct': fraud_correct and ml_correct and type_correct
            }
            
            # Add LLM judge evaluation if enabled
            if self.use_llm_judge:
                judgment = self.llm_judge.judge_fraud_classification(
                    test_case.text, prediction, test_case
                )
                result['llm_judgment'] = judgment
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating case: {e}")
            return {
                'test_case': test_case,
                'prediction': {},
                'fraud_flag_correct': False,
                'money_laundering_correct': False,
                'fraud_type_correct': False,
                'overall_correct': False,
                'error': str(e)
            }
    
    def evaluate_dataset(self, test_cases: Optional[List[TestCase]] = None, 
                        enable_langfuse_tracing: bool = True) -> EvaluationResult:
        """Evaluate the model on a dataset of test cases."""
        if test_cases is None:
            test_cases = self.create_test_dataset()
        
        results = []
        for i, test_case in enumerate(test_cases):
            logger.info(f"Evaluating case {i+1}/{len(test_cases)}: {test_case.title}")
            result = self.evaluate_single_case(test_case)
            results.append(result)
        
        # Calculate overall metrics
        fraud_predictions = [r['prediction'].get('fraud_flag', False) for r in results]
        fraud_ground_truth = [r['test_case'].expected_fraud_flag for r in results]
        
        if SKLEARN_AVAILABLE:
            accuracy = accuracy_score(fraud_ground_truth, fraud_predictions)
            precision = precision_score(fraud_ground_truth, fraud_predictions, zero_division=0)
            recall = recall_score(fraud_ground_truth, fraud_predictions, zero_division=0)
            f1 = f1_score(fraud_ground_truth, fraud_predictions, zero_division=0)
            cm = confusion_matrix(fraud_ground_truth, fraud_predictions).tolist()
        else:
            # Manual calculation if sklearn not available
            accuracy = sum(p == gt for p, gt in zip(fraud_predictions, fraud_ground_truth)) / len(fraud_predictions)
            precision = recall = f1 = 0.0
            cm = [[0, 0], [0, 0]]
        
        # Calculate RAGAS scores if available
        ragas_scores = None
        if RAGAS_AVAILABLE and len(results) > 0:
            try:
                ragas_scores = self._calculate_ragas_scores(results)
            except Exception as e:
                logger.warning(f"RAGAS evaluation failed: {e}")
        
        evaluation_result = EvaluationResult(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            confusion_matrix=cm,
            detailed_results=results,
            ragas_scores=ragas_scores
        )
        
        # Trace to Langfuse if enabled
        if enable_langfuse_tracing:
            try:
                trace_id = trace_evaluation(
                    evaluation_result=evaluation_result,
                    model_name=self.model_name,
                    model_provider=self.model_provider,
                    test_cases=test_cases,
                    metadata={
                        "evaluation_type": "synthetic_dataset",
                        "total_cases": len(test_cases),
                        "use_llm_judge": self.use_llm_judge
                    }
                )
                if trace_id:
                    logger.info(f"Evaluation traced to Langfuse with ID: {trace_id}")
            except Exception as e:
                logger.warning(f"Langfuse tracing failed: {e}")
        
        return evaluation_result
    
    def evaluate_real_output(self, 
                           scraper,
                           max_cases: int = 10,
                           api_key: Optional[str] = None,
                           enable_langfuse_tracing: bool = True) -> EvaluationResult:
        """
        Evaluate the model on real DOJ press release output.
        
        Args:
            scraper: DOJScraper instance
            max_cases: Maximum number of cases to evaluate
            api_key: API key for LLM evaluation
            enable_langfuse_tracing: Whether to trace results to Langfuse
            
        Returns:
            EvaluationResult with real data performance metrics
        """
        # Create test dataset from real data
        test_cases = self.create_test_dataset_from_real_data(
            scraper=scraper,
            max_cases=max_cases,
            api_key=api_key
        )
        
        if not test_cases:
            logger.warning("No real test cases could be created")
            return EvaluationResult(
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                confusion_matrix=[[0, 0], [0, 0]],
                detailed_results=[],
                ragas_scores=None
            )
        
        # Evaluate on real data with Langfuse tracing
        return self.evaluate_dataset(test_cases, enable_langfuse_tracing=enable_langfuse_tracing)

    def _calculate_ragas_scores(self, results: List[Dict]) -> Dict:
        """Calculate RAGAS scores for the evaluation results."""
        try:
            # Prepare data for RAGAS
            eval_data = []
            for result in results:
                if 'error' not in result:
                    eval_data.append({
                        'question': f"Is this a fraud case: {result['test_case'].text[:200]}...",
                        'answer': json.dumps(result['prediction']),
                        'contexts': [result['test_case'].text],
                        'ground_truth': json.dumps({
                            'fraud_flag': result['test_case'].expected_fraud_flag,
                            'fraud_type': result['test_case'].expected_fraud_type,
                            'money_laundering_flag': result['test_case'].expected_money_laundering_flag
                        })
                    })
            
            if not eval_data:
                return None
            
            dataset = Dataset.from_list(eval_data)
            
            # Use available RAGAS metrics
            metrics = [answer_correctness]  # Most relevant for our use case
            
            ragas_result = evaluate(dataset, metrics=metrics)
            return ragas_result
            
        except Exception as e:
            logger.error(f"RAGAS calculation failed: {e}")
            return None
    
    def generate_report(self, evaluation_result: EvaluationResult) -> str:
        """Generate a comprehensive evaluation report."""
        report = f"""
# Fraud Detection Model Evaluation Report

**Timestamp:** {evaluation_result.timestamp}
**Model:** {self.model_name} ({self.model_provider})

## Overall Performance Metrics

- **Accuracy:** {evaluation_result.accuracy:.3f}
- **Precision:** {evaluation_result.precision:.3f}
- **Recall:** {evaluation_result.recall:.3f}
- **F1 Score:** {evaluation_result.f1_score:.3f}

## Confusion Matrix
```
                 Predicted
                 No    Yes
Actual    No    {evaluation_result.confusion_matrix[0][0]}     {evaluation_result.confusion_matrix[0][1]}
          Yes   {evaluation_result.confusion_matrix[1][0]}     {evaluation_result.confusion_matrix[1][1]}
```

## Detailed Results

"""
        
        # Add detailed case analysis
        for i, result in enumerate(evaluation_result.detailed_results):
            test_case = result['test_case']
            prediction = result.get('prediction', {})
            
            report += f"### Case {i+1}: {test_case.title}\n"
            report += f"- **Text:** {test_case.text[:100]}...\n"
            report += f"- **Expected Fraud:** {test_case.expected_fraud_flag}\n"
            report += f"- **Predicted Fraud:** {prediction.get('fraud_flag', 'N/A')}\n"
            report += f"- **Correct:** {'✓' if result.get('fraud_flag_correct', False) else '✗'}\n"
            
            if self.use_llm_judge and 'llm_judgment' in result:
                judgment = result['llm_judgment']
                report += f"- **LLM Judge Score:** {judgment.get('overall_quality', 'N/A')}/10\n"
                report += f"- **Judge Feedback:** {judgment.get('judgment_explanation', 'N/A')}\n"
            
            report += "\n"
        
        # Add RAGAS scores if available
        if evaluation_result.ragas_scores:
            report += "## RAGAS Evaluation Scores\n"
            for metric, score in evaluation_result.ragas_scores.items():
                report += f"- **{metric}:** {score:.3f}\n"
            report += "\n"
        
        # Add recommendations
        report += "## Recommendations\n"
        if evaluation_result.accuracy < 0.8:
            report += "- Consider improving training data quality\n"
            report += "- Review false positive cases for pattern analysis\n"
        if evaluation_result.precision < evaluation_result.recall:
            report += "- Focus on reducing false positives\n"
        elif evaluation_result.recall < evaluation_result.precision:
            report += "- Focus on reducing false negatives\n"
        
        return report
    
    def save_results(self, evaluation_result: EvaluationResult, filepath: str):
        """Save evaluation results to file."""
        # Convert results to serializable format
        serializable_results = {
            'accuracy': evaluation_result.accuracy,
            'precision': evaluation_result.precision,
            'recall': evaluation_result.recall,
            'f1_score': evaluation_result.f1_score,
            'confusion_matrix': evaluation_result.confusion_matrix,
            'timestamp': evaluation_result.timestamp,
            'ragas_scores': evaluation_result.ragas_scores,
            'detailed_results': []
        }
        
        # Process detailed results
        for result in evaluation_result.detailed_results:
            serializable_result = {
                'test_case': {
                    'text': result['test_case'].text,
                    'expected_fraud_flag': result['test_case'].expected_fraud_flag,
                    'expected_fraud_type': result['test_case'].expected_fraud_type,
                    'title': result['test_case'].title
                },
                'prediction': result.get('prediction', {}),
                'metrics': {
                    'fraud_flag_correct': result.get('fraud_flag_correct', False),
                    'money_laundering_correct': result.get('money_laundering_correct', False),
                    'fraud_type_correct': result.get('fraud_type_correct', False),
                    'overall_correct': result.get('overall_correct', False)
                }
            }
            
            if 'llm_judgment' in result:
                serializable_result['llm_judgment'] = result['llm_judgment']
            
            serializable_results['detailed_results'].append(serializable_result)
        
        with open(filepath, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"Evaluation results saved to {filepath}")


def quick_eval(model_provider: str = "openai", 
              model_name: str = "gpt-4o",
              api_key: Optional[str] = None,
              use_llm_judge: bool = True,
              enable_langfuse_tracing: bool = True) -> EvaluationResult:
    """Quick evaluation function for testing accuracy."""
    evaluator = FraudDetectionEvaluator(
        model_provider=model_provider,
        model_name=model_name,
        model_api_key=api_key,
        use_llm_judge=use_llm_judge
    )
    
    return evaluator.evaluate_dataset(enable_langfuse_tracing=enable_langfuse_tracing)


def quick_eval_real_data(model_provider: str = "openai",
                        model_name: str = "gpt-4o", 
                        api_key: Optional[str] = None,
                        use_llm_judge: bool = True,
                        max_cases: int = 10,
                        enable_langfuse_tracing: bool = True) -> EvaluationResult:
    """Quick evaluation function using real DOJ press release data."""
    from ..scraping.scraper import DOJScraper
    from ..core.models import ScrapingConfig
    
    # Configure scraper
    config = ScrapingConfig(
        max_pages=2,
        max_cases=max_cases,
        delay_between_requests=1.0
    )
    
    scraper = DOJScraper(config)
    evaluator = FraudDetectionEvaluator(
        model_provider=model_provider,
        model_name=model_name,
        model_api_key=api_key,
        use_llm_judge=use_llm_judge
    )
    
    return evaluator.evaluate_real_output(scraper, max_cases, api_key, enable_langfuse_tracing)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 80)
    print("SYNTHETIC TEST DATASET EVALUATION")
    print("=" * 80)
    
    # Check if Langfuse is available
    langfuse_available = get_langfuse_tracer() is not None
    print(f"Langfuse tracing: {'Enabled' if langfuse_available else 'Disabled'}")
    
    result = quick_eval(enable_langfuse_tracing=langfuse_available)
    
    evaluator = FraudDetectionEvaluator()
    report = evaluator.generate_report(result)
    print(report)
    
    # Save synthetic results
    evaluator.save_results(result, "evaluation_results_synthetic.json")
    
    print("\n" + "=" * 80)
    print("REAL DOJ PRESS RELEASE EVALUATION")
    print("=" * 80)
    
    # Uncomment to run real data evaluation (requires API key)
    # try:
    #     real_result = quick_eval_real_data(max_cases=5, enable_langfuse_tracing=langfuse_available)
    #     real_report = evaluator.generate_report(real_result)
    #     print(real_report)
    #     evaluator.save_results(real_result, "evaluation_results_real.json")
    # except Exception as e:
    #     print(f"Real data evaluation failed: {e}")
    #     print("Make sure OPENAI_API_KEY is set for real data evaluation")
    
    # Close Langfuse tracer if available
    tracer = get_langfuse_tracer()
    if tracer:
        tracer.close()