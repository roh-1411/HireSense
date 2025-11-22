# agents/resume_reality_agent.py

from typing import Dict, Any, List
from string import Template
import json
from agents.openai_client import get_client


def build_resume_profile(
    resume_text: str,
    extracted_skills: str = "",
    user_review_text: str = "",
    user_insight_text: str = "",
    parsed: Dict[str, Any] = None,
) -> Dict[str, Any]:

    """
    Stage 2: Resume Reality Engine
    - Infer the resume's real domain, strengths, weaknesses, tech stack, and signals.
    - RAW, honest, recruiter-style judgment (will be softened later).
    """

    client = get_client()

    prompt_template = """
You are HireSense's RESUME REALITY ENGINE.

Your job:
- Read the resume text and extracted skills.
- Infer the *real* domain and profile of this candidate.
- Be direct and honest (this is not user-facing yet).

Domains you can use:
- "Software Engineering"
- "Data Engineering"
- "Data Science / ML"
- "Analytics / BI"
- "DevOps / Infra / SRE"
- "Product / Business / Other"

RESUME SKILLS:
$extracted_skills

RESUME TEXT:
$resume_text

Return ONLY valid JSON with this exact structure:

{
  "resume_domain": "",            // one of the domains above (best guess)
  "core_strengths_raw": [],       // direct strengths e.g. "Strong Python + SQL", "Hands-on Spark + Airflow"
  "core_weaknesses_raw": [],      // direct weaknesses e.g. "No evidence of system design", "Projects look academic"
  "tech_stack_clusters": [],      // grouped stacks e.g. ["Python + SQL + Pandas", "Spark + Kafka"]
  "project_signals": [],          // what the projects reveal (toy vs production, scale, ownership)
  "seniority_signal": "",         // e.g. "student / fresher", "junior", "mid-level"
  "missing_signals_for_role": []  // generic gaps that would matter for most tech roles (even before knowing exact role)
}
"""

    prompt = Template(prompt_template).substitute(
        extracted_skills=extracted_skills or "Not provided.",
        resume_text=resume_text or "Not provided.",
    )

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content

    try:
        data = json.loads(raw)
    except Exception:
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            data = json.loads(raw[start : end + 1])
        except Exception:
            data = {}

    defaults = {
        "resume_domain": "",
        "core_strengths_raw": [],
        "core_weaknesses_raw": [],
        "tech_stack_clusters": [],
        "project_signals": [],
        "seniority_signal": "",
        "missing_signals_for_role": [],
    }

    for k, v in defaults.items():
        if k not in data:
            data[k] = v

    return data
