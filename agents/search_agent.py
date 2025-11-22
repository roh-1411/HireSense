# agents/search_agent.py

import os
import requests
from typing import List, Dict


SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")


def _query_serpapi(q: str, num_results: int = 8) -> List[Dict[str, str]]:
    """Low-level helper to query SerpAPI Google Search."""
    if not SERPAPI_KEY:
        # Fail soft: if no key, return empty list so app still runs
        return []

    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": q,
        "api_key": SERPAPI_KEY,
        "num": num_results,
        "hl": "en",
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    results: List[Dict[str, str]] = []

    for item in data.get("organic_results", []):
        title = item.get("title") or ""
        snippet = item.get("snippet") or ""
        link = item.get("link") or ""

        if not (title and snippet):
            continue

        # try to categorize by domain
        domain = "web"
        if "glassdoor" in link:
            domain = "glassdoor"
        elif "reddit.com" in link:
            domain = "reddit"
        elif "geeksforgeeks" in link:
            domain = "geeksforgeeks"
        elif "leetcode.com" in link:
            domain = "leetcode_discuss"
        elif "teamblind" in link or "blind.com" in link:
            domain = "blind"

        results.append(
            {
                "source": domain,
                "title": title,
                "snippet": snippet,
                "url": link,
            }
        )

    return results


def search_public_interview_data(company: str, role: str) -> List[Dict[str, str]]:
    """
    High-level search for public interview reviews & patterns.

    Uses SerpAPI with focused queries targeting:
    - Glassdoor
    - Reddit
    - GeeksforGeeks
    - LeetCode Discuss
    - General interview-experience blogs
    """

    if not company and not role:
        return []

    base = f"{company} {role}".strip()

    queries = [
        f"{base} interview experience",
        f"{base} interview rounds",
        f"site:glassdoor.com {base} interview",
        f"site:reddit.com {company} interview experience",
        f"site:geeksforgeeks.org {company} interview experience",
        f"site:leetcode.com/discuss {company} interview",
        f"{company} {role} interview experience blog",
    ]

    all_results: List[Dict[str, str]] = []

    for q in queries:
        all_results.extend(_query_serpapi(q, num_results=8))

    # Deduplicate by URL
    seen_urls = set()
    deduped: List[Dict[str, str]] = []
    for r in all_results:
        url = r.get("url")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append(r)

    return deduped
