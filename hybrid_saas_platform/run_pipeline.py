"""
Run Pipeline - Main Orchestrator
=================================
Implements the complete 5-step pipeline:

1️⃣ Intake & Protocol Listener
2️⃣ Validation & Security
3️⃣ Labs & Agents Execution
4️⃣ Maturity Gate & ML Overlay
5️⃣ Enforcement Layer & Protocol Sovereignty

Flow matches the Hybrid Protocol Sovereign System diagram:
INPUT → RAW → NORMALIZED → TEST → IMMATURE → MATURE → ML OVERLAY → ENFORCEMENT

Key Principles:
- Append-only canonical table
- ML aktivizohet vetëm mbi rreshtat e pjekur (MATURE)
- Listen First, Enforce After Maturity
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .core.canonical_table import (
    CanonicalTable, 
    CanonicalRow, 
    compute_maturity_state,
    get_global_table
)
from .core.parser import parse_input
from .core.validator import validate_security, validate_schema
from .labs.lab_executor import execute_lab
from .agents.agent_registry import select_agent, get_agent_manager
from .ml_overlay.ml_manager import run_ml_models, is_ml_eligible
from .enforcement.enforcement_manager import apply_enforcement

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HybridPipeline')


class PipelineConfig:
    """Configuration for pipeline execution"""
    
    def __init__(self, 
                 security_method: str = "NONE",
                 run_labs: bool = True,
                 run_ml: bool = True,
                 run_enforcement: bool = True,
                 verbose: bool = True):
        self.security_method = security_method
        self.run_labs = run_labs
        self.run_ml = run_ml
        self.run_enforcement = run_enforcement
        self.verbose = verbose


class PipelineResult:
    """Result of pipeline execution"""
    
    def __init__(self):
        self.row_id: Optional[str] = None
        self.success: bool = False
        self.steps_completed: List[str] = []
        self.final_status: str = "RAW"
        self.final_maturity: str = "IMMATURE"
        self.ml_applied: bool = False
        self.enforcement_applied: bool = False
        self.errors: List[str] = []
        self.timing: Dict[str, float] = {}
        self.final_row: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'row_id': self.row_id,
            'success': self.success,
            'steps_completed': self.steps_completed,
            'final_status': self.final_status,
            'final_maturity': self.final_maturity,
            'ml_applied': self.ml_applied,
            'enforcement_applied': self.enforcement_applied,
            'errors': self.errors,
            'timing': self.timing,
            'final_row': self.final_row
        }


class HybridPipeline:
    """
    Main pipeline orchestrator for Hybrid Protocol Sovereign System
    
    Implements the 5-step flow:
    1. Intake - Parse input from any protocol
    2. Validation - Security & schema checks
    3. Labs/Agents - Execute tests, generate artifacts
    4. Maturity Gate & ML - Apply ML only on MATURE rows
    5. Enforcement - Protocol sovereignty for MATURE rows
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.table = get_global_table()
    
    def run(self, input_payload: Any, protocol_type: str,
            credentials: Optional[Dict[str, Any]] = None) -> PipelineResult:
        """
        Execute the complete pipeline
        
        Args:
            input_payload: Raw input data
            protocol_type: Source protocol (REST, GraphQL, gRPC, Webhook, File)
            credentials: Optional security credentials
            
        Returns:
            PipelineResult with execution details
        """
        result = PipelineResult()
        start_time = datetime.utcnow()
        
        try:
            # -----------------------------
            # 1️⃣ INTAKE & PROTOCOL LISTENER
            # -----------------------------
            step_start = datetime.utcnow()
            
            if self.config.verbose:
                logger.info(f"Step 1: Intake - Protocol: {protocol_type}")
            
            # Parse input to canonical format
            canonical_row = parse_input(input_payload, protocol_type)
            canonical_row['status'] = 'RAW'
            canonical_row['security'] = 'PENDING'
            canonical_row['schema_validation'] = 'PENDING'
            canonical_row['maturity_state'] = 'IMMATURE'
            
            # Append to table
            row = self.table.append(CanonicalRow.from_dict(canonical_row))
            result.row_id = row.row_id
            
            result.steps_completed.append("intake")
            result.timing['intake_ms'] = (datetime.utcnow() - step_start).total_seconds() * 1000
            
            if self.config.verbose:
                logger.info(f"  → Row created: {row.row_id[:8]}... Status: RAW")
            
            # -----------------------------
            # 2️⃣ VALIDATION & SECURITY
            # -----------------------------
            step_start = datetime.utcnow()
            
            if self.config.verbose:
                logger.info("Step 2: Validation & Security")
            
            # Security check
            security_result = validate_security(
                canonical_row, 
                self.config.security_method,
                credentials
            )
            canonical_row['security'] = security_result
            
            # Schema validation
            validation_result = validate_schema(canonical_row)
            canonical_row['schema_validation'] = validation_result
            
            # Update status based on validation
            if security_result == 'PASS' and validation_result == 'PASS':
                canonical_row['status'] = 'NORMALIZED'
            else:
                canonical_row['status'] = 'FAIL'
                result.errors.append(f"Validation failed: Security={security_result}, Schema={validation_result}")
            
            # Compute initial maturity
            canonical_row['maturity_state'] = compute_maturity_state(canonical_row)
            
            # Update row in table
            self.table.update_row(row.row_id, canonical_row)
            
            result.steps_completed.append("validation")
            result.timing['validation_ms'] = (datetime.utcnow() - step_start).total_seconds() * 1000
            
            if self.config.verbose:
                logger.info(f"  → Security: {security_result}, Validation: {validation_result}")
                logger.info(f"  → Status: {canonical_row['status']}, Maturity: {canonical_row['maturity_state']}")
            
            # -----------------------------
            # 3️⃣ LABS & AGENTS EXECUTION
            # -----------------------------
            if self.config.run_labs and canonical_row['status'] != 'FAIL':
                step_start = datetime.utcnow()
                
                if self.config.verbose:
                    logger.info("Step 3: Labs & Agents Execution")
                
                # Select agent
                agent_id = select_agent(canonical_row)
                canonical_row['agent'] = agent_id
                
                if self.config.verbose:
                    logger.info(f"  → Agent selected: {agent_id}")
                
                # Update status to TEST
                canonical_row['status'] = 'TEST'
                
                # Execute labs
                lab_results, artifact_ids = execute_lab(canonical_row)
                canonical_row['lab'] = lab_results
                canonical_row['artifacts'] = artifact_ids
                
                # Determine final status
                if lab_results.get('labs_failed', 0) == 0 and artifact_ids:
                    canonical_row['status'] = 'READY'
                else:
                    canonical_row['status'] = 'FAIL'
                    if not artifact_ids:
                        result.errors.append("No artifacts generated")
                
                # Recompute maturity
                canonical_row['maturity_state'] = compute_maturity_state(canonical_row)
                
                # Update row
                self.table.update_row(row.row_id, canonical_row)
                
                result.steps_completed.append("labs_agents")
                result.timing['labs_ms'] = (datetime.utcnow() - step_start).total_seconds() * 1000
                
                if self.config.verbose:
                    logger.info(f"  → Labs executed: {lab_results.get('labs_executed', 0)}")
                    logger.info(f"  → Artifacts: {len(artifact_ids)}")
                    logger.info(f"  → Status: {canonical_row['status']}, Maturity: {canonical_row['maturity_state']}")
            else:
                if self.config.verbose:
                    logger.info("Step 3: Labs skipped (validation failed or disabled)")
            
            # -----------------------------
            # 4️⃣ ML OVERLAY
            # -----------------------------
            if self.config.run_ml and canonical_row['maturity_state'] == 'MATURE':
                step_start = datetime.utcnow()
                
                if self.config.verbose:
                    logger.info("Step 4: ML Overlay")
                
                # Run ML models
                ml_results = run_ml_models(canonical_row)
                canonical_row.update(ml_results)
                
                result.ml_applied = ml_results.get('ml_applied', False)
                
                # Update row
                self.table.update_row(row.row_id, canonical_row)
                
                result.steps_completed.append("ml_overlay")
                result.timing['ml_ms'] = (datetime.utcnow() - step_start).total_seconds() * 1000
                
                if self.config.verbose:
                    logger.info(f"  → ML Score: {ml_results.get('ml_score', 'N/A')}")
                    logger.info(f"  → Suggested Agent: {ml_results.get('ml_suggested_agent', 'N/A')}")
                    logger.info(f"  → Anomaly Prob: {ml_results.get('ml_anomaly_prob', 'N/A')}")
            else:
                if self.config.verbose:
                    reason = "disabled" if not self.config.run_ml else f"not MATURE ({canonical_row['maturity_state']})"
                    logger.info(f"Step 4: ML Overlay skipped ({reason})")
            
            # -----------------------------
            # 5️⃣ ENFORCEMENT LAYER
            # -----------------------------
            if self.config.run_enforcement and canonical_row['maturity_state'] == 'MATURE':
                step_start = datetime.utcnow()
                
                if self.config.verbose:
                    logger.info("Step 5: Enforcement Layer")
                
                # Apply enforcement
                enforcement_results = apply_enforcement(canonical_row)
                canonical_row.update(enforcement_results)
                
                result.enforcement_applied = enforcement_results.get('enforcement_applied', False)
                
                # Update row
                self.table.update_row(row.row_id, canonical_row)
                
                result.steps_completed.append("enforcement")
                result.timing['enforcement_ms'] = (datetime.utcnow() - step_start).total_seconds() * 1000
                
                if self.config.verbose:
                    logger.info(f"  → Compliance: {enforcement_results.get('compliance_status', 'N/A')}")
                    logger.info(f"  → Action: {enforcement_results.get('action_taken', 'N/A')}")
            else:
                if self.config.verbose:
                    reason = "disabled" if not self.config.run_enforcement else f"not MATURE ({canonical_row['maturity_state']})"
                    logger.info(f"Step 5: Enforcement skipped ({reason})")
            
            # -----------------------------
            # FINALIZE
            # -----------------------------
            result.success = canonical_row['status'] == 'READY'
            result.final_status = canonical_row['status']
            result.final_maturity = canonical_row['maturity_state']
            result.final_row = canonical_row
            
            total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.timing['total_ms'] = total_time
            
            if self.config.verbose:
                logger.info("=" * 50)
                logger.info(f"Pipeline Complete: {'SUCCESS' if result.success else 'FAILED'}")
                logger.info(f"  Final Status: {result.final_status}")
                logger.info(f"  Final Maturity: {result.final_maturity}")
                logger.info(f"  ML Applied: {result.ml_applied}")
                logger.info(f"  Enforcement Applied: {result.enforcement_applied}")
                logger.info(f"  Total Time: {total_time:.2f}ms")
                logger.info("=" * 50)
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logger.error(f"Pipeline error: {e}")
            raise
        
        return result


