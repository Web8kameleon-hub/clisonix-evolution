from typing import Optional


class PersonaRouter:
    def __init__(self):
        # Lazy imports to avoid circular dependencies
        from personas.medical_science_analyst import MedicalScienceAnalyst
        from personas.lora_iot_analyst import LoRaIoTAnalyst
        from personas.security_analyst import SecurityAnalyst
        from personas.systems_architecture_analyst import SystemsArchitectureAnalyst
        from personas.natural_science_analyst import NaturalScienceAnalyst
        from personas.industrial_process_analyst import IndustrialProcessAnalyst
        from personas.agi_analyst import AGIAnalyst
        from personas.business_analyst import BusinessAnalyst
        from personas.smart_human_analyst import SmartHumanAnalyst  # UPGRADED!
        from personas.academic_analyst import AcademicAnalyst
        from personas.media_analyst import MediaAnalyst
        from personas.culture_analyst import CultureAnalyst
        from personas.hobby_analyst import HobbyAnalyst
        from personas.entertainment_analyst import EntertainmentAnalyst

        self.personas = [
            MedicalScienceAnalyst(),
            LoRaIoTAnalyst(),
            SecurityAnalyst(),
            SystemsArchitectureAnalyst(),
            NaturalScienceAnalyst(),
            IndustrialProcessAnalyst(),
            AGIAnalyst(),
            BusinessAnalyst(),
            SmartHumanAnalyst(),  # UPGRADED Smart Human Analyst with translation!
            AcademicAnalyst(),
            MediaAnalyst(),
            CultureAnalyst(),
            HobbyAnalyst(),
            EntertainmentAnalyst(),
        ]

        self.mapping = {
            "agi_systems": ["agi", "cognitive", "autonomous", "intelligence"],
            "medical_science": ["brain", "neuro", "health", "biology", "medical"],
            "lora_iot": ["lora", "iot", "sensor", "gateway", "telemetry"],
            "security": ["security", "vulnerability", "secret", "encrypted", "auth"],
            "systems_architecture": ["api", "infrastructure", "system"],
            "natural_science": ["physics", "chemistry", "energy", "quantum", "atom"],
            "industrial_process": ["cycle", "production", "factory", "throughput"],
            "business": ["kpi", "revenue", "growth", "strategy", "business"],
            # Human handles greetings, general questions, Albanian
            "human": ["hello", "hi", "hey", "explain", "clarify", "human", "understand",
                      "pershendetje", "tungjatjeta", "miredita", "si je", "cfare",
                      "çfarë", "shpjego", "thuaj", "trego", "ndihmo", "pse", "ku", "kur", "sa",
                      "consciousness", "conscious", "ndërgjegj", "vetëdij", "yourself", "who are you",
                      "kush je", "cili je", "what can you", "help", "capability", "abilities",
                      "hallo", "guten", "was", "wie", "warum", "laboratories", "laborator", "labs"],
            "academic": ["theory", "research", "academic", "study", "thesis"],
            "media": ["news", "media", "journalism", "report", "current"],
            "culture": ["culture", "tradition", "art", "heritage", "society"],
            "hobby": ["hobby", "craft", "learn", "practice", "activity"],
            "entertainment": ["movie", "game", "music", "fun", "entertainment", "film"],
        }

    def route(self, question: str) -> Optional[object]:
        """Route question to appropriate analyst based on keywords."""
        q = question.lower()

        for domain, keywords in self.mapping.items():
            if any(k in q for k in keywords):
                return self._get(domain)

        # Default to Human Analyst if no domain matched
        return self._get("human")

    def _get(self, domain: str) -> Optional[object]:
        """Get persona by domain."""
        for p in self.personas:
            if getattr(p, "domain", None) == domain:
                return p
        return None
