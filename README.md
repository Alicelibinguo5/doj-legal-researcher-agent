<div align="center">

# DOJ Legal Fraud Research Agent

[![License](https://img.shields.io/github/license/Alicelibinguo5/doj-case-research-agent)](LICENSE)

</div>

A friendly, end-to-end tool for exploring and categorizing DOJ press releases, with a focus on fraud detection. Includes a dashboard, API, and CLI for legal research and data analysis.

---

## Why?
Built to help my husband (a legal researcher) quickly find and analyze DOJ fraud cases. If you’re a legal pro, data nerd, or just curious, give it a try and let’s make legal research easier for everyone!

---

## How it Works

- **Streamlit Dashboard**: User-friendly web UI
- **FastAPI Backend**: Handles scraping, analysis, and GPT-4o fraud detection
- **Docker Compose**: One command to run everything

---

## Quickstart

1. **Clone & Enter the Repo**
   ```bash
   git clone https://github.com/Alicelibinguo5/doj-legal-research-agent.git
   cd doj-legal-research-agent
   ```
2. **Run with Docker Compose**
   ```bash
   docker compose build
   docker compose up
   ```
   - Dashboard: [http://localhost:8501](http://localhost:8501)
   - API: [http://localhost:8000](http://localhost:8000)

3. **(Optional) Local Dev**
   ```bash
   poetry install
   poetry shell
   streamlit run app/streamlit_agent.py
   ```

---

## Need Help?
- Check the dashboard for tips
- Use `docker compose logs` for debugging
- Open an issue or PR—feedback welcome!

---

## License
MIT. See [LICENSE](LICENSE).
