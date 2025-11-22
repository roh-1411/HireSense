#############################################
# HireSense – Streamlit App + Orchestrator
#############################################

import streamlit as st
from typing import List, Dict, Any

# Import agents
from agents.role_reality_agent import build_role_profile
from agents.resume_reality_agent import build_resume_profile
from agents.fit_agent import compute_fit_profile
from agents.friendly_agent import build_friendly_report
from agents.resume_parser_agent import parse_resume


#############################################
# HELPER FUNCTIONS – FORMAT RAW PROFILES
#############################################

def format_role_reality_markdown(role_profile: Dict[str, Any]) -> str:
    """Convert role_profile_raw dict into nice markdown."""
    if not role_profile:
        return "_No role reality data available._"

    lines: List[str] = []

    # Rounds
    rounds = role_profile.get("rounds", [])
    if rounds:
        lines.append("### 🧱 Interview Rounds (From Public Reviews)\n")
        for r in rounds:
            name = r.get("name", "Interview Round")
            desc = r.get("description", "")
            lines.append(f"#### • {name}")
            if desc:
                lines.append(desc + "\n")

            # Topics
            topics = r.get("topics", [])
            if topics:
                lines.append("**Common topics:**")
                lines.extend([f"- {t}" for t in topics])
                lines.append("")

            # Subrounds (for onsite breakdown)
            subrounds = r.get("subrounds", [])
            for sr in subrounds:
                sr_name = sr.get("name", "Sub-round")
                sr_desc = sr.get("description", "")
                lines.append(f"##### ⤷ {sr_name}")
                if sr_desc:
                    lines.append(sr_desc + "\n")
                sr_topics = sr.get("topics", [])
                if sr_topics:
                    lines.append("Common concepts:")
                    lines.extend([f"- {t}" for t in sr_topics])
                    lines.append("")

    # Skills
    smor = role_profile.get("skills_most_often_required", [])
    if smor:
        lines.append("### 🎯 Skills Most Often Required")
        lines.extend([f"- {s}" for s in smor])
        lines.append("")

    snth = role_profile.get("skills_nice_to_have", [])
    if snth:
        lines.append("### ✨ Nice-to-Have Skills")
        lines.extend([f"- {s}" for s in snth])
        lines.append("")

    # Themes, questions, projects
    themes = role_profile.get("common_interview_themes", [])
    if themes:
        lines.append("### 📌 Common Interview Themes")
        lines.extend([f"- {t}" for t in themes])
        lines.append("")

    q_patterns = role_profile.get("common_questions_patterns", [])
    if q_patterns:
        lines.append("### ❓ Question Patterns (High-Level)")
        lines.extend([f"- {q}" for q in q_patterns])
        lines.append("")

    projects = role_profile.get("projects_they_like", [])
    if projects:
        lines.append("### 🧪 Project Types They Like")
        lines.extend([f"- {p}" for p in projects])
        lines.append("")

    edu = role_profile.get("education_or_experience_expectations", [])
    if edu:
        lines.append("### 🎓 Education & Experience Expectations")
        lines.extend([f"- {e}" for e in edu])
        lines.append("")

    # Difficulty & seniority
    diff = role_profile.get("difficulty", "")
    round_count = role_profile.get("round_count", "")
    seniority_pattern = role_profile.get("seniority_pattern", "")
    if diff or round_count or seniority_pattern:
        lines.append("### 📊 Overall Pattern")
        if round_count:
            lines.append(f"- Typical number of rounds: **{round_count}**")
        if diff:
            lines.append(f"- Overall difficulty: **{diff}**")
        if seniority_pattern:
            lines.append(f"- Seniority expectations: {seniority_pattern}")
        lines.append("")

    summary = role_profile.get("public_interview_summary", "")
    if summary:
        lines.append("### 📝 Public Interview Summary")
        lines.append(summary)

    return "\n".join(lines).strip()


