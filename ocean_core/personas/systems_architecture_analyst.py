from typing import Dict, Any


class SystemsArchitectureAnalyst:
    name = "Systems Architecture Analyst"
    domain = "systems_architecture"

    def answer(self, q: str, internal: Dict[str, Any]) -> str:
        api_status = internal.get("api_status", "unknown")
        
        return (
            f"🏗️ {self.name}\n"
            f"Pyetja: {q}\n"
            f"- API status: {api_status}\n"
            f"- Arkitekturë: minimaliste, e kontrolluar, pa surprises.\n"
            f"- Fokus: stabilitet, observability, CI/CD i pastër.\n"
        )
