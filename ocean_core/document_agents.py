"""
DOCUMENT AGENTS
===============
Specialized agents for document generation.

Types:
- DocumentAgent: Main orchestrator for document requests
- ExcelAgent: Generates Excel/CSV reports
- PDFAgent: Generates PDF documents
- ReportAgent: Generates business intelligence reports

Each agent:
1. Receives user request
2. Calls Ocean Core for content
3. Structures data according to contract
4. Adds provenance tracking
5. Validates against governance
6. Returns validated document or error
"""

import hashlib
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import requests

from document_contracts import (
    DocumentContract,
    DocumentData,
    DocumentProvenance,
    ValidationStatus,
)
from provenance_engine import get_provenance_validator

logger = logging.getLogger("document_agents")

OCEAN_CORE_URL = "http://localhost:8030"


class AgentType(str, Enum):
    """Agent types"""
    DOCUMENT_ORCHESTRATOR = "document_orchestrator"
    EXCEL_AGENT = "excel_agent"
    PDF_AGENT = "pdf_agent"
    REPORT_AGENT = "report_agent"
    DATA_AGENT = "data_agent"


class BaseDocumentAgent:
    """
    Base class for document agents.
    
    Workflow:
    1. Receive request with contract + query
    2. Call Ocean Core to get intelligent response
    3. Parse response into contract rows
    4. Track provenance (source = Ocean Core, agent_id = self.agent_id)
    5. Validate against contract + governance
    6. Return DocumentData with full chain of custody
    """

    def __init__(self, agent_id: str, agent_type: AgentType):
        """Initialize agent"""
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.ocean_url = OCEAN_CORE_URL
        self.validator = get_provenance_validator()
        logger.info(f"✅ {self.__class__.__name__} initialized: {agent_id}")

    def query_ocean_core(
        self, query: str, language: str = "en"
    ) -> Dict[str, Any]:
        """
        Query Ocean Core for content.
        
        Returns:
        {
            "response": "...",
            "intent": "...",
            "confidence": 0.95,
            "sources": [...],
            "personas_used": [...]
        }
        """
        try:
            payload = {
                "query": query,
                "message": query,
                "language": language,
                "response_language": language,
            }
            response = requests.post(
                f"{self.ocean_url}/api/v1/query",
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ocean Core at {self.ocean_url}")
            raise
        except Exception as e:
            logger.error(f"Ocean Core query failed: {str(e)}")
            raise

    def create_provenance(
        self,
        source_url: str,
        raw_data: Dict[str, Any],
        language: str,
        retrieval_duration_ms: int,
    ) -> DocumentProvenance:
        """
        Create provenance tracking object.
        
        Captures:
        - source_url (where data came from)
        - agent_id (who created this)
        - raw_data_hash (SHA256 for auditability)
        - retrieval_timestamp
        """
        raw_data_str = str(raw_data)
        raw_data_hash = hashlib.sha256(raw_data_str.encode()).hexdigest()

        provenance = DocumentProvenance(
            source_url=source_url,
            source_type="ocean_core",
            retrieved_at=datetime.utcnow(),
            retrieval_duration_ms=retrieval_duration_ms,
            agent_id=self.agent_id,
            agent_version="1.0.0",
            raw_data_hash=raw_data_hash,
            raw_data_size_bytes=len(raw_data_str),
            validation_status=ValidationStatus.PENDING,
            data_completeness_percent=100.0,
            data_accuracy_score=0.95,  # Assume high accuracy from Ocean Core
        )
        logger.info(f"✅ Provenance created: {self.agent_id} | Hash: {raw_data_hash[:8]}...")
        return provenance

    def generate_document(
        self,
        contract: DocumentContract,
        query: str,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Generate document: Query Ocean + Structure + Validate.
        
        Returns:
        {
            "success": bool,
            "document": DocumentData (if success),
            "errors": [...] (if failed),
            "validation_status": "VALIDATED" | "REJECTED"
        }
        """
        try:
            logger.info(f"[{self.agent_id}] Starting document generation for: {contract.title}")

            # Step 1: Query Ocean Core
            import time
            start_time = time.time()
            ocean_response = self.query_ocean_core(query, language)
            retrieval_ms = int((time.time() - start_time) * 1000)

            response_content = ocean_response.get("response", "")
            if not response_content:
                return {
                    "success": False,
                    "errors": ["Ocean Core returned empty response"],
                    "validation_status": "REJECTED",
                }

            logger.info(
                f"[{self.agent_id}] Ocean Core responded in {retrieval_ms}ms"
            )

            # Step 2: Create provenance
            provenance = self.create_provenance(
                source_url=f"{self.ocean_url}/api/v1/query",
                raw_data=ocean_response,
                language=language,
                retrieval_duration_ms=retrieval_ms,
            )

            # Step 3: Structure data according to contract
            rows = self.structure_data(response_content, contract)
            if not rows:
                return {
                    "success": False,
                    "errors": [
                        "Could not structure Ocean Core response into contract"
                    ],
                    "validation_status": "REJECTED",
                }

            logger.info(f"[{self.agent_id}] Structured {len(rows)} rows from response")

            # Step 4: Create DocumentData
            document = DocumentData(
                contract=contract,
                rows=rows,
                provenance=provenance,
                metadata={
                    "query": query,
                    "language": language,
                    "ocean_personas": ocean_response.get("personas_used", []),
                    "ocean_confidence": ocean_response.get("confidence", 0),
                },
                generated_by_agent=self.agent_id,
            )

            # Step 5: Validate
            is_valid, errors = self.validator.validate_document(document)

            if not is_valid:
                logger.warning(
                    f"[{self.agent_id}] Document validation FAILED: {errors}"
                )
                return {
                    "success": False,
                    "errors": errors,
                    "validation_status": "REJECTED",
                    "document": document.to_dict(),
                }

            logger.info(f"[{self.agent_id}] ✅ Document VALIDATED and ready for export")
            return {
                "success": True,
                "document": document,
                "validation_status": "VALIDATED",
                "provenance": provenance.to_dict(),
            }

        except Exception as e:
            logger.error(f"[{self.agent_id}] Document generation failed: {str(e)}")
            return {
                "success": False,
                "errors": [f"Document generation error: {str(e)}"],
                "validation_status": "REJECTED",
            }

    def structure_data(
        self, response_content: str, contract: DocumentContract
    ) -> List[Dict[str, Any]]:
        """
        Structure Ocean Core response into contract rows.
        Override in subclasses for specific formatting.
        """
        # Base implementation: single row with response as content
        column_names = [col.name for col in contract.columns]
        if len(column_names) == 0:
            return []

        # Try to fit response into first column, leave others empty
        row: Dict[str, Any] = {column_names[0]: response_content}
        for col_name in column_names[1:]:
            row[col_name] = None

        return [row]


class ExcelDocumentAgent(BaseDocumentAgent):
    """Agent for generating Excel/CSV documents"""

    def __init__(self):
        super().__init__("excel_document_agent", AgentType.EXCEL_AGENT)

    def structure_data(
        self, response_content: str, contract: DocumentContract
    ) -> List[Dict[str, Any]]:
        """Structure response for tabular Excel format"""
        # Parse response into rows (this is simplified)
        lines = response_content.split("\n")
        rows = []

        column_names = [col.name for col in contract.columns]
        for line in lines:
            if line.strip():
                # Create row with available data
                row = {}
                for idx, col_name in enumerate(column_names):
                    row[col_name] = line if idx == 0 else None
                rows.append(row)

        return rows if rows else [{col: None for col in column_names}]


class PDFDocumentAgent(BaseDocumentAgent):
    """Agent for generating PDF documents"""

    def __init__(self):
        super().__init__("pdf_document_agent", AgentType.PDF_AGENT)

    def structure_data(
        self, response_content: str, contract: DocumentContract
    ) -> List[Dict[str, Any]]:
        """Structure response for PDF format"""
        # For PDFs, content often goes into fewer, larger fields
        column_names = [col.name for col in contract.columns]
        return [
            {
                col_name: response_content if col_name == column_names[0] else None
                for col_name in column_names
            }
        ]


class ReportDocumentAgent(BaseDocumentAgent):
    """Agent for generating business intelligence reports"""

    def __init__(self):
        super().__init__(
            "report_document_agent", AgentType.REPORT_AGENT
        )

    def structure_data(
        self, response_content: str, contract: DocumentContract
    ) -> List[Dict[str, Any]]:
        """Structure response for report format"""
        # Split into sections
        sections = response_content.split("##")
        rows = []
        column_names = [col.name for col in contract.columns]

        for section in sections:
            if section.strip():
                row = {}
                parts = section.split(":", 1)
                row[column_names[0]] = parts[0].strip() if len(parts) > 0 else ""
                row[column_names[1] if len(column_names) > 1 else column_names[0]] = (
                    parts[1].strip() if len(parts) > 1 else ""
                )
                for col_name in column_names[2:]:
                    row[col_name] = None
                rows.append(row)

        return rows if rows else [{col: None for col in column_names}]


# Agent registry
DOCUMENT_AGENTS = {
    "excel": ExcelDocumentAgent(),
    "pdf": PDFDocumentAgent(),
    "report": ReportDocumentAgent(),
}


def get_agent(agent_name: str) -> Optional[BaseDocumentAgent]:
    """Get document agent by name"""
    agent = DOCUMENT_AGENTS.get(agent_name)
    if not agent:
        logger.warning(f"Unknown agent: {agent_name}")
    return agent


def list_agents() -> Dict[str, str]:
    """List all available document agents"""
    return {
        name: agent.agent_id for name, agent in DOCUMENT_AGENTS.items()
    }
