"""Exercise the actual reader, report renderer and download contract in isolation."""
import asyncio
import hashlib
import importlib.util
import io
import zipfile
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pypdf import PdfReader


@pytest.fixture
def pipeline(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORT_OUTPUT_DIR", str(tmp_path))
    path = Path(__file__).resolve().parents[2] / "apps/api/routers/v1_router.py"
    spec = importlib.util.spec_from_file_location("workspace_report_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = FastAPI()
    app.include_router(module.router)
    # Local renderer contract tests only; this does not prove production auth.
    app.dependency_overrides[module.require_api_key] = lambda: None
    with TestClient(app) as client:
        yield module, client, tmp_path


def test_source_to_real_pdf_and_download(pipeline):
    module, client, folder = pipeline
    content = b"Measured production: 17 items on 2026-09-26."
    result = client.post("/api/v1/reader/ingest-file", files={"file": ("observations.txt", content)})
    assert result.status_code == 201
    source = result.json()["source"]
    assert source["sha256"] == hashlib.sha256(content).hexdigest()
    assert source["preview"] == content.decode()
    assert list(folder.iterdir()) == []  # Uploaded original is not retained.
    response = client.post("/api/v1/commands/execute", json={
        "command": "Report the provided measurements", "output_format": "pdf",
        "sources": [source["source_id"]],
    })
    assert response.status_code == 202
    job_id = response.json()["job"]["job_id"]
    job = client.get(f"/api/v1/reports/jobs/{job_id}").json()["job"]
    assert job["status"] == "complete"
    download = client.get(job["download_url"])
    assert download.status_code == 200
    assert download.content.startswith(b"%PDF-")
    assert "17 items" in "\n".join(page.extract_text() for page in PdfReader(io.BytesIO(download.content)).pages)


def test_missing_source_is_not_a_success(pipeline):
    _, client, _ = pipeline
    response = client.post("/api/v1/commands/execute", json={"command": "Report", "sources": []})
    assert response.status_code == 422


@pytest.mark.parametrize("output_format", ["excel", "word", "pptx"])
def test_office_artifact_contains_actual_source(pipeline, output_format):
    _, client, _ = pipeline
    source = client.post("/api/v1/reader/ingest-file", files={
        "file": ("measurement.txt", b"Verified measurement: 17 items."),
    }).json()["source"]
    accepted = client.post("/api/v1/commands/execute", json={
        "command": "Report measurements", "output_format": output_format,
        "sources": [source["source_id"]],
    })
    assert accepted.status_code == 202
    job_id = accepted.json()["job"]["job_id"]
    job = client.get(f"/api/v1/reports/jobs/{job_id}").json()["job"]
    assert job["status"] == "complete", job.get("error")
    download = client.get(job["download_url"])
    assert download.status_code == 200
    with zipfile.ZipFile(io.BytesIO(download.content)) as artifact:
        assert any(b"17 items" in artifact.read(name) for name in artifact.namelist() if name.endswith('.xml'))


def test_binary_is_not_presented_as_document_text(pipeline):
    _, client, folder = pipeline
    response = client.post("/api/v1/reader/ingest-file", files={"file": ("document.pdf", b"%PDF-")})
    assert response.status_code == 415
    assert list(folder.iterdir()) == []


@pytest.mark.parametrize("extra,expected", [(0, 201), (1, 413)])
def test_one_gib_boundary_without_allocating_one_gib(pipeline, extra, expected):
    module, _, folder = pipeline

    class ChunkedSource:
        filename = "large.txt"
        closed = False
        count = 0

        async def read(self, size):
            assert size == 1024 * 1024
            self.count += 1
            if self.count <= 1024:
                return b"a" * size
            return b"a" if self.count == 1025 and extra else b""

        async def close(self):
            self.closed = True

    source = ChunkedSource()
    if expected == 413:
        with pytest.raises(HTTPException) as error:
            asyncio.run(module.ingest_file(source))
        assert error.value.status_code == expected
        assert not module._SOURCES
    else:
        response = asyncio.run(module.ingest_file(source))
        assert response.status_code == expected
        retained = next(iter(module._SOURCES.values()))
        assert retained["size_bytes"] == 1024**3
        assert len(retained["preview"]) == 12000
        assert retained["preview_truncated"] is True
    assert source.closed
    assert list(folder.iterdir()) == []
