import streamlit as st
import requests
import sys
sys.path.insert(0, '.')
from streamlit_app.styles import get_css

st.set_page_config(
    page_title="Candidate Portal · TalentLens",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_css(), unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

st.markdown("""
<div class="tl-page-header fade-in">
    <h1>📄 Candidate Portal</h1>
    <p>Upload your resume or paste your profile to find matching jobs</p>
</div>
""", unsafe_allow_html=True)

input_method = st.radio(
    "Input:",
    ["Paste Profile Text", "Upload PDF Resume"],
    horizontal=True,
    label_visibility="collapsed",
)

candidate_text = ""

if input_method == "Paste Profile Text":
    candidate_text = st.text_area(
        "profile",
        height=130,
        placeholder="Paste your skills, experience, and background here...",
        label_visibility="collapsed",
    )
else:
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            response = requests.post(
                f"{API_URL}/candidates/upload",
                files={"file": (uploaded_file.name, uploaded_file, "application/pdf")},
            )
            if response.status_code == 200:
                data = response.json()
                candidate_text = data["full_text"]
                st.success(f"✓ Extracted {data['text_length']} characters")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

col_s, col_b = st.columns([4, 1])
with col_s:
    top_k = st.slider("Matches to return:", 5, 20, 10)
with col_b:
    st.markdown("<div style='margin-top:26px;'>", unsafe_allow_html=True)
    search_btn = st.button("🔍 Find Jobs", type="primary", disabled=not candidate_text)
    st.markdown("</div>", unsafe_allow_html=True)

if search_btn and candidate_text:
    with st.spinner("Running pipeline..."):
        response = requests.post(
            f"{API_URL}/candidates/match",
            json={"text": candidate_text, "top_k": top_k},
        )

    if response.status_code == 200:
        data = response.json()
        skills = data["candidate_skills"]

        st.markdown('<hr class="tl-sep">', unsafe_allow_html=True)
        st.markdown('<span class="tl-section-title">Detected Skills</span>', unsafe_allow_html=True)

        if skills:
            tags = " ".join([f'<span class="skill-tag">{s}</span>' for s in skills])
            st.markdown(f'<div style="margin:8px 0 18px;">{tags}</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3, gap="small")
        for col, val, label in zip(
            [c1, c2, c3],
            [len(skills), data["total_retrieved"], data["total_returned"]],
            ["Skills Found", "Jobs Retrieved", "Jobs Returned"],
        ):
            with col:
                st.markdown(f"""
                <div class="tl-metric">
                    <div class="value">{val}</div>
                    <div class="label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<hr class="tl-sep">', unsafe_allow_html=True)
        st.markdown('<span class="tl-section-title">Top Job Matches</span>', unsafe_allow_html=True)
        st.markdown("<div style='margin-top:10px;'>", unsafe_allow_html=True)

        for i, job in enumerate(data["matches"], 1):
            score = job.get("rerank_score", 0)
            retrieval = job.get("retrieval_score", 0)

            if score > 0:
                badge = '<span class="badge-strong">Strong</span>'
            elif score > -5:
                badge = '<span class="badge-good">Good</span>'
            else:
                badge = '<span class="badge-partial">Relevant</span>'

            with st.expander(
                f"#{i} — {job['title']}  ·  {job['company_name']}",
                expanded=(i <= 2),
            ):
                st.markdown(f"""
                <div class="job-card">
                    <div class="job-title">{job['title']}</div>
                    <div class="job-meta">
                        🏢 {job['company_name']} &nbsp;·&nbsp;
                        📍 {job['location']} &nbsp;·&nbsp;
                        💼 {job['experience_level']} &nbsp;·&nbsp;
                        {badge}
                    </div>
                    <div style="margin-top:8px; font-size:0.73rem; color:rgba(255,255,255,0.3);">
                        Relevance:
                        <span style="color:#a78bfa; font-weight:600;">{score:.3f}</span>
                        &nbsp;·&nbsp; Vector:
                        <span style="color:#34d399; font-weight:600;">{retrieval:.3f}</span>
                        &nbsp;·&nbsp; Remote: {'✓' if job.get('remote_allowed') else '✗'}
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

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(f"API Error {response.status_code}")