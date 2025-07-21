# Langfuse Integration for DOJ Research Agent

This document explains how to use Langfuse tracing and scoring with the DOJ Research Agent evaluation system.

## Overview

The Langfuse integration provides:
- **Automatic tracing** of evaluation runs
- **Score tracking** for fraud detection metrics
- **Performance monitoring** across different models
- **Detailed analytics** in the Langfuse dashboard

## Setup

### 1. Install Dependencies

```bash
# Install Langfuse and python-dotenv
poetry add langfuse python-dotenv
```

### 2. Configure Environment Variables

Create a `.env` file in your project root:

```env
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Evaluation Configuration
ENABLE_LANGFUSE_TRACING=true
EVALUATION_MAX_CASES=10
EVALUATION_USE_LLM_JUDGE=true
```

### 3. Get Langfuse Credentials

1. Sign up at [Langfuse Cloud](https://cloud.langfuse.com)
2. Create a new project
3. Copy your public and secret keys from the project settings

## Usage

### Basic Evaluation with Tracing

```python
from doj_research_agent.evaluate import quick_eval

# Run evaluation with automatic Langfuse tracing
result = quick_eval(
    model_provider="openai",
    model_name="gpt-4o",
    api_key="your_openai_key",
    enable_langfuse_tracing=True
)

print(f"Accuracy: {result.accuracy:.3f}")
```

### Real Data Evaluation

```python
from doj_research_agent.evaluate import quick_eval_real_data

# Evaluate on real DOJ press releases
result = quick_eval_real_data(
    max_cases=10,
    enable_langfuse_tracing=True
)
```

### Custom Evaluator with Tracing

```python
from doj_research_agent.evaluate import FraudDetectionEvaluator

evaluator = FraudDetectionEvaluator(
    model_provider="openai",
    model_name="gpt-4o",
    use_llm_judge=True
)

# Run evaluation with tracing
result = evaluator.evaluate_dataset(enable_langfuse_tracing=True)
```

## What Gets Traced

### Overall Metrics
- **fraud_detection_accuracy**: Overall accuracy score
- **fraud_detection_precision**: Precision score
- **fraud_detection_recall**: Recall score
- **fraud_detection_f1**: F1 score
- **fraud_detection_overall_quality**: Average of all metrics

### Per-Case Metrics
- **case_{n}_accuracy**: Individual case accuracy
- **case_{n}_fraud_flag_accuracy**: Fraud flag accuracy per case
- **case_{n}_money_laundering_accuracy**: Money laundering accuracy per case
- **case_{n}_llm_judge_{metric}**: LLM judge scores (if enabled)

### RAGAS Metrics
- **ragas_{metric}**: RAGAS evaluation scores (if available)

## Dashboard Features

### Traces
Each evaluation run creates a trace with:
- Model information (name, provider)
- Evaluation timestamp
- Number of test cases
- Evaluation type (synthetic/real data)
- Custom metadata

### Scores
Individual scores are tracked for:
- Overall performance metrics
- Per-case accuracy
- LLM judge assessments
- RAGAS evaluation scores

### Analytics
Use Langfuse dashboard to:
- Compare model performance over time
- Analyze individual case failures
- Track improvement trends
- Set up alerts for performance degradation

## Testing the Integration

Run the test script to verify everything works:

```bash
python test_langfuse_integration.py
```

This will:
1. Test Langfuse initialization
2. Run a sample evaluation
3. Verify traces are created
4. Show test results

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LANGFUSE_PUBLIC_KEY` | Your Langfuse public key | Required |
| `LANGFUSE_SECRET_KEY` | Your Langfuse secret key | Required |
| `LANGFUSE_HOST` | Langfuse host URL | `https://cloud.langfuse.com` |
| `ENABLE_LANGFUSE_TRACING` | Enable/disable tracing | `true` |
| `EVALUATION_MAX_CASES` | Max cases for real data eval | `10` |
| `EVALUATION_USE_LLM_JUDGE` | Enable LLM judge | `true` |

### Programmatic Configuration

```python
from doj_research_agent.langfuse_integration import LangfuseTracer

# Custom tracer configuration
tracer = LangfuseTracer(
    public_key="your_key",
    secret_key="your_secret",
    host="https://cloud.langfuse.com",
    enabled=True
)
```

## Troubleshooting

### Common Issues

1. **"Langfuse credentials not found"**
   - Check your `.env` file exists
   - Verify `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set
   - Ensure `python-dotenv` is installed

2. **"Failed to initialize Langfuse client"**
   - Check your credentials are correct
   - Verify network connectivity to Langfuse
   - Check Langfuse project is active

3. **"Tracing disabled"**
   - Set `ENABLE_LANGFUSE_TRACING=true` in `.env`
   - Check `langfuse` package is installed

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Use Environment Variables**: Never hardcode credentials
2. **Test Regularly**: Run the test script before production use
3. **Monitor Performance**: Set up alerts in Langfuse dashboard
4. **Clean Up**: Always close the tracer when done
5. **Version Control**: Add `.env` to `.gitignore`

## Example Workflow

```python
# 1. Set up environment
import os
from dotenv import load_dotenv
load_dotenv()

# 2. Run evaluation with tracing
from doj_research_agent.evaluate import quick_eval

result = quick_eval(
    model_provider="openai",
    model_name="gpt-4o",
    enable_langfuse_tracing=True
)

# 3. Check results
print(f"Evaluation completed with {result.accuracy:.3f} accuracy")

# 4. View in Langfuse dashboard
print("Check https://cloud.langfuse.com for detailed traces")
```

## Support

For issues with:
- **Langfuse Integration**: Check this README and test script
- **Langfuse Platform**: Visit [Langfuse Documentation](https://langfuse.com/docs)
- **DOJ Research Agent**: Check the main project README 