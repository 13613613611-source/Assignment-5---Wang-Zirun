# ============================================================
# Streamlit Dashboard -- Research Paper Pipeline Dashboard
# Mini-Assignment 5: Dashboard Development (5%)
# Style: Digital Archivist (DESIGN.md)
# ============================================================
"""
AI Agent Dashboard — "The Digital Archivist"
Research Paper Pipeline with premium editorial aesthetics.
"""

import json
import os
import sys
from pathlib import Path

import streamlit as st

from agent import process

# ============================================================
# Design Tokens (Digital Archivist)
# ============================================================

BACKGROUND   = "#fbf9f4"   # Ivory White — base surface
SURFACE_LOW  = "#f5f4ed"   # Slightly darker surface for sections
SURFACE_HIGH = "#efeee6"   # Cards / elevated containers
WHITE        = "#ffffff"   # Floating cards / modals
SURFACE_TOP  = "#e2e3d9"   # High-contrast callouts

ON_SURFACE      = "#31332c"   # Titles, primary text — not pure black
ON_SURFACE_VAR  = "#5e6058"  # Secondary text, labels
PRIMARY         = "#5f5e5e"   # Primary color
PRIMARY_DIM     = "#535252"   # Button gradient end
TERTIARY        = "#486272"   # Accent / tertiary emphasis
ERROR           = "#9f403d"   # Error state

RADIUS_LG = "0.75rem"   # Card corner radius
RADIUS_MD = "0.5rem"    # Input / button radius

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="The Digital Archivist",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# Global CSS Injection
# ============================================================

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..800;1,6..72,300..800&family=Manrope:wght@300;400;500;600;700&display=swap');

/* ---- Base Reset ---- */
.stApp, .stApp > header {{
    background-color: {BACKGROUND} !important;
}}

/* ---- Typography ---- */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Newsreader', Georgia, serif !important;
    color: {ON_SURFACE} !important;
    line-height: 1.3 !important;
    font-weight: 600 !important;
}}

.stApp {{
    font-family: 'Manrope', system-ui, sans-serif !important;
    color: {ON_SURFACE} !important;
    background-color: {BACKGROUND} !important;
}}

/* ---- Remove default borders & dividers ---- */
.stDivider, hr {{
    border: none !important;
    display: none !important;
}}

/* ---- Custom metric containers ---- */
.stMainBlockContainer {{
    padding-top: max(3.5rem, 5vh) !important;
    padding-bottom: 2rem !important;
}}

/* ---- Push content below Streamlit's native header ---- */
.stApp > header {{
    height: 3.5rem !important;
    min-height: 3.5rem !important;
}}

/* ---- Tabs ---- */
div[data-testid="stTabBar"] {{
    background: none !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 0 !important;
    background: {SURFACE_LOW} !important;
    border-radius: {RADIUS_LG} !important;
    padding: 4px !important;
    border: none !important;
}}

.stTabs [data-baseweb="tab"] {{
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: {ON_SURFACE_VAR} !important;
    background: transparent !important;
    border: none !important;
    border-radius: {RADIUS_MD} !important;
    padding: 10px 24px !important;
}}

.stTabs [aria-selected="true"] {{
    background: {WHITE} !important;
    color: {ON_SURFACE} !important;
    box-shadow: 0 4px 16px rgba(49,51,44,0.06) !important;
}}

.stTabs [data-baseweb="tab-panel"] {{
    padding: 2rem 0 0 0 !important;
    border: none !important;
}}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {{
    background-color: {SURFACE_LOW} !important;
    border-right: none !important;
}}

/* ---- Buttons ---- */
.stMainBlockContainer .stButton > button[kind="primary"] {{
    background: linear-gradient(145deg, {PRIMARY}, {PRIMARY_DIM}) !important;
    color: {WHITE} !important;
    border: none !important;
    border-radius: {RADIUS_MD} !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.75rem 1.5rem !important;
    width: 100% !important;
    box-shadow: 0 12px 32px rgba(49,51,44,0.08) !important;
    transition: all 0.2s ease !important;
}}

.stMainBlockContainer .stButton > button[kind="primary"]:hover {{
    box-shadow: 0 16px 40px rgba(49,51,44,0.12) !important;
    transform: translateY(-1px) !important;
}}

