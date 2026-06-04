import streamlit as st
import plotly.graph_objects as go
import sys
sys.path.insert(0, '.')
from streamlit_app.styles import get_css
from ml.training.skill_extractor import SkillExtractor

st.set_page_config(
    page_title="Skill Gap · TalentLens",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_css(), unsafe_allow_html=True)

st.markdown("""
<div class="tl-page-header fade-in">
    <h1>📊 Skill Gap Analysis</h1>
    <p>Compare your profile against any job description instantly</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="medium")
with col1:
    st.markdown(
        '<span class="tl-section-title">Your Profile</span>',
        unsafe_allow_html=True,
    )
    candidate_text = st.text_area(
        "profile", height=150,
        placeholder="Paste your skills and experience...",
        label_visibility="collapsed",
    )
with col2:
    st.markdown(
        '<span class="tl-section-title">Target Job Description</span>',
        unsafe_allow_html=True,
    )
    job_text = st.text_area(
        "job", height=150,
        placeholder="Paste the job description here...",
        label_visibility="collapsed",
    )

analyze_btn = st.button("📊 Analyze Skill Gap", type="primary")

if analyze_btn:
    if not candidate_text or not job_text:
        st.warning("Please fill in both fields.")
    else:
        with st.spinner("Analyzing skills..."):
            extractor = SkillExtractor(use_bert=False)
            candidate_skills = set(extractor.extract_skills(candidate_text))
            job_skills = set(extractor.extract_skills(job_text))

        if not job_skills:
            st.warning("No skills detected in job description.")
        else:
            matching = sorted(candidate_skills & job_skills)
            missing  = sorted(job_skills - candidate_skills)
            extra    = sorted(candidate_skills - job_skills)
            match_pct = int(len(matching) / max(len(job_skills), 1) * 100)

            st.markdown('<hr class="tl-sep">', unsafe_allow_html=True)

            # ── Score metrics ──────────────────────────────
            c1, c2, c3, c4 = st.columns(4, gap="small")
            for col, val, label in zip(
                [c1, c2, c3, c4],
                [f"{match_pct}%", len(matching), len(missing), len(extra)],
                ["Match Score", "You Have", "You Need", "Your Extras"],
            ):
                with col:
                    st.markdown(f"""
                    <div class="tl-metric fade-in">
                        <div class="value">{val}</div>
                        <div class="label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('<hr class="tl-sep">', unsafe_allow_html=True)

            col_chart, col_skills = st.columns([1, 1], gap="medium")

            # ── Radar chart ────────────────────────────────
            with col_chart:
                st.markdown(
                    '<span class="tl-section-title">Skill Coverage Radar</span>',
                    unsafe_allow_html=True,
                )
                all_skills = list(job_skills)[:8]
                if all_skills:
                    values = [1 if s in candidate_skills else 0
                              for s in all_skills]
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=[1]*len(all_skills),
                        theta=all_skills,
                        fill="toself",
                        name="Job Requires",
                        fillcolor="rgba(167,139,250,0.15)",
                        line=dict(color="#a78bfa", width=2.5),
                    ))
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=all_skills,
                        fill="toself",
                        name="You Have",
                        fillcolor="rgba(52,211,153,0.3)",
                        line=dict(color="#34d399", width=2.5),
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 1],
                                showticklabels=False,
                                gridcolor="rgba(255,255,255,0.08)",
                                linecolor="rgba(255,255,255,0.05)",
                            ),
                            bgcolor="rgba(15,14,23,0.9)",
                            angularaxis=dict(
                                color="rgba(255,255,255,0.4)",
                                tickfont=dict(
                                    size=10,
                                    color="rgba(255,255,255,0.7)",
                                ),
                                gridcolor="rgba(255,255,255,0.06)",
                                linecolor="rgba(255,255,255,0.05)",
                            ),
                        ),
                        showlegend=True,
                        height=300,
                        margin=dict(l=50, r=50, t=30, b=40),
                        paper_bgcolor="rgba(0,0,0,0)",
                        legend=dict(
                            font=dict(
                                size=10,
                                color="rgba(255,255,255,0.6)",
                            ),
                            orientation="h",
                            y=-0.18,
                            bgcolor="rgba(0,0,0,0)",
                        ),
                    )
                    # Radar wrapped in dark box
                    st.markdown(
                        '<div class="radar-wrap">',
                        unsafe_allow_html=True,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            # ── Skill breakdown ────────────────────────────
            with col_skills:
                st.markdown(
                    '<span class="tl-section-title">Skill Breakdown</span>',
                    unsafe_allow_html=True,
                )

                if matching:
                    st.markdown(
                        '<p style="font-size:0.76rem; color:#34d399; '
                        'font-weight:600; margin:10px 0 6px;">✅ You Have</p>',
                        unsafe_allow_html=True,
                    )
                    tags = " ".join([
                        f'<span class="skill-tag">{s}</span>'
                        for s in matching
                    ])
                    st.markdown(
                        f'<div style="margin-bottom:14px;">{tags}</div>',
                        unsafe_allow_html=True,
                    )

                if missing:
                    st.markdown(
                        '<p style="font-size:0.76rem; color:#f87171; '
                        'font-weight:600; margin:0 0 6px;">❌ You Need</p>',
                        unsafe_allow_html=True,
                    )
                    tags = " ".join([
                        f'<span style="display:inline-block;'
                        f'background:rgba(248,113,113,0.1);'
                        f'color:#f87171;'
                        f'border:1px solid rgba(248,113,113,0.25);'
                        f'padding:4px 11px; border-radius:6px;'
                        f'font-size:0.71rem; margin:2px 3px;">'
                        f'{s}</span>'
                        for s in missing
                    ])
                    st.markdown(
                        f'<div style="margin-bottom:14px;">{tags}</div>',
                        unsafe_allow_html=True,
                    )

                if extra:
                    st.markdown(
                        '<p style="font-size:0.76rem; color:#fbbf24; '
                        'font-weight:600; margin:0 0 6px;">➕ Your Extras</p>',
                        unsafe_allow_html=True,
                    )
                    tags = " ".join([
                        f'<span class="skill-tag-light">{s}</span>'
                        for s in extra[:10]
                    ])
                    st.markdown(f'<div>{tags}</div>', unsafe_allow_html=True)