#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  CLISONIX BLOG AUTO-PUBLISHER                                                 ║
║  Automatically publishes articles from Blerina & Dr. Albana to GitHub Pages   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Features:                                                                    ║
║  - Auto-converts articles to Jekyll format                                    ║
║  - Publishes new articles immediately (continuous auto-publish)              ║
║  - Pushes to GitHub Pages repository                                          ║
║  - Tracks published articles to avoid duplicates                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Target: https://ledjanahmati.github.io/clisonix-blog/
Port: 8041
Author: Ledjan Ahmati (CEO, ABA GmbH)
"""

import asyncio
import base64
import hashlib
import html
import json
import logging
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("BlogPublisher")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PORT = int(os.getenv("PUBLISHER_PORT", "8041"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "LedjanAhmati/clisonix-blog")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
BLERINA_URL = os.getenv("BLERINA_URL", "http://clisonix-blerina:8037")
DR_ALBANA_URL = os.getenv("DR_ALBANA_URL", "http://clisonix-dr-albana:8040")
GOOGLE_ADSENSE_PUBLISHER_ID = os.getenv("GOOGLE_ADSENSE_PUBLISHER_ID", "")
NEXT_PUBLIC_GOOGLE_ADSENSE_ID = os.getenv("NEXT_PUBLIC_GOOGLE_ADSENSE_ID", "")
GOOGLE_ADSENSE_SLOT_FOOTER = os.getenv("GOOGLE_ADSENSE_SLOT_FOOTER", "")
GOOGLE_ADSENSE_SLOT_SIDEBAR = os.getenv("GOOGLE_ADSENSE_SLOT_SIDEBAR", "")
GOOGLE_ADSENSE_SLOT_INLINE = os.getenv("GOOGLE_ADSENSE_SLOT_INLINE", "")

INVALID_CONTENT_MARKERS = (
    "[content pending",
    "content pending",
    "i can't fulfill",
    "i cannot fulfill",
    "cannot provide",
    "error from ollama",
    "connection error",
    "multiple verified sources confirm this update",
    "further analysis will be published as new data becomes available",
    "operational newsroom brief generated from",
)

# Source directories for articles
BLERINA_PILLARS_DIR = Path(os.getenv("BLERINA_PILLARS_DIR", "/app/blerina_pillars"))
DR_ALBANA_PILLARS_DIR = Path(os.getenv("DR_ALBANA_PILLARS_DIR", "/app/medical_pillars"))
LAGTER_PILLARS_DIR = Path(os.getenv("LAGTER_PILLARS_DIR", "/app/lagter_pillars"))

# LinkedIn publishing configuration
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN", "")
LINKEDIN_ORGANIZATION_URN = os.getenv("LINKEDIN_ORGANIZATION_URN", "")
LINKEDIN_ENABLED = bool(LINKEDIN_ACCESS_TOKEN)

# Local tracking
PUBLISHED_TRACKER = Path("/app/published_tracker.json")
AUTO_PUBLISH_INTERVAL_SECONDS = max(30, int(os.getenv("AUTO_PUBLISH_INTERVAL_SECONDS", "30")))
ACTIVE_PUBLISH_RESCAN_SECONDS = max(10.0, float(os.getenv("ACTIVE_PUBLISH_RESCAN_SECONDS", "10")))
BURST_PUBLISH_DELAY_SECONDS = max(1.0, float(os.getenv("BURST_PUBLISH_DELAY_SECONDS", "1.0")))
SCHEDULER_ERROR_RETRY_SECONDS = max(30, int(os.getenv("SCHEDULER_ERROR_RETRY_SECONDS", "30")))
AUTO_PUBLISH_MAX_PER_CYCLE = max(1, int(os.getenv("AUTO_PUBLISH_MAX_PER_CYCLE", "20")))
GITHUB_AUTH_FAILURE_COOLDOWN_SECONDS = max(60, int(os.getenv("GITHUB_AUTH_FAILURE_COOLDOWN_SECONDS", "600")))

GITHUB_AUTH_FAILURE_UNTIL = 0.0

# ═══════════════════════════════════════════════════════════════════════════════
# APP INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Clisonix Blog Auto-Publisher",
    description="Automatically publishes articles to GitHub Pages",
    version="1.0.0"
)

# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class PublishRequest(BaseModel):
    """Manual publish request"""
    article_id: str = Field(..., description="Article ID from Blerina or Dr. Albana")
    source: str = Field("blerina", description="Source: blerina, dr_albana, or lagter")
    schedule_time: Optional[str] = Field(None, description="ISO datetime to schedule, or None for immediate")

class DirectPublishRequest(BaseModel):
    """Direct publish request for externally generated content"""
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article markdown/plain content")
    source: str = Field("newsroom", description="Content source identifier")
    article_id: Optional[str] = Field(None, description="Optional external article ID")

class PublishResponse(BaseModel):
    """Publish result"""
    status: str
    message: str
    github_url: Optional[str] = None
    post_filename: str

class ScheduleStatus(BaseModel):
    """Schedule status"""
    total_scheduled: int
    total_published_today: int
    next_publish_time: Optional[str]
    pending_articles: List[str]

# ═══════════════════════════════════════════════════════════════════════════════
# LINKEDIN PUBLISHER - DYNAMIC REAL-TIME POSTING
# ═══════════════════════════════════════════════════════════════════════════════

class LinkedInPublisher:
    """Publish to LinkedIn - Dynamic Real-Time Posting on Article Generation"""

    def __init__(self, access_token: Optional[str], person_urn: Optional[str] = None, org_urn: Optional[str] = None):
        self.access_token = access_token
        self.person_urn = person_urn or ""
        self.org_urn = org_urn or ""
        self.api_url = "https://api.linkedin.com/v2"

    def _build_hashtags(self, content_type: str = "tech", article_title: str = "") -> str:
        """Build broader public-discovery hashtags aligned with Clisonix architecture."""
        title_lower = (article_title or "").lower()

        if any(term in title_lower for term in ("medical", "clinical", "health", "therapy", "patient")):
            content_type = "medical"
        elif any(term in title_lower for term in ("eeg", "brain", "neuro", "bci")):
            content_type = "eeg"
        elif any(term in title_lower for term in ("audio", "speech", "voice", "signal")):
            content_type = "audio"
        elif any(term in title_lower for term in ("industry", "industrial", "factory", "iot", "edge")):
            content_type = "industrial"

        base_tags = {
            "tech": [
                "#Clisonix", "#ClisonixCloud", "#AI", "#ArtificialIntelligence", "#MachineLearning",
                "#Innovation", "#CloudComputing", "#SaaS", "#DigitalTransformation", "#FutureTech"
            ],
            "medical": [
                "#Clisonix", "#HealthTech", "#DigitalHealth", "#ClinicalAI", "#MedicalResearch",
                "#HealthcareInnovation", "#WellnessTech", "#PatientCare", "#EEG", "#Neurotechnology"
            ],
            "audio": [
                "#Clisonix", "#AudioAI", "#SignalProcessing", "#SpeechRecognition", "#MultimodalAI",
                "#RealtimeAI", "#MachineLearning", "#Innovation", "#DSP", "#VoiceTech"
            ],
            "eeg": [
                "#Clisonix", "#EEG", "#BrainComputerInterface", "#Neuroscience", "#Neurotechnology",
                "#BrainHealth", "#ClinicalAI", "#DigitalHealth", "#Research", "#AI"
            ],
            "industrial": [
                "#Clisonix", "#IndustrialAI", "#Industry40", "#EdgeAI", "#IoT", "#Automation",
                "#RealtimeSystems", "#SmartManufacturing", "#CloudArchitecture", "#Innovation"
            ],
        }

        extra_tags: List[str] = []
        keyword_map = {
            "ethic": ["#EthicalAI", "#ResponsibleAI"],
            "governance": ["#AIGovernance", "#TrustworthyAI"],
            "research": ["#Research", "#Science"],
            "multilingual": ["#MultilingualAI", "#LanguageTechnology"],
            "payment": ["#FinTech", "#DigitalPayments"],
            "monitor": ["#Observability", "#PlatformEngineering"],
        }
        for term, tags in keyword_map.items():
            if term in title_lower:
                extra_tags.extend(tags)

        selected: List[str] = []
        seen = set()
        for tag in base_tags.get(content_type, base_tags["tech"]) + extra_tags + ["#Web8", "#EthicalTech"]:
            if tag not in seen:
                seen.add(tag)
                selected.append(tag)

        return " ".join(selected[:12])

    async def publish(self, excerpt: str, article_title: str, article_url: str = "", is_medical: bool = False) -> Dict[str, Any]:
        """Publish post to LinkedIn - DYNAMIC REAL-TIME"""

        if not self.access_token:
            logger.warning("LinkedIn publishing skipped: No access token configured")
            return {"success": False, "error": "No LinkedIn token configured", "platform": "linkedin"}

        try:
            if not httpx:
                return {"success": False, "error": "httpx not available", "platform": "linkedin"}

            # Build rich post with hashtags
            hashtags = self._build_hashtags("medical" if is_medical else "tech", article_title)
            excerpt_clean = excerpt[:280] if len(excerpt) > 280 else excerpt

            # Format: Emoji + Title + Excerpt + Article Link + Rich Hashtags
            emoji = "🏥" if is_medical else "🚀"

            if article_url:
                post_text = f"{emoji} {article_title}\n\n{excerpt_clean}\n\n📖 Read: {article_url}\n\n{hashtags}"
            else:
                post_text = f"{emoji} {article_title}\n\n{excerpt_clean}\n\n{hashtags}"

            # Ensure we respect LinkedIn's 3000 char limit
            post_text = post_text[:2950]

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Use provided URN directly
                author_urn = self.person_urn if self.person_urn else "urn:li:person:unknown"

                # Create post payload
                post_data = {
                    "author": author_urn,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": post_text},
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
                }

                response = await client.post(
                    f"{self.api_url}/ugcPosts",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json",
                        "X-Restli-Protocol-Version": "2.0.0"
                    },
                    json=post_data,
                    timeout=30.0
                )

                if response.status_code in [200, 201]:
                    post_id = response.headers.get("x-restli-id", "unknown")
                    logger.info(f"✅ LinkedIn post published: {article_title[:50]}... (ID: {post_id})")
                    return {
                        "success": True,
                        "platform": "linkedin",
                        "post_id": post_id,
                        "url": f"https://www.linkedin.com/feed/update/{post_id}",
                        "published_at": datetime.now(timezone.utc).isoformat(),
                        "dynamic": True,
                        "is_medical": is_medical
                    }
                else:
                    logger.error(f"❌ LinkedIn post failed: {response.status_code} - {response.text[:200]}")
                    return {"success": False, "error": response.text[:200], "platform": "linkedin", "dynamic": True}

        except Exception as e:
            logger.error(f"LinkedIn publishing exception: {str(e)}")
            return {"success": False, "error": str(e), "platform": "linkedin", "dynamic": True}

# ═══════════════════════════════════════════════════════════════════════════════
# TRACKING & STATE
# ═══════════════════════════════════════════════════════════════════════════════

def load_published_tracker() -> Dict[str, Any]:
    """Load published articles tracker"""
    if PUBLISHED_TRACKER.exists():
        data = json.loads(PUBLISHED_TRACKER.read_text())
        data.setdefault("published", [])
        data.setdefault("scheduled", [])
        data.setdefault("records", {})
        data.setdefault("title_records", {})
        data.setdefault("last_publish_date", None)
        return data
    return {"published": [], "scheduled": [], "records": {}, "title_records": {}, "last_publish_date": None}

def save_published_tracker(data: Dict[str, Any]):
    """Save published articles tracker"""
    PUBLISHED_TRACKER.parent.mkdir(parents=True, exist_ok=True)
    PUBLISHED_TRACKER.write_text(json.dumps(data, indent=2))

def _tracker_key(article_id: str, source: str) -> str:
    return f"{source}:{article_id}"

def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def _normalize_title(title: str) -> str:
    normalized = title.strip().lower()
    normalized = re.sub(r"[^\w\s-]", "", normalized)
    normalized = re.sub(r"[\s_-]+", " ", normalized)
    return normalized.strip()

def _title_tracker_key(source: str, title: str) -> str:
    return f"{source}:{_normalize_title(title)}"

def get_published_record(article_id: str, source: str) -> Optional[Dict[str, Any]]:
    """Get a published record for a source/article pair."""
    tracker = load_published_tracker()
    records = tracker.get("records", {})
    record = records.get(_tracker_key(article_id, source))
    if isinstance(record, dict):
        return record
    return None

def get_published_record_by_title(title: str, source: str) -> Optional[Dict[str, Any]]:
    """Get a published record for a source/title pair."""
    tracker = load_published_tracker()
    records = tracker.get("records", {})
    title_records = tracker.get("title_records", {})
    record_key = title_records.get(_title_tracker_key(source, title))
    if not record_key:
        return None
    record = records.get(record_key)
    if isinstance(record, dict):
        return record
    return None

def resolve_existing_record(article_id: str, source: str, title: Optional[str] = None) -> Optional[Dict[str, Any]]:
    by_id = get_published_record(article_id, source)
    if by_id:
        return by_id
    if title:
        return get_published_record_by_title(title, source)
    return None

def is_already_published(article_id: str, source: str, content: Optional[str] = None, title: Optional[str] = None) -> bool:
    """Check if an article has already been published with the same content."""
    tracker = load_published_tracker()
    record = resolve_existing_record(article_id, source, title)
    if record:
        if content is None:
            return True
        return record.get("content_hash") == _content_hash(content)
    return article_id in tracker.get("published", [])

def mark_as_published(article_id: str, source: str, github_url: str, content: str, post_filename: str, title: str):
    """Mark an article as published"""
    tracker = load_published_tracker()
    if article_id not in tracker["published"]:
        tracker["published"].append(article_id)
    record_key = _tracker_key(article_id, source)
    tracker.setdefault("records", {})[record_key] = {
        "article_id": article_id,
        "source": source,
        "title": title,
        "normalized_title": _normalize_title(title),
        "github_url": github_url,
        "content_hash": _content_hash(content),
        "post_filename": post_filename,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    tracker.setdefault("title_records", {})[_title_tracker_key(source, title)] = record_key
    tracker["last_publish_date"] = datetime.now(timezone.utc).isoformat()
    save_published_tracker(tracker)

# ═══════════════════════════════════════════════════════════════════════════════
# JEKYLL CONVERTER
# ═══════════════════════════════════════════════════════════════════════════════

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text[:80]  # Limit length

def extract_title_from_markdown(content: str) -> str:
    """Extract title from markdown content"""
    # Try to find # Title
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Fallback to first line
    lines = content.strip().split('\n')
    if lines:
        return lines[0].strip('#').strip()
    return "Untitled Article"


def _strip_frontmatter(content: str) -> str:
    """Remove optional Jekyll frontmatter before content analysis."""
    if not content:
        return ""
    match = re.match(r'^---\n.*?\n---\n+', content.strip(), re.DOTALL)
    if match:
        return content.strip()[match.end():].strip()
    return content.strip()


def _body_without_title(content: str) -> str:
    """Return article body without leading markdown title line."""
    body = _strip_frontmatter(content)
    lines = body.splitlines()
    if lines and lines[0].lstrip().startswith('#'):
        return '\n'.join(lines[1:]).strip()
    return body


def _extract_excerpt(content: str, fallback_title: str) -> str:
    """Build a useful excerpt from the first real paragraph, not just the title."""
    body = _body_without_title(content)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip()]
    for paragraph in paragraphs:
        cleaned = re.sub(r'\s+', ' ', paragraph).strip()
        if len(cleaned) >= 80:
            return cleaned[:197] + '...' if len(cleaned) > 200 else cleaned

    cleaned_body = re.sub(r'\s+', ' ', body).strip()
    if cleaned_body:
        return cleaned_body[:197] + '...' if len(cleaned_body) > 200 else cleaned_body

    title = fallback_title.strip() or "Clisonix article"
    return title[:147] + '...' if len(title) > 150 else title


def is_placeholder_news_brief(content: str) -> bool:
    """Reject the thin one-paragraph newsroom briefs that harmed the live blog."""
    body = _body_without_title(content)
    lowered = body.lower()
    paragraph_count = len([p for p in re.split(r'\n\s*\n', body) if p.strip()])
    has_status_brief_signature = (
        "reported by" in lowered
        and "live signal:" in lowered
        and "multiple verified sources confirm this update" in lowered
    )
    has_deferred_analysis = "further analysis will be published as new data becomes available" in lowered
    if has_status_brief_signature and has_deferred_analysis:
        return True
    if paragraph_count <= 1 and "reported by" in lowered and len(body.split()) < 140:
        return True
    return False


def is_publishable_content(content: Optional[str]) -> bool:
    """Validate that content is complete enough for publishing."""
    if not content:
        return False
    normalized = content.strip()
    if not normalized:
        return False
    lowered = normalized.lower()
    if any(marker in lowered for marker in INVALID_CONTENT_MARKERS):
        return False
    if is_placeholder_news_brief(normalized):
        return False
    if len(normalized) < 500 or len(normalized.split()) < 80:
        return False
    if normalized.count("\n\n") < 2:
        return False
    return True


async def find_existing_post_filename_by_title(title: str) -> Optional[str]:
    """Find an existing blog post filename by slug in the remote blog repo."""
    if not GITHUB_TOKEN:
        return None

    slug = slugify(title)
    if not slug:
        return None

    headers = _github_headers()
    async with httpx.AsyncClient(timeout=30.0) as client:
        for page in range(1, 11):
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/_posts?ref={GITHUB_BRANCH}&per_page=100&page={page}"
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Could not scan remote _posts page {page}: {response.status_code}")
                return None

            items = response.json()
            if not isinstance(items, list) or not items:
                return None

            suffix = f"-{slug}.md"
            for item in items:
                name = str(item.get("name", ""))
                if name.endswith(suffix):
                    return name

    return None

def determine_categories(content: str, source: str) -> List[str]:
    """Determine article categories based on content"""
    categories = []
    content_lower = content.lower()

    if source == "dr_albana":
        categories.append("Medical Research")
        if "cardio" in content_lower or "heart" in content_lower or "cardiac" in content_lower:
            categories.append("Cardiology")
        if "hepat" in content_lower or "liver" in content_lower:
            categories.append("Hepatology")
        if "hormon" in content_lower or "cortisol" in content_lower or "testosterone" in content_lower:
            categories.append("Endocrinology")
        if "obesity" in content_lower or "muscle" in content_lower or "body composition" in content_lower:
            categories.append("Body Composition")
    elif source == "lagter":
        categories.append("Research Notes")
        if "cell" in content_lower or "qeliz" in content_lower:
            categories.append("Cell Research")
        if "material" in content_lower or "amorph" in content_lower or "amorfe" in content_lower:
            categories.append("Materials Science")
    elif source == "newsroom":
        categories.append("Newsroom")
        categories.append("AI Industry")
        if "health" in content_lower or "clinical" in content_lower or "medical" in content_lower:
            categories.append("Health")
        elif "policy" in content_lower or "ethics" in content_lower or "compliance" in content_lower:
            categories.append("Governance")
        else:
            categories.append("Technology")
    else:  # blerina
        categories.append("Technology")
        if "eeg" in content_lower or "brain" in content_lower or "neural" in content_lower:
            categories.append("Neurotechnology")
        if "bci" in content_lower or "brain-computer" in content_lower:
            categories.append("Brain-Computer Interface")
        if "python" in content_lower or "code" in content_lower or "algorithm" in content_lower:
            categories.append("Software Engineering")
        if "ai" in content_lower or "machine learning" in content_lower:
            categories.append("Artificial Intelligence")

    return categories[:3]  # Max 3 categories


def build_frontmatter_tags(categories: List[str], source: str) -> List[str]:
    """Expand metadata tags for broader public discovery and indexing."""
    tags: List[str] = ["Clisonix", "ClisonixCloud", source.replace("_", "-")]
    tags.extend(categories)

    source_defaults = {
        "dr_albana": ["HealthTech", "DigitalHealth", "ClinicalAI"],
        "lagter": ["Research", "Science", "Innovation"],
        "newsroom": ["AI", "Technology", "PublicIntelligence"],
        "blerina": ["AI", "MultimodalAI", "Neurotechnology"],
    }
    tags.extend(source_defaults.get(source, ["AI", "Innovation"]))

    cleaned: List[str] = []
    seen = set()
    for tag in tags:
        value = str(tag).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        cleaned.append(value)
    return cleaned[:6]


def convert_to_jekyll(content: str, source: str, article_id: str, existing_filename: Optional[str] = None) -> tuple[str, str]:
    """
    Convert markdown content to Jekyll format with YAML frontmatter
    Returns: (jekyll_content, filename)
    """
    title_match = re.search(r'^title:\s*"(.+)"$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else extract_title_from_markdown(content)
    categories = determine_categories(content, source)
    frontmatter_tags = build_frontmatter_tags(categories, source)

    # Generate or reuse filename
    now = datetime.now(timezone.utc)
    if existing_filename:
        filename = existing_filename
    else:
        date_str = now.strftime("%Y-%m-%d")
        slug = slugify(title)
        filename = f"{date_str}-{slug}.md"

    author_name = (
        "Dr. Albana" if source == "dr_albana"
        else "Lagter" if source == "lagter"
        else "Clisonix Newsroom" if source == "newsroom"
        else "Blerina"
    )

    # Build YAML frontmatter
    excerpt = _extract_excerpt(content, title).replace('"', '\\"')

    frontmatter = f"""---
