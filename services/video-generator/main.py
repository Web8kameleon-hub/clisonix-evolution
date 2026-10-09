#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  VIDEO GENERATOR API — FastAPI Wrapper for BLERINA Video Pipeline            ║
║  Part of Clisonix Cloud Industrial Backend                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Port: 8008                                                                   ║
║  Endpoints:                                                                   ║
║  - GET  /health          - Health check                                       ║
║  - GET  /status          - Detailed status                                    ║
║  - POST /generate        - Generate a video                                   ║
║  - GET  /videos          - List generated videos                              ║
║  - GET  /videos/{id}     - Get video info                                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Date: 2026-02-08
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Import the video generator
import video_generator_blerina as vg

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PORT = int(os.getenv("PORT", "8008"))
VIDEO_OUTPUT_DIR = Path(os.getenv("VIDEO_OUTPUT_DIR", "./generated_videos"))
VIDEO_OUTPUT_DIR.mkdir(exist_ok=True)
YOUTUBE_ACCESS_TOKEN = os.getenv("YOUTUBE_ACCESS_TOKEN", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_CATEGORY_ID = os.getenv("YOUTUBE_CATEGORY_ID", "22")
YOUTUBE_DEFAULT_PRIVACY = os.getenv("YOUTUBE_PRIVACY_STATUS", "public")

# Track jobs
JOBS: Dict[str, Dict[str, Any]] = {}

# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Video Generator BLERINA",
    description="AI-powered video generation for Clisonix",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class VideoRequest(BaseModel):
    """Request to generate a video."""
    topic: str = Field(..., description="Video topic/title", min_length=3, max_length=500)
    title: Optional[str] = Field(default=None, description="Optional display title override")
    style: str = Field(
        default="educational",
        description="Video style: educational, documentary, tutorial, presentation, social_media"
    )
    voice: str = Field(
        default="professional",
        description="Voice style: professional, friendly, narrator, energetic"
    )
    add_subtitles: bool = Field(default=True, description="Add SRT subtitles")
    source: str = Field(default="manual", description="Content source: manual, blog, newsroom")
    article_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional article payload when generating from an existing blog/newsroom item",
    )


VideoRequest.model_rebuild()


class VideoResponse(BaseModel):
    """Response with video generation result."""
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    """Status of a video generation job."""
    job_id: str
    status: str  # pending, processing, completed, failed
    topic: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class YouTubePublishRequest(BaseModel):
    video_name: str = Field(..., description="Video name with or without .mp4")
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(default="")
    tags: list[str] = Field(default_factory=list)
    privacy_status: str = Field(default=YOUTUBE_DEFAULT_PRIVACY)


# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND TASK
# ═══════════════════════════════════════════════════════════════════════════════

