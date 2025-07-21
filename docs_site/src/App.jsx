import React, { useState } from 'react';
import './App.css';

const DOCS = [
  { id: 'overview', label: 'Overview' },
  { id: 'quickstart', label: 'Quickstart' },
  { id: 'api', label: 'API Reference' },
  { id: 'feedback', label: 'Feedback System' },
  { id: 'architecture', label: 'Architecture' },
];

const GITHUB_URL = 'https://github.com/your-org/your-repo'; // TODO: update with real repo
const LANGFUSE_URL = 'https://us.cloud.langfuse.com/project/cmdckuujh0bvnad07ptolsqrb/scores';

function App() {
  const [section, setSection] = useState('overview');

  return (
    <div className="docs-root">
      <aside className="sidebar">
        <h1 className="logo">DOJ Research Agent</h1>
        <nav>
          <ul>
            {DOCS.map(doc => (
              <li key={doc.id}>
                <button
                  className={section === doc.id ? 'active' : ''}
                  onClick={() => setSection(doc.id)}
                >
                  {doc.label}
                </button>
              </li>
            ))}
          </ul>
        </nav>
        <div className="sidebar-links">
          <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">GitHub</a>
          <a href={LANGFUSE_URL} target="_blank" rel="noopener noreferrer">Langfuse Portal</a>
        </div>
      </aside>
      <main className="content">
        {section === 'overview' && <Overview />}
        {section === 'quickstart' && <Quickstart />}
        {section === 'api' && <APIReference />}
        {section === 'feedback' && <FeedbackSystem />}
        {section === 'architecture' && <Architecture />}
      </main>
    </div>
  );
}

function Overview() {
  return (
    <section>
      <h2>Overview</h2>
      <p>
        <b>DOJ Research Agent</b> is an AI-powered system for analyzing DOJ press releases, detecting fraud, and enabling human-in-the-loop feedback for continuous model improvement.
      </p>
      <ul>
        <li>Automated scraping and analysis of DOJ press releases</li>
        <li>LLM-based fraud detection and evaluation</li>
        <li>Human feedback loop for model improvement</li>
        <li>React dashboard for explainable results</li>
        <li>Langfuse integration for tracing and monitoring</li>
      </ul>
    </section>
  );
}

function Quickstart() {
  return (
    <section>
      <h2>Quickstart</h2>
      <ol>
        <li>Clone the repository from <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">GitHub</a>.</li>
        <li>Follow the README for backend and frontend setup.</li>
        <li>Run <code>docker-compose up</code> to start all services.</li>
        <li>Access the dashboard at <code>http://localhost:3000</code>.</li>
        <li>See the <b>Langfuse Portal</b> for evaluation traces.</li>
      </ol>
    </section>
  );
}

function APIReference() {
  return (
    <section>
      <h2>API Reference</h2>
      <ul>
        <li><b>POST /analyze/</b> — Start a new analysis job</li>
        <li><b>GET /job/&lt;job_id&gt;</b> — Get job status/results</li>
        <li><b>POST /feedback/</b> — Submit feedback for a case</li>
        <li><b>GET /feedback/stats</b> — Get feedback statistics</li>
        <li><b>GET /feedback/improvements</b> — Get model improvement insights</li>
      </ul>
      <p>See the backend <code>main.py</code> for full details.</p>
    </section>
  );
}

function FeedbackSystem() {
  return (
    <section>
      <h2>Feedback System</h2>
      <p>
        Users can provide thumbs up/down and comments on each analyzed case. Feedback is used to improve model accuracy and is available for export as training data.
      </p>
      <ul>
        <li>Feedback is stored and processed by the backend</li>
        <li>Model thresholds are automatically adjusted based on feedback</li>
        <li>Feedback statistics and export available via API</li>
      </ul>
    </section>
  );
}

function Architecture() {
  return (
    <section>
      <h2>Architecture</h2>
      <p>See the <b>PROJECT_PLAN.md</b> for the latest Mermaid diagram.</p>
      <pre style={{background:'#f8f8f8', padding:'1em', overflowX:'auto'}}>
{`
React Dashboard → FastAPI Backend → LangGraph Orchestrator
    ├─ Scrape & Analyze
    ├─ Evaluate Results
    ├─ Human Feedback Loop
    └─ Model Improvement
`}
      </pre>
      <p>
        <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">View on GitHub</a>
      </p>
    </section>
  );
}

export default App; 