layout: post
title: "{title}"
date: {now.strftime("%Y-%m-%d %H:%M:%S %z")}
categories: [{', '.join(categories)}]
author: {author_name}
source: {source}
article_id: {article_id}
tags: [{', '.join(frontmatter_tags)}]
excerpt: "{excerpt}"
---

"""

    # Remove the original title from content if it starts with #
    content_lines = content.strip().split('\n')
    if content_lines and content_lines[0].startswith('#'):
        content = '\n'.join(content_lines[1:]).strip()

    jekyll_content = frontmatter + content

    return jekyll_content, filename


def render_static_article_html(content: str, title: str, source: str, article_id: str, filename: str) -> str:
    """Render a lightweight standalone HTML page for static hosting."""
    body = content.strip()

    # Remove Jekyll frontmatter if present
    frontmatter_match = re.match(r'^---\n.*?\n---\n+', body, re.DOTALL)
    if frontmatter_match:
        body = body[frontmatter_match.end():].strip()

    lines = body.splitlines()
    if lines and lines[0].lstrip().startswith('#'):
        body = '\n'.join(lines[1:]).strip()

    def _inline_markdown(text: str) -> str:
        safe = html.escape(text)
        safe = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', safe)
        safe = re.sub(r'\*(.+?)\*', r'<em>\1</em>', safe)
        safe = re.sub(r'`(.+?)`', r'<code>\1</code>', safe)
        return safe

    rendered_lines: List[str] = []
    in_list = False
    for raw_line in body.splitlines():
        line = raw_line.strip()

        if not line:
            if in_list:
                rendered_lines.append('</ul>')
                in_list = False
            continue

        if line == '---':
            if in_list:
                rendered_lines.append('</ul>')
                in_list = False
            rendered_lines.append('<hr />')
            continue

        if line.startswith('- '):
            if not in_list:
                rendered_lines.append('<ul>')
                in_list = True
            rendered_lines.append(f"<li>{_inline_markdown(line[2:])}</li>")
            continue

        if in_list:
            rendered_lines.append('</ul>')
            in_list = False

        if line.startswith('### '):
            rendered_lines.append(f"<h3>{_inline_markdown(line[4:])}</h3>")
        elif line.startswith('## '):
            rendered_lines.append(f"<h2>{_inline_markdown(line[3:])}</h2>")
        elif line.startswith('# '):
            rendered_lines.append(f"<h1>{_inline_markdown(line[2:])}</h1>")
        else:
            rendered_lines.append(f"<p>{_inline_markdown(line)}</p>")

    if in_list:
        rendered_lines.append('</ul>')

    article_html = '\n'.join(rendered_lines)

    published_date = filename[:10]
    author = 'Dr. Albana' if source == 'dr_albana' else 'Blerina'
    static_filename = filename.rsplit('.', 1)[0] + ".html"
    canonical_url = f"https://ledjanahmati.github.io/clisonix-blog/static/{quote(static_filename)}"
    og_image = "https://clisonix.com/images/clisonix-og-default.png"
    plain_text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', article_html)).strip()
    description = plain_text[:197] + '...' if len(plain_text) > 200 else plain_text
    if not description:
        description = f"Read the latest insights from {author} on Clisonix Blog."

    safe_title = html.escape(title)
    safe_description = html.escape(description)
    safe_canonical = html.escape(canonical_url)
    safe_og_image = html.escape(og_image)
    safe_author = html.escape(author)
    safe_date = html.escape(published_date)
    safe_article_id = html.escape(article_id)

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <meta name=\"description\" content=\"{safe_description}\" />
    <meta name=\"robots\" content=\"index,follow\" />
    <link rel=\"canonical\" href=\"{safe_canonical}\" />
    <meta property=\"og:type\" content=\"article\" />
    <meta property=\"og:title\" content=\"{safe_title}\" />
    <meta property=\"og:description\" content=\"{safe_description}\" />
    <meta property=\"og:url\" content=\"{safe_canonical}\" />
    <meta property=\"og:image\" content=\"{safe_og_image}\" />
    <meta property=\"og:site_name\" content=\"Clisonix Blog\" />
    <meta property=\"article:author\" content=\"{safe_author}\" />
    <meta property=\"article:published_time\" content=\"{safe_date}\" />
    <meta name=\"twitter:card\" content=\"summary_large_image\" />
    <meta name=\"twitter:title\" content=\"{safe_title}\" />
    <meta name=\"twitter:description\" content=\"{safe_description}\" />
    <meta name=\"twitter:image\" content=\"{safe_og_image}\" />
    <title>{safe_title} | Clisonix Blog</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #0f172a; margin: 0; }}
        .wrap {{ max-width: 900px; margin: 0 auto; padding: 32px 20px 56px; }}
        .meta {{ color: #475569; margin-bottom: 24px; }}
        article {{ line-height: 1.8; font-size: 1.05rem; }}
        h1, h2, h3 {{ color: #0f172a; line-height: 1.25; }}
        p {{ margin: 0 0 16px; }}
        ul {{ margin: 0 0 16px 24px; }}
        a {{ color: #2563eb; }}
    </style>
</head>
<body>
    <div class=\"wrap\">
        <p><a href=\"/clisonix-blog/\">← Back to Clisonix Blog</a></p>
        <h1>{safe_title}</h1>
        <div class=\"meta\">{safe_date} • {safe_author} • {safe_article_id}</div>
        <article>
            {article_html}
        </article>
    </div>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# GITHUB PUBLISHER
# ═══════════════════════════════════════════════════════════════════════════════

async def publish_to_github(content: str, filename: str) -> Optional[str]:
    """
    Publish content to GitHub Pages repository using GitHub API
    Returns the URL of the published post
    """
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN not set!")
        return None

    path = f"_posts/{filename}"
    static_filename = filename.rsplit('.', 1)[0] + ".html"
    static_path = f"static/{static_filename}"
    title_match = re.search(r'^title:\s*"(.+)"$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else extract_title_from_markdown(content)
    source_match = re.search(r'^source:\s*(.+)$', content, re.MULTILINE)
    article_id_match = re.search(r'^article_id:\s*(.+)$', content, re.MULTILINE)
    source = source_match.group(1).strip() if source_match else "blog"
    article_id = article_id_match.group(1).strip() if article_id_match else filename.rsplit('.', 1)[0]
    static_html = render_static_article_html(content, title, source, article_id, filename)

    try:
        success = await upsert_github_file(
            path=path,
            content=content,
            message=f"Auto-publish: {filename}"
        )
        if success:
            static_success = await upsert_github_file(
                path=static_path,
                content=static_html,
                message=f"Auto-publish static: {static_filename}"
            )
            if not static_success:
                logger.error(f"Static HTML publish failed: {static_filename}")
                return None
            compat_success = await upsert_compat_static_alias(static_filename, static_html)
            if not compat_success:
                logger.warning(f"Compat static alias publish failed: clisonix-blog/static/{static_filename}")
            logger.info(f"Successfully published: {filename}")
            base_name = filename.rsplit('.', 1)[0]
            match = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$", base_name)
            if match:
                yyyy, mm, dd, slug = match.groups()
                slug_escaped = quote(slug)
                blog_url = f"https://ledjanahmati.github.io/clisonix-blog/{yyyy}/{mm}/{dd}/{slug_escaped}.html"
            else:
                blog_url = f"https://ledjanahmati.github.io/clisonix-blog/static/{quote(static_filename)}"
            return blog_url
        return None

    except Exception as e:
        logger.error(f"Error publishing to GitHub: {e}")
        return None

def _github_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


def _mark_github_auth_failure(reason: str) -> None:
    global GITHUB_AUTH_FAILURE_UNTIL
    GITHUB_AUTH_FAILURE_UNTIL = max(
        GITHUB_AUTH_FAILURE_UNTIL,
        time.time() + float(GITHUB_AUTH_FAILURE_COOLDOWN_SECONDS),
    )
    logger.error(
        "GitHub authentication failure detected (%s). Scheduler cooldown active for %ss.",
        reason,
        GITHUB_AUTH_FAILURE_COOLDOWN_SECONDS,
    )

async def upsert_github_file(path: str, content: str, message: str) -> bool:
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = _github_headers()
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": GITHUB_BRANCH
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        check_response = await client.get(api_url, headers=headers)
        if check_response.status_code == 200:
            payload["sha"] = check_response.json().get("sha")
        elif check_response.status_code == 401:
            _mark_github_auth_failure(f"GET {path} returned 401")
            logger.error(f"GitHub check failed for {path}: 401 Unauthorized")
            return False
        elif check_response.status_code != 404:
            logger.error(f"GitHub check failed for {path}: {check_response.status_code} - {check_response.text[:200]}")
            return False

        response = await client.put(api_url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return True

        if response.status_code == 401:
            _mark_github_auth_failure(f"PUT {path} returned 401")

        logger.error(f"GitHub upsert failed for {path}: {response.status_code} - {response.text[:200]}")
        return False

async def upsert_compat_static_alias(static_filename: str, static_html: str) -> bool:
    """Create/update compatibility static alias for duplicated baseurl links."""
    compat_path = f"clisonix-blog/static/{static_filename}"
    return await upsert_github_file(
        path=compat_path,
        content=static_html,
        message=f"Auto-publish compat static alias: {static_filename}"
    )

def _format_article_title_from_filename(filename: str) -> str:
    stem = filename.rsplit(".", 1)[0]
    parts = stem.split("-", 3)
    if len(parts) == 4:
        slug = parts[3]
    else:
        slug = stem
    return slug.replace("-", " ").strip().title()

def _build_dynamic_index_html(entries: List[Dict[str, str]]) -> str:
    payload = json.dumps(entries)
    repo = GITHUB_REPO
    branch = GITHUB_BRANCH
    return rf"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Clisonix Blog - AI & Industrial Intelligence</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }}
    .wrap {{ max-width: 1080px; margin: 0 auto; padding: 24px; }}
    header {{ margin-bottom: 18px; }}
    h1 {{ font-size: 2rem; margin-bottom: 6px; }}
    .sub {{ color: #94a3b8; margin-bottom: 12px; }}
    .toolbar {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }}
    input {{ flex: 1 1 260px; min-width: 220px; padding: 10px 12px; border: 1px solid #334155; border-radius: 8px; background: #111827; color: #e2e8f0; }}
    .meta {{ color: #38bdf8; font-size: 0.95rem; }}
    .grid {{ display: grid; gap: 10px; }}
    .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 12px; }}
    .card a {{ color: #60a5fa; text-decoration: none; font-weight: 600; }}
    .card a:hover {{ text-decoration: underline; }}
    .date {{ color: #94a3b8; font-size: 0.85rem; margin-top: 4px; }}
    .pager {{ display: flex; align-items: center; gap: 8px; margin-top: 14px; }}
    button {{ padding: 8px 10px; border-radius: 8px; border: 1px solid #334155; background: #1f2937; color: #e2e8f0; cursor: pointer; }}
    button:disabled {{ opacity: .45; cursor: not-allowed; }}
    footer {{ margin-top: 24px; color: #64748b; text-align: center; }}
  </style>
</head>
<body>
    <div class="wrap">
    <header>
      <h1>Clisonix Blog</h1>
    <p class="sub">AI, EEG Analytics, Industrial Intelligence & Compliance</p>
    <p class="meta" id="count"></p>
    </header>
        <div class="toolbar">
            <input id="search" placeholder="Search articles..." />
    </div>
        <div id="list" class="grid"></div>
        <div class="pager">
            <button id="prev">Prev</button>
            <span id="pageInfo"></span>
            <button id="next">Next</button>
    </div>
    <footer>© 2026 Clisonix - Powered by AI</footer>
  </div>

  <script>
        (function normalizeDuplicatedBasePath() {{
            const duplicated = '/clisonix-blog/clisonix-blog/';
            if (window.location.pathname.includes(duplicated)) {{
                const fixedPath = window.location.pathname.replace(duplicated, '/clisonix-blog/');
                const fixedUrl = `${{window.location.origin}}${{fixedPath}}${{window.location.search}}${{window.location.hash}}`;
                window.location.replace(fixedUrl);
            }}
        }})();

        let allArticles = {payload};
    const state = {{ q: '', page: 1, size: 20 }};
        const githubRepo = {json.dumps(repo)};
        const githubBranch = {json.dumps(branch)};

    const list = document.getElementById('list');
    const count = document.getElementById('count');
    const prev = document.getElementById('prev');
    const next = document.getElementById('next');
    const pageInfo = document.getElementById('pageInfo');
    const search = document.getElementById('search');

        function normalizeTitleFromFilename(filename) {{
            const name = String(filename || '');
            const match = name.match(/^\d{{4}}-\d{{2}}-\d{{2}}-(.+)\.[^.]+$/i);
            const slug = match ? match[1] : name.replace(/\.[^.]+$/, '');
            return slug.replace(/-/g, ' ').trim().replace(/\b\w/g, c => c.toUpperCase());
        }}

        function escapePathSegment(value) {{
            return encodeURIComponent(String(value || '').trim());
        }}

        function buildJekyllUrl(yyyy, mm, dd, slug) {{
            return `/clisonix-blog/${{yyyy}}/${{mm}}/${{dd}}/${{escapePathSegment(slug)}}.html`;
        }}

        function parsePostName(name, dir) {{
            const match = String(name || '').match(/^(\d{{4}})-(\d{{2}})-(\d{{2}})-(.+)\.(md|html)$/i);
            if (!match) return null;
            const [, yyyy, mm, dd, slug] = match;
            const base = `${{yyyy}}-${{mm}}-${{dd}}-${{slug}}`;
            return {{
                id: base,
                title: normalizeTitleFromFilename(name),
                url: buildJekyllUrl(yyyy, mm, dd, slug),
                static_url: `/clisonix-blog/static/${{base}}.html`,
                date: `${{yyyy}}-${{mm}}-${{dd}}`,
                display_date: `${{mm}}/${{dd}}/${{yyyy}}`,
                has_static: dir === 'static'
            }};
        }}

        async function fetchDirEntries(dir) {{
            const endpoint = `https://api.github.com/repos/${{githubRepo}}/contents/${{dir}}?ref=${{encodeURIComponent(githubBranch)}}`;
            const response = await fetch(endpoint, {{ headers: {{ 'Accept': 'application/vnd.github+json' }} }});
            if (!response.ok) return [];
            const items = await response.json();
            return Array.isArray(items) ? items : [];
        }}

        async function fetchLiveArticlesFromRepo() {{
            const dirs = ['_posts', 'static'];
            let parsed = [];

            for (const dir of dirs) {{
                const entries = await fetchDirEntries(dir);
                const items = entries
                    .filter((item) => item && item.type === 'file')
                    .map((item) => item.name || '')
                    .map((name) => parsePostName(name, dir))
                    .filter(Boolean);
                parsed = parsed.concat(items);
            }}

            const byId = new Map();
            parsed.forEach((item) => {{
                const current = byId.get(item.id);
                if (!current) {{
                    byId.set(item.id, item);
                    return;
                }}
                if (!current.has_static && item.has_static) {{
                    byId.set(item.id, item);
                }}
            }});

            const posts = Array.from(byId.values())
                .sort((a, b) => (a.date === b.date ? b.url.localeCompare(a.url) : b.date.localeCompare(a.date)));

            if (posts.length > 0) {{
                allArticles = posts;
            }}
            render();
        }}

        async function refreshLiveArticles() {{
            try {{
                await fetchLiveArticlesFromRepo();
            }} catch (error) {{
                console.error('Live articles refresh failed:', error);
            }}
        }}

    function filtered() {{
      const q = state.q.toLowerCase().trim();
      return allArticles.filter(a => !q || a.title.toLowerCase().includes(q));
    }}

    function render() {{
      const items = filtered();
      const totalPages = Math.max(1, Math.ceil(items.length / state.size));
      if (state.page > totalPages) state.page = totalPages;
      const start = (state.page - 1) * state.size;
      const pageItems = items.slice(start, start + state.size);

      count.textContent = `${{items.length}} Articles`;
      pageInfo.textContent = `Page ${{state.page}} / ${{totalPages}}`;
      prev.disabled = state.page <= 1;
      next.disabled = state.page >= totalPages;

            list.innerHTML = pageItems.map(a => `
                                <article class="card">
                                        <a href="${{a.has_static ? a.static_url : a.url}}">${{a.title}}</a>
                                        <div class="date">${{a.display_date}}</div>
                </article>
            `).join('');
    }}

    search.addEventListener('input', (e) => {{
      state.q = e.target.value;
      state.page = 1;
      render();
    }});
    prev.addEventListener('click', () => {{ if (state.page > 1) {{ state.page--; render(); }} }});
    next.addEventListener('click', () => {{ state.page++; render(); }});

        render();
        refreshLiveArticles();
        setInterval(refreshLiveArticles, 20000);
  </script>
</body>
</html>
"""

