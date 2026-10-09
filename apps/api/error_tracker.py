"""
ERROR TRACKER MODULE
Ndjek të gjithë errore me referenca unike (ERR-001, ERR-002, etj)
Shfaq numrin e rreshtit, funksionin, kodin e gabimit dhe detajet
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
import logging
from pathlib import Path
import traceback
import inspect

logger = logging.getLogger(__name__)

# Error log file path
ERROR_LOG_DIR = Path("./error_logs")
ERROR_LOG_DIR.mkdir(exist_ok=True)


@dataclass
class ErrorReference:
    """Një referencë errori me detaje të plotë"""
    error_id: str  # ERR-001
    timestamp: str
    line_number: int  # Numri i rreshtit ku ndodhi errori
    function_name: str  # Emri i funksionit
    error_type: str  # ValueError, TypeError, etj
    error_message: str
    stack_trace: str
    file_path: str
    details: Dict[str, Any]  # Kontekst shtesë


class ErrorTracker:
    """Ndjekësi i errore me log file dhe në memorje"""

    def __init__(self):
        self.errors: List[ErrorReference] = []
        self.error_counter = 0
        self.log_file = ERROR_LOG_DIR / f"errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    def track_error(
        self,
        exception: Exception,
        function_name: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Ndjek një error dhe kthen referencën e tij (ERR-001, ERR-002, etj)
        """
        self.error_counter += 1
        error_id = f"ERR-{self.error_counter:03d}"

        # Get stack trace
        tb = traceback.format_exc()

        # Get the line number from the stack
        tb_lines = tb.split('\n')
        line_number = 0
        file_path = ""
        
        # Extract line number from traceback
        for line in tb_lines:
            if 'line' in line.lower():
                try:
                    # Parse "line XXX in function_name"
                    parts = line.split(',')
                    for part in parts:
                        if 'line' in part.lower():
                            line_number = int(''.join(c for c in part if c.isdigit()))
                            break
                except:
                    pass
            if '.py' in line and 'File' in line:
                file_path = line.strip()

        # Get current frame info
        frame = inspect.currentframe()
        if frame:
            caller_frame = frame.f_back
            if caller_frame:
                line_number = caller_frame.f_lineno
                file_path = caller_frame.f_code.co_filename
                if not function_name:
                    function_name = caller_frame.f_code.co_name

        error_ref = ErrorReference(
            error_id=error_id,
            timestamp=datetime.now().isoformat(),
            line_number=line_number,
            function_name=function_name or "unknown",
            error_type=type(exception).__name__,
            error_message=str(exception),
            stack_trace=tb,
            file_path=file_path,
            details=details or {},
        )

        self.errors.append(error_ref)
        self._save_to_file(error_ref)

        logger.error(
            f"{error_id} | Line {line_number} | {function_name} | "
            f"{type(exception).__name__}: {str(exception)}"
        )

        return error_id

    def _save_to_file(self, error_ref: ErrorReference):
        """Shëno erroren në JSON file"""
        try:
            errors_data = []
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    errors_data = json.load(f)
            
            errors_data.append(asdict(error_ref))
            
            with open(self.log_file, 'w') as f:
                json.dump(errors_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save error to file: {str(e)}")

    def get_all_errors(self) -> List[Dict[str, Any]]:
        """Merr listën e të gjithë erroreve"""
        return [
            {
                "error_id": e.error_id,
                "timestamp": e.timestamp,
                "line_number": e.line_number,
                "function_name": e.function_name,
                "error_type": e.error_type,
                "error_message": e.error_message,
                "file_path": e.file_path,
                "details": e.details,
            }
            for e in self.errors
        ]

    def get_errors_by_function(self, function_name: str) -> List[Dict[str, Any]]:
        """Merr errore sipas emrit të funksionit"""
        return [
            asdict(e) for e in self.errors if e.function_name == function_name
        ]

    def get_error_summary(self) -> Dict[str, Any]:
        """Merr një përmbledhje të erroreve"""
        error_types = {}
        for error in self.errors:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1

        return {
            "total_errors": len(self.errors),
            "error_types": error_types,
            "last_error": asdict(self.errors[-1]) if self.errors else None,
            "most_common_function": self._get_most_common_function(),
        }

    def _get_most_common_function(self) -> Optional[str]:
        """Merr funksionin me më shumë errore"""
        if not self.errors:
            return None
        
        func_counts = {}
        for error in self.errors:
            func_counts[error.function_name] = func_counts.get(error.function_name, 0) + 1
        
        return max(func_counts, key=func_counts.get) if func_counts else None

    def clear_errors(self):
        """Pastro të gjithë errore nga memoria"""
        self.errors.clear()
        self.error_counter = 0

    def export_errors_as_table(self) -> str:
        """Eksporto errore si tabela për shfaqje"""
        if not self.errors:
            return "No errors recorded"
        
        table = "ERROR REFERENCE LOG\n"
        table += "=" * 120 + "\n"
        table += f"{'ID':<10} {'TIMESTAMP':<25} {'LINE':<6} {'FUNCTION':<25} {'TYPE':<20} {'MESSAGE':<40}\n"
        table += "-" * 120 + "\n"
        
        for error in self.errors:
            msg = error.error_message[:37] + "..." if len(error.error_message) > 40 else error.error_message
            table += f"{error.error_id:<10} {error.timestamp:<25} {error.line_number:<6} {error.function_name:<25} {error.error_type:<20} {msg:<40}\n"
        
        return table


# Global error tracker instance
error_tracker = ErrorTracker()
