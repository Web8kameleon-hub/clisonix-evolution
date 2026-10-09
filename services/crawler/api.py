from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

SERVICE_NAME = "clisonix-crawler"
SERVICE_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", "9211"))
DB_PATH = os.getenv("CRAWLER_DB_PATH", "/data/crawler.db")
WORKERS = max(int(os.getenv("CRAWLER_WORKERS", "1")), 1)
REQUEST_DELAY_MS = max(int(os.getenv("CRAWLER_REQUEST_DELAY_MS", "250")), 0)
MAX_PAGES_DEFAULT = max(int(os.getenv("CRAWLER_MAX_PAGES_DEFAULT", "50")), 1)


job_queue: asyncio.Queue[str] = asyncio.Queue()
workers: list[asyncio.Task] = []
jobs_memory: dict[str, dict[str, Any]] = {}


class CrawlRequest(BaseModel):
    seed_url: HttpUrl
    max_pages: int = Field(default=MAX_PAGES_DEFAULT, ge=1, le=1000)
    same_domain_only: bool = True


class CrawlResponse(BaseModel):
    job_id: str
    status: str


@dataclass
class PageResult:
    url: str
    status_code: int | None
    title: str | None
    depth: int
    links_count: int
    error: str | None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    clean = parsed._replace(fragment="", query="")
    return urlunparse(clean)


def same_domain(url: str, domain: str) -> bool:
    return urlparse(url).netloc == domain


def ensure_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS crawl_jobs (
                job_id TEXT PRIMARY KEY,
                seed_url TEXT NOT NULL,
                status TEXT NOT NULL,
                same_domain_only INTEGER NOT NULL,
                max_pages INTEGER NOT NULL,
                pages_discovered INTEGER NOT NULL DEFAULT 0,
                pages_crawled INTEGER NOT NULL DEFAULT 0,
                pages_failed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                error_message TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS crawled_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                url TEXT NOT NULL,
                status_code INTEGER,
                title TEXT,
                depth INTEGER NOT NULL,
                links_count INTEGER NOT NULL,
                error TEXT,
                crawled_at TEXT NOT NULL,
                UNIQUE(job_id, url)
            )
            """
        )
        conn.commit()


def create_job(seed_url: str, max_pages: int, same_domain_only_flag: bool) -> str:
    job_id = str(uuid.uuid4())
    created_at = now_iso()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO crawl_jobs (
                job_id, seed_url, status, same_domain_only, max_pages, created_at
            ) VALUES (?, ?, 'queued', ?, ?, ?)
            """,
            (job_id, seed_url, int(same_domain_only_flag), max_pages, created_at),
        )
        conn.commit()

    jobs_memory[job_id] = {
        "job_id": job_id,
        "seed_url": seed_url,
        "status": "queued",
        "max_pages": max_pages,
        "same_domain_only": same_domain_only_flag,
        "created_at": created_at,
        "started_at": None,
        "finished_at": None,
        "pages_discovered": 0,
        "pages_crawled": 0,
        "pages_failed": 0,
        "error_message": None,
    }
    return job_id


def update_job(job_id: str, **fields: Any) -> None:
    if not fields:
        return

    if job_id in jobs_memory:
        jobs_memory[job_id].update(fields)

    columns = ", ".join(f"{k} = ?" for k in fields.keys())
    values = list(fields.values()) + [job_id]
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f"UPDATE crawl_jobs SET {columns} WHERE job_id = ?", values)
        conn.commit()


def insert_page(job_id: str, page: PageResult) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO crawled_pages (
                job_id, url, status_code, title, depth, links_count, error, crawled_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                page.url,
                page.status_code,
                page.title,
                page.depth,
                page.links_count,
                page.error,
                now_iso(),
            ),
        )
        conn.commit()


def get_job(job_id: str) -> dict[str, Any] | None:
    if job_id in jobs_memory:
        return jobs_memory[job_id]

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM crawl_jobs WHERE job_id = ?", (job_id,)).fetchone()
        if not row:
            return None
        data = dict(row)
        data["same_domain_only"] = bool(data.get("same_domain_only", 1))
        jobs_memory[job_id] = data
        return data


def parse_html_links(base_url: str, html: str) -> tuple[str | None, list[str]]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else None

    links: list[str] = []
    for tag in soup.find_all("a", href=True):
        href = tag.get("href")
        if not href:
            continue
        absolute = normalize_url(urljoin(base_url, href))
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        links.append(absolute)

    return title, links


