"""Persistent knowledge store"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class KnowledgeStore:
    """Persistent knowledge base with JSON storage"""

    def __init__(self, storage_path: str = ".clx/knowledge"):
        self.path = Path(storage_path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.data_file = self.path / "knowledge.json"
        self.data = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        """Load knowledge from disk"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load knowledge: {e}")
        return []

    def _save(self):
        """Save knowledge to disk using atomic write to prevent corruption"""
        try:
            tmp_file = self.data_file.with_suffix('.tmp')
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
                f.flush()
                import os
                os.fsync(f.fileno())
            tmp_file.replace(self.data_file)
        except Exception as e:
            logger.error(f"Could not save knowledge: {e}")

    def add(self, entry: Dict[str, Any]) -> str:
        """Add knowledge entry"""
        entry_id = hashlib.md5(f"{entry.get('query', '')}:{datetime.now().isoformat()}".encode()).hexdigest()

        knowledge = {
            "id": entry_id,
            "query": entry.get("query", ""),
            "response": entry.get("response", ""),
            "confidence": entry.get("confidence", 0.5),
            "sources": entry.get("sources", []),
            "language": entry.get("language", "en"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "times_used": 0,
            "helpful": True,
        }

        self.data.append(knowledge)
        self._save()
        logger.debug(f"Added knowledge: {entry_id}")
        return entry_id

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge by query (simple keyword matching)"""
        query_words = set(query.lower().split())
        results = []

        for entry in self.data:
            entry_words = set(entry.get("query", "").lower().split())
            match_count = len(query_words & entry_words)

            if match_count > 0:
                score = match_count / max(len(query_words), len(entry_words))
                results.append({
                    "id": entry.get("id"),
                    "content": entry.get("response"),
                    "score": score,
                    "language": entry.get("language"),
                })

        # Sort by score and return top N
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def get(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """Get knowledge by ID"""
        for entry in self.data:
            if entry.get("id") == knowledge_id:
                return entry
        return None

    def update_usage(self, knowledge_id: str, helpful: bool = True):
        """Record usage of a knowledge entry"""
        for entry in self.data:
            if entry.get("id") == knowledge_id:
                entry["times_used"] = entry.get("times_used", 0) + 1
                entry["helpful"] = helpful
                entry["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._save()
                break

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge statistics"""
        languages = set()
        for entry in self.data:
            languages.add(entry.get("language", "en"))

        return {
            "total_entries": len(self.data),
            "languages": list(languages),
            "avg_confidence": sum(e.get("confidence", 0) for e in self.data) / max(1, len(self.data)),
        }
