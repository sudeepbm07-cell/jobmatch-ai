import os
import json
import re
import time

from google import genai
from google.genai.errors import ServerError
from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured. "
        "Please add it to backend/.env"
    )

# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# ============================================================
# HELPER: CLEAN GEMINI RESPONSE
# ============================================================

def clean_json_response(text: str) -> str:
    text = text.strip()

    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text.strip()

# ============================================================
# HELPER: DEFAULT ANALYSIS
# ============================================================

def default_analysis():
    return {
        "candidate_summary": "Unable to generate detailed AI analysis.",
        "skills": [],
        "programming_languages": [],
        "frameworks_and_tools": [],
        "education": [],
        "projects": [],
        "experience_level": "Fresher",
        "strengths": [],
        "weaknesses": [],
        "recommended_roles": [],
        "skill_gaps": [],
        "career_roadmap": []
    }

# ============================================================
# MAIN RESUME ANALYZER
# ============================================================

def analyze_resume(resume_text: str):

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    resume_text = resume_text[:20000]

    prompt = f"""
You are an expert technical recruiter, resume analyst, career advisor, and software engineering hiring specialist.

Your task is to deeply analyze the resume provided below.

IMPORTANT:
- Use ONLY information actually present in the resume.
- Never invent companies, degrees, technologies, projects,
  certifications, work experience, or achievements.
- If information is not present, return an empty array or
  an appropriate statement.
- Be specific rather than generic.
- Return ONLY valid JSON.
- Do NOT return Markdown.
- Do NOT return ```json.
- Do NOT add explanations outside the JSON.

The output MUST follow this exact JSON structure:

{{
    "candidate_summary": "A professional 3-5 sentence summary based strictly on the resume.",

    "skills": [
        "individual technical or professional skill"
    ],

    "programming_languages": [
        "individual programming language"
    ],

    "frameworks_and_tools": [
        "framework, library, database, platform, or development tool"
    ],

    "education": [
        {{
            "degree": "degree name",
            "institution": "institution name",
            "duration": "duration or years if present",
            "cgpa": "CGPA/percentage if present"
        }}
    ],

    "projects": [
        {{
            "name": "project name",
            "year": "year if present",
            "technologies": [
                "technology actually mentioned"
            ],
            "description": "short description based only on resume"
        }}
    ],

    "experience_level": "Fresher",

    "strengths": [
        "specific strength supported by the resume"
    ],

    "weaknesses": [
        "specific area that appears weak or missing based on the resume"
    ],

    "recommended_roles": [
        "realistic job role"
    ],

    "skill_gaps": [
        "specific skill that would improve suitability for recommended roles"
    ],

    "career_roadmap": [
        "practical step 1",
        "practical step 2",
        "practical step 3"
    ]
}}

ANALYSIS REQUIREMENTS
=====================

1. CANDIDATE SUMMARY

Create a useful professional summary.

Mention when available:
- Degree
- Branch
- Current student/fresher status
- Main technical interests
- Important technologies
- Major projects
- Career direction

Do not invent anything.

2. SKILLS

Extract actual skills from the resume.

Separate individual skills.

Example:

[
    "Python",
    "C++",
    "Data Structures",
    "Machine Learning"
]

Do not combine everything into one string.

3. PROGRAMMING LANGUAGES

Extract ONLY actual programming languages.

Examples:

[
    "Python",
    "C++",
    "JavaScript"
]

Do not include frameworks here.

4. FRAMEWORKS AND TOOLS

Extract actual technologies such as:

- React
- Node.js
- FastAPI
- MongoDB
- MySQL
- Git
- GitHub
- TensorFlow

Only include technologies supported by the resume.

5. EDUCATION

Extract every education entry.

For each entry provide:

degree
institution
duration
cgpa

If something is unavailable, use an empty string.

6. PROJECTS

Extract every project you can identify.

For each project provide:

- name
- year
- technologies
- description

Do not invent technologies.

7. EXPERIENCE LEVEL

Classify the candidate as one of:

- Fresher
- Junior
- Mid
- Senior

Use "Fresher" for a current student with no professional full-time experience.

8. STRENGTHS

Identify real strengths from the resume.

Examples:

- Strong Python foundation
- Machine learning project experience
- Full-stack development interest
- Multiple technical projects

Avoid generic statements such as:

"Good candidate."

9. WEAKNESSES

Identify realistic improvement areas.

Do NOT criticize the candidate unnecessarily.

Consider:

- Missing skills
- Limited professional experience
- Lack of internships
- Limited project depth
- Missing industry technologies

10. RECOMMENDED ROLES

Recommend approximately 4-6 realistic roles.

Examples:

- Software Engineer
- Python Developer
- Full Stack Developer
- Machine Learning Engineer
- AI/ML Intern

Recommendations must be based on the actual resume.

11. SKILL GAPS

Identify skills that would improve the candidate's chances for the recommended roles.

For example:

- Advanced Data Structures and Algorithms
- REST API development
- Docker
- AWS
- System Design

Only recommend useful and realistic skills.

12. CAREER ROADMAP

Create 5-8 practical steps.

The roadmap should progress from:

Foundation → DSA → Development → Projects → Deployment → Interview preparation → Job applications

Make it useful for a college student/fresher.

RESUME
=======

{resume_text}
"""

    try:
        # ====================================================
        # CALL GEMINI (with retry on transient overload)
        # ====================================================

        max_retries = 3
        response = None

        for attempt in range(1, max_retries + 1):
            try:
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=prompt
                )
                break

            except ServerError as error:
                print(f"Gemini overloaded (attempt {attempt}/{max_retries}): {error}")

                if attempt == max_retries:
                    raise

                time.sleep(attempt * 3)

        if not response or not response.text:
            raise ValueError("Gemini returned an empty response.")

        text = clean_json_response(response.text)

        # ====================================================
        # PARSE JSON
        # ====================================================

        try:
            analysis = json.loads(text)
        except json.JSONDecodeError as error:
            print("=" * 60)
            print("JSON PARSING ERROR")
            print(repr(error))
            print("GEMINI RESPONSE:")
            print(text)
            print("=" * 60)

            raise ValueError(
                "Gemini returned an invalid JSON response."
            )

        # ====================================================
        # ENSURE REQUIRED FIELDS EXIST
        # ====================================================

        default = default_analysis()

        for key, default_value in default.items():
            if key not in analysis:
                analysis[key] = default_value

        # ====================================================
        # ENSURE ARRAY FIELDS ARE ARRAYS
        # ====================================================

        array_fields = [
            "skills",
            "programming_languages",
            "frameworks_and_tools",
            "education",
            "projects",
            "strengths",
            "weaknesses",
            "recommended_roles",
            "skill_gaps",
            "career_roadmap"
        ]

        for field in array_fields:
            if not isinstance(analysis[field], list):
                analysis[field] = []

        # ====================================================
        # RETURN CLEAN ANALYSIS
        # ====================================================

        return analysis

    except Exception as error:
        print("=" * 60)
        print("AI ANALYSIS ERROR")
        print(repr(error))
        print("=" * 60)

        raise