"""Deep requests must not silently skip the full Ocean pipeline."""
import ast
import asyncio
from contextvars import ContextVar
from pathlib import Path
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock


SOURCE = Path(__file__).resolve().parents[2] / "ocean-core/ocean_core_full.py"


class Reply:
    processing_time = 0.01
    response = "answer"
    language_detected = "sq"
    engines_used = ["MegaLayerEngine"]

    def model_dump(self):
        return {"response": self.response}


class ProcessingModeTests(IsolatedAsyncioTestCase):
    async def exercise(self, mode):
        node = next(n for n in ast.parse(SOURCE.read_text(encoding="utf-8")).body
                    if isinstance(n, ast.AsyncFunctionDef) and n.name == "chat")
        node.decorator_list = []
        short = AsyncMock(return_value=Reply())
        full = AsyncMock(return_value=Reply())
        namespace = dict(
            ChatRequest=SimpleNamespace, Request=object, ChatResponse=Reply,
            SignalRequest=SimpleNamespace, asyncio=asyncio,
            _enforce_prompt_limits=lambda prompt: None,
            _current_client_ip=ContextVar("test_client_ip", default=""),
            _realtime_extract_client_ip=lambda request: "",
            _maybe_realtime_fast_path=AsyncMock(return_value=None),
            _ingest_signal=AsyncMock(), _extract_client_id=lambda request: "test",
            _chat_via_xlc_first=short, process_query_full=full,
            _format_chat_output=lambda payload, *_: payload,
            CHAT_XLC_FIRST=True, CHAT_XLC_FIRST_FALLBACK_FULL=False,
            CHAT_FULL_TIMEOUT_S=1,
        )
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), "exec"), namespace)
        req = SimpleNamespace(message="question", language="sq", strict_mode=False,
                              clerk_user_id=None, processing_mode=mode, xlc_enabled=True)
        self.assertEqual(await namespace["chat"](req, object()), {"response": "answer"})
        return short, full

    async def test_deep_runs_full_pipeline(self):
        short, full = await self.exercise("deep")
        short.assert_not_awaited()
        full.assert_awaited_once()

    async def test_lightning_retains_xlc_route(self):
        short, full = await self.exercise("lightning")
        short.assert_awaited_once()
        full.assert_not_awaited()
