import streamlit as st
import pdfplumber
import base64
from pathlib import Path
from io import BytesIO
from datetime import datetime
from nlp_engine import extract_skills_nlp
from ats_checker import run_ats_check
from database import init_db, save_screening, get_recent_screenings, get_stats, clear_history

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

EMERALD_HEX = "#35D39A"
GOLD_HEX = "#E9B85B"
PINK_HEX = "#F276B8"

# ============================================================
# SESSION STATE
# ============================================================
init_db()

if "page" not in st.session_state:
    st.session_state.page = "dashboard"
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
# BACKEND LOGIC — now powered by NLP-based skill extraction
# (see nlp_engine.py + skills_taxonomy.py)
# ============================================================

def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return " ".join(p.text for p in doc.paragraphs)

def extract_skills(text, skills_db=None):
    # skills_db kept as param for compatibility; now uses NLP taxonomy matching
    return extract_skills_nlp(text)

def build_report_text(score, matched, missing, jd_skills, ats_result=None):
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
    if ats_result:
        lines += [
            "",
            "-" * 40,
            "ATS Compatibility Check",
            f"Score: {ats_result['score']}/100 — {ats_result['verdict']}",
            "",
        ]
        for c in ats_result["checks"]:
            status = "PASS" if c["passed"] else "FAIL"
            lines.append(f"[{status}] {c['label']} — {c['detail']}")
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

    stats = get_stats()
    total = stats["total"]
    avg_score = stats["avg_match"]
    avg_ats = stats["avg_ats"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="rf-stat"><div class="rf-stat-label">Total Screenings</div><div class="rf-stat-value">{total}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="rf-stat"><div class="rf-stat-label">Average Match</div><div class="rf-stat-value">{avg_score}%</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="rf-stat"><div class="rf-stat-label">Average ATS Score</div><div class="rf-stat-value">{avg_ats}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="rf-stat"><div class="rf-stat-label">Formats Supported</div><div class="rf-stat-value">PDF / DOCX</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    bcol1, bcol2 = st.columns(2)
    with bcol1:
        if st.button("+ Start New Screening", use_container_width=True):
            go_to("work")
            st.rerun()
    with bcol2:
        if st.button("⇄ Compare Multiple Jobs", use_container_width=True):
            go_to("compare")
            st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    col_title, col_clear = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="rf-card-title">Recent Activity</div>', unsafe_allow_html=True)
    with col_clear:
        if total > 0 and st.button("Clear History", use_container_width=True):
            clear_history()
            st.rerun()

    recent = get_recent_screenings(limit=5)
    if not recent:
        st.markdown('<div class="rf-card-description">No screenings yet — run your first analysis to see it here.</div>', unsafe_allow_html=True)
    else:
        for h in recent:
            st.markdown(
                f"""
                <div class="rf-card" style="margin-bottom:10px;padding:16px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:13px;color:#F5F5F7;font-weight:650;">{h['time']}</span>
                        <div>
                            <span class="rf-tag {'rf-tag-success' if h['match_score']>=70 else 'rf-tag-gold' if h['match_score']>=40 else 'rf-tag'}">{h['match_score']}% match</span>
                            <span class="rf-tag {'rf-tag-success' if h['ats_score']>=80 else 'rf-tag-gold' if h['ats_score']>=60 else 'rf-tag'}">ATS {h['ats_score']}</span>
                        </div>
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
            resume_bytes = resume_file.read()
            resume_file.seek(0)

            if resume_file.name.lower().endswith(".pdf"):
                resume_text = extract_text_from_pdf(resume_file)
            elif resume_file.name.lower().endswith(".docx") and DOCX_AVAILABLE:
                resume_text = extract_text_from_docx(resume_file)
            else:
                st.error("Unsupported file type.")
                resume_text = ""

            jd_text = job_desc
            resume_skills = extract_skills(resume_text)
            jd_skills = extract_skills(jd_text)

            if jd_skills:
                matched = resume_skills.intersection(jd_skills)
                missing = jd_skills - resume_skills
                score = round((len(matched) / len(jd_skills)) * 100)
                degrees = score * 3.6

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

                # ============================================================
                # ATS COMPATIBILITY CHECK (Phase 2 — differentiator feature)
                # ============================================================
                ats_result = run_ats_check(resume_text)
                ats_score = ats_result["score"]
                ats_color = EMERALD_HEX if ats_score >= 80 else GOLD_HEX if ats_score >= 60 else PINK_HEX
                ats_tag_class = "rf-tag-success" if ats_score >= 80 else "rf-tag-gold" if ats_score >= 60 else "rf-tag"

                save_screening(score, ats_score, matched, missing)

                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="rf-ai-panel">
                        <div class="rf-ai-label">✦ ATS COMPATIBILITY CHECK</div>
                        <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;margin-top:8px;">
                            <div style="font-size:40px;font-weight:800;color:{ats_color};letter-spacing:-1px;">{ats_score}<span style="font-size:16px;color:#6F7482;">/100</span></div>
                            <div>
                                <div style="color:#F5F5F7;font-size:16px;font-weight:700;">{ats_result['verdict']}</div>
                                <div style="color:#A7ABB8;font-size:12px;margin-top:3px;">Checks whether your resume can be correctly read by Applicant Tracking Systems — before a human ever sees it.</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                ats_cols = st.columns(2)
                for idx, check in enumerate(ats_result["checks"]):
                    col = ats_cols[idx % 2]
                    icon = "✓" if check["passed"] else "✕"
                    color = EMERALD_HEX if check["passed"] else PINK_HEX
                    with col:
                        st.markdown(
                            f"""
                            <div style="display:flex;gap:10px;padding:10px 4px;border-bottom:1px solid rgba(255,255,255,0.06);">
                                <div style="color:{color};font-weight:800;font-size:14px;">{icon}</div>
                                <div>
                                    <div style="color:#F5F5F7;font-size:12.5px;font-weight:600;">{check['label']}</div>
                                    <div style="color:#6F7482;font-size:11px;margin-top:2px;">{check['detail']}</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                report = build_report_text(score, matched, missing, jd_skills, ats_result)
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
# PAGE — COMPARE MODE
# One resume against multiple job descriptions, side by side
# ============================================================
def render_compare():
    render_header()

    if st.button("← Back to Dashboard"):
        go_to("dashboard")
        st.rerun()

    st.markdown(
        """
        <div class="rf-ai-panel" style="margin-top:16px;">
            <div class="rf-ai-label">✦ COMPARISON MODE</div>
            <div class="rf-ai-title">Compare one resume against multiple jobs</div>
            <p style="color:#A7ABB8;font-size:13px;line-height:1.6;margin-top:7px;">
                Upload a resume once, add up to 3 job descriptions, and see which role fits best.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    accepted_types = ["pdf", "docx"] if DOCX_AVAILABLE else ["pdf"]
    st.markdown(
        f"""
        <div class="rf-upload">
            <div class="rf-upload-icon">↑</div>
            <div class="rf-upload-title">Drop your resume here</div>
            <div class="rf-upload-description">{'PDF or DOCX' if DOCX_AVAILABLE else 'PDF'} • Used across all job comparisons</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    resume_file = st.file_uploader("Upload Resume", type=accepted_types, label_visibility="collapsed", key="compare_resume")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="rf-card-title">Job Descriptions</div>', unsafe_allow_html=True)

    job_labels = ["Job A", "Job B", "Job C"]
    jd_inputs = []
    cols = st.columns(3)
    for i, col in enumerate(cols):
        with col:
            st.markdown(f'<div style="font-size:12px;color:#A7ABB8;font-weight:650;margin-bottom:6px;">{job_labels[i]}</div>', unsafe_allow_html=True)
            jd = st.text_area(job_labels[i], height=160, label_visibility="collapsed",
                               placeholder=f"Paste {job_labels[i]} description here...", key=f"jd_{i}")
            jd_inputs.append(jd)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    compare = st.button("✦ Compare Jobs", use_container_width=True)

    if compare:
        active_jobs = [(job_labels[i], jd) for i, jd in enumerate(jd_inputs) if jd.strip()]

        if not resume_file:
            st.error("Please upload a resume.")
        elif len(active_jobs) < 2:
            st.error("Please fill in at least 2 job descriptions to compare.")
        else:
            if resume_file.name.lower().endswith(".pdf"):
                resume_text = extract_text_from_pdf(resume_file)
            elif resume_file.name.lower().endswith(".docx") and DOCX_AVAILABLE:
                resume_text = extract_text_from_docx(resume_file)
            else:
                st.error("Unsupported file type.")
                resume_text = ""

            resume_skills = extract_skills(resume_text)

            results = []
            for label, jd_text in active_jobs:
                jd_skills = extract_skills(jd_text)
                if jd_skills:
                    matched = resume_skills.intersection(jd_skills)
                    missing = jd_skills - resume_skills
                    score = round((len(matched) / len(jd_skills)) * 100)
                else:
                    matched, missing, score = set(), set(), 0
                results.append({
                    "label": label, "score": score,
                    "matched": matched, "missing": missing,
                    "jd_skill_count": len(jd_skills)
                })

            results.sort(key=lambda r: r["score"], reverse=True)
            best = results[0]

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="rf-score-panel">
                    <div class="rf-ai-label">✦ BEST FIT</div>
                    <div style="font-size:24px;font-weight:800;color:#F5F5F7;margin-top:6px;">
                        {best['label']} — {best['score']}% match
                    </div>
                    <div style="color:#A7ABB8;font-size:13px;margin-top:6px;">
                        This resume aligns most closely with {best['label']} out of the jobs compared.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            result_cols = st.columns(len(results))
            for idx, r in enumerate(results):
                tag_class = "rf-tag-success" if r["score"] >= 70 else "rf-tag-gold" if r["score"] >= 40 else "rf-tag"
                is_best = idx == 0
                with result_cols[idx]:
                    st.markdown(
                        f"""
                        <div class="rf-card" style="{'border-color:#8B5CFF;' if is_best else ''}">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div class="rf-card-title" style="margin-bottom:0;">{r['label']}{' 🏆' if is_best else ''}</div>
                            </div>
                            <div style="font-size:32px;font-weight:800;color:#F5F5F7;margin:10px 0;">{r['score']}%</div>
                            <span class="rf-tag {tag_class}">{len(r['matched'])} matched</span>
                            <div style="color:#A7ABB8;font-size:11px;line-height:1.6;margin-top:10px;">
                                <strong style="color:#35D39A;">Matched:</strong> {", ".join(sorted(r['matched'])) if r['matched'] else 'None'}
                            </div>
                            <div style="color:#A7ABB8;font-size:11px;line-height:1.6;margin-top:6px;">
                                <strong style="color:#F276B8;">Missing:</strong> {", ".join(sorted(r['missing'])) if r['missing'] else 'None'}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

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
elif st.session_state.page == "compare":
    render_compare()
else:
    st.session_state.page = "dashboard"
    render_dashboard()
