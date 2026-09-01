from fastapi import APIRouter, HTTPException, Query
from app.job_search import search_jobs, multi_search, get_cached_job

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

DEFAULT_CATEGORIES = [
    "software developer",
    "software engineer intern",
    "full stack developer",
    "python developer",
    "web developer intern",
    "machine learning intern",
    "data analyst",
    "backend developer",
]


@router.get("")
def get_jobs(
    q: str = Query("", description="Job title or keywords — leave blank for a broad mix"),
    location: str = Query("India"),
    job_type: str = Query("All"),
    max_age_days: int = Query(30, description="Only return jobs posted within this many days"),
):
    try:
        if q.strip():
            jobs = search_jobs(query=q, location=location, results_per_page=30, max_age_days=max_age_days)
        else:
            jobs = multi_search(DEFAULT_CATEGORIES, location=location, results_per_query=12, max_age_days=max_age_days)
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))

    if job_type != "All":
        jobs = [j for j in jobs if j["type"].lower() == job_type.lower()]

    return {"success": True, "count": len(jobs), "jobs": jobs}


@router.get("/{job_id}")
def get_job(job_id: str):
    job = get_cached_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found. Listings are fetched live and not stored permanently — try searching again."
        )
    return {"success": True, "job": job}


@router.get("/search/query")
def search_jobs_endpoint(q: str = "", job_type: str = "All", location: str = "India", max_age_days: int = 30):
    try:
        if q.strip():
            jobs = search_jobs(query=q, location=location, results_per_page=30, max_age_days=max_age_days)
        else:
            jobs = multi_search(DEFAULT_CATEGORIES, location=location, results_per_query=12, max_age_days=max_age_days)
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))

    if job_type != "All":
        jobs = [j for j in jobs if j["type"].lower() == job_type.lower()]

    return {"success": True, "count": len(jobs), "jobs": jobs}