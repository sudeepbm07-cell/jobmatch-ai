# AI Job Scraper & Resume Matcher

An AI-powered job discovery and resume matching application that collects relevant job listings, extracts important job details, and helps users identify opportunities that best match their skills and profile.

## 🚀 Project Overview

The system automates the job-search process by scraping job postings and organizing them into structured data. It can then be extended with resume parsing and skill-based matching to rank jobs according to a candidate's profile.

### Current Output

The job scraper successfully collected **73 job listings** in structured JSON format.

Each job record can contain:

- Job ID
- Job title
- Company
- Location
- Employment type
- Required skills
- General requirements
- Job description
- Salary information
- Experience requirement
- Work mode
- Application URL
- Posted date/label

## ✨ Key Features

- Automated job scraping
- Structured job data extraction
- Job title, company, location and skill extraction
- Salary and experience information capture
- Direct application URL collection
- JSON-based job storage
- Resume-to-job matching architecture
- Skill-based job ranking
- Scalable architecture for future AI/LLM integration

## 🏗️ System Workflow

```text
Job Sources
    ↓
Job Scraper
    ↓
Job Data Extraction
    ↓
Structured JSON / Database
    ↓
Resume Upload
    ↓
Resume Text & Skill Extraction
    ↓
Resume ↔ Job Matching
    ↓
Match Score Calculation
    ↓
Ranked Job Recommendations
```

## 🛠️ Technology Stack

- Python
- Web Scraping
- JSON
- Natural Language Processing (NLP)
- Resume Parsing
- Skill Matching
- REST/API integration (where applicable)
- Git & GitHub

## 📂 Suggested Project Structure

```text
AI-Job-Scraper/
│
├── data/
│   └── jobs.json
│
├── scraper/
│   └── scraper.py
│
├── resume/
│   └── resume_parser.py
│
├── matcher/
│   └── matcher.py
│
├── app/
│   └── app.py
│
├── requirements.txt
├── .env.example
└── README.md
```

> Update the folder names above if your actual implementation uses a different structure.

## 📊 Example Job Record

```json
{
  "id": "5864091277",
  "title": "Java Software Lead",
  "company": "Eurofins GSC IT DC",
  "location": "Bangalore, Karnataka",
  "type": "Full-time",
  "skills": ["Java"],
  "general_requirements": [],
  "description": "Job description...",
  "salary": "Not disclosed",
  "experience": "Not specified",
  "work_mode": "On-site",
  "apply_url": "https://example.com/job",
  "posted_label": "Posted today"
}
```

## 🔐 Environment Variables

If API keys or other credentials are required, keep them in a local `.env` file.

**Never commit `.env` or secret API keys to GitHub.**

Use `.env.example` to document required variables without exposing their values.

## ▶️ Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the scraper:

```bash
python scraper/scraper.py
```

Then run the application using the command defined by your implementation.

## 🎯 Future Enhancements

- Upload resumes in PDF/DOCX format
- Automatic resume text extraction
- NLP-based skill extraction
- Semantic similarity using embeddings
- AI-powered job matching
- Match percentage for every job
- Personalized job recommendations
- Filters for location, salary, experience and work mode
- Streamlit/React dashboard
- Scheduled job scraping
- Database integration
- Email/job alerts

## 📌 Project Goal

The goal of this project is to reduce the time candidates spend manually searching and comparing job opportunities by automatically collecting job postings and ranking opportunities according to the candidate's skills and resume.

## 👨‍💻 Project Status

**Phase 1:** Job scraping and structured job extraction — ✅ Completed

**Phase 2:** Resume parsing — 🔄 Next

**Phase 3:** Resume-job matching — 🔄 Planned

**Phase 4:** Ranked recommendation dashboard — 🔄 Planned
