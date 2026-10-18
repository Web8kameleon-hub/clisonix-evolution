import asyncio

import httpx

from apps.api.longo_client import LongoClient, LongoError


def test_longo_client_crud_and_query_contract() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "healthy"})
        if request.url.path.endswith("/query"):
            return httpx.Response(200, json={"data": [{"id": "doc-1", "kind": "report"}]})
        if request.method == "POST":
            return httpx.Response(201, json={"data": {"id": "doc-1", "kind": "report"}})
        if request.method == "GET":
            return httpx.Response(200, json={"data": {"id": "doc-1", "kind": "report"}})
        if request.method == "DELETE":
            return httpx.Response(204)
        raise AssertionError(f"Unexpected request: {request.method} {request.url}")

    async def exercise() -> None:
        client = LongoClient("http://longo:8030", transport=httpx.MockTransport(handler))
        try:
            assert (await client.health())["status"] == "healthy"
            created = await client.insert_document(
                "clisonix",
                "artifacts",
                {"id": "doc-1", "kind": "report"},
            )
            assert created["id"] == "doc-1"
            found = await client.find_documents(
                "clisonix",
                "artifacts",
                {"kind": "report"},
                limit=1,
                sort=[{"field": "created_at", "direction": "desc"}],
            )
            assert found == [{"id": "doc-1", "kind": "report"}]
            assert await client.delete_document("clisonix", "artifacts", "doc-1")
        finally:
            await client.close()

    asyncio.run(exercise())

    query_request = next(request for request in requests if request.url.path.endswith("/query"))
    assert query_request.method == "POST"
    assert query_request.read()


def test_longo_client_surfaces_real_error_status() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503,
            json={
                "error": {
                    "code": "STORAGE_UNAVAILABLE",
                    "message": "disk is read-only",
                }
            },
        )

    async def exercise() -> LongoError:
        client = LongoClient("http://longo:8030", transport=httpx.MockTransport(handler))
        try:
            try:
                await client.health()
            except LongoError as exc:
                return exc
            raise AssertionError("Expected LongoError")
        finally:
            await client.close()

    error = asyncio.run(exercise())
    assert error.status_code == 503
    assert error.code == "STORAGE_UNAVAILABLE"
    assert str(error) == "disk is read-only"