def run_pipeline(input_payload: Any, protocol_type: str,
                 config: Optional[PipelineConfig] = None,
                 credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main entry point: Run the hybrid pipeline
    
    Args:
        input_payload: Raw input data (dict, string, etc.)
        protocol_type: Source protocol (REST, GraphQL, gRPC, Webhook, File)
        config: Optional pipeline configuration
        credentials: Optional security credentials
        
    Returns:
        Dictionary with pipeline results
    """
    pipeline = HybridPipeline(config)
    result = pipeline.run(input_payload, protocol_type, credentials)
    return result.to_dict()


# =============================================================================
# CLI Interface
# =============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🚀 Hybrid Protocol Sovereign System - Pipeline Demo")
    print("=" * 60)
    
    # Example 1: Simple REST input that will achieve MATURE status
    example_input_1 = {
        "cycle": 1,
        "layer": "L1",
        "variant": "A",
        "input_type": "grain",
        "data": {"weight_kg": 100, "quality": "premium"}
    }
    
    print("\n📥 Example 1: REST Input (will become READY/MATURE)")
    print(f"   Input: {json.dumps(example_input_1, indent=2)}")
    
    config = PipelineConfig(verbose=True)
    result = run_pipeline(example_input_1, "REST", config)
    
    print(f"\n✅ Result Summary:")
    print(f"   Success: {result['success']}")
    print(f"   Status: {result['final_status']}")
    print(f"   Maturity: {result['final_maturity']}")
    print(f"   ML Applied: {result['ml_applied']}")
    print(f"   Enforcement: {result['enforcement_applied']}")
    
    # Example 2: GraphQL input
    print("\n" + "=" * 60)
    print("\n📥 Example 2: GraphQL Input")
    
    example_input_2 = {
        "query": "mutation CreateOrder { createOrder(input: $input) { id } }",
        "variables": {
            "cycle": 2,
            "layer": "L2",
            "variant": "B",
            "input": {"product": "bread", "quantity": 50}
        }
    }
    
    result2 = run_pipeline(example_input_2, "GraphQL", config)
    
    print(f"\n✅ Result Summary:")
    print(f"   Success: {result2['success']}")
    print(f"   Status: {result2['final_status']}")
    print(f"   Maturity: {result2['final_maturity']}")
    
    # Show canonical table stats
    print("\n" + "=" * 60)
    print("📊 Canonical Table Statistics:")
    table = get_global_table()
    print(f"   Total Rows: {len(table)}")
    print(f"   MATURE Rows: {len(table.get_mature_rows())}")
    
    # Export to Excel
    excel_path = table.export_to_excel("data/canonical_table_demo.xlsx")
    print(f"   Exported to: {excel_path}")
    
    print("\n" + "=" * 60)
    print("🎉 Pipeline Demo Complete!")
    print("=" * 60)
