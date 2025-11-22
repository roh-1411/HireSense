#############################################
# HireSense – Advanced Resume Parser Agent v2.0
# - Handles PDF upload or raw text
# - Uses LLM for deep structured parsing
# - Extracts:
#     * clean_text
#     * skills_raw_exact (as written in resume)
#     * skills_grouped (normalized/grouped skills)
#     * education / experience / projects / certifications
#     * summary_points
#     * detected_resume_domain
#     * tech_stack_clusters
#############################################

from typing import Dict, Any, List
import re
import json
from string import Template

import pdfplumber
from agents.openai_client import get_client


#############################################
# UTILITIES
#############################################

def _clean_text(text: str) -> str:
    """Normalize whitespace and remove junk characters."""
    if not text:
        return ""
    text = text.replace("\x00", "")
    text = text.replace("\r", "\n")
    # collapse multiple spaces/newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def _fallback_sections(text: str) -> Dict[str, Any]:
    """Very rough fallback if LLM parsing fails."""
    sections = {
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "summary_points": [],
        "detected_resume_domain": "",
        "tech_stack_clusters": [],
        "skills_extracted": [],
    }

    if not text:
        return sections

    # naive splitting by headings
    lower = text.lower()

    def grab_block(keyword: str, next_keywords: List[str]) -> str:
        idx = lower.find(keyword)
        if idx == -1:
            return ""
        next_idx_candidates = [lower.find(k, idx + len(keyword)) for k in next_keywords if lower.find(k, idx + len(keyword)) != -1]
        end = min(next_idx_candidates) if next_idx_candidates else len(text)
        return text[idx:end].strip()

    sections["education"] = [grab_block("education", ["experience", "projects", "skills", "certification"])]
    sections["experience"] = [grab_block("experience", ["education", "projects", "skills", "certification"])]
    sections["projects"] = [grab_block("projects", ["experience", "education", "skills", "certification"])]
    sections["certifications"] = [grab_block("certification", ["experience", "education", "projects", "skills"])]

    return sections


#############################################
# LLM HELPERS
#############################################

def _llm_structured_parse(resume_text: str) -> Dict[str, Any]:
    """
    Use LLM to parse resume into structured sections + grouped skills.
    """
    client = get_client()

    tmpl = Template(
        """
You are the ADVANCED RESUME PARSER for HireSense.

Your job is to read the resume text below and extract a clean, structured JSON representation.

Resume text:
$resume_text

Return ONLY valid JSON in this exact structure:

{
  "clean_text": "",
  "education": [],
  "experience": [],
  "projects": [],
  "certifications": [],
  "summary_points": [],
  "detected_resume_domain": "",
  "tech_stack_clusters": [],
  "skills_extracted": []
}

Guidelines:
- "clean_text": a lightly cleaned version of the resume in plain text.
- "education": list of concise strings summarizing degrees, schools, years.
- "experience": list of concise strings summarizing roles, companies, durations, and key impacts.
- "projects": list of concise descriptions of projects + tech stack + outcomes.
- "certifications": list of certifications, licenses, or notable courses.
- "summary_points": high-level bullet-style points capturing the candidate profile.
- "detected_resume_domain": one of: "SWE", "Data Engineering", "Data Science / Analytics", "ML / AI", "DevOps / SRE", "Full-Stack", "Backend", "Frontend", "Other".
- "tech_stack_clusters": high-level groupings like:
    ["Python + Pandas + SQL (data analytics stack)", "Java + Spring Boot (backend)", "React + TypeScript (frontend)", "AWS Lambda + DynamoDB + S3 (cloud)"].
- "skills_extracted": a list of normalized skill names (e.g., "Python", "Apache Spark", "AWS Lambda", "Google BigQuery", "React", "Docker").
- Do NOT invent experience or degrees that are not in the resume.
- Only extract what is actually supported by the text.
"""
    )

    prompt = tmpl.substitute(
        resume_text=resume_text.replace('"', "'")
    )

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    raw = resp.choices[0].message.content
    try:
        data = json.loads(raw)
    except Exception:
        data = _fallback_sections(resume_text)

    # ensure all keys exist
    defaults = {
        "clean_text": resume_text,
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "summary_points": [],
        "detected_resume_domain": "",
        "tech_stack_clusters": [],
        "skills_extracted": [],
    }
    for k, v in defaults.items():
        if k not in data:
            data[k] = v

    return data


