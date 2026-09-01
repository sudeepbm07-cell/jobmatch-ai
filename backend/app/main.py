from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.resume import router as resume_router
from app.job_routes import router as job_router


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="JobMatch AI",
    description="AI-powered resume analysis and job matching API",
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Deployed frontend
        "https://jobmatch-ai-13zu.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REGISTER ROUTERS
# ============================================================

app.include_router(resume_router)
app.include_router(job_router)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "JobMatch AI",
    }


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "JobMatch AI Backend is running",
        "health": "/api/health",
        "jobs": "/api/jobs",
    }