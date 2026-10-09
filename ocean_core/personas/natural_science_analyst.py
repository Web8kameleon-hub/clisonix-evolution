from typing import Dict, Any


class NaturalScienceAnalyst:
    name = "Natural Science Analyst"
    domain = "natural_science"

    def answer(self, q: str, ext: Dict[str, Any]) -> str:
        wiki = ext.get("wikipedia", "")
        
        return (
            f"🔬 {self.name}\n"
            f"Pyetja: {q}\n"
            f"- Wikipedia: {wiki}\n"
            f"- Fokus: fizikë, kimi, energji, mekanizma natyrorë.\n"
        )
