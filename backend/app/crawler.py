"""Core crawling engine — recursively fetches and cleans articles."""

import asyncio
import hashlib
import os
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Comment
from readability import Document

from app.models import CrawlJob, JobStatus, PageResult

# ── settings ────────────────────────────────────────────────────────────
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", os.path.join(os.getcwd(), "downloads"))
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
USER_AGENT = (
    "Mozilla/5.0 (compatible; ArticleDownloader/1.0; "
    "+https://github.com/dulap16/article-downloader)"
)

# In-memory job store (swap for Redis / DB in production)
_jobs: dict[str, CrawlJob] = {}


def get_job(job_id: str) -> Optional[CrawlJob]:
    return _jobs.get(job_id)


def list_jobs() -> list[CrawlJob]:
    return sorted(_jobs.values(), key=lambda j: j.created_at, reverse=True)


# ── helpers ─────────────────────────────────────────────────────────────

def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:12]


def _safe_filename(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_") or "index"
    return f"{parsed.netloc}_{path}_{_url_hash(url)}.html"


def _is_article_link(href: str) -> bool:
    """Filter out non-article links (anchors, mailto, javascript, etc.)."""
    if not href:
        return False
    skip_prefixes = ("#", "mailto:", "javascript:", "tel:", "data:")
    if any(href.startswith(p) for p in skip_prefixes):
        return False
    skip_extensions = (
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
        ".pdf", ".zip", ".tar", ".gz", ".mp3", ".mp4",
        ".css", ".js", ".json", ".xml", ".rss",
    )
    lower = href.lower().split("?")[0]
    if any(lower.endswith(ext) for ext in skip_extensions):
        return False
    return True


def _clean_html(raw_html: str, base_url: str) -> tuple[str, str, list[str]]:
    """
    Extract the main article content using readability, then clean it.
    Returns (cleaned_html, title, list_of_links).
    """
    doc = Document(raw_html)
    title = doc.title()
    content_html = doc.summary()

    soup = BeautifulSoup(content_html, "lxml")

    # Remove scripts, styles, comments
    for tag in soup.find_all(["script", "style", "noscript", "iframe"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Collect and resolve links
    links: list[str] = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if _is_article_link(href):
            absolute = urljoin(base_url, href)
            links.append(absolute)
            a_tag["href"] = absolute  # fix relative links

    # Resolve image sources
    for img in soup.find_all("img", src=True):
        img["src"] = urljoin(base_url, img["src"])

    # Wrap in a nice standalone HTML document
    final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      max-width: 800px;
      margin: 2rem auto;
      padding: 0 1rem;
      font-family: Georgia, 'Times New Roman', serif;
      line-height: 1.7;
      color: #333;
      background: #fafafa;
    }}
    img {{ max-width: 100%; height: auto; }}
    a {{ color: #0066cc; }}
    h1, h2, h3 {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .source-url {{
      font-size: 0.85rem;
      color: #888;
      border-bottom: 1px solid #ddd;
      padding-bottom: 0.5rem;
      margin-bottom: 1.5rem;
    }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p class="source-url">Source: <a href="{base_url}">{base_url}</a></p>
  {soup.decode_contents()}
</body>
</html>"""

    return final_html, title, links


# ── crawl engine ────────────────────────────────────────────────────────

async def _fetch_page(client: httpx.AsyncClient, url: str) -> Optional[str]:
    """Fetch a single page, return raw HTML or None on failure."""
    try:
        resp = await client.get(
            url,
            follow_redirects=True,
            timeout=REQUEST_TIMEOUT,
        )
        if "text/html" not in resp.headers.get("content-type", ""):
            return None
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


async def crawl(job_id: str, url: str, depth: int, same_domain_only: bool) -> None:
    """Run the recursive crawl. Updates the job in-place."""
    job = _jobs[job_id]
    job.status = JobStatus.IN_PROGRESS

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    job_dir = os.path.join(DOWNLOAD_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    visited: set[str] = set()
    base_domain = urlparse(url).netloc
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        await _crawl_recursive(
            client, job, job_dir, url, 0, depth,
            same_domain_only, base_domain, visited, semaphore,
        )

    job.status = JobStatus.COMPLETED
    job.completed_at = datetime.now(timezone.utc)


async def _crawl_recursive(
    client: httpx.AsyncClient,
    job: CrawlJob,
    job_dir: str,
    url: str,
    current_depth: int,
    max_depth: int,
    same_domain_only: bool,
    base_domain: str,
    visited: set[str],
    semaphore: asyncio.Semaphore,
) -> None:
    """Recursively crawl a URL and its child links."""
    # Normalize URL (remove fragment)
    url = url.split("#")[0]
    if url in visited:
        return
    visited.add(url)

    # Domain check
    if same_domain_only and urlparse(url).netloc != base_domain:
        return

    job.total_pages_found = len(visited)

    async with semaphore:
        raw_html = await _fetch_page(client, url)

    if raw_html is None:
        job.pages.append(PageResult(
            url=url, title="", depth=current_depth,
            link_count=0, success=False, error="Failed to fetch or non-HTML",
        ))
        return

    try:
        cleaned_html, title, links = _clean_html(raw_html, url)
    except Exception as exc:
        job.pages.append(PageResult(
            url=url, title="", depth=current_depth,
            link_count=0, success=False, error=str(exc),
        ))
        return

    # Save to disk
    filename = _safe_filename(url)
    filepath = os.path.join(job_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(cleaned_html)

    job.pages_downloaded += 1
    job.pages.append(PageResult(
        url=url, title=title, depth=current_depth,
        link_count=len(links), success=True,
    ))

    # Recurse into child links
    if current_depth < max_depth:
        tasks = []
        for link in links:
            if link not in visited:
                tasks.append(
                    _crawl_recursive(
                        client, job, job_dir, link,
                        current_depth + 1, max_depth,
                        same_domain_only, base_domain, visited, semaphore,
                    )
                )
        if tasks:
            await asyncio.gather(*tasks)


def create_job(url: str, depth: int, same_domain_only: bool) -> CrawlJob:
    """Create a new crawl job and return it."""
    job_id = _url_hash(url) + "_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    job = CrawlJob(
        job_id=job_id,
        status=JobStatus.PENDING,
        url=url,
        depth=depth,
        same_domain_only=same_domain_only,
        created_at=datetime.now(timezone.utc),
    )
    _jobs[job_id] = job
    return job
