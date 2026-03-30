"""API routes for the Article Downloader."""

import asyncio
import os
import zipfile
import io
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

from app.crawler import create_job, crawl, get_job, list_jobs, DOWNLOAD_DIR
from app.models import CrawlRequest, CrawlJob

router = APIRouter()


@router.post("/crawl", response_model=CrawlJob)
async def start_crawl(req: CrawlRequest, background_tasks: BackgroundTasks):
    """Start a new crawl job. Returns immediately with the job info."""
    job = create_job(str(req.url), req.depth, req.same_domain_only)
    background_tasks.add_task(crawl, job.job_id, str(req.url), req.depth, req.same_domain_only)
    return job


@router.get("/jobs", response_model=list[CrawlJob])
async def get_jobs():
    """List all crawl jobs."""
    return list_jobs()


@router.get("/jobs/{job_id}", response_model=CrawlJob)
async def get_job_status(job_id: str):
    """Get status of a specific crawl job."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs/{job_id}/download")
async def download_job(job_id: str):
    """Download all crawled pages for a job as a ZIP file."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job_dir = os.path.join(DOWNLOAD_DIR, job_id)
    if not os.path.isdir(job_dir):
        raise HTTPException(status_code=404, detail="No downloaded files found")

    # Build a ZIP in memory
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename in os.listdir(job_dir):
            filepath = os.path.join(job_dir, filename)
            if os.path.isfile(filepath):
                zf.write(filepath, arcname=filename)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=articles_{job_id}.zip"},
    )


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a crawl job and its downloaded files."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    # Clean up files
    job_dir = os.path.join(DOWNLOAD_DIR, job_id)
    if os.path.isdir(job_dir):
        import shutil
        shutil.rmtree(job_dir, ignore_errors=True)

    from app.crawler import _jobs
    _jobs.pop(job_id, None)

    return {"detail": "Job deleted"}
