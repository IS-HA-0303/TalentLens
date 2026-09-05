import streamlit as st
import sys
sys.path.insert(0, '.')
from streamlit_app.styles import get_css

st.set_page_config(
    page_title="TalentLens",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_css(), unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────
st.markdown("""
<div class="tl-page-header fade-in">
    <h1>🎯 TalentLens</h1>
    <p>AI-Powered Job · Candidate Matching System &nbsp;·&nbsp;
       Two-stage retrieval · BERT NER · Qdrant · Cross-Encoder</p>
</div>
""", unsafe_allow_html=True)

# ── Two EQUAL columns ──────────────────────────────────────
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("""
    <div class="tl-card fade-in-2" style="height:340px;">
        <span class="tl-section-title">What is TalentLens?</span>
        <div style="display:flex; flex-direction:column; align-items:center;
                    justify-content:center; height:calc(100% - 30px);
                    text-align:center; gap:16px;">
            <p style="font-size:0.87rem; color:rgba(255,255,255,0.65);
                      line-height:1.75; margin:0;">
                TalentLens is a
                <strong style="color:#a78bfa;">production-grade ML system</strong>
                that matches candidates to jobs using a two-stage retrieval pipeline —
                the same architecture used at
                <strong style="color:#34d399;">LinkedIn, Spotify, and Google</strong>.
            </p>
            <div style="display:flex; flex-direction:column; gap:12px; width:100%;">
                <div style="display:flex; align-items:center; gap:12px;
                            background:rgba(99,102,241,0.08);
                            border:1px solid rgba(99,102,241,0.15);
                            border-radius:10px; padding:10px 14px;">
                    <div style="background:rgba(99,102,241,0.2);
                        border:1px solid rgba(99,102,241,0.3);
                        border-radius:7px; width:26px; height:26px; flex-shrink:0;
                        display:flex; align-items:center; justify-content:center;
                        font-size:0.7rem; font-weight:700; color:#a5b4fc;">1</div>
                    <div style="text-align:left;">
                        <div style="color:#fff; font-weight:600; font-size:0.84rem;">
                            Skill Extraction</div>
                        <div style="color:rgba(255,255,255,0.4); font-size:0.75rem;">
                            Fine-tuned BERT NER detects skills</div>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:12px;
                            background:rgba(16,185,129,0.08);
                            border:1px solid rgba(16,185,129,0.15);
                            border-radius:10px; padding:10px 14px;">
                    <div style="background:rgba(16,185,129,0.15);
                        border:1px solid rgba(16,185,129,0.25);
                        border-radius:7px; width:26px; height:26px; flex-shrink:0;
                        display:flex; align-items:center; justify-content:center;
                        font-size:0.7rem; font-weight:700; color:#34d399;">2</div>
                    <div style="text-align:left;">
                        <div style="color:#fff; font-weight:600; font-size:0.84rem;">
                            Semantic Search</div>
                        <div style="color:rgba(255,255,255,0.4); font-size:0.75rem;">
                            384-dim embeddings in Qdrant vector DB</div>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:12px;
                            background:rgba(251,191,36,0.08);
                            border:1px solid rgba(251,191,36,0.12);
                            border-radius:10px; padding:10px 14px;">
                    <div style="background:rgba(251,191,36,0.12);
                        border:1px solid rgba(251,191,36,0.2);
                        border-radius:7px; width:26px; height:26px; flex-shrink:0;
                        display:flex; align-items:center; justify-content:center;
                        font-size:0.7rem; font-weight:700; color:#fbbf24;">3</div>
                    <div style="text-align:left;">
                        <div style="color:#fff; font-weight:600; font-size:0.84rem;">
                            Re-ranking</div>
                        <div style="color:rgba(255,255,255,0.4); font-size:0.75rem;">
                            Cross-encoder scores top 100 → best 10</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="tl-card fade-in-3" style="height:340px; overflow:auto;">
        <span class="tl-section-title">ML Architecture</span>
        <div style="background:#0f0e17;
            border:1px solid rgba(167,139,250,0.15);
            border-radius:10px; padding:10px 16px; margin-top:6px;
            height:calc(100% - 36px);
                    font-family:monospace; font-size:0.78rem; text-align:center;
                    display:flex; flex-direction:column; align-items:center;
                    justify-content:center; gap:2px;">
            <div style="color:#fff; font-weight:700; font-size:0.83rem;">
                Resume / Profile Text
            </div>
            <div style="color:rgba(255,255,255,0.1); font-size:0.7rem;">───────────────</div>
            <div style="color:rgba(255,255,255,0.5); font-size:0.73rem;">
                NER Skill Extraction</div>
            <div style="color:#a5b4fc; font-size:0.65rem;">(BERT fine-tuned)</div>
            <div style="color:rgba(255,255,255,0.15); font-size:0.95rem; margin:1px 0;">↓</div>
            <div style="color:rgba(255,255,255,0.5); font-size:0.73rem;">
                Bi-Encoder Embedding</div>
            <div style="color:#34d399; font-size:0.65rem;">(384-dimensional)</div>
            <div style="color:rgba(255,255,255,0.15); font-size:0.95rem; margin:1px 0;">↓</div>
            <div style="color:rgba(255,255,255,0.5); font-size:0.73rem;">
                Qdrant ANN Search</div>
            <div style="color:#fbbf24; font-size:0.65rem;">(top 100 results)</div>
            <div style="color:rgba(255,255,255,0.15); font-size:0.95rem; margin:1px 0;">↓</div>
            <div style="color:rgba(255,255,255,0.5); font-size:0.73rem;">
                Cross-Encoder Rerank</div>
            <div style="color:#f472b6; font-size:0.65rem;">(final top 10)</div>
            <div style="color:rgba(255,255,255,0.1); font-size:0.7rem;">───────────────</div>
            <div style="color:#fff; font-weight:700; font-size:0.8rem;">
                Ranked Job Matches + Skill Gap
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── System Stats ───────────────────────────────────────────
st.markdown(
    '<span class="tl-section-title fade-in-4">System Stats</span>',
    unsafe_allow_html=True,
)
c1, c2, c3, c4 = st.columns(4, gap="small")
for col, val, label in zip(
    [c1, c2, c3, c4],
    ["3,101", "91.6%", "85.0%", "384"],
    ["Jobs Indexed", "NER Model F1", "Recall @ 10", "Vector Dims"],
):
    with col:
        st.markdown(f"""
        <div class="tl-metric fade-in-4">
            <div class="value">{val}</div>
            <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
