import streamlit as st
import requests
import sys
sys.path.insert(0, '.')
from streamlit_app.styles import get_css

st.set_page_config(
    page_title="Job Search · TalentLens",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_css(), unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

st.markdown("""
<div class="tl-page-header fade-in">
    <h1>🔍 Semantic Job Search</h1>
    <p>Search jobs using natural language — no exact keywords needed</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1], gap="small")
with col1:
    query = st.text_input(
        "q",
        placeholder="e.g. machine learning engineer Python PyTorch AWS...",
        label_visibility="collapsed",
    )
with col2:
    top_k = st.selectbox("n", [5, 10, 15, 20], index=1, label_visibility="collapsed")

search_btn = st.button("🔍 Search Jobs", type="primary", disabled=not query)

st.markdown("""
<div style="margin:8px 0 16px;">
    <span style="font-size:0.71rem; color:rgba(255,255,255,0.3); margin-right:8px;">Try:</span>
    <span class="skill-tag-light">ML engineer Python PyTorch</span>
    <span class="skill-tag-light">Data engineer Spark Kafka</span>
    <span class="skill-tag-light">NLP researcher BERT</span>
    <span class="skill-tag-light">MLOps Airflow Kubernetes</span>
    <span class="skill-tag-light">Backend FastAPI PostgreSQL</span>
</div>
""", unsafe_allow_html=True)

if search_btn and query:
    with st.spinner("Searching..."):
        response = requests.post(
            f"{API_URL}/jobs/search",
            json={"query": query, "top_k": top_k},
        )

    if response.status_code == 200:
        data = response.json()
        st.markdown(
            f'<p style="font-size:0.8rem; color:rgba(255,255,255,0.35); margin-bottom:12px;">'
            f'Found <strong style="color:#a78bfa;">{data["total_results"]}</strong> '
            f'matching jobs</p>',
            unsafe_allow_html=True,
        )

        for i, job in enumerate(data["jobs"], 1):
            score = job.get("retrieval_score", 0)
            with st.expander(
                f"#{i} · {job['title']} — {job['company_name']}",
                expanded=(i <= 3),
            ):
                st.markdown(f"""
                <div class="job-card">
                    <div class="job-title">{job['title']}</div>
                    <div class="job-meta">
                        🏢 {job['company_name']} &nbsp;·&nbsp;
                        📍 {job['location']} &nbsp;·&nbsp;
                        💼 {job['experience_level']} &nbsp;·&nbsp;
                        <span style="color:#a78bfa; font-weight:600;">
                            Score: {score:.3f}
                        </span>
                    </div>
                    <div style="margin-top:10px; font-size:0.77rem;
                                color:rgba(255,255,255,0.45);
                                background:rgba(255,255,255,0.03);
                                border:1px solid rgba(255,255,255,0.06);
                                padding:10px 12px; border-radius:8px; line-height:1.65;">
                        {job.get('text_preview','')[:280]}...
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error(f"Error: {response.status_code}")