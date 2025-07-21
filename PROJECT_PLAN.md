## Project Plan 

I want to use the file to write my project plan to use llm to help achieve each feature 

- 1. add llm platform to manage workflow: done, use langchain
- 2. Build LLM Judge as eval layer to improve accuracy
    - create evaluate.py to use ragas for quick evals result for accuracy
- 3. Build langgraph for agent that make llm call and output result
    - evaluate result w score
    - push score to langfuse
- 4. add react dashboard -  done 
    - Make to more explainable w one sentence intro on Top
    - Add CVS download button on result to local computer
    - add filter for Money laundering flag
- 5. Create architecture diagram using excaldraw
- 6. Edge case handling 
   - 6.1: exclude video format () https://www.justice.gov/news/videos) - **COMPLETED**
     - Enhanced video URL filtering with comprehensive patterns
     - Added video content filtering from page content
     - Added configuration option to enable/disable video filtering
     - Filters video platforms, file extensions, and video-related paths
- 7. LangGraph: add human in the loop feedback to help agent improve accuracy - **COMPLETED**
   - 7.1: Added feedback management system with FeedbackManager
   - 7.2: Integrated feedback node into LangGraph workflow
   - 7.3: Created React UI components for thumbs up/down feedback
   - 7.4: Added feedback statistics dashboard
   - 7.5: Implemented training data export functionality
   - 7.6: **NEW**: Implemented FeedbackBasedImprover for model improvement
   - 7.7: **NEW**: Added automatic threshold adjustment based on feedback accuracy
   - 7.8: **NEW**: Created model improvement reports and API endpoints
- 8. Documentation
   - 8.1 add Langfuse portal(https://us.cloud.langfuse.com/project/cmdckuujh0bvnad07ptolsqrb/scores) in README.md - **COMPLETED**
     - Added Langfuse portal link to README.md
     - Updated architecture documentation with current system components
     - Added comprehensive features section highlighting all implemented functionality
     - Updated quickstart instructions for React dashboard and FastAPI backend
   - 8.2 create simple document UI website like (docs.lakekeeper.io) w link to github - **COMPLETED**
     - Created React-based documentation site using Vite
     - Added sidebar navigation with Overview, Quickstart, API Reference, Feedback System, and Architecture sections
     - Included prominent links to GitHub repository and Langfuse portal
     - Implemented responsive design with clean, modern styling
     - Added comprehensive documentation content for all major features
     - Site runs on http://localhost:5174/ during development

## Architecture Diagram (Mermaid)

```mermaid
graph TD
    A[React Dashboard] --> B[FastAPI Backend]
    B --> C[LangGraph Orchestrator]
    
    C --> D[Scrape & Analyze]
    D --> E[Evaluate Results]
    E --> F[Human Feedback Loop]
    F --> G[Model Improvement]
    
    D --> H[DOJ Scraper]
    D --> I[LLM Analysis]
    
    E --> J[LLM Judge]
    E --> K[RAGAS Metrics]
    
    F --> L[Feedback Manager]
    F --> M[Training Data]
    
    G --> N[Feedback Improver]
    G --> O[Threshold Adjustment]
    G --> P[Improvement Reports]
    
    A --> Q[Feedback Widget]
    Q --> B
    
    I --> R[OpenAI GPT-4o]
    J --> R
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style F fill:#e8f5e8
    style G fill:#fff8e1
    style L fill:#e8f5e8
    style N fill:#fff8e1
    style Q fill:#e8f5e8
```
    