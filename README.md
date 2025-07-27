<div align="center">

# DOJ Fraud Research Agent

[![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://doj-fraud-agent.netlify.app/) [![Langfuse](https://img.shields.io/badge/langfuse-portal-green)](https://us.cloud.langfuse.com/project/cmdckuujh0bvnad07ptolsqrb/scores) [![License](https://img.shields.io/github/license/Alicelibinguo5/doj-fraud-agent)](LICENSE)

</div>

A friendly, end-to-end tool for exploring and categorizing DOJ press releases, with a focus on fraud detection. Includes a React dashboard, FastAPI backend, and LangGraph orchestration for legal research and data analysis.

---

## Documentation
📖 **[Documentation](https://doj-fraud-agent.netlify.app/)** • 🐳 **Docker** • 📊 **Langfuse Portal**

---

## Why?
The Association of Certified Fraud Examiners is the largest fraud fighting organization on the planet. In addition to providing a world-renowned certification, the ACFE also produces various research studies to support fraud examiners globally. These studies have primairly been based on surveys and responses from ACFE membership.

This tool is an effort to expand the research capabilities of the ACFE by examining active U.S. Department of Justice (and, hopefully in the future, other jurisdictions) fraud and money laundering investigations, indictments, and recent convictions. The ability to rapidly analyze DOJ activity can help fraud examiners stay on top of new fraud trends and see what law enforcement is working on to better inform referrals and tips.

---

## How it Works

- **React Dashboard**: Modern, responsive web UI with real-time feedback
- **FastAPI Backend**: Handles scraping, analysis, and LLM-powered fraud detection
- **LangGraph Orchestration**: Intelligent workflow management with human-in-the-loop feedback
- **Langfuse Integration**: Comprehensive tracing and evaluation metrics
- **Docker Compose**: One command to run everything

## Quickstart

1. **Clone & Enter the Repo**
   ```bash
   git clone https://github.com/Alicelibinguo5/doj-fraud-agent.git
   cd doj-fraud-agent
   ```

2. **Run with Docker Compose**
   ```bash
   docker compose build
   docker compose up
   ```
   - React Dashboard: [http://localhost:3000](http://localhost:3000)
   - FastAPI Backend: [http://localhost:8000](http://localhost:8000)
   - Langfuse Portal: [https://us.cloud.langfuse.com/project/cmdckuujh0bvnad07ptolsqrb/scores](https://us.cloud.langfuse.com/project/cmdckuujh0bvnad07ptolsqrb/scores)

3. **(Optional) Local Development**
   ```bash
   # Backend
   cd backend
   python -m uvicorn main:app --reload --port 8000
   
   # Frontend
   cd frontend/react-dashboard
   npm install
   npm start
   ```

---
## Architecture

![Architecture](./images/arch.png)

### System Components

**Frontend Layer:**
- **React Dashboard**: Modern UI with real-time analysis, filtering, and feedback collection
- **Feedback Widget**: Thumbs up/down system for human-in-the-loop learning
- **Statistics Dashboard**: Performance metrics and training data export

**Backend Layer:**
- **FastAPI Server**: RESTful API for analysis requests and feedback processing
- **Redis Job Queue**: Asynchronous task management for long-running analyses
- **DOJ Scraper**: Intelligent web scraping with video content filtering

**AI/ML Layer:**
- **LangGraph Orchestrator**: Workflow management with nodes for fetching, analyzing, evaluating, and processing feedback
- **LLM Agent**: GPT-4o integration for fraud detection and case analysis
- **Evaluation Layer**: LLM-as-a-Judge with RAGAS framework for accuracy assessment

**Monitoring & Analytics:**
- **Langfuse Portal**: [https://us.cloud.langfuse.com/project/cmdckuujh0bvnad07ptolsqrb/scores](https://us.cloud.langfuse.com/project/cmdckuujh0bvnad07ptolsqrb/scores)
  - Real-time tracing of LLM calls and evaluation metrics
  - Performance monitoring and scoring dashboard
  - Training data insights and model improvement tracking

---
## Features

### 🔍 **Intelligent Analysis**
- Automated DOJ press release scraping with video content filtering
- LLM-powered fraud detection using GPT-4o
- Multi-category charge classification and analysis

### 📊 **Real-time Dashboard**
- Interactive React UI with filtering and sorting
- CSV export functionality
- Execution time tracking and performance metrics

### 🤖 **Human-in-the-Loop Learning**
- Thumbs up/down feedback system for model improvement
- Feedback statistics and training data export
- Continuous model evaluation and refinement

### 📈 **Monitoring & Evaluation**
- Langfuse integration for comprehensive tracing
- LLM-as-a-Judge evaluation framework
- RAGAS metrics for accuracy assessment

## Example Dashboard 
![Dashboard](./images/dashboard-main.png)

*See the [Documentation](https://doj-fraud-agent.netlify.app/) for detailed screenshots and usage examples.*

## Need Help?
- Check the React dashboard for interactive tips
- Monitor performance in the [Langfuse Portal](https://us.cloud.langfuse.com/project/cmdckuujh0bvnad07ptolsqrb/scores)
- Use `docker compose logs` for debugging
- Open an issue or PR—feedback welcome!

---

## License
MIT. See [LICENSE](LICENSE).
