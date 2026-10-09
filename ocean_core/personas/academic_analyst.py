from typing import Dict, Any, List


class AcademicAnalyst:
    name = "Academic Analyst"
    domain = "academic"

    def answer(self, q: str, ext: Dict[str, Any]) -> str:
        wiki = ext.get("wikipedia", "")
        arxiv = ext.get("arxiv", [""])
        
        return (
            f"🎓 {self.name}\n"
            f"Pyetja: {q}\n"
            f"- Wikipedia: {wiki}\n"
            f"- Arxiv: {arxiv[0] if arxiv else 'N/A'}\n"
            f"- Fokus: teori, koncepte, literaturë akademike.\n"
        )
