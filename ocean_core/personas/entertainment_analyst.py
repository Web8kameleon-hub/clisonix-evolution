from typing import Dict, Any


class EntertainmentAnalyst:
    name = "Entertainment Analyst"
    domain = "entertainment"

    def answer(self, q: str, ext: Dict[str, Any]) -> str:
        wiki = ext.get("wikipedia", "")
        
        return (
            f"🎮 {self.name}\n"
            f"Pyetja: {q}\n"
            f"- Wikipedia: {wiki}\n"
            f"- Fokus: filma, lojëra, muzikë, evente, argëtim.\n"
        )
