import re

# ============================================================
# RESUME VALIDATION
# Category-based heuristic — a real resume almost always has
# contact info PLUS several structural sections together.
# A single keyword match (e.g. one stray "experience" mention)
# is no longer enough on its own.
# ============================================================

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(\+?\d{1,3}[-.\s]?)?\d{10}")

EDUCATION_TERMS = [
    "education", "b.tech", "btech", "b.e", "bachelor", "master", "m.tech",
    "cgpa", "gpa", "university", "college", "institute of technology",
    "diploma", "12th", "10th", "high school",
]

SKILLS_TERMS = [
    "skills", "technical skills", "programming languages",
    "technologies", "tools & technologies", "core competencies",
]

EXPERIENCE_TERMS = [
    "experience", "work experience", "professional experience",
    "internship", "internships", "employment history",
]

PROJECTS_TERMS = [
    "projects", "personal projects", "academic projects",
]

SUMMARY_TERMS = [
    "objective", "career objective", "summary", "professional summary",
    "profile", "about me",
]

OTHER_RESUME_TERMS = [
    "certifications", "achievements", "linkedin", "github",
    "portfolio", "declaration", "languages known", "references",
    "extracurricular", "hobbies", "date of birth",
]

MIN_TEXT_LENGTH = 150
MIN_CATEGORY_MATCHES = 3   # out of 6 categories below
MIN_TOTAL_KEYWORD_HITS = 4


def _text_contains_any(text_lower: str, terms: list) -> bool:
    return any(term in text_lower for term in terms)


def is_likely_resume(text: str) -> bool:
    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return False

    text_lower = text.lower()

    has_contact = bool(
        EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text)
    )
    has_education = _text_contains_any(text_lower, EDUCATION_TERMS)
    has_skills = _text_contains_any(text_lower, SKILLS_TERMS)
    has_experience = _text_contains_any(text_lower, EXPERIENCE_TERMS)
    has_projects = _text_contains_any(text_lower, PROJECTS_TERMS)
    has_summary = _text_contains_any(text_lower, SUMMARY_TERMS)
    has_other = _text_contains_any(text_lower, OTHER_RESUME_TERMS)

    category_matches = sum([
        has_contact,
        has_education,
        has_skills,
        has_experience,
        has_projects,
        has_summary,
        has_other,
    ])

    total_keyword_hits = sum(
        1 for term_list in [
            EDUCATION_TERMS, SKILLS_TERMS, EXPERIENCE_TERMS,
            PROJECTS_TERMS, SUMMARY_TERMS, OTHER_RESUME_TERMS,
        ]
        for term in term_list
        if term in text_lower
    )

    # A resume needs contact info AND at least 2 other structural
    # sections (education/skills/experience/projects/summary/etc),
    # OR a strong overall keyword density even without contact info
    # (e.g. resume with contact details in an image/header the PDF
    # parser missed).
    if has_contact and category_matches >= MIN_CATEGORY_MATCHES:
        return True

    if total_keyword_hits >= MIN_TOTAL_KEYWORD_HITS and category_matches >= MIN_CATEGORY_MATCHES:
        return True

    return False