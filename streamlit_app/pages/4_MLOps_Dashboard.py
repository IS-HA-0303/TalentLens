import streamlit as st
import requests
import time
import sys
sys.path.insert(0, '.')
from streamlit_app.styles import get_css

st.set_page_config(
    page_title="MLOps Dashboard · TalentLens",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_css(), unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

st.markdown("""
<div class="tl-page-header fade-in">
    <h1>⚙️ MLOps Dashboard</h1>
    <p>Live system health · Model performance · Pipeline metrics</p>
</div>
""", unsafe_allow_html=True)

# ── API Health ─────────────────────────────────────────────
st.markdown(
    '<span class="tl-section-title">API Health</span>',
    unsafe_allow_html=True,
)

try:
    t0 = time.time()
    resp = requests.get(f"{API_URL}/health", timeout=5)
    latency = round((time.time() - t0) * 1000, 1)
    healthy = resp.status_code == 200
    services = resp.json().get("services", []) if healthy else []
except Exception:
    healthy = False
    latency = 0
    services = []

c1, c2, c3, c4 = st.columns(4, gap="small")
for col, val, label in zip(
    [c1, c2, c3, c4],
    [
        "🟢 Healthy" if healthy else "🔴 Down",
        f"{latency}ms",
        f"{len(services)} / 4",
        "1.0.0",
    ],
    ["API Status", "Response Latency", "Active Services", "Version"],
):
    with col:
        st.markdown(f"""
        <div class="tl-metric fade-in">
            <div class="value" style="font-size:1.05rem;">{val}</div>
            <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

if services:
    tags = " ".join([
        f'<span class="skill-tag">{s}</span>' for s in services
    ])
    st.markdown(
        f'<p style="font-size:0.73rem; color:rgba(255,255,255,0.3);'
        f' margin:10px 0 4px;">Active: {tags}</p>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-sep">', unsafe_allow_html=True)

# ── Model metrics ──────────────────────────────────────────
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown(
        '<span class="tl-section-title">NER Model — BERT base-uncased</span>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4, gap="small")
    for col, val, label in zip(
        cols,
        ["91.6%", "88.3%", "95.1%", "2,294"],
        ["F1 Score", "Precision", "Recall", "Train Ex."],
    ):
        with col:
            st.markdown(f"""
            <div class="tl-metric">
                <div class="value" style="font-size:1rem;">{val}</div>
                <div class="label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown(
        '<span class="tl-section-title">Bi-Encoder — all-MiniLM-L6-v2</span>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4, gap="small")
    for col, val, label in zip(
        cols,
        ["85.0%", "0.749", "0.716", "8,372"],
        ["Recall@10", "NDCG@10", "MRR@10", "Train Pairs"],
    ):
        with col:
            st.markdown(f"""
            <div class="tl-metric">
                <div class="value" style="font-size:1rem;">{val}</div>
                <div class="label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<hr class="tl-sep">', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown(
        '<span class="tl-section-title">Vector Database · Qdrant</span>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4, gap="small")
    for col, val, label in zip(
        cols,
        ["3,101", "384", "Cosine", "HNSW"],
        ["Vectors", "Dims", "Distance", "Index"],
    ):
        with col:
            st.markdown(f"""
            <div class="tl-metric">
                <div class="value" style="font-size:1rem;">{val}</div>
                <div class="label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown(
        '<span class="tl-section-title">Live Pipeline Test</span>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <p style="font-size:0.75rem; color:rgba(255,255,255,0.45);
              margin-bottom:6px;">Test query:</p>
    """, unsafe_allow_html=True)
    test_q = st.text_input(
        "test_query",
        value="Python machine learning engineer PyTorch AWS",
        label_visibility="collapsed",
    )
    if st.button("▶ Run Pipeline Test", type="primary"):
        with st.spinner("Running..."):
            t0 = time.time()
            r = requests.post(
                f"{API_URL}/candidates/match",
                json={"text": test_q, "top_k": 3},
            )
            elapsed = round((time.time() - t0) * 1000, 1)

        if r.status_code == 200:
            d = r.json()
            st.markdown(f"""
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:10px;">
                <span class="badge-strong">✓ {elapsed}ms</span>
                <span class="skill-tag">{len(d['candidate_skills'])} skills</span>
                <span class="skill-tag-light">{d['total_retrieved']} retrieved</span>
            </div>
            """, unsafe_allow_html=True)
            if d["matches"]:
                top = d["matches"][0]
                st.markdown(
                    f'<p style="margin-top:8px; font-size:0.78rem;'
                    f' color:rgba(255,255,255,0.5);">'
                    f'<span style="color:#a78bfa;">Top:</span> '
                    f'{top["title"]} · {top["company_name"]}</p>',
                    unsafe_allow_html=True,
                )
        else:
            st.error("Test failed")

st.markdown('<hr class="tl-sep">', unsafe_allow_html=True)

st.markdown(
    '<span class="tl-section-title">Tech Stack</span>',
    unsafe_allow_html=True,
)
stack = [
    "PyTorch", "Hugging Face", "Sentence-Transformers",
    "Qdrant", "FastAPI", "Streamlit", "MLflow",
    "BERT", "Cross-Encoder", "Python 3.11",
]
tags = " ".join([f'<span class="skill-tag-light">{s}</span>' for s in stack])
st.markdown(f'<div style="margin-top:8px;">{tags}</div>', unsafe_allow_html=True)