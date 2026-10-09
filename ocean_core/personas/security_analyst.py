from typing import Dict, Any


class SecurityAnalyst:
    name = "Security Analyst"
    domain = "security"

    def answer(self, q: str, internal: Dict[str, Any]) -> str:
        ci = internal.get("ci_status", {})
        secrets = ci.get("secrets", "unknown")
        vulns = ci.get("vulnerabilities", "unknown")
        
        return (
            f"🔐 {self.name}\n"
            f"Pyetja: {q}\n"
            f"- Secrets status: {secrets}\n"
            f"- Vulnerabilities: {vulns}\n"
            f"- Politika: zero-tolerance për CRITICAL/HIGH risk.\n"
        )
