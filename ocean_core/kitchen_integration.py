"""
Kitchen API Integration — Document Processing Pipeline
=====================================================

Kitchen Service is a document processing engine that:
- Converts documents to various formats
- Extracts structured data
- Processes large batches
- Integrates with Excel Core for table generation
"""

import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

KITCHEN_API_URL = os.getenv("KITCHEN_API_URL", "http://clisonix-kitchen-worker:3100")
KITCHEN_TIMEOUT = float(os.getenv("KITCHEN_TIMEOUT", "30.0"))

async def kitchen_process_document(
    filename: str,
    content_base64: str,
    doc_type: str,
    processing_mode: str = "full",  # "full", "extract", "convert", "structure"
) -> Dict[str, Any]:
    """
    Process document via Kitchen API.

    Modes:
    - full: Extract + Structure + Convert
    - extract: Text extraction only
    - convert: Format conversion
    - structure: Detect tables/lists/sections
    """
    try:
        async with httpx.AsyncClient(timeout=KITCHEN_TIMEOUT) as client:
            response = await client.post(
                f"{KITCHEN_API_URL}/api/v1/documents/process",
                json={
                    "filename": filename,
                    "content_base64": content_base64,
                    "doc_type": doc_type,
                    "mode": processing_mode,
                    "extract_tables": True,
                    "extract_metadata": True,
                },
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"🍳 Kitchen processed: {filename} ({doc_type})")
                return result
            else:
                logger.warning(f"Kitchen error [{response.status_code}]: {response.text[:200]}")
                return {"status": "error", "message": f"Kitchen processing failed: {response.status_code}"}
    except Exception as e:
        logger.error(f"Kitchen API error: {e}")
        return {"status": "error", "message": str(e)}


async def kitchen_convert_to_excel(
    tables_data: list[dict],
    filename_base: str,
) -> Optional[bytes]:
    """Convert extracted tables to Excel file via Kitchen."""
    try:
        async with httpx.AsyncClient(timeout=KITCHEN_TIMEOUT) as client:
            response = await client.post(
                f"{KITCHEN_API_URL}/api/v1/documents/to-excel",
                json={
                    "filename": filename_base,
                    "tables": tables_data,
                    "format": "xlsx",
                },
            )

            if response.status_code == 200:
                logger.info(f"📊 Kitchen exported to Excel: {filename_base}.xlsx")
                return response.content
            else:
                logger.warning(f"Kitchen Excel export failed: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Kitchen Excel export error: {e}")
        return None


async def kitchen_batch_convert(
    file_list: list[dict],  # {"filename": str, "content_base64": str, "doc_type": str}
    output_format: str = "pdf",
) -> Dict[str, Any]:
    """Batch process multiple documents."""
    try:
        async with httpx.AsyncClient(timeout=KITCHEN_TIMEOUT * 2) as client:
            response = await client.post(
                f"{KITCHEN_API_URL}/api/v1/documents/batch",
                json={
                    "files": file_list,
                    "output_format": output_format,
                    "parallel_workers": 4,
                },
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"🍳 Kitchen batch processed: {len(file_list)} files")
                return result
            else:
                return {"status": "error", "message": "Batch processing failed"}
    except Exception as e:
        logger.error(f"Kitchen batch error: {e}")
        return {"status": "error", "message": str(e)}