def _build_404_redirect_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Redirecting…</title>
    <script>
        (function() {
            const path = window.location.pathname || '/';
            const duplicated = '/clisonix-blog/clisonix-blog/';
            if (path.includes(duplicated)) {
                const fixed = path.replace(duplicated, '/clisonix-blog/');
                const target = `${window.location.origin}${fixed}${window.location.search}${window.location.hash}`;
                window.location.replace(target);
                return;
            }
            window.location.replace('https://ledjanahmati.github.io/clisonix-blog/');
        })();
    </script>
</head>
<body>
    Redirecting to Clisonix Blog…
</body>
</html>
"""

async def refresh_blog_index_page() -> bool:
    if not GITHUB_TOKEN:
        logger.warning("Skipping blog index refresh: GITHUB_TOKEN not set")
        return False

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/_posts"
    headers = _github_headers()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Failed to load _posts for index: {response.status_code} - {response.text[:200]}")
        return False

    items = response.json()
    entries: List[Dict[str, str]] = []
    for item in items:
        if item.get("type") != "file":
            continue
        name = item.get("name", "")
        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.(md|html)$", name)
        if not match:
            continue

        yyyy, mm, dd, slug, _ = match.groups()
        slug_escaped = quote(slug)
        entries.append({
            "title": _format_article_title_from_filename(name),
            "url": f"/clisonix-blog/{yyyy}/{mm}/{dd}/{slug_escaped}.html",
            "static_url": f"/clisonix-blog/static/{yyyy}-{mm}-{dd}-{slug}.html",
            "date": f"{yyyy}-{mm}-{dd}",
            "display_date": f"{mm}/{dd}/{yyyy}",
            "has_static": False,
        })

    entries.sort(key=lambda x: (x["date"], x["url"]), reverse=True)

    html = _build_dynamic_index_html(entries)
    ok = await upsert_github_file(
        path="index.html",
        content=html,
        message="Auto-refresh blog homepage index"
    )
    if ok:
        compat_ok = await upsert_github_file(
            path="clisonix-blog/index.html",
            content=html,
            message="Auto-refresh compat index alias"
        )
        if not compat_ok:
            logger.warning("Compat index alias publish failed: clisonix-blog/index.html")

        not_found_html = _build_404_redirect_html()
        not_found_ok = await upsert_github_file(
            path="404.html",
            content=not_found_html,
            message="Auto-refresh 404 duplicate-path redirect"
        )
        if not not_found_ok:
            logger.warning("404 redirect publish failed")

    if ok:
        logger.info(
            f"Blog homepage refreshed with {len(entries)} posts"
        )
    return ok

# ═══════════════════════════════════════════════════════════════════════════════
# ARTICLE FETCHERS
# ═══════════════════════════════════════════════════════════════════════════════

async def fetch_blerina_article(article_id: str) -> Optional[str]:
    """Fetch article content from Blerina service"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BLERINA_URL}/api/v1/pillars/{article_id}")
            if response.status_code == 200:
                data = response.json()
                return data.get("content", "")
    except Exception as e:
        logger.error(f"Error fetching from Blerina: {e}")

    # Try file-based fallback
    file_path = BLERINA_PILLARS_DIR / f"{article_id}.md"
    if file_path.exists():
        return file_path.read_text()

    return None

