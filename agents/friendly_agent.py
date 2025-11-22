#############################################
# HireSense – Friendly Agent v3.0
#############################################

from typing import Dict, Any
import json
from string import Template
from agents.openai_client import get_client


def build_friendly_report(
    company: str,
    role: str,
    resume_text: str,
    role_profile: Dict[str, Any],
    resume_profile: Dict[str, Any],
    fit_profile: Dict[str, Any],
    user_review_text: str = "",
    user_insight_text: str = "",
) -> Dict[str, Any]:

    client = get_client()

    role_json = json.dumps(role_profile, indent=2)
    resume_json = json.dumps(resume_profile, indent=2)
    fit_json = json.dumps(fit_profile, indent=2)

    tmpl = Template(
        """
You are the FRIENDLY OUTPUT ENGINE for HireSense.

Your job:
- Take all raw role, resume, and fit data
- Produce a HUMAN, FRIENDLY, EASY-TO-READ analysis
- Match the tone of a supportive career mentor
- Based ONLY on real data provided (NEVER hallucinate)

========================================
COMPANY: $company
ROLE: $role
========================================

ROLE_PROFILE (RAW JSON):
$role_json

RESUME_PROFILE (RAW JSON):
$resume_json

FIT_PROFILE (RAW JSON):
$fit_json

USER INTERVIEW REVIEW (optional):
$user_review_text

USER INSIGHT (optional):
$user_insight_text

========================================
OUTPUT FORMAT (STRICT)
========================================
Return ONLY valid JSON:

{
  "intro_message": "",
  "friendly_summary": "",
  "role_expectations_explained": "",
  "resume_strengths_explained": "",
  "resume_gaps_explained": "",
  "fit_explained": "",
  "action_plan": {
    "quick_wins": [],
    "4_week_plan": [],
    "resume_fixes": [],
    "project_ideas": []
  },
  "round_deep_dive": [
    {
      "round_name": "",
      "round_type": "",
      "difficulty": "",
      "what_they_look_for": [],
      "common_concepts": [],
      "question_patterns": [],
      "example_question_themes": [],
      "tips": []
    }
  ]
}

========================================
TONE & CONTENT RULES
========================================

INTRO:
- MUST start with: "Thank you for choosing HireSense!"
- Then something like:
  "Let’s walk through what we found about <company>'s hiring for <role> and how your profile lines up."

FRIENDLY SUMMARY:
- Blend:
  - What public interview reviews say about this company + role
  - What the resume shows (strengths + limitations)
- Explicitly mention:
  "Based on public interview reviews and resources we looked at..."

ROLE EXPECTATIONS:
- Explain:
  - Typical rounds
  - Skills expected
  - Behavioral expectations
  - Seniority expectations
- Use info from role_profile: rounds, skills_most_often_required, projects_they_like, difficulty, etc.

RESUME STRENGTHS:
- Focus on positive matches:
  - Skills that line up
  - Projects that look relevant
  - Patterns that make this candidate promising
- Be warm and encouraging.

RESUME GAPS:
- Explain gently:
  - Missing skills vs role expectations
  - Missing project types
  - Missing seniority/leadership signals
- Use soft phrasing: "You might want to...", "It could help to...", "Reviews suggest many successful candidates also..."

FIT EXPLAINED:
- Turn fit_profile into plain English:
  - Domain fit
  - Seniority fit
  - Skill match
  - Major risks
  - Overall conclusion
- Reference fit_score_percentage and fit_summary_category, but do NOT dump numbers only – explain what they mean.

ACTION PLAN:
- quick_wins:
  - Things they can realistically do in 1–7 days.
- 4_week_plan:
  - A concrete 4-week roadmap.
- resume_fixes:
  - Specific bullet-level ideas to rewrite or add to the resume.
- project_ideas:
  - 3–6 project ideas aligned with what this company likes to see for this role.

ROUND_DEEP_DIVE:
- Build a breakdown of the MOST LIKELY interview rounds based on role_profile and public patterns:
  - examples: "Online Assessment (DSA)", "Technical Screening – Coding", "Onsite – System Design", "Behavioral / Leadership".
- For each round:
  - round_name: human-friendly, e.g. "Online Assessment – DSA Coding"
  - round_type: high-level type, e.g. "DSA", "System Design", "Behavioral", "Data / SQL", "Machine Learning".
  - difficulty: "easy", "medium", "hard", or "mixed".
  - what_they_look_for: bullets like "structured thinking", "clarity of communication", "speed + correctness".
  - common_concepts: e.g. arrays, hash maps, dynamic programming, joins, star schema, microservices, CAP theorem.
  - question_patterns: generalized patterns like:
       "implement a data structure", "optimize a schedule", "design a logging service".
  - example_question_themes: realistic but non-proprietary themes like:
       "Design an API for a ride-sharing app", "Compute metrics from event logs", "Debug a flaky data pipeline".
  - tips: concrete advice like:
       "Speak your thought process", "Clarify constraints before coding", "Use STAR for behavioral answers".

DO NOT:
- Output raw JSON dumps inside any field.
- Copy large chunks of role_json or resume_json verbatim.
- Invent technologies not seen in role_profile or resume_profile.
"""
    )

    prompt = tmpl.substitute(
        company=company,
        role=role,
        role_json=role_json,
        resume_json=resume_json,
        fit_json=fit_json,
        user_review_text=user_review_text.replace('"', "'"),
        user_insight_text=user_insight_text.replace('"', "'"),
    )

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.25,
        response_format={"type": "json_object"},
    )

    raw = resp.choices[0].message.content

    try:
        data = json.loads(raw)
    except Exception:
        data = {}

    # defaults
    defaults = {
        "intro_message": "Thank you for choosing HireSense!",
        "friendly_summary": "",
        "role_expectations_explained": "",
        "resume_strengths_explained": "",
        "resume_gaps_explained": "",
        "fit_explained": "",
        "action_plan": {
            "quick_wins": [],
            "4_week_plan": [],
            "resume_fixes": [],
            "project_ideas": [],
        },
        "round_deep_dive": [],
    }

    for k, v in defaults.items():
        if k not in data:
            data[k] = v

    return data