def format_resume_reality_markdown(resume_profile: Dict[str, Any]) -> str:
    """Convert resume_profile_raw dict into nice markdown."""
    if not resume_profile:
        return "_No resume reality data available._"

    lines: List[str] = []

    domain = resume_profile.get("resume_domain", "") or resume_profile.get("likely_resume_domain", "")
    if domain:
        lines.append(f"### 🧭 Detected Resume Domain")
        lines.append(f"- **{domain}**\n")

    strengths = resume_profile.get("core_strengths_raw", []) or resume_profile.get("core_strengths", [])
    if strengths:
        lines.append("### 💪 Core Strength Signals")
        lines.extend([f"- {s}" for s in strengths])
        lines.append("")

    weaknesses = resume_profile.get("core_weaknesses_raw", []) or resume_profile.get("core_weaknesses", [])
    if weaknesses:
        lines.append("### ⚠️ Core Weakness / Risk Signals")
        lines.extend([f"- {w}" for w in weaknesses])
        lines.append("")

    tech_clusters = resume_profile.get("tech_stack_clusters", [])
    if tech_clusters:
        lines.append("### 🧰 Tech Stack Clusters")
        lines.extend([f"- {t}" for t in tech_clusters])
        lines.append("")

    proj_signals = resume_profile.get("project_signals", []) or resume_profile.get("project_summary", {}).get("project_themes", [])
    if proj_signals:
        lines.append("### 📂 Project Signals")
        lines.extend([f"- {p}" for p in proj_signals])
        lines.append("")

    seniority = resume_profile.get("seniority_signal", "") or resume_profile.get("seniority_guess", "")
    if seniority:
        lines.append("### 🎚 Seniority Signal")
        lines.append(f"- {seniority}\n")

    missing = resume_profile.get("missing_signals_for_role", []) or resume_profile.get("skill_summary", {}).get("missing_common_skills", [])
    if missing:
        lines.append("### 🔍 Signals Missing for Target Role")
        lines.extend([f"- {m}" for m in missing])
        lines.append("")

    return "\n".join(lines).strip()


def format_fit_analysis_markdown(fit_profile: Dict[str, Any]) -> str:
    """Convert fit_profile_raw dict into nice markdown."""
    if not fit_profile:
        return "_No fit analysis data available._"

    lines: List[str] = []

    score = fit_profile.get("fit_score_percentage", fit_profile.get("skill_match_score", None))
    category = fit_profile.get("fit_summary_category", "")
    if score is not None or category:
        lines.append("### 🎯 Overall Fit")
        if score is not None:
            lines.append(f"- Overall fit score: **{score}%**")
        if category:
            lines.append(f"- Category: **{category}**")
        lines.append("")

    seniority_fit = fit_profile.get("seniority_fit", "")
    domain_fit = fit_profile.get("domain_fit", "")
    experience_fit = fit_profile.get("experience_fit", "")
    project_fit = fit_profile.get("project_fit", "")
    if seniority_fit or domain_fit or experience_fit or project_fit:
        lines.append("### 🧱 Alignment Dimensions")
        if seniority_fit:
            lines.append(f"- **Seniority fit:** {seniority_fit}")
        if domain_fit:
            lines.append(f"- **Domain fit:** {domain_fit}")
        if experience_fit:
            lines.append(f"- **Experience fit:** {experience_fit}")
        if project_fit:
            lines.append(f"- **Project fit:** {project_fit}")
        lines.append("")

    strengths = fit_profile.get("matched_strengths", [])
    if strengths:
        lines.append("### ✅ Matched Strengths vs Role")
        lines.extend([f"- {s}" for s in strengths])
        lines.append("")

    risks = fit_profile.get("mismatched_risks", [])
    if risks:
        lines.append("### ⚠️ Risks / Misalignments")
        lines.extend([f"- {r}" for r in risks])
        lines.append("")

    priority_gaps = fit_profile.get("priority_gaps", [])
    if priority_gaps:
        lines.append("### 🔧 Priority Gaps to Fix")
        lines.extend([f"- {g}" for g in priority_gaps])
        lines.append("")

    missing_req = fit_profile.get("missing_role_requirements", [])
    if missing_req:
        lines.append("### 📋 Missing Formal Role Requirements")
        lines.extend([f"- {m}" for m in missing_req])
        lines.append("")

    notes = fit_profile.get("overall_alignment_notes", [])
    if notes:
        lines.append("### 📝 Alignment Notes")
        lines.extend([f"- {n}" for n in notes])

    return "\n".join(lines).strip()


