import streamlit as st
import pdfplumber
import base64
from pathlib import Path
from io import BytesIO
from datetime import datetime

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="RESUFIT — AI Resume Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# LOAD CSS
# ============================================================
def load_css():
    css_file = Path(__file__).parent / "style.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

def get_logo_base64():
    logo_path = Path(__file__).parent / "logo.png"
    if logo_path.exists():
        return base64.b64encode(logo_path.read_bytes()).decode()
    return ""

logo_b64 = get_logo_base64()

# ============================================================
# SESSION STATE
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "history" not in st.session_state:
    st.session_state.history = []
if "username" not in st.session_state:
    st.session_state.username = ""

def go_to(page_name):
    st.session_state.page = page_name

# ============================================================
# SHARED HEADER (used on dashboard + work screen)
# ============================================================
def render_header():
    st.markdown(
        f"""
        <div class="rf-header">
            <div class="rf-brand">
                <div class="rf-logo">
                    <img src="data:image/png;base64,{logo_b64}" style="width:27px;height:27px;">
                </div>
                <div>
                    <div class="rf-brand-name">RESUFIT</div>
                    <div class="rf-brand-subtitle">AI-powered resume intelligence</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# BACKEND LOGIC (real skill-matching engine)
# ============================================================
SKILLS_DB = [
    "python", "java", "c++", "sql", "html", "css", "javascript",
    "machine learning", "deep learning", "data science", "nlp",
    "react", "node.js", "flask", "django", "aws", "cloud",
    "git", "github", "docker", "kubernetes", "excel", "power bi",
    "tableau", "communication", "teamwork", "leadership",
    "problem solving", "project management", "data analysis",
    "tensorflow", "pytorch", "pandas", "numpy", "api", "rest api"
]

def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text.lower()

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return " ".join(p.text for p in doc.paragraphs).lower()

def extract_skills(text, skills_db):
    return set(skill for skill in skills_db if skill in text)

def build_report_text(score, matched, missing, jd_skills):
    lines = [
        "RESUFIT — AI Match Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "-" * 40,
        f"Match Score: {score}%",
        f"Skills Required: {len(jd_skills)}",
        f"Skills Matched: {len(matched)}",
        "",
        "Matched Skills:",
        ", ".join(matched) if matched else "None",
        "",
        "Missing Skills:",
        ", ".join(missing) if missing else "None",
        "",
        "Suggestion:",
        f"Consider adding these skills to strengthen your profile: {', '.join(missing) if missing else 'N/A'}",
    ]
    return "\n".join(lines)

# ============================================================
# PAGE 1 — SPLASH
# ============================================================
def render_splash():
    st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align:center;">
            <div style="
                width:96px;height:96px;margin:0 auto 24px;
                display:flex;align-items:center;justify-content:center;
                border-radius:24px;
                background: linear-gradient(135deg,#8B5CFF,#6F70FF,#4C8DFF);
                box-shadow: 0 0 40px rgba(139,92,255,0.25);
                overflow:hidden;
            ">
                <img src="data:image/png;base64,{logo_b64}" style="width:60px;height:60px;">
            </div>
            <div class="rf-hero-badge">✦ AI RESUME INTELLIGENCE</div>
            <h1 class="rf-hero-title">Where talent meets <span>intelligence.</span></h1>
            <p class="rf-hero-description">
                Upload a resume and a job description — RESUFIT analyzes the fit,
                highlights matched skills, and shows exactly what's missing.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Get Started →", use_container_width=True):
            go_to("login")
            st.rerun()

# ============================================================
# PAGE 2 — LOGIN
# ============================================================
def render_login():
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(
            f"""
            <div style="text-align:center;margin-bottom:20px;">
                <div class="rf-logo" style="margin:0 auto 14px;">
                    <img src="data:image/png;base64,{logo_b64}" style="width:27px;height:27px;">
                </div>
                <div style="font-size:22px;font-weight:800;color:#F5F5F7;">Welcome to RESUFIT</div>
                <div style="font-size:12px;color:#6F7482;margin-top:4px;">Sign in to continue</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="rf-card">', unsafe_allow_html=True)
        username = st.text_input("Name", placeholder="Enter your name")
        st.text_input("Password", type="password", placeholder="••••••••")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("Login →", use_container_width=True):
            st.session_state.username = username if username else "Guest"
            go_to("dashboard")
            st.rerun()

# ============================================================
# PAGE 3 — DASHBOARD
# ============================================================
def render_dashboard():
    render_header()
    st.markdown(
        f"""
        <div class="rf-hero" style="padding:30px 10px 20px;text-align:left;">
            <div class="rf-hero-badge">✦ DASHBOARD</div>
            <div style="font-size:32px;font-weight:800;color:#F5F5F7;letter-spacing:-1px;">
                Welcome to RESUFIT
            </div>
            <p class="rf-hero-description" style="margin-left:0;">
                Screen resumes against job descriptions and track your analysis history.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    total = len(st.session_state.history)
    avg_score = round(sum(h["score"] for h in st.session_state.history) / total) if total else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="rf-stat"><div class="rf-stat-label">Total Screenings</div><div class="rf-stat-value">{total}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="rf-stat"><div class="rf-stat-label">Average Match</div><div class="rf-stat-value">{avg_score}%</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="rf-stat"><div class="rf-stat-label">Formats Supported</div><div class="rf-stat-value">PDF / DOCX</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if st.button("+ Start New Screening", use_container_width=True):
        go_to("work")
        st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="rf-card-title">Recent Activity</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown('<div class="rf-card-description">No screenings yet — run your first analysis to see it here.</div>', unsafe_allow_html=True)
    else:
        for h in reversed(st.session_state.history[-5:]):
            st.markdown(
                f"""
                <div class="rf-card" style="margin-bottom:10px;padding:16px;">
                    <div style="display:flex;justify-content:space-between;">
                        <span style="font-size:13px;color:#F5F5F7;font-weight:650;">{h['time']}</span>
                        <span class="rf-tag {'rf-tag-success' if h['score']>=70 else 'rf-tag-gold' if h['score']>=40 else 'rf-tag'}">{h['score']}% match</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ============================================================
# PAGE 4 — WORK SCREEN (the screening tool)
# ============================================================
def render_work():
    render_header()

    if st.button("← Back to Dashboard"):
        go_to("dashboard")
        st.rerun()

    st.markdown(
        """
        <div class="rf-ai-panel" style="margin-top:16px;">
            <div class="rf-ai-label">✦ AI SCREENING</div>
            <div class="rf-ai-title">Start candidate analysis</div>
            <p style="color:#A7ABB8;font-size:13px;line-height:1.6;margin-top:7px;">
                Upload a resume and provide the job requirements below.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    accepted_types = ["pdf", "docx"] if DOCX_AVAILABLE else ["pdf"]

    with col1:
        st.markdown(
            f"""
            <div class="rf-upload">
                <div class="rf-upload-icon">↑</div>
                <div class="rf-upload-title">Drop your resume here</div>
                <div class="rf-upload-description">{'PDF or DOCX' if DOCX_AVAILABLE else 'PDF'} • AI-powered screening</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        resume_file = st.file_uploader("Upload Resume", type=accepted_types, label_visibility="collapsed")

    with col2:
        st.markdown('<div class="rf-card-title" style="margin-top:0;">Job Description</div>', unsafe_allow_html=True)
        job_desc = st.text_area("Paste Job Description", height=180, label_visibility="collapsed",
                                 placeholder="Paste the job description here...")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    analyze = st.button("✦ Analyze Fit", use_container_width=True)

    if analyze:
        if resume_file and job_desc:
            if resume_file.name.lower().endswith(".pdf"):
                resume_text = extract_text_from_pdf(resume_file)
            elif resume_file.name.lower().endswith(".docx") and DOCX_AVAILABLE:
                resume_text = extract_text_from_docx(resume_file)
            else:
                st.error("Unsupported file type.")
                resume_text = ""

            jd_text = job_desc.lower()
            resume_skills = extract_skills(resume_text, SKILLS_DB)
            jd_skills = extract_skills(jd_text, SKILLS_DB)

            if jd_skills:
                matched = resume_skills.intersection(jd_skills)
                missing = jd_skills - resume_skills
                score = round((len(matched) / len(jd_skills)) * 100)
                degrees = score * 3.6

                st.session_state.history.append({
                    "time": datetime.now().strftime("%d %b, %H:%M"),
                    "score": score
                })

                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                label = "Strong candidate match" if score >= 70 else \
                         "Moderate candidate match" if score >= 40 else \
                         "Limited candidate match"
                tag_class = "rf-tag-success" if score >= 70 else "rf-tag-gold" if score >= 40 else "rf-tag"

                st.markdown(
                    f"""
                    <div class="rf-score-panel">
                        <div class="rf-ai-label">✦ AI MATCH ANALYSIS</div>
                        <div class="rf-score-container">
                            <div class="rf-score-ring" style="
                                background: conic-gradient(
                                    from -90deg,
                                    #8B5CFF 0deg,
                                    #6F70FF {degrees * 0.7}deg,
                                    #4C8DFF {degrees}deg,
                                    #222733 {degrees}deg,
                                    #222733 360deg
                                );">
                                <div class="rf-score-content">
                                    <div class="rf-score-value">{score}</div>
                                    <div class="rf-score-percent">%</div>
                                </div>
                            </div>
                            <div>
                                <div style="color:#F5F5F7;font-size:24px;font-weight:750;letter-spacing:-0.7px;">{label}</div>
                                <div style="color:#A7ABB8;font-size:13px;line-height:1.65;margin-top:8px;max-width:550px;">
                                    Based on {len(matched)} of {len(jd_skills)} required skills found in this resume.
                                </div>
                                <div style="margin-top:15px;">
                                    <span class="rf-tag {tag_class}">{label.split()[0]} Match</span>
                                    <span class="rf-tag">AI Verified</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        f"""
                        <div class="rf-insight rf-insight-emerald">
                            <div style="color:#35D39A;font-size:11px;font-weight:700;letter-spacing:0.7px;">MATCHED SKILLS</div>
                            <div style="color:#F5F5F7;font-size:15px;font-weight:650;margin-top:7px;">{len(matched)} skill(s) aligned</div>
                            <div style="color:#A7ABB8;font-size:12px;line-height:1.6;margin-top:5px;">{", ".join(matched) if matched else "None found"}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with c2:
                    st.markdown(
                        f"""
                        <div class="rf-insight rf-insight-pink">
                            <div style="color:#F276B8;font-size:11px;font-weight:700;letter-spacing:0.7px;">SKILL GAPS</div>
                            <div style="color:#F5F5F7;font-size:15px;font-weight:650;margin-top:7px;">{len(missing)} skill(s) missing</div>
                            <div style="color:#A7ABB8;font-size:12px;line-height:1.6;margin-top:5px;">{", ".join(missing) if missing else "None — great fit!"}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                if missing:
                    st.markdown(
                        f"""
                        <div class="rf-insight rf-insight-gold" style="margin-top:10px;">
                            <div style="color:#E9B85B;font-size:11px;font-weight:700;letter-spacing:0.7px;">SUGGESTION</div>
                            <div style="color:#A7ABB8;font-size:12px;line-height:1.6;margin-top:5px;">
                                Add these skills to strengthen your profile: {", ".join(missing)}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                report = build_report_text(score, matched, missing, jd_skills)
                st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                st.download_button(
                    "⬇ Download Report",
                    data=report,
                    file_name="resufit_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning("No recognizable skills found in the job description. Try adding more detail.")
        else:
            st.error("Please upload a resume and paste a job description.")

    st.markdown(
        """
        <div class="rf-footer">
            <strong>RESUFIT</strong> &nbsp;•&nbsp; Where talent meets intelligence.
            <br><span style="display:inline-block;margin-top:6px;">Find the fit, not just the resume.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# ROUTER
# ============================================================
if st.session_state.page == "dashboard":
    render_dashboard()
elif st.session_state.page == "work":
    render_work()
else:
    st.session_state.page = "dashboard"
    render_dashboard()
