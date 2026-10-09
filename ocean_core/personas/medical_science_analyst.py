from typing import Dict, Any, List


class MedicalScienceAnalyst:
    name = "Medical Science Analyst"
    domain = "medical_science"

    def answer(self, q: str, ext: Dict[str, Any]) -> str:
        wiki = ext.get("wikipedia", "")
        pubmed = ext.get("pubmed", [""])
        
        return (
            f"🧬 {self.name}\n"
            f"Pyetja: {q}\n"
            f"- Wikipedia: {wiki}\n"
            f"- PubMed: {pubmed[0] if pubmed else 'N/A'}\n"
            f"- Fokus: shkencë mjekësore, biologji, shëndetësi.\n"
        )
