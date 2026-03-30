"""Pydantic models for request / response validation."""

from pydantic import BaseModel, HttpUrl, Field
from enum import Enum
from typing import Optional
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class CrawlRequest(BaseModel):
    url: HttpUrl
    depth: int = Field(default=1, ge=0, le=5, description="Recursion depth (0-5)")
    same_domain_only: bool = Field(
        default=True,
        description="Only follow links on the same domain",
    )


class PageResult(BaseModel):
    url: str
    title: str
    depth: int
    link_count: int
    success: bool
    error: Optional[str] = None


class CrawlJob(BaseModel):
    job_id: str
    status: JobStatus
    url: str
    depth: int
    same_domain_only: bool
    pages_downloaded: int = 0
    total_pages_found: int = 0
    pages: list[PageResult] = []
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