#############################################
# ORCHESTRATOR FUNCTION
#############################################

def run_hire_sense(
    company: str,
    role: str,
    resume_text: str,
    extracted_skills: str,
    results: List[Dict[str, str]],
    user_review_text: str = "",
    user_insight_text: str = "",
) -> Dict[str, Any]:

    # Stage 1 — Role Reality
    role_profile = build_role_profile(
        company=company,
        role=role,
        results=results,
        user_review_text=user_review_text,
        user_insight_text=user_insight_text,
    )

    # Stage 2 — Resume Reality
    resume_profile = build_resume_profile(
        resume_text=resume_text,
        extracted_skills=extracted_skills,
        user_review_text=user_review_text,
        user_insight_text=user_insight_text,
    )

    # Stage 3 — Fit Engine
    fit_profile = compute_fit_profile(
        role_profile=role_profile,
        resume_profile=resume_profile,
    )

    # Stage 4 — Friendly Final Report
    friendly_report = build_friendly_report(
        company=company,
        role=role,
        resume_text=resume_text,
        role_profile=role_profile,
        resume_profile=resume_profile,
        fit_profile=fit_profile,
        user_review_text=user_review_text,
        user_insight_text=user_insight_text,
    )

    return {
        "role_profile_raw": role_profile,
        "resume_profile_raw": resume_profile,
        "fit_profile_raw": fit_profile,
        "friendly_report": friendly_report,
    }


#############################################
# STREAMLIT UI
#############################################

st.set_page_config(page_title="HireSense AI", layout="wide")
st.title("🔍 HireSense — AI-Powered Resume vs Role Reality Analyzer")

st.markdown("""
Welcome to **HireSense Advanced** —  
Upload your resume, enter the target **company** and **role**,  
and get a **deep, role-aware, resume-aware analysis** powered by multi-stage AI reasoning.
""")


#############################################
# INPUT FIELDS
#############################################

company = st.text_input("🏢 Target Company")

role = st.text_input("💼 Target Role (e.g., Software Engineer, Data Engineer, ML Engineer)")


# ---------- PDF UPLOAD ----------
uploaded_pdf = st.file_uploader(
    "📎 Upload your Resume (PDF preferred)",
    type=["pdf"]
)

resume_text = ""

if uploaded_pdf:
    parsed = parse_resume(uploaded_pdf)
    resume_text = parsed["resume_text"]
    auto_skills = parsed["skills_raw_exact"]
else:
    auto_skills = []


# ---------- MANUAL RESUME TEXT ----------
resume_text_manual = st.text_area(
    "📄 Or Paste Your Resume Text",
    placeholder="Paste the FULL raw text of your resume here...",
    height=250,
)

if resume_text_manual.strip():
    resume_text = resume_text_manual.strip()


# ---------- AUTO + MANUAL SKILLS ----------
skills_manual = st.text_area(
    "🔧 Extracted Skills (optional)",
    value=", ".join(auto_skills),
    placeholder="Python, SQL, AWS, Spark, C++, React, etc."
)

# Search results placeholder (until SERP API is added)
results: List[Dict[str, str]] = []


#############################################
# USER INTERVIEW REVIEW + INSIGHTS
#############################################

st.markdown("### 🙌 Help HireSense Improve (Optional)")

col1, col2 = st.columns(2)

with col1:
    user_review_text = st.text_area(
        "💬 Share Your Interview Experience",
        placeholder="If you've interviewed for this company/role, please share your experience.\n\nExample:\n- Rounds breakdown\n- Questions asked\n- Difficulty\n- Outcomes",
        height=200
    )

with col2:
    user_insight_text = st.text_area(
        "✨ Valuable Insights for HireSense",
        placeholder="Share any ideas or insights to help enhance HireSense.\n\nExample:\n- Missing features\n- Accuracy suggestions\n- Interview trends you've seen",
        height=200
    )


#############################################
# RUN ANALYSIS
#############################################