async def execute_crawl(job_id: str) -> None:
    job = get_job(job_id)
    if not job:
        return

    seed_url = normalize_url(str(job["seed_url"]))
    same_domain_only_flag = bool(job.get("same_domain_only", True))
    max_pages = int(job.get("max_pages", MAX_PAGES_DEFAULT))
    seed_domain = urlparse(seed_url).netloc

    update_job(job_id, status="running", started_at=now_iso())

    queue: asyncio.Queue[tuple[str, int]] = asyncio.Queue()
    await queue.put((seed_url, 0))
    visited: set[str] = set()

    crawled = 0
    failed = 0
    discovered = 1

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            while not queue.empty() and crawled < max_pages:
                current_url, depth = await queue.get()
                if current_url in visited:
                    continue

                visited.add(current_url)
                try:
                    response = await client.get(current_url)
                    content_type = response.headers.get("content-type", "")
                    title = None
                    links: list[str] = []

                    if "text/html" in content_type and response.text:
                        title, links = parse_html_links(current_url, response.text)

                    insert_page(
                        job_id,
                        PageResult(
                            url=current_url,
                            status_code=response.status_code,
                            title=title,
                            depth=depth,
                            links_count=len(links),
                            error=None,
                        ),
                    )
                    crawled += 1

                    for link in links:
                        if link in visited:
                            continue
                        if same_domain_only_flag and not same_domain(link, seed_domain):
                            continue
                        if len(visited) + queue.qsize() >= max_pages:
                            break
                        await queue.put((link, depth + 1))
                        discovered += 1

                except Exception as exc:
                    insert_page(
                        job_id,
                        PageResult(
                            url=current_url,
                            status_code=None,
                            title=None,
                            depth=depth,
                            links_count=0,
                            error=str(exc),
                        ),
                    )
                    crawled += 1
                    failed += 1

                update_job(
                    job_id,
                    pages_discovered=discovered,
                    pages_crawled=crawled,
                    pages_failed=failed,
                )

                if REQUEST_DELAY_MS > 0:
                    await asyncio.sleep(REQUEST_DELAY_MS / 1000)

        update_job(job_id, status="completed", finished_at=now_iso())

    except Exception as exc:
        update_job(
            job_id,
            status="failed",
            finished_at=now_iso(),
            error_message=str(exc),
        )


async def worker_loop(worker_id: int) -> None:
    while True:
        job_id = await job_queue.get()
        try:
            await execute_crawl(job_id)
        finally:
            job_queue.task_done()


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_db()
    for index in range(WORKERS):
        workers.append(asyncio.create_task(worker_loop(index), name=f"crawler-worker-{index}"))

    try:
        yield
    finally:
        for task in workers:
            task.cancel()
        workers.clear()


app = FastAPI(
    title="Clisonix Crawler API",
    description="Internal crawler and coverage service for Clisonix web properties",
    version=SERVICE_VERSION,
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "port": PORT,
        "endpoints": ["/crawl", "/status", "/coverage", "/health"],
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": SERVICE_NAME}


@app.post("/crawl", response_model=CrawlResponse)
async def enqueue_crawl(request: CrawlRequest) -> CrawlResponse:
    job_id = create_job(
        seed_url=str(request.seed_url),
        max_pages=request.max_pages,
        same_domain_only_flag=request.same_domain_only,
    )
    await job_queue.put(job_id)
    return CrawlResponse(job_id=job_id, status="queued")


@app.get("/status")
async def status() -> dict[str, Any]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT status, COUNT(*) as count
            FROM crawl_jobs
            GROUP BY status
            """
        ).fetchall()

    counters = {row["status"]: row["count"] for row in rows}
    return {
        "service": SERVICE_NAME,
        "queue_size": job_queue.qsize(),
        "workers": WORKERS,
        "jobs": counters,
    }


@app.get("/status/{job_id}")
async def job_status(job_id: str) -> dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/coverage")
async def coverage(job_id: str | None = None) -> dict[str, Any]:
    query = """
        SELECT status_code, url, error
        FROM crawled_pages
        {where_clause}
    """
    where_clause = "WHERE job_id = ?" if job_id else ""

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            query.format(where_clause=where_clause),
            (job_id,) if job_id else (),
        ).fetchall()

    total = len(rows)
    ok = sum(1 for row in rows if row["status_code"] and 200 <= row["status_code"] < 400)
    failed = sum(1 for row in rows if row["error"] or not row["status_code"] or row["status_code"] >= 400)

    domains: dict[str, int] = {}
    for row in rows:
        domain = urlparse(row["url"]).netloc
        domains[domain] = domains.get(domain, 0) + 1

    top_domains = sorted(domains.items(), key=lambda item: item[1], reverse=True)[:10]

    result = {
        "job_id": job_id,
        "total_pages": total,
        "ok_pages": ok,
        "failed_pages": failed,
        "success_rate": round((ok / total) * 100, 2) if total > 0 else 0.0,
        "top_domains": [{"domain": domain, "pages": count} for domain, count in top_domains],
    }

    if job_id:
        job = get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        result["job"] = job

    return result


@app.get("/coverage/{job_id}")
async def coverage_by_job(job_id: str) -> dict[str, Any]:
    return await coverage(job_id=job_id)


@app.get("/jobs/recent")
async def recent_jobs(limit: int = 20) -> dict[str, Any]:
    safe_limit = max(1, min(limit, 100))
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT job_id, seed_url, status, pages_discovered, pages_crawled, pages_failed,
                   created_at, started_at, finished_at
            FROM crawl_jobs
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()

    return {"jobs": [dict(row) for row in rows], "count": len(rows)}


@app.get("/export/{job_id}")
async def export_job(job_id: str) -> dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        pages = conn.execute(
            """
            SELECT url, status_code, title, depth, links_count, error, crawled_at
            FROM crawled_pages
            WHERE job_id = ?
            ORDER BY depth ASC, crawled_at ASC
            """,
            (job_id,),
        ).fetchall()

    return {
        "job": job,
        "pages": [dict(row) for row in pages],
        "pages_count": len(pages),
        "exported_at": now_iso(),
        "format": "json",
        "schema": "v1",
        "preview": json.dumps([dict(row) for row in pages[:2]]) if pages else "[]",
    }
