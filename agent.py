# ============================================================
# Agent Module -- Research Paper Pipeline Agent
# Connects Streamlit dashboard to FF260205 pipeline logic
# ============================================================
"""
Provides a simple interface for the Streamlit dashboard to interact with
the Research Paper Pipeline (FF260205).

Functions:
    process(topic, paper_count, time_range, output_dir) -> dict
        Runs the full pipeline and returns structured results.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add FF260205 submit path to sys.path so we can import its modules
# __file__ = 05/submit/agent.py
#   .parent        = 05/submit/
#   .parent.parent = 05/              ← wrong (leads to 05/FF260205/)
#   .parent.parent.parent = workspace root/ ← correct (leads to workspace/FF260205/)
FF260205_SUBMIT = Path(__file__).resolve().parent.parent.parent / "FF260205" / "submit"
sys.path.insert(0, str(FF260205_SUBMIT))

from crews import (
    create_paper_fetch_crew,
    create_wordcloud_crew,
    create_summary_crew,
    create_citation_graph_crew,
    run_paper_fetch_sync,
    run_wordcloud_sync,
    run_summary_sync,
    run_citation_graph_sync,
    fetch_papers,
    extract_keywords_from_papers,
    keyword_frequency,
    ensure_output_dir,
)
from utils import load_env

load_env()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

MAX_RETRIES = 3


# ============================================================
# JSON Parsing Helper
# ============================================================

def _parse_json_from_output(raw_output: str) -> list[dict] | None:
    """Try to extract JSON list from agent raw output string."""
    text = raw_output.strip()
    # Find the first '[' and last ']'
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None


# ============================================================
# Stage Functions (mirrors pipeline.py logic)
# ============================================================

def _fetch_papers(
    research_topic: str,
    paper_count: int,
    time_range: Optional[dict[str, str]] = None,
) -> list[dict]:
    """Fetch paper metadata with retry and fallback."""
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            # Try Crew Agent first
            crew = create_paper_fetch_crew(
                research_topic=research_topic,
                paper_count=paper_count,
                time_range=time_range,
            )
            result = crew.kickoff(inputs={
                "research_topic": research_topic,
                "paper_count": str(paper_count),
            })
            raw_output = str(result)
            papers = _parse_json_from_output(raw_output)
            if papers:
                return papers
        except Exception as e:
            logger.warning(f"Crew1 failed (attempt {attempt + 1}): {e}")

        # Fallback to direct API
        try:
            return run_paper_fetch_sync(
                research_topic=research_topic,
                paper_count=paper_count,
                time_range=time_range,
            )
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                delay = 2 ** attempt
                logger.warning(f"Direct API failed, retrying in {delay}s: {e}")
                time.sleep(delay)

    raise RuntimeError(f"Paper fetch failed after {MAX_RETRIES} retries: {last_error}")


def _generate_wordcloud(papers: list[dict], output_path: str) -> str:
    """Generate word cloud image with retry."""
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            keywords = extract_keywords_from_papers(papers)
            freq = keyword_frequency(keywords)
            if not freq:
                raise ValueError("No keywords available for word cloud")
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            wc = WordCloud(
                width=1200, height=600,
                background_color="white",
                colormap="viridis",
                max_words=100,
            )
            wc.generate_from_frequencies(freq)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            fig.savefig(output_path, bbox_inches="tight", dpi=150)
            plt.close(fig)
            return output_path
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                delay = 2 ** attempt
                logger.warning(f"WordCloud failed (attempt {attempt + 1}): {e}, retrying in {delay}s")
                time.sleep(delay)
    raise RuntimeError(f"WordCloud generation failed: {last_error}")


def _generate_summaries(
    papers: list[dict],
    output_dir: str,
    research_topic: str,
) -> dict[str, str]:
    """Generate paper summaries with retry."""
    summaries_json_path = os.path.join(output_dir, "summaries.json")
    report_md_path = os.path.join(output_dir, "report.md")
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            result = run_summary_sync(
                papers=papers,
                summaries_json_path=summaries_json_path,
                report_md_path=report_md_path,
                research_topic=research_topic,
            )
            return result
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                delay = 2 ** attempt
                logger.warning(f"Summary generation failed (attempt {attempt + 1}): {e}, retrying in {delay}s")
                time.sleep(delay)
    raise RuntimeError(f"Summary generation failed: {last_error}")


def _generate_citation_graph(
    papers: list[dict],
    output_path: str,
    research_topic: str,
) -> str:
    """Generate citation graph with retry."""
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return run_citation_graph_sync(
                papers=papers,
                output_path=output_path,
                research_topic=research_topic,
            )
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                delay = 2 ** attempt
                logger.warning(f"Citation graph failed (attempt {attempt + 1}): {e}, retrying in {delay}s")
                time.sleep(delay)
    raise RuntimeError(f"Citation graph generation failed: {last_error}")


# ============================================================
# Main Process Function
# ============================================================

def process(
    topic: str,
    paper_count: int = 10,
    time_range: Optional[dict[str, str]] = None,
    output_dir: str = "./output",
    callback=None,
) -> dict[str, Any]:
    """
    Run the full Research Paper Pipeline.

    Args:
        topic: Research topic to search for papers.
        paper_count: Number of papers to fetch (default 10).
        time_range: Optional dict with "from" and "to" date strings.
        output_dir: Base output directory.
        callback: Optional callable(stage_name, status) for progress updates.

    Returns:
        dict with keys:
            success: bool
            error: str (if failed)
            topic: str
            paper_count: int
            stages: dict with per-stage results (papers, wordcloud_path, summaries_path, report_path, citation_graph_path)
    """
    config = {
        "research_topic": topic,
        "paper_count": paper_count,
        "time_range": time_range,
    }

    topic_safe = topic.replace(" ", "_").replace("/", "_")[:50]
    topic_output_dir = ensure_output_dir(output_dir, topic)

    stages = {}
    stage_order = [
        ("stage_1_meta", "Paper Metadata Fetching"),
        ("stage_2_wordcloud", "Keyword Word Cloud Generation"),
        ("stage_3_summary", "Paper Summary Generation"),
        ("stage_4_citation_graph", "Citation Relationship Visualization"),
    ]

    def notify(stage_label: str, status: str):
        msg = f"{stage_label}: {status}"
        logger.info(msg)
        if callback:
            callback(stage_label, status)

    # Stage 1: Fetch papers
    try:
        notify("Paper Metadata Fetching", "started")
        papers = _fetch_papers(
            research_topic=config["research_topic"],
            paper_count=config["paper_count"],
            time_range=config.get("time_range"),
        )
        # Sort and limit
        papers = sorted(papers, key=lambda x: x.get("citation_count", 0), reverse=True)
        papers = papers[: config["paper_count"]]
        papers_meta_path = os.path.join(topic_output_dir, "papers_meta.json")
        with open(papers_meta_path, "w", encoding="utf-8") as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        stages["stage_1_meta"] = {
            "papers": papers,
            "papers_meta_path": papers_meta_path,
            "success": True,
        }
        notify("Paper Metadata Fetching", "completed")
    except Exception as e:
        logger.error(f"Stage 1 failed: {e}")
        return {"success": False, "error": f"Paper fetch failed: {e}", "topic": topic, "stages": {}}

    # Stage 2: Word cloud
    try:
        notify("Keyword Word Cloud Generation", "started")
        wordcloud_path = os.path.join(topic_output_dir, "wordcloud.png")
        _generate_wordcloud(papers, wordcloud_path)
        stages["stage_2_wordcloud"] = {
            "path": wordcloud_path,
            "success": True,
        }
        notify("Keyword Word Cloud Generation", "completed")
    except Exception as e:
        logger.error(f"Stage 2 failed: {e}")
        return {"success": False, "error": f"WordCloud failed: {e}", "topic": topic, "stages": stages}

    # Stage 3: Summaries
    try:
        notify("Paper Summary Generation", "started")
        summary_result = _generate_summaries(papers, topic_output_dir, topic)
        stages["stage_3_summary"] = {
            "summaries_json": summary_result.get("summaries_json_path"),
            "report_md": summary_result.get("report_md_path"),
            "success": True,
        }
        notify("Paper Summary Generation", "completed")
    except Exception as e:
        logger.error(f"Stage 3 failed: {e}")
        return {"success": False, "error": f"Summary failed: {e}", "topic": topic, "stages": stages}

    # Stage 4: Citation graph
    try:
        notify("Citation Relationship Visualization", "started")
        citation_graph_path = os.path.join(topic_output_dir, "citation_graph.png")
        _generate_citation_graph(papers, citation_graph_path, topic)
        stages["stage_4_citation_graph"] = {
            "path": citation_graph_path,
            "success": True,
        }
        notify("Citation Relationship Visualization", "completed")
    except Exception as e:
        logger.error(f"Stage 4 failed: {e}")
        return {"success": False, "error": f"Citation graph failed: {e}", "topic": topic, "stages": stages}

    return {
        "success": True,
        "topic": topic,
        "paper_count": paper_count,
        "output_dir": topic_output_dir,
        "stages": stages,
    }
