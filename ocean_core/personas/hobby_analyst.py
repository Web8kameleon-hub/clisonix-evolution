from typing import Dict, Any


class HobbyAnalyst:
    name = "Hobby Analyst"
    domain = "hobby"

    def answer(self, q: str, _: Dict[str, Any]) -> str:
        return (
            f"🎨 {self.name}\n"
            f"Pyetja: {q}\n"
            f"- Fokus: aktivitete personale, zhvillim aftësish, ide praktike.\n"
            f"- Qëllim: frymëzim dhe praktikë.\n"
        )
