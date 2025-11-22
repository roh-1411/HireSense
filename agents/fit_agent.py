#############################################
# HireSense – Fit Agent v2.0
#
# Computes alignment between:
#   - Role Reality (expectations)
#   - Resume Reality (capabilities)
#
# Produces:
#   * skill_match_score
#   * project_fit
#   * seniority_fit
#   * domain_fit
#   * risks
#   * strengths
#   * priority_gaps
#   * final_fit_category
#############################################

from typing import Dict, Any, List
import json
from string import Template
from agents.openai_client import get_client


#############################################
# MAIN FIT AGENT
#############################################

def compute_fit_profile(
    role_profile: Dict[str, Any],
    resume_profile: Dict[str, Any],
) -> Dict[str, Any]:

    client = get_client()

    # --------------------------
    # PREPARE DATA
    # --------------------------

    role_json = json.dumps(role_profile, indent=2)
    resume_json = json.dumps(resume_profile, indent=2)

    # --------------------------
    # PROMPT
    # --------------------------

    tmpl = Template(
        """
You are the FIT ANALYSIS ENGINE for HireSense.

Your job:
- Compare the REAL role expectations (role_profile)
- With the REAL resume capabilities (resume_profile)
- Produce a QUANTITATIVE & QUALITATIVE alignment report

========================================
ROLE PROFILE (REALITY)
========================================
$role_json

========================================
RESUME PROFILE (REALITY)
========================================
$resume_json

========================================
OUTPUT JSON FORMAT (STRICT)
========================================

{
  "skill_match_score": 0,      
  "seniority_fit": "",
  "domain_fit": "",
  "experience_fit": "",
  "project_fit": "",
  "overall_alignment_notes": [],

  "matched_strengths": [],
  "mismatched_risks": [],
  "priority_gaps": [],
  "missing_role_requirements": [],

  "fit_summary_category": "",  
  "fit_score_percentage": 0    
}

========================================
RULES
========================================

- "skill_match_score": 0–100 based only on skill comparison.
- “seniority_fit”: realistic match based on resume seniority vs role expectations.
- “domain_fit”: SWE vs DE vs DS vs ML vs Full-Stack vs Backend.
- “experience_fit”: whether experience level, duration, and impact patterns match expectations.
- “project_fit”: whether project themes match the job's expectations.
- "fit_summary_category": one of:
   "Excellent Fit", "Strong Fit", "Moderate Fit", "Weak Fit", "Misaligned".

- “fit_score_percentage”: an overall normalized fit score (0–100).
- DO NOT guess missing skills — use only what resume reality shows.
- DO NOT be friendly (the Friendly Agent handles tone). Be factual.
"""
    )

    prompt = tmpl.substitute(
        role_json=role_json,
        resume_json=resume_json
    )

    # --------------------------
    # CALL LLM
    # --------------------------

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content

    try:
        data = json.loads(raw)
    except Exception:
        data = {
            "skill_match_score": 0,
            "seniority_fit": "",
            "domain_fit": "",
            "experience_fit": "",
            "project_fit": "",
            "overall_alignment_notes": [],
            "matched_strengths": [],
            "mismatched_risks": [],
            "priority_gaps": [],
            "missing_role_requirements": [],
            "fit_summary_category": "Unknown",
            "fit_score_percentage": 0
        }

    return data
