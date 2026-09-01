import os
import re
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"

# Preferred recency window — widened automatically if this returns nothing
MAX_JOB_AGE_DAYS = 30

# ============================================================
# SKILL VOCABULARY
# ============================================================

SKILL_VOCABULARY = [
    "python", "java", "c++", "c#", "javascript", "typescript", "go", "rust",
    "react.js", "react", "angular", "vue.js", "vue", "next.js", "html", "css",
    "tailwind css", "bootstrap",
    "node.js", "express.js", "django", "flask", "fastapi", "spring boot",
    "rest apis", "graphql", "microservices",
    "mongodb", "mysql", "postgresql", "sql", "redis", "firebase",
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "opencv", "computer vision", "nlp", "numpy", "pandas", "scikit-learn",
    "data structures", "algorithms", "oop", "system design",
    "git", "github", "docker", "kubernetes", "aws", "azure", "gcp",
    "ci/cd", "jenkins", "linux",
]

# ============================================================
# GENERAL / SOFT REQUIREMENTS
# Keys must match matcher.py's GENERAL_REQUIREMENT_WEIGHTS exactly.
# ============================================================

GENERAL_REQUIREMENTS_VOCAB = [
    "communication skills", "team player", "teamwork", "problem solving",
    "analytical skills", "leadership", "self motivated", "time management",
    "interpersonal skills", "attention to detail", "bachelor's degree",
    "agile", "scrum", "client interaction", "stakeholder management",
    "multitasking",
]

_JOB_CACHE = {}


def _extract_terms(text, vocabulary):
    text_lower = (text or "").lower()
    found = []
    for term in vocabulary:
        pattern = r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.append(term)
    return found


def _extract_skills(text):
    raw = _extract_terms(text, SKILL_VOCABULARY)
    return [t.title() if t.islower() else t for t in raw]


def _extract_general_requirements(text):
    return _extract_terms(text, GENERAL_REQUIREMENTS_VOCAB)


def _parse_created(raw_created):
    if not raw_created:
        return None
    try:
        return datetime.fromisoformat(raw_created.replace("Z", "+00:00"))
    except ValueError:
        return None


def _is_recent(raw_created, max_age_days):
    posted_dt = _parse_created(raw_created)
    if posted_dt is None:
        return False

    now = datetime.now(timezone.utc)
    return (now - posted_dt).days <= max_age_days


def _format_dates(raw_created):
    posted_dt = _parse_created(raw_created)

    if posted_dt is None:
        return {
            "posted_label": "Recently posted",
            "apply_by_label": "See listing for details",
        }

    now = datetime.now(timezone.utc)
    delta_days = (now - posted_dt).days

    if delta_days <= 0:
        posted_label = "Posted today"
    elif delta_days == 1:
        posted_label = "Posted 1 day ago"
    elif delta_days < 30:
        posted_label = f"Posted {delta_days} days ago"
    else:
        months = delta_days // 30
        posted_label = f"Posted {months} month{'s' if months > 1 else ''} ago"

    apply_by_dt = posted_dt + timedelta(days=30)
    apply_by_label = apply_by_dt.strftime("%d %b %Y") + " (estimated)"

    return {
        "posted_label": posted_label,
        "apply_by_label": apply_by_label,
    }


def _normalize_job(raw):
    job_id = str(raw.get("id"))
    company = raw.get("company", {}).get("display_name", "Unknown Company")
    location = raw.get("location", {}).get("display_name", "India")
    description = raw.get("description", "")
    title = raw.get("title", "Untitled Role")

    combined_text = f"{title} {description}"
    skills = _extract_skills(combined_text)
    general_requirements = _extract_general_requirements(combined_text)

    salary_min = raw.get("salary_min")
    salary_max = raw.get("salary_max")
    if salary_min and salary_max:
        salary = f"₹{int(salary_min):,} - ₹{int(salary_max):,}/year"
    else:
        salary = "Not disclosed"

    contract_time = raw.get("contract_time", "")
    if "intern" in title.lower():
        job_type = "Internship"
    elif contract_time == "part_time":
        job_type = "Part-time"
    else:
        job_type = "Full-time"

    date_info = _format_dates(raw.get("created"))

    job = {
        "id": job_id,
        "title": title,
        "company": company,
        "location": location,
        "type": job_type,
        "skills": skills,
        "general_requirements": general_requirements,
        "description": description[:600],
        "salary": salary,
        "experience": "Fresher" if job_type == "Internship" else "Not specified",
        "work_mode": "On-site",
        "apply_url": raw.get("redirect_url", ""),
        "posted_label": date_info["posted_label"],
        "apply_by_label": date_info["apply_by_label"],
        "_created_raw": raw.get("created", ""),
    }

    _JOB_CACHE[job_id] = job
    return job


def search_jobs(query="software developer", location="India", country="in",
                 results_per_page=20, page=1, max_age_days=MAX_JOB_AGE_DAYS):
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise RuntimeError(
            "ADZUNA_APP_ID / ADZUNA_APP_KEY not configured. "
            "Sign up free at https://developer.adzuna.com/ and add them to backend/.env"
        )

    url = f"{ADZUNA_BASE_URL}/{country}/search/{page}"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "where": location,
        "sort_by": "date",
        "content-type": "application/json",
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    raw_jobs = response.json().get("results", [])
    print(f"[job_search] query='{query}' location='{location}' -> {len(raw_jobs)} raw results from Adzuna")

    # --------------------------------------------------------
    # Try the requested recency window first
    # --------------------------------------------------------

    recent_raw_jobs = [
        raw for raw in raw_jobs
        if _is_recent(raw.get("created"), max_age_days)
    ]

    # --------------------------------------------------------
    # Fallback: widen the window instead of returning nothing
    # --------------------------------------------------------

    if not recent_raw_jobs and raw_jobs:
        for fallback_days in (60, 90, 180):
            recent_raw_jobs = [
                raw for raw in raw_jobs
                if _is_recent(raw.get("created"), fallback_days)
            ]
            if recent_raw_jobs:
                print(f"[job_search] no results within {max_age_days} days — widened to {fallback_days} days")
                break

        if not recent_raw_jobs:
            print("[job_search] no dated results at all — showing all raw results as fallback")
            recent_raw_jobs = raw_jobs

    normalized = [_normalize_job(raw) for raw in recent_raw_jobs]

    normalized.sort(key=lambda j: j.get("_created_raw", ""), reverse=True)

    for job in normalized:
        job.pop("_created_raw", None)

    return normalized


def get_cached_job(job_id):
    return _JOB_CACHE.get(str(job_id))


def multi_search(queries, location="India", country="in", results_per_query=10,
                  max_age_days=MAX_JOB_AGE_DAYS):
    all_jobs = {}
    for q in queries:
        try:
            jobs = search_jobs(
                query=q,
                location=location,
                country=country,
                results_per_page=results_per_query,
                max_age_days=max_age_days,
            )
            for job in jobs:
                all_jobs[job["id"]] = job
        except Exception as error:
            print(f"Job search failed for query '{q}': {error}")
    return list(all_jobs.values())