# 🎯 RESUFIT — AI Resume Intelligence

**Where talent meets intelligence.**

RESUFIT is an AI-powered resume screening tool that helps job seekers and placement cells instantly evaluate how well a resume matches a job description. It extracts skills from both the resume and job posting, calculates a match score, and highlights exactly what's missing — turning manual resume screening into a fast, data-driven decision.

## ✨ Features

- **Multi-page flow** — Splash screen → Login → Dashboard → Screening tool
- **Resume upload** — supports both PDF and DOCX formats
- **AI-based skill matching** — extracts and compares skills between resume and job description
- **Live match score** — visual circular score ring with matched/missing skill breakdown
- **Personalized suggestions** — recommends skills to add based on gaps found
- **Downloadable reports** — export analysis results as a text report
- **Screening history** — dashboard tracks past analyses in the session
- **Custom dark UI** — fully designed premium interface with a dedicated design system

## 🛠️ Tech Stack

- **Python**
- **Streamlit** — web app framework
- **pdfplumber** — PDF text extraction
- **python-docx** — DOCX text extraction
- **Custom CSS** — dark, gradient-based design system

## 🚀 Getting Started

1. Clone the repository
```bash
   git clone https://github.com/Arthijia/RESUFIT.git
   cd RESUFIT
```

2. Install dependencies
```bash
   pip install streamlit pdfplumber python-docx
```

3. Run the app
```bash
   streamlit run resufit_app.py
```

## 📋 How It Works

1. Upload a resume (PDF or DOCX)
2. Paste the job description
3. Click **Analyze Fit**
4. View your match score, matched skills, missing skills, and improvement suggestions
5. Download the full report

## 📌 Project Status

Built as part of the SIH 2026 Internal Hackathon at Sri Manakula Vinayagar Engineering College. Actively being improved with additional features planned, including more advanced NLP-based skill extraction and multi-resume comparison.

## 👤 Author

**Arthi R**
B.Tech, Artificial Intelligence and Data Science
Sri Manakula Vinayagar Engineering College
