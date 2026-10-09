"""
PROVENANCE ENGINE
=================
Validates documents against governance rules.
Ensures source tracking, agent verification, and data quality.

Key responsibility:
- No document leaves without full provenance chain
- Governance rules strictly enforced
- Audit trail preserved for regulatory compliance
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from document_contracts import (
    DocumentData,
    DocumentGovernanceRules,
    DocumentProvenance,
    ValidationStatus,
)

logger = logging.getLogger("provenance_engine")


class ProvenanceValidator:
    """
    Validates documents against governance rules.
    
    Flow:
    1. Agent generates document with raw data
    2. Provenance engine captures: source, agent_id, timestamp
    3. Validator checks: source exists? agent verified? data complete?
    4. If validation passes → mark as VALIDATED
    5. If fails → mark as REJECTED with reason
    6. Only VALIDATED documents can be exported
    """

    def __init__(self):
        """Initialize validator"""
        self.validation_log: List[Dict[str, Any]] = []
        logger.info("✅ ProvenanceValidator initialized")

    def validate_provenance(
        self,
        provenance: DocumentProvenance,
        governance: DocumentGovernanceRules,
    ) -> Tuple[bool, str, List[str]]:
        """
        Validate provenance against governance rules.
        
        Returns:
        - is_valid (bool)
        - status (str): VALIDATED | REJECTED | FLAGGED
        - errors (List[str]): List of violations if any
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Rule 1: Source requirement
        if governance.requires_source:
            if not provenance.source_url:
                errors.append("Governance LEVEL requires source_url but it's missing")
            else:
                logger.info(f"✅ Source verified: {provenance.source_url}")

        # Rule 2: Agent verification
        if governance.requires_verified_agent:
            if provenance.validation_status != ValidationStatus.VALIDATED:
                errors.append(
                    f"Agent verification required, but status is {provenance.validation_status}"
                )
            else:
                logger.info(f"✅ Agent verified: {provenance.agent_id}")

        # Rule 3: Data completeness
        if provenance.data_completeness_percent < governance.min_data_completeness:
            errors.append(
                f"Data completeness {provenance.data_completeness_percent}% below "
                f"required {governance.min_data_completeness}%"
            )
        else:
            logger.info(
                f"✅ Data completeness OK: {provenance.data_completeness_percent}%"
            )

        # Rule 4: Accuracy score
        if provenance.data_accuracy_score < governance.min_accuracy_score:
            errors.append(
                f"Accuracy score {provenance.data_accuracy_score:.2f} below "
                f"required {governance.min_accuracy_score:.2f}"
            )
        else:
            logger.info(
                f"✅ Accuracy score OK: {provenance.data_accuracy_score:.2f}"
            )

        # Rule 5: Data age check
        if governance.max_data_age_hours:
            age_hours = (
                datetime.utcnow() - provenance.retrieved_at
            ).total_seconds() / 3600
            if age_hours > governance.max_data_age_hours:
                errors.append(
                    f"Data age {age_hours:.1f}h exceeds max {governance.max_data_age_hours}h"
                )
            else:
                logger.info(f"✅ Data age OK: {age_hours:.1f}h")

        # Rule 6: Allowed agents
        if governance.allowed_agents:
            if provenance.agent_id not in governance.allowed_agents:
                errors.append(
                    f"Agent {provenance.agent_id} not in allowed list: "
                    f"{governance.allowed_agents}"
                )
            else:
                logger.info("✅ Agent in allowed list")

        # Rule 7: Allowed sources
        if governance.allowed_sources and provenance.source_url:
            source_allowed = any(
                source in provenance.source_url
                for source in governance.allowed_sources
            )
            if not source_allowed:
                errors.append(
                    f"Source {provenance.source_url} not in allowed sources: "
                    f"{governance.allowed_sources}"
                )
            else:
                logger.info("✅ Source in allowed list")

        # Determine status
        if errors:
            final_status = "REJECTED"
        elif warnings:
            final_status = "FLAGGED"
        else:
            final_status = "VALIDATED"

        # Log validation
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": provenance.agent_id,
            "source_url": provenance.source_url,
            "status": final_status,
            "errors": errors,
            "warnings": warnings,
            "governance_level": governance.level.value,
        }
        self.validation_log.append(log_entry)

        logger.info(
            f"[PROVENANCE] {final_status}: {provenance.agent_id} | "
            f"Source: {provenance.source_url} | "
            f"Errors: {len(errors)}, Warnings: {len(warnings)}"
        )

        return len(errors) == 0, final_status, errors + warnings

    def validate_document(
        self, document: DocumentData
    ) -> Tuple[bool, List[str]]:
        """
        Full document validation: contract + provenance.
        
        Returns:
        - is_valid (bool)
        - errors (List[str])
        """
        all_errors: List[str] = []

        # Validate provenance against governance
        is_prov_valid, prov_status, prov_errors = self.validate_provenance(
            document.provenance, document.contract.governance
        )
        all_errors.extend(prov_errors)

        # Validate contract
        is_contract_valid, contract_errors = document.contract.validate_rows(
            document.rows
        )
        all_errors.extend(contract_errors)

        # Final validation
        is_valid = is_prov_valid and is_contract_valid
        logger.info(
            f"[DOCUMENT] Validation: {'PASS' if is_valid else 'FAIL'} | "
            f"Errors: {len(all_errors)}"
        )

        return is_valid, all_errors

    def get_validation_log(self) -> List[Dict[str, Any]]:
        """Get validation audit trail"""
        return self.validation_log

    def clear_validation_log(self) -> None:
        """Clear validation log"""
        self.validation_log = []


class GovernanceRulesEngine:
    """
    Manages governance rules for different departments/use-cases.
    """

    def __init__(self):
        """Initialize rules engine"""
        self.rules_store: Dict[str, DocumentGovernanceRules] = {}
        logger.info("✅ GovernanceRulesEngine initialized")

    def register_rules(self, name: str, rules: DocumentGovernanceRules) -> None:
        """Register governance rules"""
        self.rules_store[name] = rules
        logger.info(f"✅ Registered governance rules: {name} (Level: {rules.level.value})")

    def get_rules(self, name: str) -> Optional[DocumentGovernanceRules]:
        """Get governance rules by name"""
        return self.rules_store.get(name)

    def list_rules(self) -> Dict[str, str]:
        """List all registered rules"""
        return {
            name: rules.level.value for name, rules in self.rules_store.items()
        }


# Global instances
_provenance_validator: Optional[ProvenanceValidator] = None
_governance_engine: Optional[GovernanceRulesEngine] = None


def get_provenance_validator() -> ProvenanceValidator:
    """Get or create provenance validator"""
    global _provenance_validator
    if _provenance_validator is None:
        _provenance_validator = ProvenanceValidator()
    return _provenance_validator


def get_governance_engine() -> GovernanceRulesEngine:
    """Get or create governance rules engine"""
    global _governance_engine
    if _governance_engine is None:
        _governance_engine = GovernanceRulesEngine()
    return _governance_engine


def initialize_governance_engine():
    """Initialize governance engine with default rules"""
    from document_contracts import GOVERNANCE_PRESETS

    engine = get_governance_engine()
    for name, rules in GOVERNANCE_PRESETS.items():
        engine.register_rules(name, rules)
    logger.info("✅ Governance engine initialized with default rules")