async def process_video_job(job_id: str, request: VideoRequest) -> None:
    """Process video generation in background."""
    try:
        JOBS[job_id]["status"] = "processing"

        result = await vg.generate_video(
            topic=request.title or request.topic,
            style=request.style,
            voice=request.voice,
            add_subtitles=request.add_subtitles,
            source=request.source,
            article_data=request.article_data,
        )

        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        JOBS[job_id]["result"] = result

    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        JOBS[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()


async def _refresh_youtube_access_token() -> str:
    if not (YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN):
        return ""

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": YOUTUBE_CLIENT_ID,
                "client_secret": YOUTUBE_CLIENT_SECRET,
                "refresh_token": YOUTUBE_REFRESH_TOKEN,
                "grant_type": "refresh_token",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code >= 400:
            return ""
        data = resp.json()
        return str(data.get("access_token") or "")


async def _get_youtube_access_token() -> str:
    if YOUTUBE_ACCESS_TOKEN:
        return YOUTUBE_ACCESS_TOKEN
    return await _refresh_youtube_access_token()


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    health_status = vg.health()
    return {
        "status": "ok" if health_status.get("ffmpeg_available") else "degraded",
        "service": "video-generator",
        "version": "1.0.0",
        "details": health_status
    }


@app.get("/status")
async def status() -> Dict[str, Any]:
    """Detailed status with job statistics."""
    health_status = vg.health()

    # Count jobs by status
    job_stats = {
        "pending": sum(1 for j in JOBS.values() if j["status"] == "pending"),
        "processing": sum(1 for j in JOBS.values() if j["status"] == "processing"),
        "completed": sum(1 for j in JOBS.values() if j["status"] == "completed"),
        "failed": sum(1 for j in JOBS.values() if j["status"] == "failed"),
    }

    # List generated videos
    videos = list(VIDEO_OUTPUT_DIR.glob("*.mp4"))

    return {
        "status": "ok",
        "service": "video-generator",
        "version": "1.0.0",
        "capabilities": health_status,
        "job_stats": job_stats,
        "videos_on_disk": len(videos),
        "output_directory": str(VIDEO_OUTPUT_DIR),
        "supported_sources": ["manual", "blog", "newsroom"],
    }


@app.post("/generate", response_model=VideoResponse)
async def generate_video(
    request: VideoRequest,
    background_tasks: BackgroundTasks
) -> VideoResponse:
    """
    Generate a video from a topic.

    This runs in the background. Use /jobs/{job_id} to check status.
    """
    # Check if FFmpeg is available
    health_status = vg.health()
    if not health_status.get("ffmpeg_available"):
        raise HTTPException(
            status_code=503,
            detail="FFmpeg not available. Video generation disabled."
        )

    # Create job
    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "topic": request.title or request.topic,
        "source": request.source,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "result": None,
        "error": None
    }

    # Start background task
    background_tasks.add_task(process_video_job, job_id, request)

    return VideoResponse(
        job_id=job_id,
        status="pending",
        message=f"Video generation started. Check status at /jobs/{job_id}"
    )


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get the status of a video generation job."""
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JOBS[job_id]


@app.get("/jobs")
async def list_jobs() -> Dict[str, Any]:
    """List all video generation jobs."""
    return {
        "total": len(JOBS),
        "jobs": list(JOBS.values())
    }


@app.get("/videos")
async def list_videos() -> Dict[str, Any]:
    """List all generated videos on disk."""
    videos = []

    for video_path in VIDEO_OUTPUT_DIR.glob("*.mp4"):
        stat = video_path.stat()
        srt_path = video_path.with_suffix(".srt")

        videos.append({
            "name": video_path.name,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
            "has_subtitles": srt_path.exists(),
            "download_url": f"/videos/download/{video_path.stem}"
        })

    return {
        "total": len(videos),
        "videos": sorted(videos, key=lambda x: x["created"], reverse=True)
    }


@app.get("/videos/download/{video_name}")
async def download_video(video_name: str) -> FileResponse:
    """Download a generated video."""
    video_path = VIDEO_OUTPUT_DIR / f"{video_name}.mp4"

    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Video {video_name} not found")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=video_path.name
    )


@app.get("/videos/subtitles/{video_name}")
async def download_subtitles(video_name: str) -> FileResponse:
    """Download subtitles for a video."""
    srt_path = VIDEO_OUTPUT_DIR / f"{video_name}.srt"

    if not srt_path.exists():
        raise HTTPException(status_code=404, detail=f"Subtitles for {video_name} not found")

    return FileResponse(
        path=srt_path,
        media_type="application/x-subrip",
        filename=srt_path.name
    )


@app.post("/publish/youtube")
async def publish_youtube(request: YouTubePublishRequest) -> Dict[str, Any]:
    token = await _get_youtube_access_token()
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Missing YouTube OAuth credentials. Set YOUTUBE_ACCESS_TOKEN or refresh-token credentials.",
        )

    name = request.video_name if request.video_name.endswith(".mp4") else f"{request.video_name}.mp4"
    video_path = VIDEO_OUTPUT_DIR / name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Video not found: {name}")

    privacy = request.privacy_status if request.privacy_status in {"private", "unlisted", "public"} else YOUTUBE_DEFAULT_PRIVACY
    metadata = {
        "snippet": {
            "title": request.title,
            "description": request.description,
            "tags": request.tags,
            "categoryId": YOUTUBE_CATEGORY_ID,
        },
        "status": {
            "privacyStatus": privacy,
        },
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        init_resp = await client.post(
            "https://www.googleapis.com/upload/youtube/v3/videos",
            params={"part": "snippet,status", "uploadType": "resumable"},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": "video/mp4",
                "X-Upload-Content-Length": str(video_path.stat().st_size),
            },
            json=metadata,
        )
        if init_resp.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"YouTube upload init failed: {init_resp.text[:500]}")

        upload_url = init_resp.headers.get("Location")
        if not upload_url:
            raise HTTPException(status_code=502, detail="YouTube did not return upload URL")

        content = video_path.read_bytes()
        upload_resp = await client.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "video/mp4",
            },
            content=content,
        )
        if upload_resp.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"YouTube upload failed: {upload_resp.text[:500]}")

        payload = upload_resp.json()
        video_id = str(payload.get("id") or "")
        if not video_id:
            raise HTTPException(status_code=502, detail="YouTube upload succeeded but no video id returned")

    return {
        "status": "published",
        "video_id": video_id,
        "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
        "title": request.title,
        "privacy_status": privacy,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("VIDEO GENERATOR API — Starting...")
    print("=" * 70)

    # Check health before starting
    health_status = vg.health()
    print("\nHealth Check:")
    print(f"  FFmpeg: {'✅' if health_status['ffmpeg_available'] else '❌'}")
    print(f"  Pillow: {'✅' if health_status['pillow_available'] else '❌'}")
    print(f"  TTS Engines: {health_status['tts_engines']}")

    if not health_status['ffmpeg_available']:
        print("\n⚠️  WARNING: FFmpeg not available. Video generation will fail!")

    print(f"\n🚀 Starting server on port {PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
