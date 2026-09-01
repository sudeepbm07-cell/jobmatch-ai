from app.jobs import JOBS

# ============================================================
# NORMALIZE SKILLS
# ============================================================

def normalize_skill(skill):
    return skill.lower().strip()

# ============================================================
# SKILL WEIGHTS
# ============================================================

SKILL_WEIGHTS = {

    # Programming
    "python": 2.0,
    "c++": 2.0,
    "javascript": 2.0,
    "java": 2.0,

    # Frontend
    "react.js": 1.8,
    "html": 1.5,
    "css": 1.5,
    "tailwind css": 1.5,

    # Backend
    "node.js": 1.8,
    "express.js": 1.8,
    "fastapi": 1.8,
    "flask": 1.8,
    "rest apis": 1.5,

    # Databases
    "mongodb": 1.5,
    "mysql": 1.5,
    "sql": 1.5,

    # AI / ML
    "machine learning": 2.0,
    "deep learning": 2.0,
    "tensorflow": 1.8,
    "pytorch": 1.8,
    "opencv": 1.8,
    "computer vision": 2.0,
    "numpy": 1.3,
    "pandas": 1.3,

    # Core CS
    "data structures": 1.8,
    "algorithms": 1.8,
    "oop": 1.5,

    # Tools
    "git": 1.0,
    "github": 1.0,
    "docker": 1.3,
}

# ============================================================
# GENERAL / SOFT REQUIREMENT WEIGHTS
# Keys must match job_search.py's GENERAL_REQUIREMENTS_VOCAB exactly.
# ============================================================

GENERAL_REQUIREMENT_WEIGHTS = {
    "communication skills": 1.0,
    "team player": 0.8,
    "teamwork": 0.8,
    "problem solving": 1.0,
    "analytical skills": 1.0,
    "leadership": 0.8,
    "self motivated": 0.6,
    "time management": 0.6,
    "interpersonal skills": 0.7,
    "attention to detail": 0.6,
    "bachelor's degree": 1.0,
    "agile": 0.8,
    "scrum": 0.8,
    "client interaction": 0.7,
    "stakeholder management": 0.7,
    "multitasking": 0.6,
}

# ============================================================
# GET RESUME SKILLS
# ============================================================

def get_resume_skills(resume_analysis):

    resume_skills = set()

    for skill in resume_analysis.get("skills", []):
        resume_skills.add(normalize_skill(skill))

    for language in resume_analysis.get("programming_languages", []):
        resume_skills.add(normalize_skill(language))

    for tool in resume_analysis.get("frameworks_and_tools", []):
        resume_skills.add(normalize_skill(tool))

    return resume_skills


def _resume_text_blob(resume_analysis):
    parts = [resume_analysis.get("candidate_summary", "")]
    parts.extend(resume_analysis.get("strengths", []))
    parts.extend(resume_analysis.get("skills", []))
    return " ".join(parts).lower()

# ============================================================
# CALCULATE MATCH
# ============================================================

def calculate_match(resume_analysis, job):

    resume_skills = get_resume_skills(resume_analysis)
    resume_blob = _resume_text_blob(resume_analysis)

    job_skills = {
        normalize_skill(skill)
        for skill in job.get("skills", [])
    }

    matching_skills = sorted(resume_skills.intersection(job_skills))
    missing_skills = sorted(job_skills - resume_skills)

    # --------------------------------------------------------
    # WEIGHTED SCORE — hard skills
    # --------------------------------------------------------

    total_weight = 0
    matched_weight = 0

    for skill in job_skills:
        weight = SKILL_WEIGHTS.get(skill, 1.0)
        total_weight += weight

        if skill in resume_skills:
            matched_weight += weight

    # --------------------------------------------------------
    # WEIGHTED SCORE — general/soft requirements
    # --------------------------------------------------------

    for req in job.get("general_requirements", []):
        weight = GENERAL_REQUIREMENT_WEIGHTS.get(req, 0.6)
        total_weight += weight

        if req in resume_blob:
            matched_weight += weight

    if total_weight == 0:
        score = 0
    else:
        score = round((matched_weight / total_weight) * 100)

    # No job is ever a literal, guaranteed 100% match.
    score = min(score, 96)

    # --------------------------------------------------------
    # MATCH LABEL
    # --------------------------------------------------------

    if score >= 90:
        match_label = "Excellent Match"
    elif score >= 75:
        match_label = "Strong Match"
    elif score >= 60:
        match_label = "Good Match"
    else:
        match_label = "Needs Improvement"

    # --------------------------------------------------------
    # MATCH EXPLANATION
    # --------------------------------------------------------

    explanation = (
        f"You match {len(matching_skills)} "
        f"of {len(job_skills)} required skills."
    )

    if missing_skills:
        explanation += (
            f" Consider improving: "
            f"{', '.join(missing_skills[:3])}."
        )
    else:
        explanation += (
            " You have all the required skills "
            "for this role."
        )

    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {
        "job_id": job["id"],
        "title": job["title"],
        "company": job["company"],
        "location": job["location"],
        "type": job["type"],
        "description": job["description"],
        "match_score": score,
        "match_label": match_label,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "match_explanation": explanation,
        "posted_label": job.get("posted_label", ""),
        "apply_by_label": job.get("apply_by_label", ""),
    }

# ============================================================
# MATCH RESUME WITH ALL JOBS
# ============================================================

def match_resume_to_jobs(resume_analysis, jobs=None):

    if jobs is None:
        jobs = JOBS

    results = []

    for job in jobs:
        result = calculate_match(resume_analysis, job)
        results.append(result)

    results.sort(key=lambda x: x["match_score"], reverse=True)

    return results