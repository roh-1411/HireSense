#############################################
# HireSense – Role Reality Agent v2.0
# (Now accepts user_review_text + user_insight_text)
#############################################

from typing import Dict, Any, List
from string import Template
import json
from agents.openai_client import get_client


def build_role_profile(
    company: str,
    role: str,
    results: List[Dict[str, str]],
    user_review_text: str = "",
    user_insight_text: str = "",
) -> Dict[str, Any]:
    """
    Builds the REAL role expectations using:
    - SERP API search results
    - Public interview review patterns
    - User-provided review (optional)
    - User-provided insights (optional)
    """

    client = get_client()

    # Convert search results to text
    collected_reviews = ""
    for r in results:
        collected_reviews += f"[{r.get('source')}] {r.get('title')}\n{r.get('snippet')}\n\n"

    # -------------- PROMPT TEMPLATE -------------------
    tmpl = Template(
        """
You are the ROLE REALITY ENGINE for HireSense.

Your job is to create a **realistic role profile** for the company and role below,
based ONLY on **public interview patterns**, **review sources**, and the user-provided input.

========================================
COMPANY: $company
ROLE: $role
========================================

========================================
PUBLIC INTERVIEW REVIEW DATA (SERP API)
========================================
$collected_reviews

========================================
USER INTERVIEW EXPERIENCE (optional)
========================================
$user_review_text

========================================
USER INSIGHTS (optional)
========================================
$user_insight_text

========================================
OUTPUT FORMAT (RETURN ONLY JSON)
========================================
{
  "rounds": [],
  "round_count": "",
  "difficulty": "",
  "skills_most_often_required": [],
  "skills_nice_to_have": [],
  "common_interview_themes": [],
  "common_questions_patterns": [],
  "projects_they_like": [],
  "education_or_experience_expectations": [],
  "seniority_pattern": "",
  "public_interview_summary": ""
}

========================================
RULES:
- DO NOT guess proprietary content.
- Use only public patterns from reviews + user input.
- Provide difficulty levels realistically (Easy/Medium/Hard/Mixed).
- Include the most common interview concepts, rounds, and themes.
- Summarize ROUND BY ROUND (OA, DSA, System Design, Behavioral, ML/DE rounds).
"""
    )

    prompt = tmpl.substitute(
        company=company,
        role=role,
        collected_reviews=collected_reviews.replace('"', "'"),
        user_review_text=user_review_text.replace('"', "'"),
        user_insight_text=user_insight_text.replace('"', "'"),
    )

    # ------------------- LLM CALL -------------------
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
        data = {
            "rounds": [],
            "round_count": "",
            "difficulty": "",
            "skills_most_often_required": [],
            "skills_nice_to_have": [],
            "common_interview_themes": [],
            "common_questions_patterns": [],
            "projects_they_like": [],
            "education_or_experience_expectations": [],
            "seniority_pattern": "",
            "public_interview_summary": "",
        }

    return data