/* ---- Text inputs ---- */
.stMainBlockContainer .stTextInput > div > div {{
    background-color: {BACKGROUND} !important;
    border-radius: {RADIUS_MD} !important;
    border: 1px solid rgba(49,51,44,0.12) !important;
    padding: 2px 12px !important;
    transition: border-color 0.2s !important;
}}

.stMainBlockContainer .stTextInput input {{
    font-family: 'Manrope', sans-serif !important;
    color: {ON_SURFACE} !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}

.stMainBlockContainer .stTextInput > div > div:focus-within {{
    border-color: {TERTIARY} !important;
    background-color: {WHITE} !important;
}}

/* ---- Number input / text input (year fields) ---- */
.stMainBlockContainer .stNumberInput > div > div,
.stMainBlockContainer .stTextInput > div > div {{
    background-color: {BACKGROUND} !important;
}}

.stMainBlockContainer .stNumberInput input {{
    font-family: 'Manrope', sans-serif !important;
    color: {ON_SURFACE} !important;
}}

/* ---- Sliders ---- */
.stMainBlockContainer .stSlider > div > div > div {{
    background-color: {SURFACE_TOP} !important;
}}

.stMainBlockContainer .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {{
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important;
    color: {ON_SURFACE} !important;
}}

/* ---- Checkbox ---- */
.stMainBlockContainer .stCheckbox {{
    font-family: 'Manrope', sans-serif !important;
    color: {ON_SURFACE_VAR} !important;
}}

.stCheckbox > label > div[data-testid="stCheckboxDecoration"] {{
    background-color: {SURFACE_LOW} !important;
    border-radius: 4px !important;
    border-color: rgba(49,51,44,0.2) !important;
}}

/* ---- Expanders ---- */
.stMainBlockContainer .streamlit-expanderHeader {{
    background-color: {SURFACE_LOW} !important;
    border: none !important;
    border-radius: {RADIUS_LG} !important;
    font-family: 'Manrope', sans-serif !important;
    color: {ON_SURFACE} !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.5rem !important;
}}

.stMainBlockContainer .streamlit-expanderHeader:hover {{
    background-color: {SURFACE_HIGH} !important;
}}

.stMainBlockContainer .streamlit-expanderContent {{
    background-color: {WHITE} !important;
    border: none !important;
    border-radius: 0 0 {RADIUS_LG} {RADIUS_LG} !important;
    padding: 1.25rem !important;
}}

/* ---- Success / Error / Info banners ---- */
.stAlert {{
    border-radius: {RADIUS_LG} !important;
    border: none !important;
    font-family: 'Manrope', sans-serif !important;
}}

/* ---- Spinner ---- */
.stSpinner > div {{
    border-color: {TERTIARY} !important;
}}

/* ---- Custom Card ---- */
.arch-card {{
    background-color: {WHITE} !important;
    border-radius: {RADIUS_LG} !important;
    padding: 1.5rem 2rem !important;
    box-shadow: 0 12px 32px rgba(49,51,44,0.05) !important;
}}

/* ---- Surface card (slightly elevated) ---- */
.arch-card-surface {{
    background-color: {SURFACE_LOW} !important;
    border-radius: {RADIUS_LG} !important;
    padding: 1.5rem 2rem !important;
}}

/* ---- Page title (masthead style) ---- */
.masthead {{
    font-family: 'Newsreader', Georgia, serif !important;
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    color: {ON_SURFACE} !important;
    letter-spacing: -0.02em !important;
    line-height: 1.1 !important;
    margin-bottom: 0.25rem !important;
}}

.masthead-sub {{
    font-family: 'Manrope', system-ui, sans-serif !important;
    font-size: 0.95rem !important;
    color: {ON_SURFACE_VAR} !important;
    font-weight: 400 !important;
    line-height: 1.6 !important;
    margin-bottom: 2rem !important;
}}

/* ---- Section heading ---- */
.section-heading {{
    font-family: 'Newsreader', Georgia, serif !important;
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: {ON_SURFACE} !important;
    margin-bottom: 1rem !important;
    line-height: 1.3 !important;
}}

/* ---- Label ---- */
.arch-label {{
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: {ON_SURFACE_VAR} !important;
    margin-bottom: 0.5rem !important;
    display: block !important;
}}

/* ---- Chip / badge ---- */
.chip {{
    display: inline-block;
    background-color: {SURFACE_TOP} !important;
    color: {TERTIARY} !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    padding: 3px 10px !important;
    border-radius: 2rem !important;
}}

/* ---- Pipeline stage item ---- */
.pipeline-item {{
    background-color: {SURFACE_LOW} !important;
    border-radius: {RADIUS_MD} !important;
    padding: 0.85rem 1.25rem !important;
    margin-bottom: 0.5rem !important;
    font-family: 'Manrope', sans-serif !important;
    color: {ON_SURFACE_VAR} !important;
    font-size: 0.85rem !important;
}}

/* ---- Citation metric ---- */
.cite-metric {{
    background-color: {SURFACE_TOP} !important;
    border-radius: {RADIUS_MD} !important;
    padding: 0.5rem 0.75rem !important;
    display: inline-block !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.75rem !important;
    color: {ON_SURFACE_VAR} !important;
}}

/* ---- Hide scrollbar for cleaner look ---- */
.stApp {{
    scrollbar-width: none;
}}
.stApp::-webkit-scrollbar {{
    display: none;
}}

/* ---- Footer ---- */
.footer {{
    margin-top: 4rem !important;
    padding-top: 1.5rem !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.75rem !important;
    color: {ON_SURFACE_VAR} !important;
    opacity: 0.7 !important;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Session State
# ============================================================

def init_state():
    defaults = {
        "results": None,
        "running": False,
        "error": None,
        "history": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.markdown('<p class="arch-label">Configuration</p>', unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)

    # Topic
    st.markdown('<p class="arch-label">Research Topic</p>', unsafe_allow_html=True)
    topic = st.text_input(
        label="research_topic",
        value="large language model in healthcare",
        placeholder="e.g., reinforcement learning in robotics",
        label_visibility="collapsed",
    )

    # Paper count
    st.markdown('<p class="arch-label">Paper Count</p>', unsafe_allow_html=True)
    paper_count = st.slider(
        label="paper_count",
        min_value=3,
        max_value=50,
        value=10,
        step=1,
        label_visibility="collapsed",
    )

    # Time filter
    st.markdown('<p class="arch-label">Time Range</p>', unsafe_allow_html=True)
    enable_time_filter = st.checkbox("Enable time filter", value=False)
    col_y1, col_y2 = st.columns(2)
    with col_y1:
        year_from = st.text_input("From", value="2020", max_chars=4, label_visibility="collapsed")
    with col_y2:
        year_to = st.text_input("To", value="2025", max_chars=4, label_visibility="collapsed")

    # Temperature
    st.markdown('<p class="arch-label">Temperature</p>', unsafe_allow_html=True)
    temperature = st.slider(
        label="temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
        label_visibility="collapsed",
    )

    st.markdown("---", unsafe_allow_html=True)

    # Run button
    if st.button("Run Pipeline", use_container_width=True):
        if not topic.strip():
            st.error("Please enter a research topic.")
        else:
            st.session_state["running"] = True
            st.session_state["results"] = None
            st.session_state["error"] = None

            time_range = None
            if enable_time_filter:
                time_range = {"from": f"{year_from}-01-01", "to": f"{year_to}-12-31"}

            try:
                with st.spinner("Running pipeline\u2026"):
                    result = process(
                        topic=topic.strip(),
                        paper_count=paper_count,
                        time_range=time_range,
                        output_dir="./output",
                    )
                st.session_state["results"] = result
                st.session_state["history"].append({"topic": topic, "result": result})
            except Exception as e:
                st.session_state["error"] = str(e)
            finally:
                st.session_state["running"] = False
                st.rerun()

# ============================================================
# Main: Masthead
# ============================================================

st.markdown('<p class="masthead">The Digital Archivist</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="masthead-sub">'
    'A multi-stage AI pipeline for exploring academic literature &mdash; '
    'paper discovery, keyword visualization, summarization, and citation mapping.'
    '</p>',
    unsafe_allow_html=True,
)

# ============================================================
# Pipeline Stages Overview (always visible)
# ============================================================

st.markdown('<p class="section-heading">Pipeline Stages</p>', unsafe_allow_html=True)

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown(
        '<div class="pipeline-item">'
        '<span class="chip">01</span>&ensp;Paper Metadata<br>'
        '<span style="font-size:0.75rem;opacity:0.7">Semantic Scholar &rarr; OpenAlex &rarr; CrossRef</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with col_s2:
    st.markdown(
        '<div class="pipeline-item">'
        '<span class="chip">02</span>&ensp;Word Cloud<br>'
        '<span style="font-size:0.75rem;opacity:0.7">Keyword frequency visualization</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with col_s3:
    st.markdown(
        '<div class="pipeline-item">'
        '<span class="chip">03</span>&ensp;Summaries<br>'
        '<span style="font-size:0.75rem;opacity:0.7">Per-paper &amp; comprehensive reports</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with col_s4:
    st.markdown(
        '<div class="pipeline-item">'
        '<span class="chip">04</span>&ensp;Citation Graph<br>'
        '<span style="font-size:0.75rem;opacity:0.7">Citation relationship network</span>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)

# ============================================================
# Results
# ============================================================

if st.session_state["running"]:
    st.info("Pipeline is running\u2026 please wait.")

elif st.session_state["error"]:
    st.error(f"Pipeline failed: {st.session_state['error']}")

elif st.session_state["results"]:
    result = st.session_state["results"]

    if not result.get("success"):
        st.error(f"Pipeline failed: {result.get('error', 'Unknown error')}")

    else:
        # Summary metrics
        st.markdown('<p class="section-heading">Run Summary</p>', unsafe_allow_html=True)
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(
                f'<div class="arch-card">'
                f'<p class="arch-label">Topic</p>'
                f'<p style="font-family:\'Newsreader\',serif;font-size:1.1rem;font-weight:600;color:{ON_SURFACE}">'
                f'{result.get("topic", "N/A")}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col_m2:
            st.markdown(
                f'<div class="arch-card">'
                f'<p class="arch-label">Papers Found</p>'
                f'<p style="font-family:\'Newsreader\',serif;font-size:1.1rem;font-weight:600;color:{ON_SURFACE}">'
                f'{result.get("paper_count", 0)}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col_m3:
            stages = result.get("stages", {})
            completed = sum(1 for s in stages.values() if s.get("success"))
            total = len(stages)
            st.markdown(
                f'<div class="arch-card">'
                f'<p class="arch-label">Stages Completed</p>'
                f'<p style="font-family:\'Newsreader\',serif;font-size:1.1rem;font-weight:600;color:{ON_SURFACE}">'
                f'{completed} / {total}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.success("Pipeline completed successfully.")
        st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)

        # Tabs
        tab_wc, tab_sum, tab_cg, tab_pl = st.tabs([
            "Word Cloud",
            "Paper Summaries",
            "Citation Graph",
            "Paper List",
        ])

        # ---- Word Cloud Tab ----
        with tab_wc:
            wc_data = result["stages"].get("stage_2_wordcloud", {})
            if wc_data.get("success") and wc_data.get("path"):
                path = wc_data["path"]
                if os.path.exists(path):
                    st.markdown('<p class="arch-label">Keyword Frequency Map</p>', unsafe_allow_html=True)
                    st.image(path, use_container_width=True)
                else:
                    st.warning(f"Word cloud file not found.")
            else:
                st.info("Word cloud not generated.")

        # ---- Paper Summaries Tab ----
        with tab_sum:
            sum_data = result["stages"].get("stage_3_summary", {})
            if sum_data.get("success"):
                md_path = sum_data.get("report_md")
                json_path = sum_data.get("summaries_json")

                if md_path and os.path.exists(md_path):
                    with open(md_path, "r", encoding="utf-8") as f:
                        report_content = f.read()
                    st.markdown('<p class="section-heading">Comprehensive Research Report</p>', unsafe_allow_html=True)
                    st.markdown(report_content)
                    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)

                if json_path and os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        summaries = json.load(f)
                    st.markdown('<p class="section-heading">Individual Paper Summaries</p>', unsafe_allow_html=True)
                    for i, item in enumerate(summaries, 1):
                        title = item.get("title", "Unknown")
                        summary_text = item.get("summary", "")
                        with st.expander(f"Paper {i}: {title}"):
                            st.markdown(f"**{title}**")
                            st.markdown(summary_text)
            else:
                st.info("Summaries not generated.")

        # ---- Citation Graph Tab ----
        with tab_cg:
            cg_data = result["stages"].get("stage_4_citation_graph", {})
            if cg_data.get("success") and cg_data.get("path"):
                path = cg_data["path"]
                if os.path.exists(path):
                    st.markdown('<p class="arch-label">Citation Relationship Network</p>', unsafe_allow_html=True)
                    st.image(path, use_container_width=True)
                else:
                    st.warning(f"Citation graph file not found.")
            else:
                st.info("Citation graph not generated.")

        # ---- Paper List Tab ----
        with tab_pl:
            meta_data = result["stages"].get("stage_1_meta", {})
            if meta_data.get("success"):
                papers = meta_data.get("papers", [])
                for i, paper in enumerate(papers, 1):
                    title = paper.get("title", "N/A")
                    year = paper.get("year", "N/A")
                    citations = paper.get("citation_count", 0)
                    venue = paper.get("venue", "N/A")
                    abstract = paper.get("abstract", "")
                    authors = paper.get("authors", [])

                    with st.expander(f"#{i}  {title}"):
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(
                                f'<p style="font-size:0.8rem;color:{ON_SURFACE_VAR};margin-bottom:0.25rem">'
                                f'{year} &ensp;&middot;&ensp;{venue}</p>',
                                unsafe_allow_html=True,
                            )
                            if authors:
                                author_str = ", ".join(authors[:3])
                                if len(authors) > 3:
                                    author_str += " et al."
                                st.markdown(
                                    f'<p style="font-size:0.8rem;color:{ON_SURFACE_VAR};margin-bottom:0.25rem">'
                                    f'{author_str}</p>',
                                    unsafe_allow_html=True,
                                )
                            if abstract:
                                abstract_trunc = abstract[:500] if len(abstract) > 500 else abstract
                                st.markdown(
                                    f'<p style="font-size:0.85rem;line-height:1.6;color:{ON_SURFACE}">'
                                    f'{abstract_trunc}'
                                    f'\u2026</p>',
                                    unsafe_allow_html=True,
                                )
                        with col_b:
                            st.markdown(
                                f'<div style="text-align:right">'
                                f'<span class="chip" style="margin-bottom:0.5rem;display:block">Citations</span>'
                                f'<p style="font-family:\'Newsreader\',serif;font-size:1.6rem;font-weight:700;'
                                f'color:{ON_SURFACE};margin:0">{citations}</p>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
            else:
                st.info("Paper metadata not available.")

else:
    # ---- Empty State ----
    st.markdown('<p class="section-heading">Getting Started</p>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown(
            f'<div class="arch-card-surface">'
            f'<p class="arch-label">How It Works</p>'
            f'<p style="line-height:1.7;font-size:0.9rem;color:{ON_SURFACE_VAR}">'
            f'Configure your research topic in the <strong>sidebar</strong>, then click '
            f'<strong>Run Pipeline</strong>. The dashboard will:'
            f'</p>'
            f'<ol style="line-height:2;font-size:0.9rem;color:{ON_SURFACE_VAR};padding-left:1.25rem">'
            f'<li>Search academic databases for relevant papers</li>'
            f'<li>Generate a keyword word cloud from the results</li>'
            f'<li>Create per-paper summaries and a comprehensive report</li>'
            f'<li>Visualize citation relationships as a network graph</li>'
            f'</ol>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_right:
        st.markdown(
            f'<div class="arch-card-surface">'
            f'<p class="arch-label">Design Philosophy</p>'
            f'<p style="line-height:1.7;font-size:0.9rem;color:{ON_SURFACE_VAR}">'
            f'This dashboard embodies the <em>Digital Archivist</em> concept &mdash; '
            f'a premium, editorial interface inspired by high-end academic libraries. '
            f'Warm ivory tones, intentional asymmetry, and generous whitespace '
            f'create a focused, distraction-free research environment.'
            f'</p>'
            f'<p style="line-height:1.7;font-size:0.9rem;color:{ON_SURFACE_VAR};margin-top:1rem">'
            f'Configure parameters in the sidebar to begin.'
            f'</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# Footer
# ============================================================

st.markdown(
    f'<div class="footer">'
    f'The Digital Archivist &mdash; Research Paper Pipeline Dashboard &bull; '
    f'Mini-Assignment 5 &bull; FF-260205'
    f'</div>',
    unsafe_allow_html=True,
)