async def fetch_dr_albana_article(article_id: str) -> Optional[str]:
    """Fetch article content from Dr. Albana service"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{DR_ALBANA_URL}/api/v1/medical/pillars/{article_id}")
            if response.status_code == 200:
                data = response.json()
                return data.get("content", "")
    except Exception as e:
        logger.error(f"Error fetching from Dr. Albana: {e}")

    # Try file-based fallback
    file_path = DR_ALBANA_PILLARS_DIR / f"{article_id}.md"
    if file_path.exists():
        return file_path.read_text()

    json_path = DR_ALBANA_PILLARS_DIR / f"{article_id}.json"
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text())
            return data.get("content", "")
        except Exception as e:
            logger.warning(f"Could not parse medical JSON fallback {json_path.name}: {e}")

    return None

async def fetch_lagter_article(article_id: str) -> Optional[str]:
    """Fetch article content from Lagter disk storage."""
    file_path = LAGTER_PILLARS_DIR / f"{article_id}.md"
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return None

def _load_sidecar_metadata(file_path: Path) -> Dict[str, Any]:
    json_path = file_path.with_suffix(".json")
    if not json_path.exists():
        return {}
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        logger.warning(f"Could not parse sidecar metadata {json_path.name}: {exc}")
        return {}

def _scan_directory_articles(directory: Path, source: str) -> List[Dict[str, str]]:
    """Scan persisted article directories for publishable markdown files."""
    if not directory.exists():
        return []

    articles: List[Dict[str, str]] = []
    for file_path in sorted(directory.glob("*.md")):
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.warning(f"Could not read {file_path.name}: {exc}")
            continue

        if not is_publishable_content(content):
            logger.debug(f"Skipping non-publishable {source} article from disk: {file_path.stem}")
            continue

        metadata = _load_sidecar_metadata(file_path)
        title = metadata.get("title") or extract_title_from_markdown(content)
        articles.append({
            "id": file_path.stem,
            "source": source,
            "title": title,
            "content": content,
        })

    return articles

def _should_publish_article(article_id: str, source: str, content: str, title: str) -> bool:
    record = resolve_existing_record(article_id, source, title)
    if record:
        return record.get("content_hash") != _content_hash(content)
    return not is_already_published(article_id, source, content, title)

async def get_unpublished_articles() -> List[Dict[str, str]]:
    """Get list of unpublished articles from both sources"""
    unpublished: List[Dict[str, str]] = []
    seen_keys = set()

    def add_candidate(article_id: str, source: str, title: str, content: Optional[str]) -> None:
        if not content:
            return
        key = _tracker_key(article_id, source)
        if key in seen_keys:
            return
        seen_keys.add(key)
        if _should_publish_article(article_id, source, content, title):
            unpublished.append({"id": article_id, "source": source, "title": title})
        else:
            logger.info(f"Skipping unchanged {source} article: {article_id}")

    # Check Blerina articles
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BLERINA_URL}/api/v1/pillars")
            if response.status_code == 200:
                pillars = response.json().get("pillars", [])
                for p in pillars:
                    content = await fetch_blerina_article(p["id"])
                    if is_publishable_content(content):
                        add_candidate(p["id"], "blerina", p.get("title", ""), content)
                    else:
                        logger.debug(f"Skipping non-publishable Blerina article: {p['id']}")
    except Exception as e:
        logger.warning(f"Could not fetch Blerina articles: {e}")

    for article in _scan_directory_articles(BLERINA_PILLARS_DIR, "blerina"):
        add_candidate(article["id"], article["source"], article["title"], article.get("content"))

    # Check Dr. Albana articles
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{DR_ALBANA_URL}/api/v1/medical/pillars")
            if response.status_code == 200:
                pillars = response.json().get("pillars", [])
                for p in pillars:
                    content = await fetch_dr_albana_article(p["id"])
                    if is_publishable_content(content):
                        add_candidate(p["id"], "dr_albana", p.get("title", ""), content)
                    else:
                        logger.debug(f"Skipping non-publishable Dr. Albana article: {p['id']}")
    except Exception as e:
        logger.warning(f"Could not fetch Dr. Albana articles: {e}")

    for article in _scan_directory_articles(DR_ALBANA_PILLARS_DIR, "dr_albana"):
        add_candidate(article["id"], article["source"], article["title"], article.get("content"))

    for article in _scan_directory_articles(LAGTER_PILLARS_DIR, "lagter"):
        add_candidate(article["id"], article["source"], article["title"], article.get("content"))

    return unpublished

# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Clisonix Blog Auto-Publisher</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f0f4f8; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
            h1 { color: #1a365d; border-bottom: 3px solid #3182ce; padding-bottom: 10px; }
            .badge { background: #38a169; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; display: inline-block; margin-bottom: 20px; }
            .endpoint { background: #ebf8ff; padding: 15px; border-left: 5px solid #3182ce; margin: 20px 0; }
            code { background: #edf2f7; padding: 2px 6px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <span class="badge">📝 AUTO-PUBLISH TO GITHUB PAGES</span>
            <h1>📰 Clisonix Blog Auto-Publisher</h1>
            <h2>Target: <a href="https://ledjanahmati.github.io/clisonix-blog/">ledjanahmati.github.io/clisonix-blog</a></h2>

            <div class="endpoint">
                <h3>📤 Publish Article</h3>
                <code>POST /api/v1/publish</code>
                <p>Manually publish an article from Blerina or Dr. Albana</p>
            </div>

            <div class="endpoint">
                <h3>🔄 Auto-Publish All Pending</h3>
                <code>POST /api/v1/publish/batch</code>
                <p>Publish all unpublished articles immediately</p>
            </div>

            <div class="endpoint">
                <h3>📋 Get Unpublished</h3>
                <code>GET /api/v1/pending</code>
                <p>List articles waiting to be published</p>
            </div>

            <div class="endpoint">
                <h3>📊 Schedule Status</h3>
                <code>GET /api/v1/status</code>
                <p>Check publishing schedule and stats</p>
            </div>

            <div class="endpoint">
                <h3>⚕️ Health Check</h3>
                <code>GET /health</code>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "blog_publisher",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_blog": f"https://ledjanahmati.github.io/clisonix-blog/",
        "github_configured": bool(GITHUB_TOKEN),
        "auto_publish_interval_seconds": AUTO_PUBLISH_INTERVAL_SECONDS
    }

@app.get("/api/v1/adsense/config")
async def adsense_config(slot: str = "footer"):
    publisher_id = GOOGLE_ADSENSE_PUBLISHER_ID or NEXT_PUBLIC_GOOGLE_ADSENSE_ID
    normalized_publisher = publisher_id if publisher_id.startswith("ca-pub-") else (f"ca-pub-{publisher_id}" if publisher_id else "")
    slot_map = {
        "footer": GOOGLE_ADSENSE_SLOT_FOOTER,
        "sidebar": GOOGLE_ADSENSE_SLOT_SIDEBAR,
        "inline": GOOGLE_ADSENSE_SLOT_INLINE,
    }
    ad_slot = slot_map.get(slot, GOOGLE_ADSENSE_SLOT_FOOTER)

    return {
        "enabled": bool(normalized_publisher and ad_slot),
        "provider": "google_adsense",
        "slot": slot,
        "publisher_id": normalized_publisher,
        "ad_slot": ad_slot,
        "script_url": f"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={normalized_publisher}" if normalized_publisher else None,
        "script_attrs": {
            "async": "true",
            "crossorigin": "anonymous",
            "data-ad-client": normalized_publisher,
        } if normalized_publisher else {},
        "render_mode": "adsense",
    }

@app.post("/api/v1/publish", response_model=PublishResponse)
async def publish_article(request: PublishRequest):
    """Manually publish a specific article"""

    # Fetch content based on source
    if request.source == "dr_albana":
        content = await fetch_dr_albana_article(request.article_id)
    elif request.source == "lagter":
        content = await fetch_lagter_article(request.article_id)
    else:
        content = await fetch_blerina_article(request.article_id)

    if not content:
        raise HTTPException(status_code=404, detail=f"Article {request.article_id} not found in {request.source}")
    if not is_publishable_content(content):
        raise HTTPException(status_code=422, detail=f"Article {request.article_id} has pending/invalid content and was not published")

    title = extract_title_from_markdown(content)
    existing_record = resolve_existing_record(request.article_id, request.source, title)
    if is_already_published(request.article_id, request.source, content, title):
        raise HTTPException(status_code=400, detail="Article already published")

    # Convert to Jekyll format
    remote_filename = await find_existing_post_filename_by_title(title)

    jekyll_content, filename = convert_to_jekyll(
        content,
        request.source,
        request.article_id,
        existing_filename=(existing_record.get("post_filename") if existing_record else None) or remote_filename,
    )

    # Extract title for LinkedIn
    excerpt = content[:500] if len(content) > 500 else content

    # Publish to GitHub FIRST (local storage always works)
    github_url = await publish_to_github(jekyll_content, filename)

    if github_url:
        mark_as_published(request.article_id, request.source, github_url, content, filename, title)
        await refresh_blog_index_page()

        # 🚀 PUBLISH TO LINKEDIN IMMEDIATELY (Dynamic Real-Time Posting)
        linkedin_result = None
        if LINKEDIN_ENABLED:
            is_medical = request.source == "dr_albana"
            linkedin_publisher = LinkedInPublisher(
                LINKEDIN_ACCESS_TOKEN,
                person_urn=LINKEDIN_PERSON_URN,
                org_urn=LINKEDIN_ORGANIZATION_URN
            )
            linkedin_result = await linkedin_publisher.publish(
                excerpt=excerpt,
                article_title=title,
                article_url=github_url,
                is_medical=is_medical
            )

            if linkedin_result.get("success"):
                logger.info(f"🚀 SUCCESS: Published to both GitHub & LinkedIn: {title}")
            else:
                logger.warning(f"⚠️  GitHub OK but LinkedIn failed: {linkedin_result.get('error')}")

        return PublishResponse(
            status="published",
            message=f"Article published successfully to GitHub Pages{' & LinkedIn' if LINKEDIN_ENABLED else ''}",
            github_url=github_url,
            post_filename=filename
        )
    else:
        return PublishResponse(
            status="error",
            message="Failed to publish to GitHub. Check GITHUB_TOKEN configuration.",
            post_filename=filename
        )

@app.post("/api/v1/publish/direct", response_model=PublishResponse)
async def publish_direct_article(request: DirectPublishRequest):
    """Publish externally supplied content directly to GitHub Pages."""
    title = request.title.strip()
    content = request.content.strip()
    if not title or not content:
        raise HTTPException(status_code=422, detail="title and content are required")

    markdown_content = content
    if not markdown_content.lstrip().startswith("#"):
        markdown_content = f"# {title}\n\n{markdown_content}"

    if not is_publishable_content(markdown_content):
        raise HTTPException(status_code=422, detail="Content is not publishable")

    article_id = request.article_id or hashlib.sha256(
        f"{request.source}:{title}:{markdown_content}".encode("utf-8")
    ).hexdigest()[:16]
    source = request.source or "newsroom"

    existing_record = resolve_existing_record(article_id, source, title)
    if is_already_published(article_id, source, markdown_content, title):
        raise HTTPException(status_code=400, detail="Article already published")

    remote_filename = await find_existing_post_filename_by_title(title)

    jekyll_content, filename = convert_to_jekyll(
        markdown_content,
        source,
        article_id,
        existing_filename=(existing_record.get("post_filename") if existing_record else None) or remote_filename,
    )

    github_url = await publish_to_github(jekyll_content, filename)

    if github_url:
        mark_as_published(article_id, source, github_url, markdown_content, filename, title)
        await refresh_blog_index_page()
        return PublishResponse(
            status="published",
            message="Article published successfully to GitHub Pages",
            github_url=github_url,
            post_filename=filename,
        )

    return PublishResponse(
        status="error",
        message="Failed to publish to GitHub. Check GITHUB_TOKEN configuration.",
        post_filename=filename,
    )

@app.post("/api/v1/publish/batch")
async def publish_batch():
    """Publish all unpublished articles immediately"""
    unpublished = await get_unpublished_articles()

    if not unpublished:
        return {"status": "no_pending", "message": "No unpublished articles found"}

    results = []

    for article in unpublished:
        try:
            request = PublishRequest(article_id=article["id"], source=article["source"], schedule_time=None)
            result = await publish_article(request)
            results.append({
                "article_id": article["id"],
                "source": article["source"],
                "status": result.status,
                "github_url": result.github_url
            })
            # Small delay between publishes
            await asyncio.sleep(2)
        except Exception as e:
            results.append({
                "article_id": article["id"],
                "source": article["source"],
                "status": "error",
                "error": str(e)
            })

    return {
        "status": "batch_complete",
        "published_count": len([r for r in results if r["status"] == "published"]),
        "results": results
    }

@app.get("/api/v1/pending")
async def get_pending_articles():
    """Get list of articles waiting to be published"""
    unpublished = await get_unpublished_articles()
    return {
        "total_pending": len(unpublished),
        "articles": unpublished
    }

@app.get("/api/v1/status", response_model=ScheduleStatus)
async def get_schedule_status():
    """Get publishing schedule status"""
    tracker = load_published_tracker()
    unpublished = await get_unpublished_articles()

    # Count published today
    today = datetime.now(timezone.utc).date()
    published_today = 0
    for article_id in tracker.get("published", []):
        # In a real implementation, we'd track publish dates
        pass

    return ScheduleStatus(
        total_scheduled=len(tracker.get("scheduled", [])),
        total_published_today=published_today,
        next_publish_time=None,
        pending_articles=[a["id"] for a in unpublished[:5]]
    )

@app.get("/api/v1/published")
async def get_published_articles():
    """Get list of already published articles"""
    tracker = load_published_tracker()
    return {
        "total_published": len(tracker.get("published", [])),
        "articles": tracker.get("published", []),
        "last_publish_date": tracker.get("last_publish_date")
    }

@app.get("/api/v1/articles/latest")
async def get_latest_articles_for_video(limit: int = 5):
    """
    Get latest published articles with full content for video generation.
    Used by the video-generator service to consume real article content.
    Returns: list of {id, source, title, content, published_url, published_at}
    """
    tracker = load_published_tracker()
    published_records = tracker.get("records", {})

    if not published_records:
        return {"total": 0, "articles": []}

    # Sort by published_at descending, take the top N
    sorted_records = sorted(
        published_records.items(),
        key=lambda kv: kv[1].get("published_at", ""),
        reverse=True,
    )[:limit]

    results = []
    for key, record in sorted_records:
        article_id = record.get("article_id", "")
        source = record.get("source", "blerina")

        if source == "dr_albana":
            content = await fetch_dr_albana_article(article_id)
        elif source == "lagter":
            content = await fetch_lagter_article(article_id)
        else:
            content = await fetch_blerina_article(article_id)

        if not content:
            continue

        # Strip Jekyll frontmatter if present
        clean_content = content
        fm_match = re.match(r'^---\n.*?\n---\n+', content, re.DOTALL)
        if fm_match:
            clean_content = content[fm_match.end():].strip()

        title = record.get("title") or extract_title_from_markdown(content)
        results.append({
            "id": article_id,
            "source": source,
            "title": title,
            "content": clean_content,
            "published_url": record.get("github_url", ""),
            "published_at": record.get("published_at", ""),
        })

    return {"total": len(results), "articles": results}


async def refresh_index_now():
    """Force refresh blog index from current GitHub _posts."""
    ok = await refresh_blog_index_page()
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to refresh blog index")
    return {"status": "ok", "message": "Blog index refreshed"}


@app.post("/api/v1/index/refresh")
async def refresh_index_endpoint():
    """HTTP endpoint to force refresh blog index from current GitHub _posts."""
    return await refresh_index_now()

# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND SCHEDULER (for cron-like auto-publishing)
# ═══════════════════════════════════════════════════════════════════════════════

async def auto_publish_scheduler():
    """Background task that continuously auto-publishes newly generated articles"""
    while True:
        try:
            now = time.time()
            if GITHUB_AUTH_FAILURE_UNTIL > now:
                remaining = int(GITHUB_AUTH_FAILURE_UNTIL - now)
                logger.warning(
                    "Skipping auto-publish while GitHub auth is unhealthy (cooldown remaining: %ss)",
                    remaining,
                )
                await asyncio.sleep(min(float(remaining), float(SCHEDULER_ERROR_RETRY_SECONDS)))
                continue

            unpublished = await get_unpublished_articles()
            if unpublished:
                logger.info(f"Auto-publish detected {len(unpublished)} pending article(s)")

            to_process = unpublished[:AUTO_PUBLISH_MAX_PER_CYCLE]
            if unpublished and len(unpublished) > len(to_process):
                logger.info(
                    "Auto-publish cycle capped at %s article(s); %s deferred to next cycle",
                    len(to_process),
                    len(unpublished) - len(to_process),
                )

            for article in to_process:
                try:
                    request = PublishRequest(article_id=article["id"], source=article["source"], schedule_time=None)
                    result = await publish_article(request)

                    if result.status == "published" and result.github_url:
                        logger.info(f"Auto-published: {article['id']} -> {result.github_url}")
                    else:
                        logger.warning(
                            "Auto-publish skipped/failed for %s: %s",
                            article["id"],
                            result.message,
                        )
                    await asyncio.sleep(BURST_PUBLISH_DELAY_SECONDS)
                except Exception as e:
                    logger.error(f"Auto-publish failed for {article['id']}: {e}")

            # Never busy-loop: even with pending articles, re-scan on a throttled interval.
            if unpublished:
                await asyncio.sleep(ACTIVE_PUBLISH_RESCAN_SECONDS)
            else:
                await asyncio.sleep(AUTO_PUBLISH_INTERVAL_SECONDS)

        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            await asyncio.sleep(SCHEDULER_ERROR_RETRY_SECONDS)

@app.on_event("startup")
async def startup_event():
    """Start background scheduler on app startup"""
    asyncio.create_task(auto_publish_scheduler())
    logger.info(
        "Blog Auto-Publisher started with dynamic immediate mode "
        f"(idle_poll={AUTO_PUBLISH_INTERVAL_SECONDS}s, burst_delay={BURST_PUBLISH_DELAY_SECONDS}s, error_retry={SCHEDULER_ERROR_RETRY_SECONDS}s)"
    )

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
