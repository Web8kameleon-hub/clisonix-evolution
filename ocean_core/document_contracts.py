"""
CLISONIX DOCUMENT CONTRACT SYSTEM
==================================
Enterprise-grade document generation with provenance tracking & governance.

Defines strict contracts for all document types:
- Excel Reports
- PDF Documents
- Structured Data Exports
- Business Intelligence Tables

Each document:
1. Has explicit contract (columns, rows, format)
2. Tracks provenance (source, agent, retrieval_time)
3. Validates governance rules (no source = no export)
4. Is auditable (full chain of custody)
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("document_contracts")


class DocumentFormat(str, Enum):
    """Supported document formats"""
    XLSX = "xlsx"
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


class ValidationStatus(str, Enum):
    """Document validation status"""
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    PUBLISHED = "published"


class GovernanceLevel(str, Enum):
    """Governance strictness levels"""
    LEVEL_1_OPEN = "level_1_open"          # No restrictions
    LEVEL_2_SOURCED = "level_2_sourced"    # Must have source_url
    LEVEL_3_VERIFIED = "level_3_verified"  # Must have verified agent + source
    LEVEL_4_STRICT = "level_4_strict"      # Medical/Finance grade - full validation
    LEVEL_5_AUDIT = "level_5_audit"        # Regulatory audit trail required


@dataclass
class DataColumn:
    """Defines a column contract"""
    name: str
    data_type: str  # string, number, date, boolean
    required: bool = True
    nullable: bool = False
    description: str = ""
    validation_rules: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentProvenance:
    """Tracks source, agent, and validation chain"""
    source_url: Optional[str]  # Where data came from
    source_type: str  # api, database, file, user_input, ocean_core
    retrieved_at: datetime
    retrieval_duration_ms: int
    agent_id: str  # Which agent/persona generated this
    agent_version: str
    raw_data_hash: str  # SHA256 of raw data (for auditability)
    raw_data_size_bytes: int
    validation_by: Optional[str] = None  # Which validation engine
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_timestamp: Optional[datetime] = None
    validation_notes: Optional[str] = None
    data_completeness_percent: float = 100.0
    data_accuracy_score: float = 0.0  # 0-100%

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["retrieved_at"] = self.retrieved_at.isoformat()
        if self.validation_timestamp:
            result["validation_timestamp"] = self.validation_timestamp.isoformat()
        return result

    def is_valid(self) -> bool:
        """Check if provenance passes governance"""
        return self.validation_status == ValidationStatus.VALIDATED

    def validate_governance(self, governance: "DocumentGovernanceRules") -> Tuple[bool, str]:
        """
        Validates provenance against governance rules.
        Returns (is_valid, error_message)
        """
        # Source requirement
        if governance.requires_source and not self.source_url:
            return False, "Governance requires source_url but it's missing"

        # Agent verification
        if governance.requires_verified_agent and self.validation_status != ValidationStatus.VALIDATED:
            return False, f"Governance requires verified agent, but validation status is {self.validation_status}"

        # Data completeness
        if self.data_completeness_percent < governance.min_data_completeness:
            return False, f"Data completeness {self.data_completeness_percent}% below required {governance.min_data_completeness}%"

        # Accuracy score
        if self.data_accuracy_score < governance.min_accuracy_score:
            return False, f"Accuracy score {self.data_accuracy_score} below required {governance.min_accuracy_score}"

        # Allowed agents
        if governance.allowed_agents:
            if self.agent_id not in governance.allowed_agents:
                return False, f"Agent {self.agent_id} not in allowed list: {governance.allowed_agents}"

        # Allowed sources
        if governance.allowed_sources and self.source_url:
            if not any(source in self.source_url for source in governance.allowed_sources):
                return False, f"Source {self.source_url} not in allowed sources"

        # Data age
        if governance.max_data_age_hours:
            age_hours = (datetime.utcnow() - self.retrieved_at).total_seconds() / 3600
            if age_hours > governance.max_data_age_hours:
                return False, f"Data age {age_hours}h exceeds max {governance.max_data_age_hours}h"

        return True, "OK"


@dataclass
class DocumentGovernanceRules:
    """Defines governance strictness for document"""
    level: GovernanceLevel
    requires_source: bool
    requires_verified_agent: bool
    min_data_completeness: float = 95.0  # %
    min_accuracy_score: float = 0.85  # 0-1
    require_audit_trail: bool = False
    max_data_age_hours: Optional[int] = None
    allowed_agents: Optional[List[str]] = None
    allowed_sources: Optional[List[str]] = None

    def validate(self, provenance: DocumentProvenance) -> Tuple[bool, str]:
        """
        Validates provenance against rules.
        Returns (is_valid, error_message)
        """
        # Source requirement
        if self.requires_source and not provenance.source_url:
            return False, "Governance requires source_url but it's missing"

        # Agent verification
        if self.requires_verified_agent and provenance.validation_status != ValidationStatus.VALIDATED:
            return False, "Governance requires verified agent, but validation not complete"

        # Data completeness
        if provenance.data_completeness_percent < self.min_data_completeness:
            return False, f"Data completeness {provenance.data_completeness_percent}% below required {self.min_data_completeness}%"

        # Accuracy score
        if provenance.data_accuracy_score < self.min_accuracy_score:
            return False, f"Accuracy score {provenance.data_accuracy_score} below required {self.min_accuracy_score}"

        # Allowed agents
        if self.allowed_agents:
            if provenance.agent_id not in self.allowed_agents:
                return False, f"Agent {provenance.agent_id} not in allowed list: {self.allowed_agents}"

        # Allowed sources
        if self.allowed_sources and provenance.source_url:
            if not any(source in provenance.source_url for source in self.allowed_sources):
                return False, f"Source {provenance.source_url} not in allowed sources"

        # Data age
        if self.max_data_age_hours:
            age_hours = (datetime.utcnow() - provenance.retrieved_at).total_seconds() / 3600
            if age_hours > self.max_data_age_hours:
                return False, f"Data age {age_hours}h exceeds max {self.max_data_age_hours}h"

        return True, "OK"


@dataclass
class DocumentContract:
    """
    Enterprise document contract: specifies exactly what a document contains.
    
    Usage:
    1. Define contract (what columns, format, governance)
    2. Fill with data
    3. Validate against contract
    4. Track provenance
    5. Check governance rules
    6. Export/publish if valid
    """
    contract_id: str
    title: str
    description: str
    doc_format: DocumentFormat
    columns: List[DataColumn]
    governance: DocumentGovernanceRules
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["doc_format"] = self.doc_format.value
        result["governance"]["level"] = self.governance.level.value
        result["created_at"] = self.created_at.isoformat()
        return result

    def validate_row(self, row: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates a row against contract.
        Returns (is_valid, list_of_errors)
        """
        errors = []

        for column in self.columns:
            value = row.get(column.name)

            # Check required
            if column.required and value is None:
                errors.append(f"Column '{column.name}' is required but missing")

            # Check nullable
            if value is None and not column.nullable:
                errors.append(f"Column '{column.name}' is not nullable")

            # Type validation
            if value is not None:
                if column.data_type == "number":
                    if not isinstance(value, (int, float)):
                        errors.append(f"Column '{column.name}' should be number, got {type(value).__name__}")
                elif column.data_type == "date":
                    if not isinstance(value, (str, datetime)):
                        errors.append(f"Column '{column.name}' should be date, got {type(value).__name__}")
                elif column.data_type == "boolean":
                    if not isinstance(value, bool):
                        errors.append(f"Column '{column.name}' should be boolean, got {type(value).__name__}")

        return len(errors) == 0, errors

    def validate_rows(self, rows: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validates all rows against contract.
        Returns (is_valid, list_of_errors)
        """
        all_errors = []
        for idx, row in enumerate(rows):
            is_valid, row_errors = self.validate_row(row)
            if not is_valid:
                for error in row_errors:
                    all_errors.append(f"Row {idx}: {error}")
        return len(all_errors) == 0, all_errors


@dataclass
class DocumentData:
    """
    Document with data + provenance + governance status.
    This is what gets exported.
    """
    contract: DocumentContract
    rows: List[Dict[str, Any]]
    provenance: DocumentProvenance
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    generated_by_agent: str = ""
    document_hash: str = ""  # SHA256 hash of complete document

    def __post_init__(self):
        """Calculate document hash for auditability"""
        if not self.document_hash:
            doc_json = json.dumps({
                "contract_id": self.contract.contract_id,
                "rows_count": len(self.rows),
                "provenance_source": self.provenance.source_url,
                "created_at": self.created_at.isoformat()
            }, sort_keys=True)
            self.document_hash = hashlib.sha256(doc_json.encode()).hexdigest()

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Full validation: contract + governance.
        Returns (is_valid, list_of_errors)
        """
        all_errors = []

        # Validate contract against governance
        is_governance_valid, governance_error = self.provenance.validate_governance(self.contract.governance)
        if not is_governance_valid:
            all_errors.append(f"Governance violation: {governance_error}")

        # Validate each row against contract
        for idx, row in enumerate(self.rows):
            is_valid, row_errors = self.contract.validate_row(row)
            if not is_valid:
                for error in row_errors:
                    all_errors.append(f"Row {idx}: {error}")

        return len(all_errors) == 0, all_errors

    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary"""
        return {
            "contract": self.contract.to_dict(),
            "rows": self.rows,
            "provenance": self.provenance.to_dict(),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "generated_by_agent": self.generated_by_agent,
            "document_hash": self.document_hash,
            "validation": {
                "is_valid": self.validate()[0],
                "errors": self.validate()[1]
            }
        }

    def to_export_json(self) -> str:
        """Export as JSON string"""
        return json.dumps(self.to_dict(), indent=2)


# Predefined governance levels
GOVERNANCE_PRESETS = {
    "open": DocumentGovernanceRules(
        level=GovernanceLevel.LEVEL_1_OPEN,
        requires_source=False,
        requires_verified_agent=False,
    ),
    "sourced": DocumentGovernanceRules(
        level=GovernanceLevel.LEVEL_2_SOURCED,
        requires_source=True,
        requires_verified_agent=False,
        min_data_completeness=90.0,
    ),
    "verified": DocumentGovernanceRules(
        level=GovernanceLevel.LEVEL_3_VERIFIED,
        requires_source=True,
        requires_verified_agent=True,
        min_data_completeness=95.0,
        min_accuracy_score=0.90,
    ),
    "strict_medical": DocumentGovernanceRules(
        level=GovernanceLevel.LEVEL_4_STRICT,
        requires_source=True,
        requires_verified_agent=True,
        min_data_completeness=99.0,
        min_accuracy_score=0.99,
        require_audit_trail=True,
        max_data_age_hours=24,
    ),
    "audit": DocumentGovernanceRules(
        level=GovernanceLevel.LEVEL_5_AUDIT,
        requires_source=True,
        requires_verified_agent=True,
        min_data_completeness=100.0,
        min_accuracy_score=0.99,
        require_audit_trail=True,
        max_data_age_hours=1,
    ),
}


# Example contract: CPI Report
def create_cpi_report_contract() -> DocumentContract:
    """Create contract for CPI (Consumer Price Index) report"""
    return DocumentContract(
        contract_id="cpi_monthly_report_v1",
        title="Monthly CPI Report",
        description="Consumer Price Index monthly data with year-over-year comparison",
        doc_format=DocumentFormat.XLSX,
        columns=[
            DataColumn("Month", "string", required=True, description="Month name"),
            DataColumn("CPI_Value", "number", required=True, description="CPI index value"),
            DataColumn("YoY_Change_Percent", "number", required=True, description="Year-over-year change %"),
            DataColumn("Inflation_Rate", "number", required=True, description="Inflation rate %"),
        ],
        governance=GOVERNANCE_PRESETS["verified"],
        created_by="system_cpi_module",
        tags=["economics", "inflation", "monthly"],
    )


def create_research_report_contract() -> DocumentContract:
    """Create contract for research report"""
    return DocumentContract(
        contract_id="research_report_v1",
        title="Research Report",
        description="Academic research report with findings and citations",
        doc_format=DocumentFormat.PDF,
        columns=[
            DataColumn("Section", "string", required=True),
            DataColumn("Content", "string", required=True),
            DataColumn("Source_URL", "string", required=False, nullable=True),
            DataColumn("Citation_Count", "number", required=False),
        ],
        governance=GOVERNANCE_PRESETS["sourced"],
        created_by="system_research_module",
        tags=["research", "academic"],
    )
