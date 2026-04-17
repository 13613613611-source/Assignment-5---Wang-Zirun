# Research Paper Pipeline Dashboard

> Mini-Assignment 5 — Dashboard Development (5%)

---

## 1. System Overview

This dashboard provides a web interface for the **Research Paper Pipeline** (FF260205). Users enter a research topic, and the pipeline automatically:

1. **Fetches paper metadata** from Semantic Scholar / OpenAlex / CrossRef
2. **Generates a keyword word cloud** from paper metadata
3. **Creates paper summaries** and a comprehensive research report
4. **Visualizes citation relationships** in a network graph

All results are displayed interactively in the Streamlit dashboard.

---

## 2. How to Run

### Prerequisites

Install dependencies:

```bash
pip install -r requirements.txt
```

Set up your `.env` file in the project root (one level above `05/submit/`):

```env
OPENAI_API_KEY=your_openai_api_key_here
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key_here
OPENALEX_API_KEY=your_openalex_api_key_here
CROSSREF_API_KEY=your_crossref_api_key_here
```

### Launch the Dashboard

```bash
cd 05/submit
streamlit run app.py
```

---

## 3. Features Implemented

| Feature | Description |
|---------|-------------|
| **Sidebar Configuration** | Research topic input, paper count slider, time range filter, temperature slider |
| **Pipeline Execution** | Full 4-stage pipeline (meta → wordcloud → summaries → citation graph) |
| **Progress Feedback** | `st.spinner()` loading indicator during processing |
| **Word Cloud Display** | Renders generated word cloud image inline |
| **Summary Reports** | Displays both markdown report and per-paper summaries in expanders |
| **Citation Graph** | Renders citation network visualization inline |
| **Paper List** | Expandable list of all fetched papers with metadata (title, authors, year, venue, citations, abstract) |
| **Error Handling** | Graceful error messages on failure; individual stage errors don't crash the whole pipeline |
| **Input Validation** | Topic must be non-empty; year fields are validated |

---

## 4. Design Decisions

- **Synchronous execution**: Pipeline runs in a single `st.spinner()` block to keep the UI simple and avoid threading complexity. The 4-stage progress is logged in the agent module.
- **Result caching via `st.session_state`**: Results are stored in session state so they persist across widget interactions without re-running the pipeline.
- **Tabs for output separation**: Each output type (word cloud, summaries, citation graph, paper list) gets its own tab for a clean, organized layout.
- **Agent layer abstraction**: `agent.py` wraps FF260205's pipeline logic, providing a single `process(topic, paper_count, time_range)` entry point for the dashboard. This keeps `app.py` focused purely on UI.
- **No API key in code**: All keys loaded from `.env` via `python-dotenv`, following the作业要求.
