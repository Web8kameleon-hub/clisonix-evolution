from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator
from urllib.parse import quote

import httpx


class LongoError(RuntimeError):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class LongoClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("Longo base URL is required")
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(timeout_seconds),
            transport=transport,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def health(self) -> dict[str, Any]:
        response = await self._client.get("/health")
        return self._decode(response)

    async def list_documents(self, database: str, collection: str) -> list[dict[str, Any]]:
        response = await self._client.get(self._collection_path(database, collection))
        payload = self._decode(response)
        data = payload.get("data")
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise LongoError(502, "INVALID_LONGO_RESPONSE", "Longo returned an invalid document list")
        return data

    async def get_document(
        self,
        database: str,
        collection: str,
        document_id: str,
    ) -> dict[str, Any] | None:
        response = await self._client.get(
            f"{self._collection_path(database, collection)}/{quote(document_id, safe='')}"
        )
        if response.status_code == 404:
            return None
        payload = self._decode(response)
        data = payload.get("data")
        if not isinstance(data, dict):
            raise LongoError(502, "INVALID_LONGO_RESPONSE", "Longo returned an invalid document")
        return data

    async def insert_document(
        self,
        database: str,
        collection: str,
        document: dict[str, Any],
    ) -> dict[str, Any]:
        response = await self._client.post(
            self._collection_path(database, collection),
            json=document,
        )
        return self._document_data(response)

    async def replace_document(
        self,
        database: str,
        collection: str,
        document_id: str,
        document: dict[str, Any],
    ) -> dict[str, Any] | None:
        response = await self._client.put(
            f"{self._collection_path(database, collection)}/{quote(document_id, safe='')}",
            json=document,
        )
        if response.status_code == 404:
            return None
        return self._document_data(response)

    async def upsert_document(
        self,
        database: str,
        collection: str,
        document_id: str,
        document: dict[str, Any],
    ) -> dict[str, Any]:
        values = dict(document)
        values["id"] = document_id
        replaced = await self.replace_document(
            database,
            collection,
            document_id,
            values,
        )
        if replaced is not None:
            return replaced
        try:
            return await self.insert_document(database, collection, values)
        except LongoError as exc:
            if exc.status_code != 400:
                raise
            replaced = await self.replace_document(
                database,
                collection,
                document_id,
                values,
            )
            if replaced is None:
                raise
            return replaced

    async def delete_document(
        self,
        database: str,
        collection: str,
        document_id: str,
    ) -> bool:
        response = await self._client.delete(
            f"{self._collection_path(database, collection)}/{quote(document_id, safe='')}"
        )
        if response.status_code == 404:
            return False
        if response.status_code != 204:
            self._decode(response)
        return True

    async def find_one(
        self,
        database: str,
        collection: str,
        **fields: Any,
    ) -> dict[str, Any] | None:
        documents = await self.find_documents(
            database,
            collection,
            fields,
            limit=1,
        )
        return documents[0] if documents else None

    async def find_documents(
        self,
        database: str,
        collection: str,
        fields: dict[str, Any],
        *,
        limit: int = 100,
        sort: list[dict[str, str]] | None = None,
    ) -> list[dict[str, Any]]:
        response = await self._client.post(
            f"{self._collection_path(database, collection)}/query",
            json={"where": fields, "limit": limit, "sort": sort},
        )
        payload = self._decode(response)
        data = payload.get("data")
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise LongoError(502, "INVALID_LONGO_RESPONSE", "Longo returned an invalid query result")
        return data

    def _document_data(self, response: httpx.Response) -> dict[str, Any]:
        payload = self._decode(response)
        data = payload.get("data")
        if not isinstance(data, dict):
            raise LongoError(502, "INVALID_LONGO_RESPONSE", "Longo returned an invalid document")
        return data

    @staticmethod
    def _decode(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise LongoError(
                502,
                "INVALID_LONGO_RESPONSE",
                f"Longo returned non-JSON HTTP {response.status_code}",
            ) from exc
        if not isinstance(payload, dict):
            raise LongoError(502, "INVALID_LONGO_RESPONSE", "Longo returned a non-object response")
        if response.is_error:
            error = payload.get("error")
            if isinstance(error, dict):
                code = str(error.get("code") or "LONGO_ERROR")
                message = str(error.get("message") or "Longo request failed")
            else:
                code = "LONGO_ERROR"
                message = f"Longo request failed with HTTP {response.status_code}"
            raise LongoError(response.status_code, code, message)
        return payload

    @staticmethod
    def _collection_path(database: str, collection: str) -> str:
        return (
            f"/v1/databases/{quote(database, safe='')}"
            f"/collections/{quote(collection, safe='')}/documents"
        )


class LongoSyncClient:
    def __init__(self, base_url: str, timeout_seconds: float = 10.0) -> None:
        if not base_url:
            raise ValueError("Longo base URL is required")
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(timeout_seconds),
        )

    def close(self) -> None:
        self._client.close()

    def get_document(
        self,
        database: str,
        collection: str,
        document_id: str,
    ) -> dict[str, Any] | None:
        response = self._client.get(
            f"{LongoClient._collection_path(database, collection)}/{quote(document_id, safe='')}"
        )
        if response.status_code == 404:
            return None
        payload = LongoClient._decode(response)
        data = payload.get("data")
        if not isinstance(data, dict):
            raise LongoError(502, "INVALID_LONGO_RESPONSE", "Longo returned an invalid document")
        return data

    def insert_document(
        self,
        database: str,
        collection: str,
        document: dict[str, Any],
    ) -> dict[str, Any]:
        response = self._client.post(
            LongoClient._collection_path(database, collection),
            json=document,
        )
        return self._document_data(response)

    def upsert_document(
        self,
        database: str,
        collection: str,
        document_id: str,
        document: dict[str, Any],
    ) -> dict[str, Any]:
        values = dict(document)
        values["id"] = document_id
        path = f"{LongoClient._collection_path(database, collection)}/{quote(document_id, safe='')}"
        response = self._client.put(path, json=values)
        if response.status_code != 404:
            return self._document_data(response)
        try:
            return self.insert_document(database, collection, values)
        except LongoError as exc:
            if exc.status_code != 409:
                raise
            retry = self._client.put(path, json=values)
            return self._document_data(retry)

    @staticmethod
    def _document_data(response: httpx.Response) -> dict[str, Any]:
        payload = LongoClient._decode(response)
        data = payload.get("data")
        if not isinstance(data, dict):
            raise LongoError(502, "INVALID_LONGO_RESPONSE", "Longo returned an invalid document")
        return data


@contextmanager
def get_longo_sync_client() -> Iterator[LongoSyncClient]:
    longo_url = os.getenv("LONGO_URL")
    if not longo_url:
        raise RuntimeError("LONGO_URL is not configured")
    client = LongoSyncClient(longo_url)
    try:
        yield client
    finally:
        client.close()
