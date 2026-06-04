def get_css():
    return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Root Background ── */
    .stApp {
        background: #0f0e17;
        min-height: 100vh;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* ══════════════════════════════════
       SIDEBAR
    ══════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: #0a0914 !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
        width: 220px !important;
        min-width: 220px !important;
    }
    [data-testid="stSidebar"] > div {
        padding: 0 !important;
    }
    [data-testid="stSidebarNav"] {
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"]::before {
        content: '🎯  TalentLens';
        display: block;
        padding: 24px 20px 20px;
        font-size: 0.95rem;
        font-weight: 700;
        color: #fff;
        letter-spacing: 0.3px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        background: linear-gradient(135deg, #1a1040 0%, #0a0914 100%);
    }
    [data-testid="stSidebarNav"] a {
        display: flex !important;
        align-items: center !important;
        padding: 10px 20px !important;
        margin: 2px 8px !important;
        border-radius: 8px !important;
        color: rgba(255,255,255,0.5) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        text-decoration: none !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.2px !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(167,139,250,0.1) !important;
        color: rgba(255,255,255,0.9) !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(135deg,
            rgba(167,139,250,0.2),
            rgba(99,102,241,0.15)) !important;
        color: #a78bfa !important;
        font-weight: 600 !important;
        border-left: 2px solid #a78bfa !important;
    }
    [data-testid="stSidebarNav"] span {
        color: inherit !important;
    }

    /* ══════════════════════════════════
       PAGE HEADER
    ══════════════════════════════════ */
    .tl-page-header {
        background: linear-gradient(135deg,
            rgba(167,139,250,0.12) 0%,
            rgba(99,102,241,0.08) 50%,
            rgba(16,185,129,0.06) 100%);
        border: 1px solid rgba(167,139,250,0.15);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .tl-page-header::before {
        content: '';
        position: absolute;
        top: -60%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle,
            rgba(167,139,250,0.08) 0%,
            transparent 65%);
        pointer-events: none;
    }
    .tl-page-header h1 {
        font-size: 1.7rem;
        font-weight: 800;
        color: #fff;
        margin: 0;
        letter-spacing: -0.5px;
        position: relative;
    }
    .tl-page-header p {
        color: rgba(255,255,255,0.45);
        font-size: 0.85rem;
        margin: 5px 0 0 0;
        position: relative;
    }

    /* ══════════════════════════════════
       CARDS — always show subtle glow
    ══════════════════════════════════ */
    .tl-card {
        background: #1a1825;
        border: 1px solid rgba(167,139,250,0.15);
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 14px;
        transition: all 0.25s ease;
        box-shadow: 0 4px 16px rgba(167,139,250,0.06),
                    0 0 0 1px rgba(167,139,250,0.06);
    }
    .tl-card:hover {
        border-color: rgba(167,139,250,0.35);
        box-shadow: 0 10px 36px rgba(167,139,250,0.16),
                    0 0 0 1px rgba(167,139,250,0.15);
        transform: translateY(-2px);
    }

    /* ══════════════════════════════════
       SECTION TITLES
    ══════════════════════════════════ */
    .tl-section-title {
        font-size: 0.68rem;
        font-weight: 700;
        color: rgba(167,139,250,0.8);
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        display: block;
    }

    /* ══════════════════════════════════
       METRIC CARDS — always show subtle glow
    ══════════════════════════════════ */
    .tl-metric {
        background: #1a1825;
        border: 1px solid rgba(167,139,250,0.12);
        border-radius: 12px;
        padding: 16px 12px;
        text-align: center;
        transition: all 0.25s ease;
        cursor: default;
        box-shadow: 0 3px 12px rgba(167,139,250,0.05);
    }
    .tl-metric:hover {
        background: #211f30;
        border-color: rgba(167,139,250,0.35);
        box-shadow: 0 10px 28px rgba(167,139,250,0.16);
        transform: translateY(-3px);
    }
    .tl-metric .value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #fff;
        letter-spacing: -0.5px;
    }
    .tl-metric .label {
        font-size: 0.63rem;
        color: rgba(255,255,255,0.35);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 4px;
    }

    /* ══════════════════════════════════
       SKILL TAGS
    ══════════════════════════════════ */
    .skill-tag {
        display: inline-block;
        background: rgba(99,102,241,0.18);
        color: #a5b4fc;
        border: 1px solid rgba(99,102,241,0.25);
        padding: 4px 11px;
        border-radius: 6px;
        font-size: 0.71rem;
        margin: 2px 3px;
        font-weight: 500;
        transition: all 0.18s ease;
    }
    .skill-tag:hover {
        background: rgba(99,102,241,0.28);
        transform: translateY(-1px);
    }
    .skill-tag-light {
        display: inline-block;
        background: rgba(255,255,255,0.06);
        color: rgba(255,255,255,0.55);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 4px 11px;
        border-radius: 6px;
        font-size: 0.71rem;
        margin: 2px 3px;
        transition: all 0.18s ease;
    }
    .skill-tag-light:hover {
        background: rgba(255,255,255,0.1);
        color: rgba(255,255,255,0.8);
    }

    /* ══════════════════════════════════
       BADGES
    ══════════════════════════════════ */
    .badge-strong {
        background: rgba(16,185,129,0.15);
        color: #34d399;
        border: 1px solid rgba(16,185,129,0.25);
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.68rem;
        font-weight: 600;
    }
    .badge-good {
        background: rgba(251,191,36,0.12);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.2);
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.68rem;
        font-weight: 600;
    }
    .badge-partial {
        background: rgba(255,255,255,0.06);
        color: rgba(255,255,255,0.4);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.68rem;
        font-weight: 600;
    }

    /* ══════════════════════════════════
       JOB CARDS
    ══════════════════════════════════ */
    .job-card {
        background: #1e1c2a;
        border: 1px solid rgba(255,255,255,0.07);
        border-left: 2px solid rgba(167,139,250,0.5);
        border-radius: 10px;
        padding: 14px 16px;
        transition: all 0.22s ease;
    }
    .job-card:hover {
        background: #232134;
        border-color: rgba(167,139,250,0.25);
        border-left-color: #a78bfa;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transform: translateX(3px);
    }
    .job-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #fff;
    }
    .job-meta {
        font-size: 0.74rem;
        color: rgba(255,255,255,0.38);
        margin-top: 5px;
    }

    /* ══════════════════════════════════
       BUTTONS
    ══════════════════════════════════ */
    .stButton > button {
        background: #fff !important;
        color: #0f0e17 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.2px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
    }
    .stButton > button:hover {
        background: rgba(255,255,255,0.9) !important;
        box-shadow: 0 4px 16px rgba(255,255,255,0.15) !important;
        transform: translateY(-1px) !important;
    }

    /* ══════════════════════════════════
    INPUTS — fix white box issue
    ══════════════════════════════════ */
    .stTextArea > div,
    .stTextArea > div > div {
        background: transparent !important;
    }
    .stTextInput > div,
    .stTextInput > div > div {
        background: transparent !important;
    }
    [data-baseweb="textarea"],
    [data-baseweb="base-input"],
    [data-baseweb="input"] {
        background: #1a1825 !important;
        border-color: rgba(167,139,250,0.2) !important;
        border-radius: 10px !important;
    }
    textarea {
        background: #e8e6f0 !important;
        color: #000000 !important;
        caret-color: #a78bfa !important;
        border-color: rgba(167,139,250,0.2) !important;
    }
    }
    textarea:focus {
        border-color: rgba(167,139,250,0.5) !important;
        box-shadow: 0 0 0 3px rgba(167,139,250,0.12) !important;
    }
    textarea::placeholder {
        color: rgba(255,255,255,0.25) !important;
    }
    input[type="text"], input[type="search"] {
        background: #1a1825 !important;
        color: #ffffff !important;
        border-color: rgba(167,139,250,0.2) !important;
        border-radius: 10px !important;
    }
    input:focus {
        border-color: rgba(167,139,250,0.5) !important;
        box-shadow: 0 0 0 3px rgba(167,139,250,0.12) !important;
    }
    input::placeholder {
        color: rgba(255,255,255,0.25) !important;
    }
    .stTextArea label,
    .stTextInput label {
        color: rgba(255,255,255,0.45) !important;
        font-size: 0.78rem !important;
    }
    /* ══════════════════════════════════
       FILE UPLOADER — fix white box
    ══════════════════════════════════ */
    [data-testid="stFileUploader"] {
        background: #1a1825 !important;
        border: 1.5px dashed rgba(167,139,250,0.3) !important;
        border-radius: 12px !important;
        transition: all 0.2s !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(167,139,250,0.6) !important;
        background: rgba(167,139,250,0.05) !important;
    }
    [data-testid="stFileUploader"] * {
        color: rgba(255,255,255,0.5) !important;
    }
    [data-testid="stFileUploader"] section {
        background: transparent !important;
        border: none !important;
    }

    /* ══════════════════════════════════
       EXPANDER
    ══════════════════════════════════ */
    .streamlit-expanderHeader {
        background: #1a1825 !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 10px !important;
        color: rgba(255,255,255,0.75) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
        padding: 12px 16px !important;
    }
    .streamlit-expanderHeader:hover {
        background: #211f30 !important;
        border-color: rgba(167,139,250,0.25) !important;
        color: #fff !important;
    }
    [data-testid="stExpander"] {
        border: none !important;
        background: transparent !important;
        margin-bottom: 6px !important;
    }
    [data-testid="stExpanderDetails"] {
        background: #16141f !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 14px !important;
    }

    /* ══════════════════════════════════
       RADIO
    ══════════════════════════════════ */
    .stRadio label {
        color: rgba(255,255,255,0.6) !important;
        font-size: 0.82rem !important;
    }
    .stRadio > div { background: transparent !important; }

    /* ══════════════════════════════════
       SELECTBOX
    ══════════════════════════════════ */
    .stSelectbox > div > div {
        background: #1a1825 !important;
        border-color: rgba(167,139,250,0.2) !important;
        color: #fff !important;
        border-radius: 8px !important;
    }
    .stSelectbox svg { color: rgba(255,255,255,0.4) !important; }

    /* ══════════════════════════════════
       SLIDER
    ══════════════════════════════════ */
    .stSlider label {
        color: rgba(255,255,255,0.5) !important;
        font-size: 0.8rem !important;
    }
    .stSlider > div > div > div { background: #a78bfa !important; }

    /* ══════════════════════════════════
       ALERTS
    ══════════════════════════════════ */
    [data-testid="stAlert"] {
        background: rgba(16,185,129,0.08) !important;
        border: 1px solid rgba(16,185,129,0.2) !important;
        border-radius: 10px !important;
    }
    [data-testid="stAlert"] p { color: #6ee7b7 !important; }

    /* ══════════════════════════════════
       SPINNER
    ══════════════════════════════════ */
    .stSpinner > div { border-top-color: #a78bfa !important; }

    /* ══════════════════════════════════
       SEPARATOR
    ══════════════════════════════════ */
    .tl-sep {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.06);
        margin: 16px 0;
    }

    /* ══════════════════════════════════
       RADAR BOX
    ══════════════════════════════════ */
    .radar-wrap {
        background: #0f0e17;
        border: 1px solid rgba(167,139,250,0.25);
        border-radius: 12px;
        padding: 10px;
        margin-top: 8px;
    }

    /* ══════════════════════════════════
       SCROLLBAR
    ══════════════════════════════════ */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.12);
        border-radius: 99px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.2);
    }

    /* ══════════════════════════════════
       ANIMATIONS
    ══════════════════════════════════ */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .fade-in   { animation: fadeInUp 0.4s ease both; }
    .fade-in-2 { animation: fadeInUp 0.4s ease 0.08s both; }
    .fade-in-3 { animation: fadeInUp 0.4s ease 0.16s both; }
    .fade-in-4 { animation: fadeInUp 0.4s ease 0.24s both; }

    /* ══════════════════════════════════
       PROGRESS
    ══════════════════════════════════ */
    .stProgress > div > div { background: #a78bfa !important; }

    /* ══════════════════════════════════
       GLOBAL TEXT
    ══════════════════════════════════ */
    .stMarkdown p {
        color: rgba(255,255,255,0.6);
        font-size: 0.85rem;
        line-height: 1.7;
    }
    h1, h2, h3 { color: #fff !important; }


    /* ── Force black text in textareas ── */
.stTextArea textarea,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] textarea,
.stTextArea div div textarea {
    color: #000000 !important;
    background-color: #dddae8 !important;
    -webkit-text-fill-color: #000000 !important;
}

div[data-baseweb="textarea"] {
    background-color: #dddae8 !important;
}

div[data-baseweb="textarea"] > div {
    background-color: #dddae8 !important;
}
</style>
"""