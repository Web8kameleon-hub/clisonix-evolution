from typing import Dict, Set
from fastapi import WebSocket
from asyncio import Lock

class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}
        self.lock = Lock()

    async def join(self, room: str, ws: WebSocket):
        await ws.accept()
        async with self.lock:
            self.rooms.setdefault(room, set()).add(ws)

    async def leave(self, room: str, ws: WebSocket):
        async with self.lock:
            if room in self.rooms:
                self.rooms[room].discard(ws)
                if not self.rooms[room]:
                    self.rooms.pop(room, None)

    async def broadcast(self, room: str, data: dict):
        # dërgo në të gjithë përdoruesit e dhomës
        dead = []
        conns = list(self.rooms.get(room, set()))
        for ws in conns:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        if dead:
            async with self.lock:
                for ws in dead:
                    self.rooms.get(room, set()).discard(ws)

manager = ConnectionManager()
