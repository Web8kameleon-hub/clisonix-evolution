#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLX BRAIN FastAPI Router
Exposes cognitive engine endpoints
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .clx_brain_core import CLXBrain, RedisUnlimited

logger = logging.getLogger("CLXBrain.API")

# ═════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═════════════════════════════════════════════════════════════════════════════

class ProcessRequest(BaseModel):
    """Request model for cognitive processing"""
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class ProcessResponse(BaseModel):
    """Response model for cognitive processing"""
    vendim: Dict[str, Any]
    metrikat: Dict[str, Any]
    gjendja: Dict[str, Any]
    koha_procesimit_ms: float


class LearningRequest(BaseModel):
    """Request model for learning/experience"""
    tipi: str
    eksperiencë: Dict[str, Any]


class StatusResponse(BaseModel):
    """Status response model"""
    operacionale: bool
    emri: str
    versioni: str
    id: str
    gjendja_mendore: str
    energjia: float
    neurone_total: int
    lidhje_total: int
    rregulla_total: int


# ═════════════════════════════════════════════════════════════════════════════
# Routes
# ═════════════════════════════════════════════════════════════════════════════

class CLXBrainRouter:
    """CLX Brain API Router"""

    def __init__(self):
        self.router = APIRouter(prefix="/brain", tags=["cognitive"])
        self.brain: Optional[CLXBrain] = None
        self.redis = RedisUnlimited()
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup all routes"""
        self.router.add_api_route(
            "/initialize",
            self.initialize,
            methods=["POST"],
            response_model=Dict[str, str],
        )
        self.router.add_api_route(
            "/process",
            self.process,
            methods=["POST"],
            response_model=ProcessResponse,
        )
        self.router.add_api_route(
            "/learn",
            self.learn,
            methods=["POST"],
            response_model=Dict[str, str],
        )
        self.router.add_api_route(
            "/status",
            self.status,
            methods=["GET"],
            response_model=StatusResponse,
        )
        self.router.add_api_route(
            "/history",
            self.get_history,
            methods=["GET"],
        )
        self.router.add_api_route(
            "/metrics",
            self.get_metrics,
            methods=["GET"],
        )
        self.router.add_api_route(
            "/rules",
            self.get_rules,
            methods=["GET"],
        )
        self.router.add_api_route(
            "/neurons",
            self.get_neurons,
            methods=["GET"],
        )
        self.router.add_websocket_route(
            "/stream",
            self.websocket_stream,
        )

    async def initialize(self) -> Dict[str, str]:
        """Initialize CLX Brain"""
        try:
            if not self.brain:
                self.brain = CLXBrain(emri="CLXBrain-API", versioni="1.0.0")
                await self.brain.initialize_redis()
                await self.redis.initialize()

                # Store brain status in Redis
                await self.redis.set_json(
                    "clx_brain:status",
                    {
                        "emri": self.brain.emri,
                        "versioni": self.brain.versioni,
                        "inicializuar": datetime.now(timezone.utc).isoformat(),
                    },
                    ttl=3600,
                )

                logger.info("✅ CLX Brain initialized successfully")
                return {
                    "status": "initialized",
                    "brain_id": self.brain.id,
                    "versioni": self.brain.versioni,
                }
            else:
                return {
                    "status": "already_initialized",
                    "brain_id": self.brain.id,
                }
        except Exception as e:
            logger.error(f"❌ Brain initialization failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def process(self, request: ProcessRequest) -> ProcessResponse:
        """Process input through cognitive engine"""
        if not self.brain:
            raise HTTPException(
                status_code=503,
                detail="Brain not initialized. Call /brain/initialize first.",
            )

        try:
            # Merge context if provided
            input_data = dict(request.input_data)
            if request.context:
                input_data.update(request.context)

            # Process through brain
            koha_fillimi = datetime.now(timezone.utc)
            hasil = self.brain.procesoj(input_data)
            koha_mbarimi = datetime.now(timezone.utc)
            koha_ms = (koha_mbarimi - koha_fillimi).total_seconds() * 1000

            # Store in Redis for history
            await self.redis.stream_append(
                "clx_brain:processing_stream",
                {
                    "input": input_data,
                    "output": hasil,
                    "koha_ms": koha_ms,
                    "timestamp": koha_mbarimi.isoformat(),
                },
            )

            return ProcessResponse(
                vendim=hasil["vendim"],
                metrikat=hasil["metrikat"],
                gjendja=hasil["gjendja"],
                koha_procesimit_ms=koha_ms,
            )
        except Exception as e:
            logger.error(f"❌ Processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def learn(self, request: LearningRequest) -> Dict[str, str]:
        """Learn from experience"""
        if not self.brain:
            raise HTTPException(
                status_code=503,
                detail="Brain not initialized. Call /brain/initialize first.",
            )

        try:
            self.brain.mëso(request.eksperiencë)

            # Store learning in Redis
            await self.redis.stream_append(
                "clx_brain:learning_stream",
                {
                    "tipi": request.tipi,
                    "eksperiencë": request.eksperiencë,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            return {
                "status": "learned",
                "tipi": request.tipi,
                "elasticiteti": str(self.brain.rrjeti.elasticiteti),
            }
        except Exception as e:
            logger.error(f"❌ Learning failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def status(self) -> StatusResponse:
        """Get brain status"""
        if not self.brain:
            raise HTTPException(
                status_code=503,
                detail="Brain not initialized. Call /brain/initialize first.",
            )

        status_data = self.brain.status()
        return StatusResponse(
            operacionale=status_data["operacionale"],
            emri=status_data["emri"],
            versioni=status_data["versioni"],
            id=status_data["id"],
            gjendja_mendore=status_data["gjendja_mendore"],
            energjia=status_data["energjia"],
            neurone_total=status_data["neurone_total"],
            lidhje_total=status_data["lidhje_total"],
            rregulla_total=status_data["rregulla_total"],
        )

    async def get_history(self) -> Dict[str, Any]:
        """Get processing history"""
        if not self.brain:
            raise HTTPException(status_code=503, detail="Brain not initialized")

        try:
            entries = await self.redis.stream_read(
                "clx_brain:processing_stream", count=50
            )
            return {
                "count": len(entries),
                "entries": entries,
                "historiku_memorie": len(self.brain.kujtesa),
            }
        except Exception as e:
            logger.error(f"❌ Failed to get history: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_metrics(self) -> Dict[str, Any]:
        """Get cognitive metrics"""
        if not self.brain:
            raise HTTPException(status_code=503, detail="Brain not initialized")

        return {
            "metrikat": self.brain.metrikat,
            "rrjeti": {
                "neurone_total": len(self.brain.rrjeti.neurone),
                "lidhje_total": len(self.brain.rrjeti.lidhjet),
                "elasticiteti": self.brain.rrjeti.elasticiteti,
                "neurone_aktive": self.brain.rrjeti.metrikat.get("neurone_aktive", 0),
                "sinapsa_aktive": self.brain.rrjeti.metrikat.get("sinapsa_aktive", 0),
            },
            "etika": {
                "pesha": self.brain.etika.pesha_etike,
                "vlera": [v.value for v in self.brain.etika.vlerat_themelore],
            },
        }

    async def get_rules(self) -> Dict[str, Any]:
        """Get decision rules"""
        if not self.brain:
            raise HTTPException(status_code=503, detail="Brain not initialized")

        rregullat = []
        for rr in self.brain.motori_vendimmarrjes.rregullat:
            rregullat.append({
                "emri": rr.emri,
                "pesha": rr.pesha,
                "prioriteti": rr.prioriteti,
                "përdorimet": rr.përdorimet,
                "suksesi": rr.suksesi,
                "elasticiteti": rr.elasticiteti,
            })

        return {
            "total": len(rregullat),
            "rregullat": rregullat,
            "elasticiteti_global": self.brain.motori_vendimmarrjes.elasticiteti_global,
        }

    async def get_neurons(self) -> Dict[str, Any]:
        """Get neuron network info"""
        if not self.brain:
            raise HTTPException(status_code=503, detail="Brain not initialized")

        neurone_lista = []
        for neuron_id, neuron in self.brain.rrjeti.neurone.items():
            neurone_lista.append({
                "id": neuron_id,
                "emri": neuron.emri,
                "lloji": neuron.lloji,
                "potenciali": neuron.potenciali,
                "gjendja": neuron.gjendja,
                "energjia": neuron.energjia,
                "sinapsa_count": len(neuron.sinapsat),
            })

        return {
            "total": len(neurone_lista),
            "neurone": neurone_lista,
            "lidhje": len(self.brain.rrjeti.lidhjet),
        }

    async def websocket_stream(self, websocket: WebSocket) -> None:
        """WebSocket for real-time cognitive stream"""
        await websocket.accept()
        logger.info("✅ WebSocket connected for real-time stream")

        try:
            while True:
                # Receive input from client
                data = await websocket.receive_text()
                input_data = json.loads(data)

                if not self.brain:
                    await websocket.send_json({
                        "error": "Brain not initialized",
                        "status": 503,
                    })
                    continue

                try:
                    # Process through brain
                    hasil = self.brain.procesoj(input_data)

                    # Send response
                    await websocket.send_json({
                        "vendim": hasil["vendim"],
                        "metrikat": hasil["metrikat"],
                        "gjendja": hasil["gjendja"],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                except Exception as e:
                    await websocket.send_json({
                        "error": str(e),
                        "status": 500,
                    })
        except WebSocketDisconnect:
            logger.info("❌ WebSocket disconnected")
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            await websocket.close(code=1011, reason=str(e))

    async def shutdown(self) -> None:
        """Shutdown brain and close connections"""
        if self.brain:
            await self.brain.close_redis()
        await self.redis.close()
        logger.info("🛑 CLX Brain shut down")


# ═════════════════════════════════════════════════════════════════════════════
# Factory function to get router
# ═════════════════════════════════════════════════════════════════════════════

def get_clx_brain_router() -> APIRouter:
    """Get CLX Brain API router"""
    router_instance = CLXBrainRouter()
    return router_instance.router
