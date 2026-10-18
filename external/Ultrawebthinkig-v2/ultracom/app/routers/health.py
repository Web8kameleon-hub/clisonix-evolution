from fastapi import APIRouter
from datetime import datetime
router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True, "service": "UltraCom", "ts": datetime.utcnow().isoformat()}