def _llm_exact_skills(resume_text: str) -> List[str]:
    """
    Use LLM to extract EXACT skills as they appear in the resume text.
    No normalization, no rewriting – literal phrases.
    """
    client = get_client()

    tmpl = Template(
        """
You are the EXACT SKILL EXTRACTOR AGENT for HireSense.

Your task:
- Read the resume text below.
- Extract ALL technical skills, tools, libraries, frameworks, cloud services, databases, platforms, and languages.
- Return them EXACTLY as written in the resume:
  - Preserve capitalization (e.g., "Python", "AWS Lambda", "Google BigQuery", "C++", "PyTorch").
  - Preserve spaces and punctuation.
- Do NOT:
  - Normalize or reword skills.
  - Add skills that are not present.
  - Merge or group skills.
  - Expand abbreviations.

Return ONLY valid JSON:

{
  "skills_raw_exact": []
}

Resume text:
$resume_text
"""
    )

    prompt = tmpl.substitute(
        resume_text=resume_text.replace('"', "'")
    )

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"},
    )

    raw = resp.choices[0].message.content
    try:
        data = json.loads(raw)
        skills = data.get("skills_raw_exact", [])
        # ensure list of strings
        skills = [s for s in skills if isinstance(s, str)]
        return skills
    except Exception:
        return []


#############################################
# MAIN ENTRYPOINT
#############################################

def parse_resume(uploaded_file_or_text) -> Dict[str, Any]:
    """
    Main function used by app.py

    It accepts either:
      - A Streamlit UploadedFile (PDF)
      - A raw text string

    Returns a dict with at least:
      - "resume_text": cleaned resume text
      - "skills_raw_exact": list[str]
      - "skills_grouped": list[str]
      - "education", "experience", "projects", "certifications"
      - "summary_points"
      - "detected_resume_domain"
      - "tech_stack_clusters"
    """

    resume_text = ""

    # Case 1: Streamlit UploadedFile (PDF)
    if hasattr(uploaded_file_or_text, "read"):
        try:
            with pdfplumber.open(uploaded_file_or_text) as pdf:
                pages = []
                for page in pdf.pages:
                    extracted = page.extract_text() or ""
                    pages.append(extracted)
                resume_text = "\n".join(pages)
        except Exception as e:
            print("PDF parsing failed in resume_parser_agent:", e)
            resume_text = ""

    # Case 2: Already a raw string
    elif isinstance(uploaded_file_or_text, str):
        resume_text = uploaded_file_or_text

    resume_text = _clean_text(resume_text)

    if not resume_text:
        # Return empty skeleton if nothing to parse
        return {
            "resume_text": "",
            "skills_raw_exact": [],
            "skills_grouped": [],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "summary_points": [],
            "detected_resume_domain": "",
            "tech_stack_clusters": [],
        }

    # ---- LLM structured parse ----
    structured = _llm_structured_parse(resume_text)

    # ---- LLM exact skills ----
    skills_exact = _llm_exact_skills(resume_text)

    # Backfill if exact skills LLM fails
    if not skills_exact:
        # fallback: use structured["skills_extracted"] as approximate
        skills_exact = structured.get("skills_extracted", [])

    return {
        "resume_text": structured.get("clean_text", resume_text),
        "skills_raw_exact": skills_exact,
        "skills_grouped": structured.get("skills_extracted", []),
        "education": structured.get("education", []),
        "experience": structured.get("experience", []),
        "projects": structured.get("projects", []),
        "certifications": structured.get("certifications", []),
        "summary_points": structured.get("summary_points", []),
        "detected_resume_domain": structured.get("detected_resume_domain", ""),
        "tech_stack_clusters": structured.get("tech_stack_clusters", []),
    }