if st.button("Analyze My Resume", type="primary"):
    if not (company and role and resume_text.strip()):
        st.error("❗ Please fill in: company, role, and resume text.")
    else:

        with st.spinner("Analyzing your resume with HireSense..."):
            output = run_hire_sense(
                company=company,
                role=role,
                resume_text=resume_text,
                extracted_skills=skills_manual,
                results=results,
                user_review_text=user_review_text,
                user_insight_text=user_insight_text,
            )

        report = output["friendly_report"]

        st.success("Analysis complete! Scroll down to view your full report.")


        #############################################
        # USER-FACING REPORT (CLEAN)
        #############################################

        st.header("👋 Intro Message")
        st.write(report.get("intro_message", ""))

        st.header("🧠 Friendly Summary")
        st.write(report.get("friendly_summary", ""))

        st.header("📌 Role Expectations Explained")
        st.write(report.get("role_expectations_explained", ""))

        st.header("💪 Your Strengths")
        st.write(report.get("resume_strengths_explained", ""))

        st.header("⚠️ Gaps / Things to Improve")
        st.write(report.get("resume_gaps_explained", ""))

        st.header("🎯 Fit Summary")
        st.write(report.get("fit_explained", ""))


        #############################################
        # ACTION PLAN
        #############################################

        action_plan = report.get("action_plan", {}) or {}

        st.header("🚀 Action Plan Tailored for You")

        st.subheader("✔ Quick Wins (1–7 Days)")
        quick_wins = action_plan.get("quick_wins", [])
        if quick_wins:
            st.write("\n".join(f"- {x}" for x in quick_wins))
        else:
            st.write("_No quick wins generated._")

        st.subheader("📆 4-Week Improvement Plan")
        four_week = action_plan.get("4_week_plan", [])
        if four_week:
            st.write("\n".join(f"- {x}" for x in four_week))
        else:
            st.write("_No 4-week plan generated._")

        st.subheader("📝 Resume Fixes")
        resume_fixes = action_plan.get("resume_fixes", [])
        if resume_fixes:
            st.write("\n".join(f"- {x}" for x in resume_fixes))
        else:
            st.write("_No resume fixes generated._")

        st.subheader("⚙ Project Ideas")
        project_ideas = action_plan.get("project_ideas", [])
        if project_ideas:
            st.write("\n".join(f"- {x}" for x in project_ideas))
        else:
            st.write("_No project ideas generated._")


        #############################################
        # ROUND-BY-ROUND BREAKDOWN (User-facing)
        #############################################

        rounds = report.get("round_deep_dive", [])
        if rounds:
            st.header("🧩 Round-by-Round Interview Breakdown (From Public Reviews + Patterns)")
            for r in rounds:
                title = r.get("round_name", "Interview Round")

                if r.get("round_type"):
                    title += f" — {r['round_type']}"
                if r.get("difficulty"):
                    title += f" (Difficulty: {r['difficulty']})"

                st.subheader(f"• {title}")

                def show(label: str, items: Any):
                    if items:
                        st.markdown(f"**{label}:**")
                        st.markdown("\n".join(f"- {i}" for i in items))

                show("What they look for", r.get("what_they_look_for", []))
                show("Common concepts", r.get("common_concepts", []))
                show("Question patterns", r.get("question_patterns", []))
                show("Example question themes", r.get("example_question_themes", []))
                show("Tips", r.get("tips", []))


        #############################################
        # RAW ROLE / RESUME / FIT – HUMAN FORMAT
        #############################################

        st.header("🛠 Role Reality (Raw Breakdown)")
        st.write("This is how HireSense understands the REAL expectations of this role, based on public reviews and patterns.")
        st.markdown(format_role_reality_markdown(output.get("role_profile_raw", {})))

        st.header("📄 Resume Reality (Raw Breakdown)")
        st.write("This is how HireSense interprets the TRUE content and signals in your resume.")
        st.markdown(format_resume_reality_markdown(output.get("resume_profile_raw", {})))

        st.header("📊 Fit Analysis (Raw Breakdown)")
        st.write("This is the realistic fit assessment between your resume and the role expectations.")
        st.markdown(format_fit_analysis_markdown(output.get("fit_profile_raw", {})))


st.markdown("---")
st.caption("Powered by HireSense Advanced — Multi-Stage Role-Aware AI Resume Analysis.")
