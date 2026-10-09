from typing import Dict, Any


class BusinessAnalyst:
    name = "Business Analyst"
    domain = "business"

    def answer(self, q: str, internal: Dict[str, Any]) -> str:
        kpi = internal.get("kpi", {})
        revenue = kpi.get("revenue", "N/A")
        growth = kpi.get("growth", "N/A")
        
        return (
            f"💼 {self.name}\n"
            f"Pyetja: {q}\n"
            f"- Revenue: {revenue}\n"
            f"- Growth: {growth}\n"
            f"- Fokus: strategji, KPI, rritje biznesi.\n"
        )
