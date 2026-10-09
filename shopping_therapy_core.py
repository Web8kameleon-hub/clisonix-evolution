"""
shopping_therapy_core.py — Shopping Therapy Engine
====================================================
Lexon çdo link që ka shërbime shopping dhe ia shfaq userit kur ai kërkon.

Subsisteme:
  ShopCatalogue  — regjistron / ruan linkat e shërbimeve
  LinkReader     — fetch + parse HTML → ekstrakton titull, çmim, përshkrim, imazh
  TherapySearch  — kërkon sipas query-t mbi katalogun
  ShoppingEngine — orkestron gjithçka + SSE stream
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional
from urllib.parse import urljoin, urlparse

# Ocean Curiosity — internal address inside Docker network
OCEAN_CORE_URL: str = os.environ.get("OCEAN_CORE_URL", "http://clisonix-ocean-core:8030")

# ─────────────────────────────────────────────────────────────
# ENUMS & MODELS
# ─────────────────────────────────────────────────────────────

class ShopCategory(str, Enum):
    FASHION     = "fashion"
    BEAUTY      = "beauty"
    WELLNESS    = "wellness"
    HOME        = "home"
    FOOD        = "food"
    GADGETS     = "gadgets"
    GIFTS       = "gifts"
    SPORTS      = "sports"
    KIDS        = "kids"
    BOOKS       = "books"
    OTHER       = "other"

CATEGORY_EMOJI = {
    ShopCategory.FASHION:   "👗",
    ShopCategory.BEAUTY:    "💄",
    ShopCategory.WELLNESS:  "🧘",
    ShopCategory.HOME:      "🏠",
    ShopCategory.FOOD:      "🍽️",
    ShopCategory.GADGETS:   "📱",
    ShopCategory.GIFTS:     "🎁",
    ShopCategory.SPORTS:    "🏋️",
    ShopCategory.KIDS:      "🧸",
    ShopCategory.BOOKS:     "📚",
    ShopCategory.OTHER:     "🛍️",
}


@dataclass
class ShopService:
    """A single registered shopping‐therapy service/link."""
    id: str
    url: str
    name: str
    category: ShopCategory
    description: str
    tags: List[str] = field(default_factory=list)
    image_url: str = ""
    price_range: str = ""          # e.g. "€5–€200"
    rating: float = 0.0
    verified: bool = False
    added_at: float = field(default_factory=time.time)
    last_read_at: float = 0.0
    read_snippet: str = ""         # extracted text from last fetch

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        d["emoji"] = CATEGORY_EMOJI.get(self.category, "🛍️")
        return d


# ─────────────────────────────────────────────────────────────
# BUILT-IN CATALOGUE (seed data — therapist-curated links)
# ─────────────────────────────────────────────────────────────

SEED_CATALOGUE: List[Dict[str, Any]] = [
    # ── Fashion ──
    {"url": "https://www.zara.com", "name": "Zara", "category": "fashion",
     "description": "Koleksione mode globale, trendet e fundit.", "tags": ["clothes","trendy","fast-fashion"], "price_range": "€10–€150"},
    {"url": "https://www.hm.com", "name": "H&M", "category": "fashion",
     "description": "Mode e qëndrueshme me çmime të aksesueshme.", "tags": ["clothes","sustainable"], "price_range": "€5–€80"},
    {"url": "https://www.asos.com", "name": "ASOS", "category": "fashion",
     "description": "Mbi 85,000 produkte mode online.", "tags": ["clothes","shoes","accessories"], "price_range": "€8–€200"},
    {"url": "https://www.farfetch.com", "name": "Farfetch", "category": "fashion",
     "description": "Luksi global — dizajnerë nga e tëra bota.", "tags": ["luxury","designer","premium"], "price_range": "€100–€5000"},
    # ── Beauty ──
    {"url": "https://www.sephora.com", "name": "Sephora", "category": "beauty",
     "description": "Kozmetikë, parfume, kujdes lëkure premium.", "tags": ["makeup","skincare","perfume"], "price_range": "€10–€300"},
    {"url": "https://www.lookfantastic.com", "name": "LOOKFANTASTIC", "category": "beauty",
     "description": "Produktet e bukurisë me zbritje deri 50%.", "tags": ["beauty","haircare","deals"], "price_range": "€8–€120"},
    {"url": "https://www.cultbeauty.co.uk", "name": "Cult Beauty", "category": "beauty",
     "description": "Markat e kultit të bukurisë, të selektuara me kujdes.", "tags": ["niche","premium","skincare"], "price_range": "€15–€250"},
    # ── Wellness ──
    {"url": "https://www.goop.com", "name": "Goop", "category": "wellness",
     "description": "Wellness, kujdes shëndetësor dhe mënyrë jetese holistic.", "tags": ["wellness","mindfulness","organic"], "price_range": "€20–€500"},
    {"url": "https://eu.lululemon.com", "name": "Lululemon", "category": "wellness",
     "description": "Veshje teknike yoga & sport me cilësi të lartë.", "tags": ["yoga","sport","activewear"], "price_range": "€50–€200"},
    # ── Home ──
    {"url": "https://www.ikea.com", "name": "IKEA", "category": "home",
     "description": "Mobilje dhe aksesorë shtëpie me dizajn skandinav.", "tags": ["furniture","decor","diy"], "price_range": "€1–€2000"},
    {"url": "https://www.westelm.com", "name": "West Elm", "category": "home",
     "description": "Dizajn modern i shtëpisë, materiale të qëndrueshme.", "tags": ["modern","sustainable","interior"], "price_range": "€30–€3000"},
    {"url": "https://www.anthropologie.com", "name": "Anthropologie", "category": "home",
     "description": "Dizajn oshënar — shtëpi, modë dhe aksesore artizanale.", "tags": ["eclectic","art","boho"], "price_range": "€20–€800"},
    # ── Gadgets ──
    {"url": "https://www.apple.com/shop", "name": "Apple Store", "category": "gadgets",
     "description": "iPhone, Mac, iPad, Audio — ekosistemi Apple.", "tags": ["apple","tech","premium"], "price_range": "€29–€4000"},
    {"url": "https://www.amazon.com/electronics", "name": "Amazon Electronics", "category": "gadgets",
     "description": "Gama e gjerë e elektronikës me dërgim të shpejtë.", "tags": ["electronics","deals","variety"], "price_range": "€5–€5000"},
    # ── Food ──
    {"url": "https://www.eataly.com", "name": "Eataly", "category": "food",
     "description": "Produkte ushqimore italiane premium online.", "tags": ["italian","gourmet","organic"], "price_range": "€5–€150"},
    {"url": "https://www.goldbelly.com", "name": "Goldbelly", "category": "food",
     "description": "Ushqime artizanale të dërguara nga restorante ikonike.", "tags": ["artisan","delivery","special"], "price_range": "€20–€200"},
    # ── Gifts ──
    {"url": "https://www.etsy.com", "name": "Etsy", "category": "gifts",
     "description": "Produkte artizanale unike, mundësi personalizimi.", "tags": ["handmade","unique","personalized"], "price_range": "€5–€500"},
    {"url": "https://www.notonthehighstreet.com", "name": "Not On The High Street", "category": "gifts",
     "description": "Dhurata unike nga krijues të pavarur.", "tags": ["unique","creative","personalized"], "price_range": "€10–€300"},
    # ── Books ──
    {"url": "https://www.bookdepository.com", "name": "Book Depository", "category": "books",
     "description": "Libra nga e tëra bota me dërgim falas.", "tags": ["books","free-shipping","worldwide"], "price_range": "€5–€50"},
    {"url": "https://www.thriftbooks.com", "name": "ThriftBooks", "category": "books",
     "description": "Libra të dorës dytë me çmime shumë të ulëta.", "tags": ["used","cheap","variety"], "price_range": "€2–€20"},
    # ── Sports ──
    {"url": "https://www.nike.com", "name": "Nike", "category": "sports",
     "description": "Veshje dhe pajisje sportive — Just Do It.", "tags": ["sport","shoes","performance"], "price_range": "€20–€300"},
    {"url": "https://www.decathlon.com", "name": "Decathlon", "category": "sports",
     "description": "Sport për të gjithë me çmime të aksesueshme.", "tags": ["sport","outdoor","value"], "price_range": "€5–€500"},
    # ── Kids ──
    {"url": "https://www.smythstoys.com", "name": "Smyths Toys", "category": "kids",
     "description": "Lodra, lojëra dhe aksesore për fëmijë.", "tags": ["toys","kids","games"], "price_range": "€5–€300"},
]


def _make_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


# ─────────────────────────────────────────────────────────────
# SHOP CATALOGUE
# ─────────────────────────────────────────────────────────────

class ShopCatalogue:
    """In-memory catalogue with optional JSON persistence."""

    def __init__(self, persist_path: Optional[str] = None) -> None:
        self._path = Path(persist_path) if persist_path else None
        self._items: Dict[str, ShopService] = {}
        self._load_seed()
        self._load_persisted()

    # ── Seed ─────────────────────────────────────────────────
    def _load_seed(self) -> None:
        for entry in SEED_CATALOGUE:
            svc = ShopService(
                id=_make_id(entry["url"]),
                url=entry["url"],
                name=entry["name"],
                category=ShopCategory(entry["category"]),
                description=entry["description"],
                tags=entry.get("tags", []),
                price_range=entry.get("price_range", ""),
                verified=True,
            )
            self._items[svc.id] = svc

    def _load_persisted(self) -> None:
        if not self._path or not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text())
            for item in data:
                svc = ShopService(
                    id=item["id"],
                    url=item["url"],
                    name=item["name"],
                    category=ShopCategory(item["category"]),
                    description=item.get("description", ""),
                    tags=item.get("tags", []),
                    image_url=item.get("image_url", ""),
                    price_range=item.get("price_range", ""),
                    rating=item.get("rating", 0.0),
                    verified=item.get("verified", False),
                    added_at=item.get("added_at", time.time()),
                    last_read_at=item.get("last_read_at", 0.0),
                    read_snippet=item.get("read_snippet", ""),
                )
                self._items[svc.id] = svc
        except Exception:
            pass

    def _persist(self) -> None:
        if not self._path:
            return
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps([s.to_dict() for s in self._items.values()], ensure_ascii=False, indent=2)
            )
        except Exception:
            pass

    # ── CRUD ─────────────────────────────────────────────────
    def register(
        self,
        url: str,
        name: str,
        category: ShopCategory = ShopCategory.OTHER,
        description: str = "",
        tags: Optional[List[str]] = None,
        price_range: str = "",
    ) -> ShopService:
        sid = _make_id(url)
        svc = ShopService(
            id=sid,
            url=url,
            name=name,
            category=category,
            description=description,
            tags=tags or [],
            price_range=price_range,
            verified=False,
        )
        self._items[sid] = svc
        self._persist()
        return svc

    def update_snippet(self, service_id: str, snippet: str, image_url: str = "") -> None:
        if service_id in self._items:
            self._items[service_id].read_snippet = snippet[:500]
            self._items[service_id].image_url = image_url or self._items[service_id].image_url
            self._items[service_id].last_read_at = time.time()
            self._persist()

    def get(self, service_id: str) -> Optional[ShopService]:
        return self._items.get(service_id)

    def all(self) -> List[ShopService]:
        return sorted(self._items.values(), key=lambda s: (s.category.value, s.name))

    def by_category(self, cat: ShopCategory) -> List[ShopService]:
        return [s for s in self._items.values() if s.category == cat]

    def categories_summary(self) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for svc in self._items.values():
            result[svc.category.value] = result.get(svc.category.value, 0) + 1
        return dict(sorted(result.items()))


# ─────────────────────────────────────────────────────────────
# LINK READER
# ─────────────────────────────────────────────────────────────

class LinkReader:
    """Fetches a URL and extracts shopping-relevant metadata."""

    FETCH_TIMEOUT = 8.0
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )

    async def read(self, url: str) -> Dict[str, Any]:
        """Return dict with: title, description, image_url, price_hints, snippet."""
        try:
            import aiohttp
            headers = {"User-Agent": self.USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.FETCH_TIMEOUT),
                headers=headers,
            ) as session:
                async with session.get(url, allow_redirects=True) as resp:
                    if resp.status != 200:
                        return {"error": f"HTTP {resp.status}", "url": url}
                    html = await resp.text(encoding="utf-8", errors="replace")
            return self._parse(html, url)
        except asyncio.TimeoutError:
            return {"error": "timeout", "url": url}
        except Exception as exc:
            return {"error": str(exc)[:120], "url": url}

    def _parse(self, html: str, base_url: str) -> Dict[str, Any]:
        """Extract metadata without lxml/bs4 — pure regex."""

        def meta(name: str) -> str:
            patterns = [
                rf'<meta[^>]+property=["\']og:{name}["\'][^>]+content=["\'](.*?)["\']',
                rf'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:{name}["\']',
                rf'<meta[^>]+name=["\']{name}["\'][^>]+content=["\'](.*?)["\']',
                rf'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']{name}["\']',
            ]
            for p in patterns:
                m = re.search(p, html, re.IGNORECASE | re.DOTALL)
                if m:
                    return _clean(m.group(1))
            return ""

        # Title
        title = meta("title") or meta("site_name")
        if not title:
            m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            title = _clean(m.group(1)) if m else urlparse(base_url).netloc

        # Description
        description = meta("description")

        # Image
        image_url = meta("image")
        if image_url and image_url.startswith("/"):
            parsed = urlparse(base_url)
            image_url = f"{parsed.scheme}://{parsed.netloc}{image_url}"

        # Price hints (€ $ £ €XX.XX etc.)
        price_pattern = r"(?:€|£|\$|USD|EUR)\s*\d+(?:[.,]\d{1,2})?"
        prices = list(set(re.findall(price_pattern, html[:20000])))[:6]

        # Strip tags for snippet
        clean_text = re.sub(r"<[^>]+>", " ", html[:8000])
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        snippet = clean_text[:400]

        return {
            "url": base_url,
            "title": title,
            "description": description or snippet[:160],
            "image_url": image_url,
            "price_hints": prices,
            "snippet": snippet,
        }


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


# ─────────────────────────────────────────────────────────────
# THERAPY SEARCH
# ─────────────────────────────────────────────────────────────

class TherapySearch:
    """Ranks catalogue items by relevance to a user query."""

    STOP_WORDS = {"the","a","an","and","or","in","on","for","with","is","are","to","of","do","i","me","my","shop"}

    def search(
        self,
        query: str,
        catalogue: ShopCatalogue,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[ShopService]:
        tokens = self._tokenize(query)
        items = catalogue.by_category(ShopCategory(category)) if category else catalogue.all()

        scored: List[tuple[float, ShopService]] = []
        for svc in items:
            score = self._score(tokens, svc)
            scored.append((score, svc))

        scored.sort(key=lambda x: -x[0])
        # If no query, return all sorted by verified + name
        if not tokens:
            return [s for _, s in scored[:limit]]
        return [s for score, s in scored if score > 0][:limit]

    def _tokenize(self, text: str) -> List[str]:
        return [w for w in re.findall(r"\w+", text.lower()) if w not in self.STOP_WORDS and len(w) > 1]

    def _score(self, tokens: List[str], svc: ShopService) -> float:
        if not tokens:
            return 1.0 + (0.5 if svc.verified else 0)
        score = 0.0
        text = " ".join([
            svc.name.lower() * 3,
            svc.description.lower(),
            " ".join(svc.tags).lower() * 2,
            svc.category.value.lower() * 2,
            svc.read_snippet.lower(),
        ])
        for token in tokens:
            if token in text:
                score += text.count(token) * 0.1
                if token in svc.name.lower():
                    score += 2.0
                if token in svc.category.value:
                    score += 1.5
                if token in svc.tags:
                    score += 1.0
        if svc.verified:
            score += 0.3
        return score


# ─────────────────────────────────────────────────────────────
# SHOPPING ENGINE — main entry point
# ─────────────────────────────────────────────────────────────

class ShoppingEngine:
    """Orchestrates catalogue, reading, and search for shopping therapy."""

    def __init__(self, persist_path: Optional[str] = None) -> None:
        self.catalogue = ShopCatalogue(persist_path)
        self.reader = LinkReader()
        self.search = TherapySearch()
        self._request_count = 0

    # ── Public API ─────────────────────────────────────────────

    def search_services(
        self,
        query: str = "",
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        results = self.search.search(query, self.catalogue, category, limit)
        return [s.to_dict() for s in results]

    async def read_and_register(
        self,
        url: str,
        name: str = "",
        category: str = "other",
        description: str = "",
    ) -> Dict[str, Any]:
        """Fetch a URL, parse it, and add/update in catalogue."""
        self._request_count += 1
        parsed_data = await self.reader.read(url)

        if "error" in parsed_data:
            return {"success": False, "error": parsed_data["error"], "url": url}

        cat = ShopCategory(category) if category in ShopCategory._value2member_map_ else ShopCategory.OTHER
        resolved_name = name or parsed_data.get("title", urlparse(url).netloc)
        resolved_desc = description or parsed_data.get("description", "")

        svc = self.catalogue.register(
            url=url,
            name=resolved_name,
            category=cat,
            description=resolved_desc,
        )
        self.catalogue.update_snippet(
            service_id=svc.id,
            snippet=parsed_data.get("snippet", ""),
            image_url=parsed_data.get("image_url", ""),
        )
        return {
            "success": True,
            "service": self.catalogue.get(svc.id).to_dict(),
            "read": parsed_data,
        }

    async def read_url_preview(self, url: str) -> Dict[str, Any]:
        """Fetch and parse a URL — no registration."""
        self._request_count += 1
        return await self.reader.read(url)

    def get_catalogue(self, category: Optional[str] = None) -> Dict[str, Any]:
        items = self.catalogue.by_category(ShopCategory(category)) if category else self.catalogue.all()
        return {
            "total": len(items),
            "categories": self.catalogue.categories_summary(),
            "items": [s.to_dict() for s in items],
        }

    async def therapy_stream(
        self,
        query: str = "",
        category: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """SSE stream — yields results progressively."""
        t0 = time.time()
        results = self.search_services(query, category, limit=12)

        yield _sse({"event": "start", "total": len(results), "query": query})

        for i, svc in enumerate(results):
            await asyncio.sleep(0)  # yield control
            yield _sse({"event": "item", "index": i, "item": svc})

        yield _sse({
            "event": "done",
            "total": len(results),
            "elapsed_ms": round((time.time() - t0) * 1000),
        })
        yield "data: [DONE]\n\n"

    async def ocean_chat_stream(
        self,
        query: str,
        messages: Optional[List[Dict]] = None,
    ) -> AsyncGenerator[str, None]:
        """Relay user query + Shopping Therapy catalogue context → Ocean Curiosity SSE stream."""
        import aiohttp

        # Build shopping context from top matching catalogue results
        top = self.search_services(query, limit=6)
        ctx_lines = [
            f"- {s['name']} ({s['category']}): {s['description']} "
            f"[{s.get('price_range','')}] → {s['url']}"
            for s in top
        ]
        catalogue_context = (
            "\n".join(ctx_lines)
            if ctx_lines
            else "Katalogu i Shopping Therapy është i zbrazët."
        )

        enriched_message = (
            f"{query}\n\n"
            f"[Kontekst nga Shopping Therapy — shërbime relevante nga katalogu]\n"
            f"{catalogue_context}"
        )

        payload = {"message": enriched_message, "messages": messages or []}
        ocean_url = f"{OCEAN_CORE_URL}/api/v1/chat/stream"

        self._request_count += 1
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    ocean_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status != 200:
                        yield _sse({"event": "error", "message": f"Ocean returned {resp.status}"})
                        yield "data: [DONE]\n\n"
                        return
                    async for chunk in resp.content.iter_chunked(512):
                        if chunk:
                            yield chunk.decode("utf-8", errors="replace")
        except Exception as exc:
            yield _sse({"event": "error", "message": str(exc)[:200]})
            yield "data: [DONE]\n\n"

    def status(self) -> Dict[str, Any]:
        return {
            "engine": "shopping-therapy",
            "status": "ready",
            "ocean_core_url": OCEAN_CORE_URL,
            "catalogue_size": len(self.catalogue.all()),
            "categories": self.catalogue.categories_summary(),
            "requests_total": self._request_count,
        }


def _sse(data: Dict[str, Any]) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
