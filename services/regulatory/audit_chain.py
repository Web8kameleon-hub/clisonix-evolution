from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


class LiabilityChain:
    """Prediction-level chain of custody for model, data snapshot, and jurisdiction."""

    def __init__(self, output_file: str = "./data/liability_chain.jsonl") -> None:
        self._records: Dict[str, Dict[str, Any]] = {}
        self._output = Path(output_file)
        self._output.parent.mkdir(parents=True, exist_ok=True)

    def link_prediction(
        self,
        *,
        prediction_id: str,
        model_version: str,
        training_data_snapshot: str,
        jurisdiction: str,
        regulation_profile: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "prediction_id": prediction_id,
            "model_version": model_version,
            "training_data_snapshot": training_data_snapshot,
            "jurisdiction": jurisdiction,
            "regulation_profile": regulation_profile,
            "metadata": metadata or {},
            "timestamp": _utc_now_iso(),
        }
        self._records[prediction_id] = record
        self._append(record)
        return record

    def get_record(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        cached = self._records.get(prediction_id)
        if cached:
            return cached

        if not self._output.exists():
            return None

        try:
            with self._output.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if item.get("prediction_id") == prediction_id:
                        self._records[prediction_id] = item
                        return item
        except Exception:
            return None

        return None

    def _append(self, record: Dict[str, Any]) -> None:
        with self._output.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
