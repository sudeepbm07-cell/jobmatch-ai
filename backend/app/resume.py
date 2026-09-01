from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz

from app.ai.analyzer import analyze_resume
from app.matcher import match_resume_to_jobs
from app.job_search import multi_search
from app.resume_validator import is_likely_resume

router = APIRouter(
    prefix="/api/resume",
    tags=["Resume"]
)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...)
):
    # ============================================================
    # 1. CHECK FILE TYPE
    # ============================================================

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was selected."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    # ============================================================
    # 2. READ UPLOADED FILE
    # ============================================================

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    # ============================================================
    # 3. CHECK FILE SIZE
    # ============================================================

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Please add a PDF less than 10 MB."
        )

    # ============================================================
    # 4. EXTRACT TEXT FROM PDF
    # ============================================================

    try:
        pdf = fitz.open(
            stream=contents,
            filetype="pdf"
        )

        extracted_text = ""

        for page in pdf:
            page_text = page.get_text()

            if page_text:
                extracted_text += page_text + "\n"

        page_count = len(pdf)
        pdf.close()

    except Exception as error:
        print("=" * 60)
        print("PDF EXTRACTION ERROR:")
        print(repr(error))
        print("=" * 60)

        raise HTTPException(
            status_code=400,
            detail="Could not read the PDF."
        )

    # ============================================================
    # 5. CHECK EXTRACTED TEXT
    # ============================================================

    extracted_text = extracted_text.strip()

    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not extract text from this PDF. "
                "Please upload a text-based PDF resume."
            )
        )

    # ============================================================
    # 6. VALIDATE THAT THIS IS ACTUALLY A RESUME
    # ============================================================

    if not is_likely_resume(extracted_text):
        raise HTTPException(
            status_code=400,
            detail="This doesn't look like a resume. Please upload your resume."
        )

    # ============================================================
    # 7. SEND RESUME TO GEMINI AI
    # ============================================================

    try:
        analysis = analyze_resume(extracted_text)

    except Exception as error:
        print("=" * 60)
        print("AI ANALYSIS ERROR:")
        print(repr(error))
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(error)}"
        )

    # ============================================================
    # 8. FETCH REAL, LIVE JOBS BASED ON THE RESUME
    # ============================================================

    try:
        roles = analysis.get("recommended_roles") or []
        queries = roles[:3] if roles else ["software developer"]

        real_jobs = multi_search(
            queries,
            location="India",
            results_per_query=10
        )

        if not real_jobs:
            fallback_skills = (
                analysis.get("programming_languages", [])
                or analysis.get("skills", [])
            )
            fallback_query = (
                fallback_skills[0]
                if fallback_skills
                else "software developer"
            )
            real_jobs = multi_search(
                [fallback_query],
                location="India",
                results_per_query=10
            )

    except Exception as error:
        print("=" * 60)
        print("JOB FETCH ERROR:")
        print(repr(error))
        print("=" * 60)

        real_jobs = []

    # ============================================================
    # 9. MATCH RESUME WITH REAL JOBS
    # ============================================================

    try:
        job_matches = match_resume_to_jobs(
            analysis,
            real_jobs
        )

    except Exception as error:
        print("=" * 60)
        print("JOB MATCHING ERROR:")
        print(repr(error))
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=f"Job matching failed: {str(error)}"
        )

    # ============================================================
    # 10. TEXT PREVIEW
    # ============================================================

    text_preview = extracted_text[:1500]

    # ============================================================
    # 11. RETURN COMPLETE RESULT
    # ============================================================

    return {
        "success": True,
        "filename": file.filename,
        "message": "Resume analyzed and matched successfully.",
        "pages": page_count,
        "text_length": len(extracted_text),
        "text_preview": text_preview,

        # Gemini analysis
        "analysis": analysis,

        # Live job matching results
        "job_matches": job_matches
    }