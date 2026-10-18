from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi import status
from typing import List
from datetime import datetime
from ..models import MessageIn, MessageOut, SendDTO
from ..storage import save_message, get_history
from ..deps import auth_http, auth_ws
from ..auth import TokenData
from ..manager import manager

router = APIRouter(prefix="/chat", tags=["chat"])

# REST: dërgo mesazh (p.sh. nga AGI/IoT hooks ose kur s'ke WS)
@router.post("/send", response_model=MessageOut)
async def send(dto: SendDTO, tok: TokenData = Depends(auth_http)):
    # vetëm technician/admin mund të dërgojnë me role të tjera
    if tok.role == "client" and (dto.role != "client" or dto.sender != tok.sub):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    m = await save_message(dto.room, dto.role, dto.sender, dto.text)
    out = {"id": m.id, "room": m.room, "role": m.role, "sender": m.sender, "text": m.text, "ts": m.ts}
    await manager.broadcast(dto.room, {"type":"message","data":out})
    return out

# REST: histori dhome
@router.get("/history", response_model=List[MessageOut])
async def history(room: str, limit: int = 50, offset: int = 0, tok: TokenData = Depends(auth_http)):
    # mund të shtosh rregulla aksesimi sipas biznesit
    msgs = await get_history(room, limit, offset)
    return [{"id": m.id, "room": m.room, "role": m.role, "sender": m.sender, "text": m.text, "ts": m.ts} for m in msgs]

# WS: komunikimi live (klientë + teknikë)
@router.websocket("/ws/{room}")
async def ws_room(ws: WebSocket, room: str):
    tok = await auth_ws(ws)  # mbyll ws nëse token s'vlen
    await manager.join(room, ws)
    try:
        # sinjal hyrjeje (opsional)
        await manager.broadcast(room, {"type":"presence","data":{"user": tok.sub, "role": tok.role, "event":"join","ts": datetime.utcnow().isoformat()}})
        # loop mesazhesh
        while True:
            msg = await ws.receive_json()
            text = (msg or {}).get("text")
            if not text:
                continue
            m = await save_message(room, tok.role, tok.sub, text)
            out = {"id": m.id, "room": m.room, "role": m.role, "sender": m.sender, "text": m.text, "ts": m.ts}
            await manager.broadcast(room, {"type":"message","data": out})
    except WebSocketDisconnect:
        await manager.leave(room, ws)
        await manager.broadcast(room, {"type":"presence","data":{"user": tok.sub, "role": tok.role, "event":"leave","ts": datetime.utcnow().isoformat()}})
    except Exception:
        await manager.leave(room, ws)
