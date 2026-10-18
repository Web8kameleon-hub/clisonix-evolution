"""Fault-injection tests for the upstream stream boundary, not inference evidence."""
import ast
import json
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from typing import AsyncGenerator
from fastapi import HTTPException


class Response:
    status_code = 200

    def __init__(self, lines):
        self.lines = lines

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def aiter_lines(self):
        for line in self.lines:
            yield line


class StreamIntegrityTests(unittest.IsolatedAsyncioTestCase):
    async def run_stream(self, lines):
        response = Response(lines)

        class Client(Response):
            def __init__(self, **kwargs):
                pass

            def stream(self, *args, **kwargs):
                return response

        path = Path(__file__).resolve().parents[2] / 'ocean-core/ocean_core_full.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'stream_ollama_response')
        namespace = dict(AsyncGenerator=AsyncGenerator, List=list, json=json,
                         httpx=SimpleNamespace(AsyncClient=Client), HTTPException=HTTPException,
                         logger=logging.getLogger('test'), OLLAMA_HOST='http://test',
                         _utf8_safe_json=lambda x: x, _utf8_safe_text=str,
                         _resolve_llm_timeout=lambda *args: 1, _elastic_chunk_chars=lambda n: 100)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
        return [x async for x in namespace['stream_ollama_response']('test', [], {}, [], 'en')]

    async def test_complete_stream_preserves_answer(self):
        self.assertEqual(await self.run_stream(['{"response":"391","done":true}']), ['391'])

    async def test_partial_output_does_not_become_success(self):
        result = await self.run_stream(['{"response":"39"}'])
        self.assertEqual(result[-1], '[STREAM_ERROR:upstream_incomplete_stream]')

    async def test_malformed_or_error_stream_fails_closed(self):
        for line in ['not-json', '{"error":"generation failed"}']:
            with self.subTest(line=line):
                result = await self.run_stream([line])
                self.assertTrue(result[-1].startswith('[STREAM_ERROR:'))


if __name__ == '__main__':
    unittest.main()
