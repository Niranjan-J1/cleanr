import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid
import shutil
import pandas as pd
from pathlib import Path

from detector.engine import analyze_csv
from detector.fixer import Fixer
from detector.models import CleaningReport

app = FastAPI(title="CLEANR API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local storage folders — swap for S3 later
UPLOAD_DIR = Path("storage/uploads")
CLEAN_DIR  = Path("storage/cleaned")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# In-memory job store — swap for Redis/Postgres later
jobs = {}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted")

    # Validate file size (100MB limit)
    contents = await file.read()
    if len(contents) > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 100MB")

    # Save file
    job_id   = str(uuid.uuid4())
    filepath = UPLOAD_DIR / f"{job_id}.csv"
    with open(filepath, "wb") as f:
        f.write(contents)

    # Run analysis immediately (background tasks come later)
    report = analyze_csv(str(filepath), file.filename, job_id)

    # Store job
    jobs[job_id] = {
        "job_id":   job_id,
        "filename": file.filename,
        "status":   "analyzed",
        "report":   report,
    }

    return {
        "job_id":   job_id,
        "filename": file.filename,
        "status":   "analyzed",
    }


@app.get("/report/{job_id}")
def get_report(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    report = jobs[job_id]["report"]
    return report.to_dict()


@app.post("/fix/{job_id}")
def fix_csv(job_id: str, user_selections: dict):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job      = jobs[job_id]
    report   = job["report"]
    filepath = UPLOAD_DIR / f"{job_id}.csv"

    # Load original CSV and apply fixes
    df        = pd.read_csv(str(filepath), dtype=str)
    fixer     = Fixer(df, report, user_selections)
    clean_df  = fixer.apply_all()

    # Save clean file
    clean_path = CLEAN_DIR / f"{job_id}_clean.csv"
    clean_df.to_csv(str(clean_path), index=False)

    jobs[job_id]["status"]     = "fixed"
    jobs[job_id]["clean_path"] = str(clean_path)

    return {
        "job_id":  job_id,
        "status":  "fixed",
        "rows_in":  len(df),
        "rows_out": len(clean_df),
    }


@app.get("/download/{job_id}")
def download_csv(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job["status"] != "fixed":
        raise HTTPException(status_code=400, detail="File not fixed yet")

    clean_path = job["clean_path"]
    filename   = job["filename"].replace(".csv", "_clean.csv")

    return FileResponse(
        path=clean_path,
        filename=filename,
        media_type="text/csv"
    )