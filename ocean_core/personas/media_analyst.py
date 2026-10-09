from typing import Dict, Any


class MediaAnalyst:
    name = "Media Analyst"
    domain = "media"

    def answer(self, q: str, ext: Dict[str, Any]) -> str:
        wiki = ext.get("wikipedia", "")
        
        return (
            f"📰 {self.name}\n"
            f"Pyetja: {q}\n"
            f"- Wikipedia: {wiki}\n"
            f"- Fokus: informacion publik, narrative mediatike, aktualitete.\n"
        )
