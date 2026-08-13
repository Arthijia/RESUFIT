"""
RESUFIT — ATS Compatibility Checker

Checks resume formatting/structure for common issues that cause
Applicant Tracking Systems (ATS) to misread or reject resumes,
BEFORE a human recruiter ever sees them.

This is rule-based and explainable — no external AI calls needed.
"""

import re

REQUIRED_SECTIONS = {
    "contact info": [r"email", r"@", r"phone", r"\+?\d{10}"],
    "experience": [r"experience", r"work history", r"employment"],
    "education": [r"education", r"degree", r"university", r"college", r"b\.?tech", r"bachelor"],
    "skills": [r"skills", r"technical skills", r"competencies"],
}

DATE_PATTERN = re.compile(
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}|"
    r"\d{4}\s*[-–—to]+\s*(\d{4}|present|current)",
    re.IGNORECASE
)

def check_sections(text):
    """Checks presence of standard resume sections ATS systems look for."""
    text_lower = text.lower()
    results = []
    for section, patterns in REQUIRED_SECTIONS.items():
        found = any(re.search(p, text_lower) for p in patterns)
        results.append({"section": section, "found": found})
    return results

def check_contact_info(text):
    """Checks for email and phone number presence — critical for ATS parsing."""
    has_email = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
    has_phone = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\d{10}", text))
    return has_email, has_phone

def check_dates(text):
    """Checks whether work/education entries include dates — ATS uses these for timeline parsing."""
    return bool(DATE_PATTERN.search(text))

def check_word_count(text):
    """Very short resumes often mean missing content; very long ones may be poorly parsed."""
    words = len(text.split())
    if words < 150:
        return "too_short", words
    elif words > 1200:
        return "too_long", words
    return "good", words

def check_bullet_usage(text):
    """ATS-friendly resumes typically use simple bullet characters, not complex symbols."""
    bullet_chars = ["•", "-", "*", "▪", "◦"]
    has_bullets = any(ch in text for ch in bullet_chars)
    return has_bullets

def check_special_characters(text):
    """Excessive special/unicode characters can indicate a table/graphic-heavy resume,
    which many ATS parsers fail to read correctly."""
    weird_chars = re.findall(r"[^\x00-\x7F]", text)
    ratio = len(weird_chars) / max(len(text), 1)
    return ratio > 0.03  # flag if >3% non-ASCII

def run_ats_check(text):
    """
    Runs the full ATS compatibility check and returns a structured result:
    {
        "score": int (0-100),
        "checks": [ {label, passed, detail}, ... ],
        "verdict": str
    }
    """
    checks = []
    score = 0
    max_score = 0

    # 1. Section presence (40 points total, 10 each)
    section_results = check_sections(text)
    for r in section_results:
        max_score += 10
        if r["found"]:
            score += 10
        checks.append({
            "label": f"{r['section'].title()} section detected",
            "passed": r["found"],
            "detail": "Found" if r["found"] else "Not clearly detected — ATS may not parse this section"
        })

    # 2. Contact info (15 points)
    has_email, has_phone = check_contact_info(text)
    max_score += 15
    contact_ok = has_email and has_phone
    if has_email:
        score += 8
    if has_phone:
        score += 7
    checks.append({
        "label": "Email address present",
        "passed": has_email,
        "detail": "Found" if has_email else "No valid email detected"
    })
    checks.append({
        "label": "Phone number present",
        "passed": has_phone,
        "detail": "Found" if has_phone else "No valid phone number detected"
    })

    # 3. Dates present (15 points)
    max_score += 15
    dates_ok = check_dates(text)
    if dates_ok:
        score += 15
    checks.append({
        "label": "Dates for experience/education found",
        "passed": dates_ok,
        "detail": "Found" if dates_ok else "No clear dates detected — ATS may struggle to build a timeline"
    })

    # 4. Word count (15 points)
    max_score += 15
    length_status, word_count = check_word_count(text)
    length_ok = length_status == "good"
    if length_ok:
        score += 15
    elif length_status == "too_short":
        score += 5
    else:
        score += 8
    checks.append({
        "label": "Resume length is appropriate",
        "passed": length_ok,
        "detail": f"{word_count} words — {'good length' if length_ok else ('too short, add more detail' if length_status=='too_short' else 'quite long, consider trimming')}"
    })

    # 5. Bullet usage (10 points)
    max_score += 10
    bullets_ok = check_bullet_usage(text)
    if bullets_ok:
        score += 10
    checks.append({
        "label": "Uses clear bullet points",
        "passed": bullets_ok,
        "detail": "Found" if bullets_ok else "No bullet points detected — ATS-friendly resumes typically use them"
    })

    # 6. Special characters (5 points)
    max_score += 5
    special_flag = check_special_characters(text)
    special_ok = not special_flag
    if special_ok:
        score += 5
    checks.append({
        "label": "Minimal special/unusual characters",
        "passed": special_ok,
        "detail": "Clean text" if special_ok else "High proportion of unusual characters — may indicate tables/graphics that ATS can't parse"
    })

    final_score = round((score / max_score) * 100) if max_score else 0

    if final_score >= 80:
        verdict = "Excellent — highly ATS-compatible"
    elif final_score >= 60:
        verdict = "Good — minor improvements recommended"
    elif final_score >= 40:
        verdict = "Fair — several issues may affect ATS parsing"
    else:
        verdict = "Poor — significant formatting issues detected"

    return {
        "score": final_score,
        "checks": checks,
        "verdict": verdict
    }
