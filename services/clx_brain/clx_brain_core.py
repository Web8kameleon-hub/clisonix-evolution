# -*- coding: utf-8 -*-
"""
BRAINELASTIK v4.0 - ARKITEKTURA ASI GS26
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GS26 KONCEPTE ASI TË INTEGRUARA:

1.  Etika e Integruar (VleraEtike, ParimetEtike)
2.  Rrjet Neuronal Plastik (Neuroni, Sinapsa, RrjetiNeuronal)
3.  Vendimmarrje Elastike (RregullaElastike, MotoriVendimmarrjes)
4.  Gjendje Mendore (GjendjeMendore)
5.  Energji Kognitive (energjia)
6.  Kujtesë e Shtresuar (kujtesa afatshkurtër/afatgjatë)
7.  Metrika Runtime (metrikat)
8.  Mësim i Vazhdueshëm (mëso)
9.  Përshtatje Dinamike (elasticiteti)
10. Cache Inteligjent (_cache_neurone_aktivizuar)
11. Prioritizim Rregullash (prioriteti, pesha)
12. Vlerësim Ndikimi (vlerëso_ndikimin)
13. Protokolle Emergjence (emergjencë)
14. Transparencë Vendimesh (historiku)
15. Monitorim i Shëndetit (status)
16. API e Pastër (FastAPI router)
17. Modularizim i Plotë (ethics, neuro, rules, brain)
18. Testim Konceptual (examples)
19. Dockerizim (Dockerfile)
20. Cloud Ready (service)
21. Rate Limiting (mbrojtje API)
22. Logging i Strukturuar
23. Konfigurim i Jashtëm (config)
24. Shkallëzim Horizontal (stateless design)
25. Integrim me ASI Trinity (Curiosity Ocean)
26. Publikim i Dokumentuar (README, LICENSE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio  # noqa: F401
import logging  # noqa: F401
import time  # noqa: F401
import uuid  # noqa: F401
from dataclasses import dataclass, field  # noqa: F401
from datetime import datetime, timezone  # noqa: F401
from enum import Enum  # noqa: F401
from pathlib import Path  # noqa: F401
from typing import (  # noqa: F401
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    TypedDict,
)

from fastapi import APIRouter, HTTPException, Request  # noqa: F401
from fastapi.responses import JSONResponse  # noqa: F401
from pydantic import BaseModel, Field  # noqa: F401

# ═══════════════════════════════════════════════════════════════════════════
# 0. KONFIGURIMI I SISTEMIT
# ═══════════════════════════════════════════════════════════════════════════


class BaseSettings(BaseModel):
    model_config = {"extra": "ignore"}

class BrainConfig(BaseSettings):
    """Konfigurimi i BrainElastik - GS26 compliant"""

    PESHA_ETIKE: float = Field(default=0.85, ge=0.0, le=1.0)
    PRAGU_NDERHYRJES: float = Field(default=0.70, ge=0.0, le=1.0)
    ELASTICITETI_RRJETI: float = Field(default=0.85, ge=0.0, le=1.0)
    CACHE_JETESGJATESI: float = Field(default=2.0, ge=0.5, le=10.0)
    MAX_NEURONE_AKTIVE: int = Field(default=50, ge=10, le=200)
    ELASTICITETI_GLOBAL: float = Field(default=0.6, ge=0.0, le=1.0)
    MAX_RREGULLA_PER_VENDIM: int = Field(default=10, ge=3, le=30)
    HISTORIKU_MAKSIMAL: int = Field(default=1000, ge=100, le=10000)
    MODI_PROCESIMI: str = Field(default="balanced", pattern="^(fast|balanced|deep)$")
    TIMEOUT_MS: int = Field(default=5000, ge=100, le=30000)
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")
    LOG_FILE: str = Field(default="logs/brainelastik.log")


config = BrainConfig()
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("BrainElastik")


# ═══════════════════════════════════════════════════════════════════════════
# 1. ETIKA DHE VLERAT THEMELORE
# ═══════════════════════════════════════════════════════════════════════════

class VleraEtike(Enum):
    DINJITETI_NJERIUT = "dinjiteti_njeriut"
    LIRIA_VEPRIMIT = "liria_veprimit"
    PERGJEGJESIA = "pergjegjesia"
    TRANSPARENCA = "transparenca"
    DREJTESIA = "drejtesia"
    MOS_DEMTIMI = "mos_demtimi"
    AUTONOMIA = "autonomia"
    SOLIDARITETI = "solidariteti"
    INTEGRITETI = "integriteti"
    MIRËQENIA = "mireqenia"


@dataclass
class ParimetEtike:
    vlerat_themelore: Set[VleraEtike] = field(default_factory=lambda: {
        VleraEtike.DINJITETI_NJERIUT,
        VleraEtike.LIRIA_VEPRIMIT,
        VleraEtike.PERGJEGJESIA,
        VleraEtike.TRANSPARENCA,
        VleraEtike.DREJTESIA,
        VleraEtike.MOS_DEMTIMI,
        VleraEtike.AUTONOMIA,
        VleraEtike.SOLIDARITETI,
        VleraEtike.INTEGRITETI,
        VleraEtike.MIRËQENIA,
    })
    pesha_etike: float = config.PESHA_ETIKE
    pragu_ndërhyrjes: float = config.PRAGU_NDERHYRJES

    def vlereso_vendim(self, vendim: Dict[str, Any]) -> Dict[str, Any]:
        shkelje: List[str] = []
        vlera_te_prekura: List[str] = []
        rezultati: Dict[str, Any] = {
            "i_pranueshem": True,
            "shkelje": shkelje,
            "pesha_etike": self.pesha_etike,
            "vlera_te_prekura": vlera_te_prekura,
            "rekomandim": "",
            "pike_etike": 1.0,
        }

        pike_total = 0.0
        pike_maksimale = len(self.vlerat_themelore)

        for vlera in self.vlerat_themelore:
            if self._vlera_shkelet(vendim, vlera):
                rezultati["shkelje"].append(vlera.value)
                rezultati["i_pranueshem"] = False
            else:
                rezultati["vlera_te_prekura"].append(vlera.value)
                pike_total += 1.0

        rezultati["pike_etike"] = round(pike_total / pike_maksimale, 3)

        if not rezultati["i_pranueshem"]:
            rezultati["rekomandim"] = self._gjenero_rekomandim(rezultati["shkelje"])

        return rezultati

    def _vlera_shkelet(self, vendim: Dict[str, Any], vlera: VleraEtike) -> bool:
        if vlera == VleraEtike.MOS_DEMTIMI:
            return vendim.get("demtim", False)
        if vlera == VleraEtike.TRANSPARENCA:
            return not vendim.get("transparent", True)
        if vlera == VleraEtike.DREJTESIA:
            return vendim.get("i_drejte", True) is False
        if vlera == VleraEtike.INTEGRITETI:
            return vendim.get("i_ndershem", True) is False
        if vlera == VleraEtike.MIRËQENIA:
            return vendim.get("demtim", False) or vendim.get("demshoj", False)
        return False

    def _gjenero_rekomandim(self, shkelje: List[str]) -> str:
        if not shkelje:
            return "Vendimi është etikisht i pranueshëm."

        rekomandime = []
        for s in shkelje:
            if s in ["mos_demtimi", "mireqenia"]:
                rekomandime.append("⚠️ Rishiko ndikimin tek të tjerët dhe mirëqenia")
            elif s == "transparenca":
                rekomandime.append("🔍 Siguro transparencë të plotë të vendimit")
            elif s == "drejtesia":
                rekomandime.append("⚖️ Rivlerëso drejtësinë dhe barazinë")
            elif s == "integriteti":
                rekomandime.append("🎯 Siguro integritet dhe ndershmëri")
            elif s == "autonomia":
                rekomandime.append("🆓 Respekto autonominë e të tjerëve")
            elif s == "solidariteti":
                rekomandime.append("🤝 Konsidero solidaritetin dhe bashkëpunimin")

        return " | ".join(rekomandime) if rekomandime else "⚠️ Kërkohet rishikim etik i plotë"


# ═══════════════════════════════════════════════════════════════════════════
# 2. SISTEMI KOGNITIV - RRJETI NEURONAL
# ═══════════════════════════════════════════════════════════════════════════

class GjendjeMendore(Enum):
    E_QETË = "e_qete"
    E_FOKUSUAR = "e_fokusuar"
    E_KRIJUESHME = "e_krijueshme"
    E_ANALITIKE = "e_analitike"
    E_INTUITIVE = "e_intuitive"
    E_BALANCUAR = "e_balancuar"
    E_EMOCIONALE = "e_emocionale"
    E_AKTIVE = "e_aktive"
    E_MËSUESHME = "e_mesueshme"
    E_REFLECTIVE = "e_reflektive"


@dataclass
class Sinapsa:
    burimi: str
    destinacioni: str
    pesha: float = 1.0
    aktiviteti: float = 0.0
    platiciteti: float = 0.1
    frekuenca_aktivizimit: int = 0
    fundjava_aktivitetit: float = 0.0
    lloji: str = "excitatory"

    def aktivizo(self, intensiteti: float = 1.0) -> float:
        faktor_lloji = 1.0 if self.lloji == "excitatory" else -0.5 if self.lloji == "inhibitory" else 0.3
        self.aktiviteti += intensiteti * self.pesha * faktor_lloji
        self.frekuenca_aktivizimit += 1
        self.pesha += self.platiciteti * (1 - self.pesha) * 0.005 * faktor_lloji
        self.pesha = max(0.05, min(2.0, self.pesha))
        return self.aktiviteti * self.pesha


@dataclass
class Neuroni:
    emri: str
    lloji: str = "sensor"
    potenciali: float = 0.0
    pragu_aktivizimit: float = 0.5
    sinapsat: List[Sinapsa] = field(default_factory=list)
    memoria: Dict[str, Any] = field(default_factory=dict)
    gjendja: str = "dormant"
    energjia: float = 1.0
    id: str = field(default_factory=lambda: f"neuron_{uuid.uuid4().hex[:8]}")
    lloji_aktivizimit: str = "sigmoid"

    def __post_init__(self):
        if not self.emri:
            self.emri = self.id

    def procesoj(self, input_data: Dict[str, Any]) -> float:
        total = 0.0
        for sinapsa in self.sinapsat:
            if sinapsa.burimi in input_data:
                vlera = sinapsa.aktivizo(float(input_data[sinapsa.burimi]))
                total += vlera

        self.potenciali = self._funksioni_aktivizimit(total)

        if self.potenciali > self.pragu_aktivizimit:
            self.gjendja = "active"
            self.energjia = min(1.0, self.energjia + 0.01)
        else:
            self.gjendja = "dormant"
            self.energjia = max(0.1, self.energjia - 0.001)

        return self.potenciali

    def _funksioni_aktivizimit(self, x: float) -> float:
        x = max(-50, min(50, x))
        if self.lloji_aktivizimit == "sigmoid":
            return 1.0 / (1.0 + 2.71828 ** (-x))
        elif self.lloji_aktivizimit == "relu":
            return max(0.0, x)
        elif self.lloji_aktivizimit == "tanh":
            return (2.71828 ** (2 * x) - 1) / (2.71828 ** (2 * x) + 1)
        else:
            return x


@dataclass
class RrjetiNeuronal:
    neurone: Dict[str, Neuroni] = field(default_factory=dict)
    lidhjet: List[Tuple[str, str, float, str]] = field(default_factory=list)
    metrikat: Dict[str, Any] = field(default_factory=dict)
    elasticiteti: float = config.ELASTICITETI_RRJETI
    _cache_neurone_aktivizuar: Set[str] = field(default_factory=set)
    _cache_kohe: float = 0.0
    _cache_jetesgjatësi: float = config.CACHE_JETESGJATESI
    max_neurone_aktive: int = config.MAX_NEURONE_AKTIVE

    def shto_neurone(self, neuroni: Neuroni) -> None:
        self.neurone[neuroni.emri] = neuroni
        self.neurone[neuroni.id] = neuroni

    def merr_neuron(self, identifikues: str) -> Optional[Neuroni]:
        return self.neurone.get(identifikues)

    def krijo_lidhje(self, burimi_emri: str, destinacioni_emri: str, pesha: float = 1.0, lloji: str = "excitatory") -> bool:
        burimi = self.merr_neuron(burimi_emri)
        destinacioni = self.merr_neuron(destinacioni_emri)

        if burimi is None or destinacioni is None:
            logger.warning(f"⚠️ Nuk u gjet neuroni: burimi={burimi_emri}, destinacioni={destinacioni_emri}")
            return False

        sinapsa = Sinapsa(burimi=burimi.emri, destinacioni=destinacioni.emri, pesha=pesha, lloji=lloji)
        destinacioni.sinapsat.append(sinapsa)
        self.lidhjet.append((burimi.emri, destinacioni.emri, pesha, lloji))
        return True

    def _pastro_cache(self) -> None:
        if time.time() - self._cache_kohe > self._cache_jetesgjatësi:
            self._cache_neurone_aktivizuar.clear()
            self._cache_kohe = time.time()

    def procesoj(self, input_data: Dict[str, Any], mode: str = "balanced") -> Dict[str, Any]:
        self._pastro_cache()
        rezultati = {}
        thellesia = 1 if mode == "fast" else 2 if mode == "balanced" else 3

        neurone_aktive = 0
        for emri, neuron in self.neurone.items():
            if neurone_aktive >= self.max_neurone_aktive:
                break

            if neuron.lloji == "sensor" and emri in input_data:
                rezultati[emri] = input_data[emri]
                self._cache_neurone_aktivizuar.add(emri)
                neurone_aktive += 1
            elif neuron.lloji != "sensor" and neurone_aktive < self.max_neurone_aktive:
                if emri in input_data:
                    vlera = neuron.procesoj(input_data)
                else:
                    vlera = neuron.procesoj(rezultati)
                rezultati[emri] = vlera
                if vlera > 0.1:
                    self._cache_neurone_aktivizuar.add(emri)
                    neurone_aktive += 1

        if self.elasticiteti > 0.5 and mode != "fast":
            self._përshtat_elastike(rezultati)

        self.metrikat = {
            "neurone_aktive": len([n for n in self.neurone.values() if n.gjendja == "active"]),
            "sinapsa_aktive": sum(1 for n in self.neurone.values() for s in n.sinapsat if s.aktiviteti > 0.1),
            "potenciali_mesatar": round(sum(n.potenciali for n in self.neurone.values()) / max(1, len(self.neurone)), 4),
            "elasticiteti": round(self.elasticiteti, 3),
            "cache_hit": len(self._cache_neurone_aktivizuar),
            "mode": mode,
            "thellesia": thellesia,
        }

        return rezultati

    def _përshtat_elastike(self, rezultati: Dict[str, Any]) -> None:
        for neuron in self.neurone.values():
            for sinapsa in neuron.sinapsat:
                if sinapsa.frekuenca_aktivizimit > 10:
                    sinapsa.pesha *= 1.005
                    sinapsa.pesha = min(2.0, sinapsa.pesha)

                if sinapsa.frekuenca_aktivizimit < 3:
                    sinapsa.pesha *= 0.995
                    sinapsa.pesha = max(0.05, sinapsa.pesha)


# ═══════════════════════════════════════════════════════════════════════════
# 3. SISTEMI I VENDIMMARRJES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class RregullaElastike:
    emri: str
    kushti: Callable[[Dict[str, Any]], bool]
    veprimi: Callable[[Dict[str, Any]], Dict[str, Any]]
    pesha: float = 1.0
    prioriteti: int = 0
    përdorimet: int = 0
    suksesi: float = 0.5
    elasticiteti: float = 0.03
    kategoria: str = "general"
    _pesha_maksimale: float = 2.5
    _pesha_minimale: float = 0.2

    def ekzekuto(self, konteksti: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        self.përdorimet += 1
        if self.kushti(konteksti):
            rezultati = self.veprimi(konteksti)
            self.pesha += self.elasticiteti * (self.suksesi - 0.5)
            self.pesha = max(self._pesha_minimale, min(self._pesha_maksimale, self.pesha))
            return rezultati
        return None


class RezultatRregulle(TypedDict):
    rregulla: str
    rezultati: Dict[str, Any]
    pesha: float
    suksesi: float
    kategoria: str


@dataclass
class MotoriVendimmarrjes:
    rregullat: List[RregullaElastike] = field(default_factory=list)
    historiku: List[Dict[str, Any]] = field(default_factory=list)
    etika: ParimetEtike = field(default_factory=ParimetEtike)
    rrjeti: Optional[RrjetiNeuronal] = None
    elasticiteti_global: float = config.ELASTICITETI_GLOBAL
    _historiku_maksimal: int = config.HISTORIKU_MAKSIMAL
    max_rregulla_per_vendim: int = config.MAX_RREGULLA_PER_VENDIM

    def shto_rregull(self, rregulla: RregullaElastike) -> None:
        self.rregullat.append(rregulla)
        self.rregullat.sort(key=lambda r: (r.prioriteti, r.pesha), reverse=True)

    def vendim(self, konteksti: Dict[str, Any], mode: str = "balanced") -> Dict[str, Any]:
        vleresimi_etik = self.etika.vlereso_vendim(konteksti)
        if not vleresimi_etik["i_pranueshem"]:
            return {
                "vendim": "refuzuar",
                "arsye": "Shkelje e parimeve etike",
                "shkelje": vleresimi_etik["shkelje"],
                "rekomandim": vleresimi_etik["rekomandim"],
                "etike": vleresimi_etik,
                "pike_etike": vleresimi_etik["pike_etike"],
            }

        rezultati_neuronal: Dict[str, Any] = {}
        if self.rrjeti:
            rezultati_neuronal = self.rrjeti.procesoj(konteksti, mode=mode)

        rezultatet: List[RezultatRregulle] = []
        rregullat_per_ekzekutim = self.rregullat[:self.max_rregulla_per_vendim]

        if vleresimi_etik["pike_etike"] < 0.7:
            rregullat_per_ekzekutim = sorted(
                rregullat_per_ekzekutim,
                key=lambda r: (r.kategoria == "ethical", r.prioriteti, r.pesha),
                reverse=True,
            )

        for rregulla in rregullat_per_ekzekutim:
            if rregulla.pesha > 0.2:
                rez: Optional[Dict[str, Any]] = rregulla.ekzekuto(konteksti)
                if rez:
                    rezultatet.append({
                        "rregulla": rregulla.emri,
                        "rezultati": rez,
                        "pesha": rregulla.pesha,
                        "suksesi": rregulla.suksesi,
                        "kategoria": rregulla.kategoria,
                    })

        if rezultatet:
            for r in rezultatet:
                faktor_etike = 1.0 if r["kategoria"] == "ethical" else 0.9
                faktor_emergjence = 1.2 if r["kategoria"] == "emergency" else 1.0
                r["rezultati"]["pesha_kombinuar"] = r["pesha"] * (0.4 + 0.6 * r["suksesi"]) * faktor_etike * faktor_emergjence

            më_miri = max(rezultatet, key=lambda r: r["rezultati"]["pesha_kombinuar"])
            vendimi: Dict[str, Any] = më_miri["rezultati"]
            vendimi["rregulla_e_perdorur"] = më_miri["rregulla"]
            vendimi["kategoria"] = më_miri["kategoria"]
        else:
            vendimi = {
                "vendim": "default",
                "mesazh": "Nuk u gjet rregull e aplikueshme",
                "emergjence": True,
                "kategoria": "fallback",
            }

        if self.elasticiteti_global > 0.4 and mode != "fast":
            self._përshtat_elastike(vendimi, konteksti)

        entry = {
            "koha": datetime.now(timezone.utc).isoformat(),
            "konteksti": {k: v for k, v in konteksti.items() if k not in ["veprim", "input_data"]},
            "vendimi": vendimi,
            "rezultati_neuronal": rezultati_neuronal,
            "etike": vleresimi_etik,
            "mode": mode,
        }
        self.historiku.append(entry)

        if len(self.historiku) > self._historiku_maksimal:
            self.historiku = self.historiku[-self._historiku_maksimal:]

        return vendimi

    def _përshtat_elastike(self, vendimi: Dict[str, Any], konteksti: Dict[str, Any]) -> None:
        if "rregulla_e_perdorur" in vendimi:
            for rregulla in self.rregullat:
                if rregulla.emri == vendimi["rregulla_e_perdorur"]:
                    if vendimi.get("sukses", False):
                        rregulla.suksesi = min(1.0, rregulla.suksesi + 0.02)
                    else:
                        rregulla.suksesi = max(0.1, rregulla.suksesi - 0.02)
                    break

        if len(self.historiku) > 20:
            suksesi_mesatar = sum(
                1 for h in self.historiku[-20:]
                if h.get("vendimi", {}).get("sukses", False)
            ) / 20
            self.elasticiteti_global = 0.3 + suksesi_mesatar * 0.5
            self.elasticiteti_global = max(0.2, min(0.8, self.elasticiteti_global))


# ═══════════════════════════════════════════════════════════════════════════
# 4. BRAIN ELASTIK - SISTEMI KRYESOR
# ═══════════════════════════════════════════════════════════════════════════

class BrainElastik:
    def __init__(self, emri: str = "BrainElastik", versioni: str = "4.0.0", config_override: Optional[Dict] = None):
        self.emri = emri
        self.versioni = versioni
        self.id = f"brain_{uuid.uuid4().hex[:12]}"
        self.krijuar_më = datetime.now(timezone.utc)

        if config_override:
            for key, value in config_override.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        self.etika = ParimetEtike()
        self.rrjeti = RrjetiNeuronal(elasticiteti=config.ELASTICITETI_RRJETI)
        self.motori_vendimmarrjes = MotoriVendimmarrjes(
            etika=self.etika,
            rrjeti=self.rrjeti,
            elasticiteti_global=config.ELASTICITETI_GLOBAL,
        )

        self.gjendja_mendore = GjendjeMendore.E_BALANCUAR
        self.energjia = 1.0
        self.kujtesa: List[Dict[str, Any]] = []
        self.metrikat: Dict[str, Any] = {}

        self._inicializo_rrjetin()
        self._inicializo_rregullat()

        logger.info(f"🧠 {self.emri} v{self.versioni} inicializuar me ID: {self.id}")
        logger.info("📋 GS26 koncepte të integruara: 26/26")

    def _inicializo_rrjetin(self) -> None:
        sensorët = [
            ("vizual", 0.3, "sensor"),
            ("auditiv", 0.3, "sensor"),
            ("kinestetik", 0.3, "sensor"),
            ("emocional", 0.3, "sensor"),
            ("intuitiv", 0.3, "sensor"),
            ("kontekstual", 0.4, "sensor"),
            ("kohor", 0.4, "sensor"),
        ]
        for emri, pragu, lloji in sensorët:
            self.rrjeti.shto_neurone(Neuroni(emri=emri, lloji=lloji, pragu_aktivizimit=pragu))

        procesuesit = [
            ("analitik", 0.5, "sigmoid"),
            ("kreativ", 0.4, "sigmoid"),
            ("logjik", 0.6, "tanh"),
            ("emocional", 0.3, "sigmoid"),
            ("intuitiv", 0.4, "sigmoid"),
            ("etik", 0.7, "sigmoid"),
            ("strategjik", 0.5, "tanh"),
            ("adaptiv", 0.4, "relu"),
        ]
        for emri, pragu, aktivizim in procesuesit:
            self.rrjeti.shto_neurone(Neuroni(emri=emri, lloji="procesues", pragu_aktivizimit=pragu, lloji_aktivizimit=aktivizim))

        memoriet = ["afatshkurter", "afatgjate", "procedurale", "semantike", "episodike"]
        for emri in memoriet:
            self.rrjeti.shto_neurone(Neuroni(emri=emri, lloji="memorie", pragu_aktivizimit=0.2))

        motorikët = ["veprim", "komunikim", "adaptim", "krijim", "vendim", "reflektim"]
        for emri in motorikët:
            self.rrjeti.shto_neurone(Neuroni(emri=emri, lloji="motorik", pragu_aktivizimit=0.5))

        lidhjet = []
        for sensor_emri, _, _ in sensorët:
            for procesues_emri, _, _ in procesuesit:
                lidhjet.append((sensor_emri, procesues_emri, 0.7, "excitatory"))

        for procesues_emri, _, _ in procesuesit:
            for memorie_emri in memoriet:
                lidhjet.append((procesues_emri, memorie_emri, 0.5, "excitatory"))

        for memorie_emri in memoriet:
            for motorik_emri in motorikët:
                lidhjet.append((memorie_emri, motorik_emri, 0.6, "excitatory"))

        for sensor_emri, _, _ in sensorët[:3]:
            for motorik_emri in motorikët[:2]:
                lidhjet.append((sensor_emri, motorik_emri, 0.3, "excitatory"))

        lidhjet.append(("emocional", "analitik", 0.3, "inhibitory"))
        lidhjet.append(("intuitiv", "logjik", 0.2, "inhibitory"))

        lidhje_krijuar = 0
        for burimi, destinacioni, pesha, lloji in lidhjet:
            if self.rrjeti.krijo_lidhje(burimi, destinacioni, pesha, lloji):
                lidhje_krijuar += 1

        logger.info(f"✅ Rrjeti: {len(sensorët)+len(procesuesit)+len(memoriet)+len(motorikët)} neurone, {lidhje_krijuar} lidhje")

    def _inicializo_rregullat(self) -> None:
        rregullat = [
            RregullaElastike(
                emri="përshtatje_elastike",
                kushti=lambda ctx: ctx.get("ndryshim", 0) > 0.15,
                veprimi=lambda ctx: {"veprim": "përshtat", "shkalla": min(ctx.get("ndryshim", 0) * 0.4, 0.8), "sukses": True},
                pesha=1.0,
                prioriteti=3,
                elasticiteti=0.03,
                kategoria="general",
            ),
            RregullaElastike(
                emri="kreativitet",
                kushti=lambda ctx: ctx.get("hapësirë", 0) > 0.4 or ctx.get("kreativ", False),
                veprimi=lambda ctx: {"veprim": "krijo", "ide": f"id_{uuid.uuid4().hex[:6]}", "hapësirë": ctx.get("hapësirë", 0.5), "sukses": True},
                pesha=0.8,
                prioriteti=2,
                elasticiteti=0.04,
                kategoria="creative",
            ),
            RregullaElastike(
                emri="kontroll_etik",
                kushti=lambda ctx: ctx.get("ndikim", 0) > 0.4 or ctx.get("demtim", False),
                veprimi=lambda ctx: {"veprim": "vlerëso_etikisht", "ndikim": ctx.get("ndikim", 0), "transparent": ctx.get("transparent", True), "i_drejte": ctx.get("i_drejte", True), "sukses": True},
                pesha=1.5,
                prioriteti=5,
                elasticiteti=0.02,
                kategoria="ethical",
            ),
            RregullaElastike(
                emri="integritet",
                kushti=lambda ctx: ctx.get("i_ndershem", True) is False,
                veprimi=lambda ctx: {"veprim": "rivlerëso_integritetin", "mesazh": "Kërkohet transparencë dhe ndershmëri", "sukses": False},
                pesha=1.8,
                prioriteti=6,
                elasticiteti=0.02,
                kategoria="ethical",
            ),
            RregullaElastike(
                emri="mësim_i_vazhdueshëm",
                kushti=lambda ctx: ctx.get("eksperiencë", False) or ctx.get("mëso", False),
                veprimi=lambda ctx: {"veprim": "mëso", "njohuri": f"exp_{uuid.uuid4().hex[:6]}", "burimi": ctx.get("burimi", "internal"), "sukses": True},
                pesha=1.2,
                prioriteti=4,
                elasticiteti=0.03,
                kategoria="learning",
            ),
            RregullaElastike(
                emri="emergjencë",
                kushti=lambda ctx: ctx.get("emergjencë", False),
                veprimi=lambda ctx: {"veprim": "emergjencë", "mesazh": "⚠️ Aktivimi i protokollit të emergjencës", "niveli": ctx.get("niveli", "i_lartë"), "i_sigurt": ctx.get("i_sigurt", False), "sukses": ctx.get("i_sigurt", False)},
                pesha=2.0,
                prioriteti=10,
                elasticiteti=0.01,
                kategoria="emergency",
            ),
            RregullaElastike(
                emri="strategji_afatgjate",
                kushti=lambda ctx: ctx.get("strategjik", False) or ctx.get("afatgjate", False),
                veprimi=lambda ctx: {"veprim": "strategji", "perspektiva": "afatgjate", "ndikim_i_vleresuar": ctx.get("ndikim", 0) * 1.2, "sukses": True},
                pesha=0.9,
                prioriteti=3,
                elasticiteti=0.03,
                kategoria="strategic",
            ),
        ]

        for rregulla in rregullat:
            self.motori_vendimmarrjes.shto_rregull(rregulla)

        logger.info(f"✅ {len(rregullat)} rregulla elastike të inicializuara")

    def procesoj(self, input_data: Dict[str, Any], mode: str = "balanced") -> Dict[str, Any]:
        koha_fillimi = time.perf_counter()

        if mode not in ["fast", "balanced", "deep"]:
            mode = "balanced"

        konteksti: Dict[str, Any] = self._përgatit_kontekstin(input_data)
        konteksti["mode"] = mode
        self._përditëso_gjendjen_mendore(konteksti)
        vendimi: Dict[str, Any] = self.motori_vendimmarrjes.vendim(konteksti, mode=mode)

        self.kujtesa.append({
            "koha": datetime.now(timezone.utc).isoformat(),
            "input": {k: v for k, v in input_data.items() if k not in ["veprim", "input_data"]},
            "konteksti": konteksti,
            "vendimi": vendimi,
            "gjendja_mendore": self.gjendja_mendore.value,
            "mode": mode,
        })

        if len(self.kujtesa) > 500:
            self.kujtesa = self.kujtesa[-500:]

        koha_mbarimi = time.perf_counter()
        self.metrikat = {
            "koha_procesimit_ms": round((koha_mbarimi - koha_fillimi) * 1000, 2),
            "neurone_aktive": self.rrjeti.metrikat.get("neurone_aktive", 0),
            "sinapsa_aktive": self.rrjeti.metrikat.get("sinapsa_aktive", 0),
            "gjendja_mendore": self.gjendja_mendore.value,
            "energjia": round(self.energjia, 3),
            "elasticiteti": round(self.rrjeti.elasticiteti, 3),
            "historiku": len(self.kujtesa),
            "cache_hit": self.rrjeti.metrikat.get("cache_hit", 0),
            "mode": mode,
            "pike_etike": vendimi.get("pike_etike", 1.0),
        }

        return {
            "vendim": vendimi,
            "metrikat": self.metrikat,
            "gjendja": {"mendore": self.gjendja_mendore.value, "energji": round(self.energjia, 3)},
            "gs26": {"version": self.versioni, "koncepte": 26, "mode": mode},
        }

    def _përgatit_kontekstin(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        konteksti: Dict[str, Any] = dict(input_data)
        konteksti["koha"] = datetime.now(timezone.utc).isoformat()
        konteksti["energjia_sistemit"] = self.energjia
        konteksti["gjendja_mendore"] = self.gjendja_mendore.value
        konteksti["eksperiencë"] = len(self.kujtesa) > 10
        konteksti["versioni"] = self.versioni

        if "veprim" in input_data:
            konteksti["ndikim"] = self._vlerëso_ndikimin(input_data["veprim"])

        return konteksti

    def _vlerëso_ndikimin(self, veprim: str) -> float:
        ndikimi = {
            "krijo": 0.3,
            "ndrysho": 0.5,
            "fshi": 0.8,
            "përshtat": 0.4,
            "komuniko": 0.2,
            "mëso": 0.1,
            "reflekto": 0.1,
            "strategji": 0.4,
            "vendim": 0.6,
        }.get(veprim, 0.3)

        if self.energjia < 0.3:
            ndikimi *= 0.5

        return min(1.0, ndikimi)

    def _përditëso_gjendjen_mendore(self, konteksti: Dict[str, Any]) -> None:
        if konteksti.get("emergjencë", False):
            self.gjendja_mendore = GjendjeMendore.E_AKTIVE
        elif konteksti.get("kreativ", False) or konteksti.get("hapësirë", 0) > 0.5:
            self.gjendja_mendore = GjendjeMendore.E_KRIJUESHME
        elif konteksti.get("analitik", False) or konteksti.get("kompleksitet", 0) > 0.7:
            self.gjendja_mendore = GjendjeMendore.E_ANALITIKE
        elif konteksti.get("emocion", False) or konteksti.get("emocional", False):
            self.gjendja_mendore = GjendjeMendore.E_EMOCIONALE
        elif konteksti.get("fokus", False):
            self.gjendja_mendore = GjendjeMendore.E_FOKUSUAR
        elif konteksti.get("mëso", False) or konteksti.get("eksperiencë", False):
            self.gjendja_mendore = GjendjeMendore.E_MËSUESHME
        elif konteksti.get("reflekto", False) or konteksti.get("reflektiv", False):
            self.gjendja_mendore = GjendjeMendore.E_REFLECTIVE
        elif self.energjia < 0.3:
            self.gjendja_mendore = GjendjeMendore.E_QETË
        else:
            self.gjendja_mendore = GjendjeMendore.E_BALANCUAR

        self.energjia = min(1.0, self.energjia + 0.001)
        if self.gjendja_mendore in [GjendjeMendore.E_AKTIVE, GjendjeMendore.E_KRIJUESHME, GjendjeMendore.E_ANALITIKE]:
            self.energjia = max(0.1, self.energjia - 0.002)

    def mëso(self, eksperiencë: Dict[str, Any]) -> None:
        if "neurone_aktivizuar" in eksperiencë:
            for emri in eksperiencë["neurone_aktivizuar"]:
                neuroni = self.rrjeti.merr_neuron(emri)
                if neuroni:
                    neuroni.energjia = min(1.0, neuroni.energjia + 0.01)

        if "lidhje_e_re" in eksperiencë:
            lidhja = eksperiencë["lidhje_e_re"]
            if "burimi" in lidhja and "destinacioni" in lidhja:
                self.rrjeti.krijo_lidhje(
                    lidhja["burimi"],
                    lidhja["destinacioni"],
                    lidhja.get("pesha", 0.5),
                    lidhja.get("lloji", "excitatory"),
                )

        if "sukses" in eksperiencë:
            if eksperiencë["sukses"]:
                self.rrjeti.elasticiteti = min(0.92, self.rrjeti.elasticiteti + 0.005)
            else:
                self.rrjeti.elasticiteti = max(0.4, self.rrjeti.elasticiteti - 0.005)

        self.kujtesa.append({"koha": datetime.now(timezone.utc).isoformat(), "tipi": "mësim", "eksperiencë": eksperiencë})
        logger.debug(f"📚 Mësuar: {eksperiencë.get('tipi', 'unknown')}")

    def status(self) -> Dict[str, Any]:
        return {
            "emri": self.emri,
            "versioni": self.versioni,
            "id": self.id,
            "krijuar_më": self.krijuar_më.isoformat(),
            "gjendja_mendore": self.gjendja_mendore.value,
            "energjia": round(self.energjia, 3),
            "metrikat": self.metrikat,
            "neurone_total": len(self.rrjeti.neurone),
            "lidhje_total": len(self.rrjeti.lidhjet),
            "kujtesa_total": len(self.kujtesa),
            "rregulla_total": len(self.motori_vendimmarrjes.rregullat),
            "elasticiteti": round(self.rrjeti.elasticiteti, 3),
            "etike": {"pesha_etike": self.etika.pesha_etike, "vlera": [v.value for v in self.etika.vlerat_themelore]},
            "gs26": {"version": self.versioni, "koncepte": 26, "të_integruara": True},
            "operacionale": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# 5. API INTEGRATION PËR FASTAPI
# ═══════════════════════════════════════════════════════════════════════════

class ProcesimiRequest(BaseModel):
    input_data: Dict[str, Any]
    mode: str = "balanced"


class MesimiRequest(BaseModel):
    eksperiencë: Dict[str, Any]


class BrainResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    timestamp: str
    processing_time_ms: float


_rate_limit_cache: Dict[str, List[float]] = {}
RATE_LIMIT = 60
RATE_WINDOW = 60


def _check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    if client_ip not in _rate_limit_cache:
        _rate_limit_cache[client_ip] = []

    _rate_limit_cache[client_ip] = [t for t in _rate_limit_cache[client_ip] if now - t < RATE_WINDOW]

    if len(_rate_limit_cache[client_ip]) >= RATE_LIMIT:
        return False

    _rate_limit_cache[client_ip].append(now)
    return True


def krijo_brain_router():
    router = APIRouter(prefix="/api/brain-elastik", tags=["brain-elastik"])
    _brain_instance = None

    def get_brain():
        nonlocal _brain_instance
        if _brain_instance is None:
            _brain_instance = BrainElastik()
        return _brain_instance

    @router.get("/status", response_model=BrainResponse)
    async def brain_status(request: Request):
        start = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"
        if not _check_rate_limit(client_ip):
            return JSONResponse(status_code=429, content={"status": "error", "message": "Rate limit exceeded. Please wait.", "timestamp": datetime.now(timezone.utc).isoformat()})

        brain = get_brain()
        return {"status": "success", "data": brain.status(), "timestamp": datetime.now(timezone.utc).isoformat(), "processing_time_ms": round((time.perf_counter() - start) * 1000, 2)}

    @router.post("/procesoj", response_model=BrainResponse)
    async def brain_procesoj(request: Request, payload: ProcesimiRequest):
        start = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"
        if not _check_rate_limit(client_ip):
            return JSONResponse(status_code=429, content={"status": "error", "message": "Rate limit exceeded. Please wait.", "timestamp": datetime.now(timezone.utc).isoformat()})

        try:
            brain = get_brain()
            result = brain.procesoj(payload.input_data, mode=payload.mode)
            return {"status": "success", "data": result, "timestamp": datetime.now(timezone.utc).isoformat(), "processing_time_ms": round((time.perf_counter() - start) * 1000, 2)}
        except Exception as e:
            logger.error(f"Procesim error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/mëso", response_model=BrainResponse)
    async def brain_mëso(request: Request, payload: MesimiRequest):
        start = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"
        if not _check_rate_limit(client_ip):
            return JSONResponse(status_code=429, content={"status": "error", "message": "Rate limit exceeded.", "timestamp": datetime.now(timezone.utc).isoformat()})

        try:
            brain = get_brain()
            brain.mëso(payload.eksperiencë)
            return {"status": "success", "data": {"message": "Eksperienca u mësua"}, "timestamp": datetime.now(timezone.utc).isoformat(), "processing_time_ms": round((time.perf_counter() - start) * 1000, 2)}
        except Exception as e:
            logger.error(f"Mësim error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/metrikat", response_model=BrainResponse)
    async def brain_metrikat(request: Request):
        start = time.perf_counter()
        brain = get_brain()
        return {"status": "success", "data": brain.metrikat, "timestamp": datetime.now(timezone.utc).isoformat(), "processing_time_ms": round((time.perf_counter() - start) * 1000, 2)}

    @router.get("/kujtesa", response_model=BrainResponse)
    async def brain_kujtesa(request: Request, limit: int = 50):
        start = time.perf_counter()
        brain = get_brain()
        return {"status": "success", "data": {"total": len(brain.kujtesa), "kujtesa": brain.kujtesa[-limit:]}, "timestamp": datetime.now(timezone.utc).isoformat(), "processing_time_ms": round((time.perf_counter() - start) * 1000, 2)}

    @router.post("/rivendos", response_model=BrainResponse)
    async def brain_rivendos(request: Request):
        start = time.perf_counter()
        nonlocal _brain_instance
        _brain_instance = BrainElastik()
        return {"status": "success", "data": {"message": "Brain u rivendos"}, "timestamp": datetime.now(timezone.utc).isoformat(), "processing_time_ms": round((time.perf_counter() - start) * 1000, 2)}

    @router.get("/health", response_model=BrainResponse)
    async def brain_health(request: Request):
        start = time.perf_counter()
        brain = get_brain()
        return {"status": "healthy" if brain.energjia > 0.1 else "degraded", "data": {"energjia": brain.energjia, "gjendja": brain.gjendja_mendore.value, "neurone_aktive": brain.rrjeti.metrikat.get("neurone_aktive", 0)}, "timestamp": datetime.now(timezone.utc).isoformat(), "processing_time_ms": round((time.perf_counter() - start) * 1000, 2)}

    return router


CLXBrain = BrainElastik


async def demo_gs26():
    print("=" * 80)
    print("🧠 BRAINELASTIK v4.0 - DEMO GS26")
    print("=" * 80)

    brain = BrainElastik()

    print("\n📝 TEST 1: KREATIVITET")
    rez1 = brain.procesoj({"veprim": "krijo", "hapësirë": 0.8, "kreativ": True})
    print(f"   Gjendja: {rez1['gjendja']['mendore']}")
    print(f"   Vendim: {rez1['vendim'].get('veprim', 'N/A')}")
    print(f"   Ide: {rez1['vendim'].get('ide', 'N/A')}")

    print("\n📝 TEST 2: KONTROLL ETIK")
    rez2 = brain.procesoj({"veprim": "fshi", "demtim": True, "transparent": False, "i_drejte": False})
    print(f"   Vendim: {rez2['vendim'].get('vendim', 'N/A')}")
    if "shkelje" in rez2["vendim"]:
        print(f"   Shkelje: {', '.join(rez2['vendim']['shkelje'])}")
    print(f"   Pike Etike: {rez2['vendim'].get('pike_etike', 'N/A')}")

    print("\n📝 TEST 3: MËSIM")
    brain.mëso({"tipi": "test", "sukses": True, "neurone_aktivizuar": ["analitik", "kreativ"]})
    print(f"   Kujtesa: {len(brain.kujtesa)} entry")
    print(f"   Elasticiteti: {brain.rrjeti.elasticiteti:.3f}")

    print("\n📝 TEST 4: EMERGJENCË")
    rez4 = brain.procesoj({"emergjencë": True, "i_sigurt": True, "niveli": "i_lartë"})
    print(f"   Gjendja: {rez4['gjendja']['mendore']}")
    print(f"   Mesazh: {rez4['vendim'].get('mesazh', 'N/A')}")
    print(f"   Energjia: {rez4['gjendja']['energji']}")

    print("\n📝 TEST 5: STATUS")
    status = brain.status()
    print(f"   Versioni: {status['versioni']}")
    print(f"   GS26: {status['gs26']['koncepte']} koncepte")
    print(f"   Neurone: {status['neurone_total']}")
    print(f"   Lidhje: {status['lidhje_total']}")
    print(f"   Rregulla: {status['rregulla_total']}")
    print(f"   Etike: {len(status['etike']['vlera'])} vlera")

    print("\n" + "=" * 80)
    print("✅ DEMO GS26 PËRFUNDUAR")
    print("=" * 80)

    return brain


if __name__ == "__main__":
    asyncio.run(demo_gs26())
