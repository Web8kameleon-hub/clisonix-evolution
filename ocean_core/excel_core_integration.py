"""
Excel Core Integration — Real-time Table & Spreadsheet Management
================================================================

Excel Core API (Port 8002) handles:
- Real-time spreadsheet operations
- Table creation/update/delete
- Data validation & formulas
- Export to multiple formats
- Sync with external data sources
"""

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

EXCEL_CORE_URL = os.getenv("EXCEL_CORE_URL", "http://clisonix-excel:8002")
EXCEL_TIMEOUT = float(os.getenv("EXCEL_TIMEOUT", "15.0"))

async def excel_create_workbook(
    title: str,
    data: List[List[Any]],
    column_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a new Excel workbook with data.

    Example:
    ```
    data = [
        [1, "Apple", 10, 150],
        [2, "Banana", 20, 100],
        [3, "Cherry", 15, 200],
    ]
    column_names = ["ID", "Product", "Quantity", "Price"]
    ```
    """
    try:
        async with httpx.AsyncClient(timeout=EXCEL_TIMEOUT) as client:
            response = await client.post(
                f"{EXCEL_CORE_URL}/api/v1/workbooks/create",
                json={
                    "title": title,
                    "data": data,
                    "column_names": column_names,
                    "auto_format": True,
                    "freeze_header": True,
                },
            )

            if response.status_code == 201:
                result = response.json()
                logger.info(f"📊 Excel workbook created: {title}")
                return result
            else:
                logger.warning(f"Excel creation failed: {response.status_code}")
                return {"status": "error"}
    except Exception as e:
        logger.error(f"Excel create error: {e}")
        return {"status": "error", "message": str(e)}


async def excel_insert_rows(
    workbook_id: str,
    sheet_name: str,
    rows: List[List[Any]],
) -> Dict[str, Any]:
    """Insert rows into existing worksheet."""
    try:
        async with httpx.AsyncClient(timeout=EXCEL_TIMEOUT) as client:
            response = await client.post(
                f"{EXCEL_CORE_URL}/api/v1/workbooks/{workbook_id}/sheets/{sheet_name}/rows",
                json={"rows": rows},
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Excel rows inserted: {len(rows)} rows to {sheet_name}")
                return result
            else:
                return {"status": "error"}
    except Exception as e:
        logger.error(f"Excel insert rows error: {e}")
        return {"status": "error", "message": str(e)}


async def excel_apply_formula(
    workbook_id: str,
    sheet_name: str,
    cell: str,
    formula: str,
) -> Dict[str, Any]:
    """Apply formula to a cell (e.g. "=SUM(A1:A10)")."""
    try:
        async with httpx.AsyncClient(timeout=EXCEL_TIMEOUT) as client:
            response = await client.post(
                f"{EXCEL_CORE_URL}/api/v1/workbooks/{workbook_id}/sheets/{sheet_name}/formulas",
                json={"cell": cell, "formula": formula},
            )

            if response.status_code == 200:
                logger.info(f"📐 Excel formula applied: {cell}")
                return response.json()
            else:
                return {"status": "error"}
    except Exception as e:
        logger.error(f"Excel formula error: {e}")
        return {"status": "error"}


async def excel_get_data(
    workbook_id: str,
    sheet_name: str,
) -> Dict[str, Any]:
    """Retrieve data from worksheet."""
    try:
        async with httpx.AsyncClient(timeout=EXCEL_TIMEOUT) as client:
            response = await client.get(
                f"{EXCEL_CORE_URL}/api/v1/workbooks/{workbook_id}/sheets/{sheet_name}/data"
            )

            if response.status_code == 200:
                result = response.json()
                logger.debug(f"📥 Excel data retrieved from {sheet_name}")
                return result
            else:
                return {"status": "error"}
    except Exception as e:
        logger.error(f"Excel get data error: {e}")
        return {"status": "error"}


async def excel_export(
    workbook_id: str,
    format: str = "xlsx",  # xlsx, csv, pdf, json
) -> Optional[bytes]:
    """Export workbook to file."""
    try:
        async with httpx.AsyncClient(timeout=EXCEL_TIMEOUT * 2) as client:
            response = await client.get(
                f"{EXCEL_CORE_URL}/api/v1/workbooks/{workbook_id}/export",
                params={"format": format},
            )

            if response.status_code == 200:
                logger.info(f"💾 Excel exported: {format}")
                return response.content
            else:
                logger.warning(f"Excel export failed: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        return None
