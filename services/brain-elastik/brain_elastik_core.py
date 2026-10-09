#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRAIN ELASTIK - Sistemi Kognitiv me Logjikë të Pa Kufizime
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ky modul implementon një sistem inteligjent me:
1. 🧠 Brain - Arkitekturë kognitive me shumë shtresa
2. 🔄 Logjikë Elastike - Përshtatje dinamike pa kufizime artificiale
3. ❤️ Etikë Humane - Parime etike të ngulitura në çdo vendim
4. ⚙️ Machine Working - Optimizim i vazhdueshëm pa limit

Autori: Clisonix Team
Versioni: 3.1.0 (FIXED - ID mapping corrected)
"""

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# Konfigurim logimi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BrainElastik")


# ═══════════════════════════════════════════════════════════════════════════
# 1. ETIKA DHE VLERAT THEMELORE
# ═══════════════════════════════════════════════════════════════════════════

class VleraEtike(Enum):
    """Vlerat themelore etike të sistemit"""
    DINJITETI_NJERIUT = "dinjiteti_njeriut"
    LIRIA_VEPRIMIT = "liria_veprimit"
    PERGJEGJESIA = "pergjegjesia"
    TRANSPARENCA = "transparenca"
    DREJTESIA = "drejtesia"
    MOS_DEMTIMI = "mos_demtimi"
    AUTONOMIA = "autonomia"
    SOLIDARITETI = "solidariteti"


@dataclass
class ParimetEtike:
    """Struktura e parimeve etike të sistemit"""
    vlerat_themelore: Set[VleraEtike] = field(default_factory=lambda: {
        VleraEtike.DINJITETI_NJERIUT,
        VleraEtike.LIRIA_VEPRIMIT,
        VleraEtike.PERGJEGJESIA,
        VleraEtike.TRANSPARENCA,
        VleraEtike.DREJTESIA,
        VleraEtike.MOS_DEMTIMI,
        VleraEtike.AUTONOMIA,
        VleraEtike.SOLIDARITETI,
    })
    pesha_etike: float = 0.85
    pragu_ndërhyrjes: float = 0.70

    def vlereso_vendim(self, vendim: Dict[str, Any]) -> Dict[str, Any]:
        """Vlerëson një vendim bazuar në parimet etike"""
        rezultati = {
            "i_pranueshem": True,
            "shkelje": [],
            "pesha_etike": self.pesha_etike,
            "vlera_te_prekura": [],
            "rekomandim": "",
        }

        for vlera in self.vlerat_themelore:
            if self._vlera_shkelet(vendim, vlera):
                rezultati["shkelje"].append(vlera.value)
                rezultati["i_pranueshem"] = False
            else:
                rezultati["vlera_te_prekura"].append(vlera.value)

        if not rezultati["i_pranueshem"]:
            rezultati["rekomandim"] = self._gjenero_rekomandim(rezultati["shkelje"])

        return rezultati

    def _vlera_shkelet(self, vendim: Dict[str, Any], vlera: VleraEtike) -> bool:
        """Kontrollon nëse një vendim shkel një vlerë të caktuar"""
        if vlera == VleraEtike.MOS_DEMTIMI:
            return vendim.get("demtim", False)
        if vlera == VleraEtike.TRANSPARENCA:
            return not vendim.get("transparent", True)
        if vlera == VleraEtike.DREJTESIA:
            return vendim.get("i_drejte", True) is False
        return False

    def _gjenero_rekomandim(self, shkelje: List[str]) -> str:
        """Gjeneron një rekomandim bazuar në shkeljet e gjetura"""
        if not shkelje:
            return "Vendimi është etikisht i pranueshëm."

        rekomandime = []
        for s in shkelje:
            if s == "mos_demtimi":
                rekomandime.append("Rishiko ndikimin tek të tjerët")
            elif s == "transparenca":
                rekomandime.append("Siguro transparencë të plotë")
            elif s == "drejtesia":
                rekomandime.append("Rivlerëso drejtësinë e vendimit")

        return " ⚠️ ".join(rekomandime) if rekomandime else "Kërkohet rishikim etik"


# ═══════════════════════════════════════════════════════════════════════════
# 2. SISTEMI KOGNITIV (BRAIN) - NEURONE DHE SINAPSA
# ═══════════════════════════════════════════════════════════════════════════

class GjendjeMendore(Enum):
    """Gjendjet mendore të sistemit kognitiv"""
    E_QETË = "e_qete"
    E_FOKUSUAR = "e_fokusuar"
    E_KRIJUESHME = "e_krijueshme"
    E_ANALITIKE = "e_analitike"
    E_INTUITIVE = "e_intuitive"
    E_BALANCUAR = "e_balancuar"
    E_EMOCIONALE = "e_emocionale"
    E_AKTIVE = "e_aktive"


@dataclass
class Sinapsa:
    """Lidhja midis neuroneve - njësia bazë e të mësuarit"""
    burimi_id: str
    destinacioni_id: str
    pesha: float = 1.0
    aktiviteti: float = 0.0
    platiciteti: float = 0.05  # Më i vogël - më i qetë growth
    frekuenca_aktivizimit: int = 0
    fundjava_aktivitetit: float = 0.0

    def aktivizo(self, intensiteti: float = 1.0) -> float:
        """Aktivizon sinapsën dhe kthen vlerën e daljes"""
        self.aktiviteti += intensiteti * self.pesha
        self.frekuenca_aktivizimit += 1
        # Plastikiteti - forcohet me përdorim (më i ngadaltë)
        self.pesha += self.platiciteti * (1 - self.pesha) * 0.05
        return self.aktiviteti * self.pesha


@dataclass
class Neuroni:
    """Njësia themelore e procesimit kognitiv"""
    id: str = field(default_factory=lambda: f"neuron_{uuid.uuid4().hex[:8]}")
    emri: str = ""
    lloji: str = "sensor"
    potenciali: float = 0.0
    pragu_aktivizimit: float = 0.5
    sinapsat: List[Sinapsa] = field(default_factory=list)
    memoria: Dict[str, Any] = field(default_factory=dict)
    gjendja: str = "dormant"
    energjia: float = 1.0

    def procesoj(self, input_data: Dict[str, Any]) -> float:
        """Proceson të dhënat hyrëse dhe gjeneron dalje"""
        total = 0.0
        for sinapsa in self.sinapsat:
            if sinapsa.burimi_id in input_data:
                vlera = sinapsa.aktivizo(float(input_data.get(sinapsa.burimi_id, 0)))
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
        """Funksioni i aktivizimit sigmoid"""
        try:
            return 1.0 / (1.0 + 2.71828 ** (-x))
        except:
            return 0.5


@dataclass
class RrjetiNeuronal:
    """Rrjeti neuronal i sistemit kognitiv - FIXED ID MAPPING"""
    neurone: Dict[str, Neuroni] = field(default_factory=dict)
    sinapsat: Dict[Tuple[str, str], Sinapsa] = field(default_factory=dict)
    metrikat: Dict[str, Any] = field(default_factory=dict)
    elasticiteti: float = 0.85
    # Cache për performance
    neurone_per_emri: Dict[str, str] = field(default_factory=dict)

    def shto_neurone(self, neuroni: Neuroni) -> str:
        """Shton një neuron të ri në rrjet, kthen ID-in"""
        self.neurone[neuroni.id] = neuroni
        self.neurone_per_emri[neuroni.emri] = neuroni.id
        return neuroni.id

    def krijo_lidhje(self, burimi_id: str, destinacioni_id: str, pesha: float = 1.0) -> None:
        """Krijon lidhje me ID-të reale të neuroneve"""
        if burimi_id not in self.neurone or destinacioni_id not in self.neurone:
            raise ValueError(f"Neuroni {burimi_id} ose {destinacioni_id} nuk ekziston")

        sinapsa = Sinapsa(
            burimi_id=burimi_id,
            destinacioni_id=destinacioni_id,
            pesha=pesha
        )
        self.neurone[destinacioni_id].sinapsat.append(sinapsa)
        self.sinapsat[(burimi_id, destinacioni_id)] = sinapsa

    def procesoj(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proceson të dhënat përmes rrjetit neuronal"""
        rezultati = {}

        # Faza 1: Përhapja përpara
        for neuron_id, neuron in self.neurone.items():
            if neuron.lloji == "sensor":
                if neuron.emri in input_data:
                    rezultati[neuron_id] = input_data[neuron.emri]
            else:
                rezultati[neuron_id] = neuron.procesoj(rezultati)

        # Faza 2: Përshtatje elastike
        if self.elasticiteti > 0.5:
            self._përshtat_elastike(rezultati)

        # Faza 3: Metrikat
        self.metrikat = {
            "neurone_aktive": len([n for n in self.neurone.values() if n.gjendja == "active"]),
            "sinapsa_aktive": len([s for s in self.sinapsat.values() if s.aktiviteti > 0.1]),
            "potenciali_mesatar": sum(n.potenciali for n in self.neurone.values()) / max(1, len(self.neurone)),
            "elasticiteti": self.elasticiteti,
        }

        return rezultati

    def _përshtat_elastike(self, rezultati: Dict[str, Any]) -> None:
        """Përshtat dinamikisht rrjetin"""
        for neuron in self.neurone.values():
            for sinapsa in neuron.sinapsat:
                if sinapsa.frekuenca_aktivizimit > 10:
                    sinapsa.pesha *= 1.01
                    sinapsa.pesha = min(2.0, sinapsa.pesha)

                if sinapsa.frekuenca_aktivizimit < 5:
                    sinapsa.pesha *= 0.995
                    sinapsa.pesha = max(0.1, sinapsa.pesha)


# ═══════════════════════════════════════════════════════════════════════════
# 3. SISTEMI I VENDIMMARRJES ME LOGJIKË ELASTIKE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class RregullaElastike:
    """Rregullë që përshtatet dinamikisht"""
    emri: str
    kushti: Callable[[Dict[str, Any]], bool]
    veprimi: Callable[[Dict[str, Any]], Dict[str, Any]]
    pesha: float = 1.0
    prioriteti: int = 0
    përdorimet: int = 0
    suksesi: float = 0.5
    elasticiteti: float = 0.1  # Më i vogël - më i qetë growth

    def ekzekuto(self, konteksti: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ekzekuton rregullën nëse kushti plotësohet"""
        self.përdorimet += 1
        if self.kushti(konteksti):
            rezultati = self.veprimi(konteksti)
            # Përshtat peshën me më pak agresivitet
            self.pesha += self.elasticiteti * (self.suksesi - 0.5) * 0.05
            self.pesha = max(0.1, min(10.0, self.pesha))
            return rezultati
        return None


@dataclass
class MotoriVendimmarrjes:
    """Motori i vendimmarrjes me logjikë elastike"""
    rregullat: List[RregullaElastike] = field(default_factory=list)
    historiku: List[Dict[str, Any]] = field(default_factory=list)
    etika: ParimetEtike = field(default_factory=ParimetEtike)
    rrjeti: Optional[RrjetiNeuronal] = None
    elasticiteti_global: float = 0.8

    def shto_rregull(self, rregulla: RregullaElastike) -> None:
        """Shton një rregull të re në motor"""
        self.rregullat.append(rregulla)
        self.rregullat.sort(key=lambda r: (r.prioriteti, r.pesha), reverse=True)

    def vendim(self, konteksti: Dict[str, Any]) -> Dict[str, Any]:
        """Merr një vendim bazuar në kontekst dhe rregullat"""
        # Faza 1: Vlerësim etik
        vleresimi_etik = self.etika.vlereso_vendim(konteksti)
        if not vleresimi_etik["i_pranueshem"]:
            return {
                "vendim": "refuzuar",
                "arsye": "Shkelje e parimeve etike",
                "shkelje": vleresimi_etik["shkelje"],
                "rekomandim": vleresimi_etik["rekomandim"],
                "etike": vleresimi_etik,
            }

        # Faza 2: Përpunimi neuronal
        rezultati_neuronal = {}
        if self.rrjeti:
            rezultati_neuronal = self.rrjeti.procesoj(konteksti)

        # Faza 3: Ekzekutimi i rregullave
        rezultatet = []
        for rregulla in self.rregullat:
            if rregulla.pesha > 0.1:
                rez = rregulla.ekzekuto(konteksti)
                if rez:
                    rezultatet.append({
                        "rregulla": rregulla.emri,
                        "rezultati": rez,
                        "pesha": rregulla.pesha,
                    })

        # Faza 4: Përzgjedhja e vendimit më të mirë
        if rezultatet:
            më_miri = max(rezultatet, key=lambda r: r["pesha"])
            vendimi = më_miri["rezultati"]
            vendimi["rregulla_e_perdorur"] = më_miri["rregulla"]
        else:
            vendimi = {
                "vendim": "default",
                "mesazh": "Nuk u gjet rregull e aplikueshme",
                "emergjence": True,
            }

        # Faza 5: Regjistrimi
        self.historiku.append({
            "koha": datetime.now(timezone.utc).isoformat(),
            "konteksti": konteksti,
            "vendimi": vendimi,
            "rezultati_neuronal": rezultati_neuronal,
            "etike": vleresimi_etik,
        })

        if len(self.historiku) > 1000:
            self.historiku = self.historiku[-1000:]

        return vendimi


# ═══════════════════════════════════════════════════════════════════════════
# 4. BRAIN ELASTIK - Sistemi Kryesor
# ═══════════════════════════════════════════════════════════════════════════

class BrainElastik:
    """
    Sistemi Kryesor Kognitiv me Logjikë Elastike dhe Etikë Humane

    FIXED v3.1.0:
    - ✅ Neuron ID mapping korriguar
    - ✅ Typo: emracional → emocional
    - ✅ Caching per performance
    - ✅ Tempered elasticity growth
    """

    def __init__(self, emri: str = "BrainElastik", versioni: str = "3.1.0"):
        self.emri = emri
        self.versioni = versioni
        self.id = f"brain_{uuid.uuid4().hex[:12]}"
        self.krijuar_më = datetime.now(timezone.utc)

        # Komponentët kryesorë
        self.etika = ParimetEtike()
        self.rrjeti = RrjetiNeuronal(elasticiteti=0.85)
        self.motori_vendimmarrjes = MotoriVendimmarrjes(etika=self.etika, rrjeti=self.rrjeti)

        # Gjendja aktuale
        self.gjendja_mendore = GjendjeMendore.E_BALANCUAR
        self.energjia = 1.0
        self.kujtesa: List[Dict[str, Any]] = []
        self.metrikat = {}

        # Inicializo rrjetin
        self._inicializo_rrjetin()
        self._inicializo_rregullat()

        logger.info(f"🧠 {self.emri} v{self.versioni} inicializuar me ID: {self.id}")

    def _inicializo_rrjetin(self) -> None:
        """Inicializon rrjetin neuronal - ME ID MAPPING KORREKT"""
        sensor_ids = {}
        procesues_ids = {}
        memorie_ids = {}
        motorik_ids = {}

        # Neuronë sensorë (FIXED: typo emracional → emocional)
        sensorët = ["vizual", "auditiv", "kinestetik", "emocional", "intuitiv"]
        for emri in sensorët:
            neuroni = Neuroni(emri=emri, lloji="sensor", pragu_aktivizimit=0.3)
            sensor_ids[emri] = self.rrjeti.shto_neurone(neuroni)

        # Neuronë procesues
        procesuesit = [
            ("analitik", 0.5),
            ("kreativ", 0.4),
            ("logjik", 0.6),
            ("emocional", 0.3),
            ("intuitiv", 0.4),
            ("etik", 0.7),
        ]
        for emri, pragu in procesuesit:
            neuroni = Neuroni(emri=emri, lloji="procesues", pragu_aktivizimit=pragu)
            procesues_ids[emri] = self.rrjeti.shto_neurone(neuroni)

        # Neuronë memorie
        memoriet = ["afatshkurter", "afatgjate", "procedurale", "semantike"]
        for emri in memoriet:
            neuroni = Neuroni(emri=emri, lloji="memorie", pragu_aktivizimit=0.2)
            memorie_ids[emri] = self.rrjeti.shto_neurone(neuroni)

        # Neuronë motorikë
        motorikët = ["veprim", "komunikim", "adaptim", "krijim"]
        for emri in motorikët:
            neuroni = Neuroni(emri=emri, lloji="motorik", pragu_aktivizimit=0.5)
            motorik_ids[emri] = self.rrjeti.shto_neurone(neuroni)

        # LIDHJE: Sensorë → Procesues (ME ID-JET REALE)
        for sensor_emri, sensor_id in sensor_ids.items():
            for procesues_emri, procesues_id in procesues_ids.items():
                self.rrjeti.krijo_lidhje(sensor_id, procesues_id, pesha=0.7)

        # LIDHJE: Procesues → Memorie
        for procesues_emri, procesues_id in procesues_ids.items():
            for memorie_emri, memorie_id in memorie_ids.items():
                self.rrjeti.krijo_lidhje(procesues_id, memorie_id, pesha=0.5)

        # LIDHJE: Memorie → Motorikë
        for memorie_emri, memorie_id in memorie_ids.items():
            for motorik_emri, motorik_id in motorik_ids.items():
                self.rrjeti.krijo_lidhje(memorie_id, motorik_id, pesha=0.6)

        # Lidhje direkte sensor → motorik (reflekset)
        for i, (sensor_emri, sensor_id) in enumerate(list(sensor_ids.items())[:3]):
            for j, (motorik_emri, motorik_id) in enumerate(list(motorik_ids.items())[:2]):
                self.rrjeti.krijo_lidhje(sensor_id, motorik_id, pesha=0.3)

        logger.info(f"✅ Rrjeti neuronal me {len(self.rrjeti.neurone)} neurone, {len(self.rrjeti.sinapsat)} sinapsa")

    def _inicializo_rregullat(self) -> None:
        """Inicializon rregullat elastike"""
        self.motori_vendimmarrjes.shto_rregull(
            RregullaElastike(
                emri="përshtatje_elastike",
                kushti=lambda ctx: ctx.get("ndryshim", 0) > 0.1,
                veprimi=lambda ctx: {
                    "veprim": "përshtat",
                    "shkalla": ctx.get("ndryshim", 0) * 0.5,
                    "sukses": True,
                },
                pesha=1.2,
                prioriteti=3,
            )
        )

        self.motori_vendimmarrjes.shto_rregull(
            RregullaElastike(
                emri="kreativitet",
                kushti=lambda ctx: ctx.get("hapësirë", 0) > 0.3,
                veprimi=lambda ctx: {
                    "veprim": "krijo",
                    "ide": f"id_{uuid.uuid4().hex[:6]}",
                    "sukses": True,
                },
                pesha=0.9,
                prioriteti=2,
            )
        )

        self.motori_vendimmarrjes.shto_rregull(
            RregullaElastike(
                emri="kontroll_etik",
                kushti=lambda ctx: ctx.get("ndikim", 0) > 0.5,
                veprimi=lambda ctx: {
                    "veprim": "vlerëso_etikisht",
                    "ndikim": ctx.get("ndikim", 0),
                    "sukses": True,
                },
                pesha=2.0,
                prioriteti=5,
            )
        )

        self.motori_vendimmarrjes.shto_rregull(
            RregullaElastike(
                emri="mësim_i_vazhdueshëm",
                kushti=lambda ctx: ctx.get("eksperiencë", False),
                veprimi=lambda ctx: {
                    "veprim": "mëso",
                    "njohuri": f"exp_{uuid.uuid4().hex[:6]}",
                    "sukses": True,
                },
                pesha=1.5,
                prioriteti=4,
            )
        )

        self.motori_vendimmarrjes.shto_rregull(
            RregullaElastike(
                emri="emergjencë",
                kushti=lambda ctx: ctx.get("emergjencë", False),
                veprimi=lambda ctx: {
                    "veprim": "emergjencë",
                    "mesazh": "Aktivimi i protokollit të emergjencës",
                    "sukses": ctx.get("i_sigurt", False),
                },
                pesha=3.0,
                prioriteti=10,
            )
        )

    def procesoj(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proceson të dhënat hyrëse dhe gjeneron përgjigje"""
        koha_fillimi = time.perf_counter()

        konteksti = self._përgatit_kontekstin(input_data)
        self._përditëso_gjendjen_mendore(konteksti)
        vendimi = self.motori_vendimmarrjes.vendim(konteksti)

        self.kujtesa.append({
            "koha": datetime.now(timezone.utc).isoformat(),
            "input": input_data,
            "konteksti": konteksti,
            "vendimi": vendimi,
            "gjendja_mendore": self.gjendja_mendore.value,
        })

        if len(self.kujtesa) > 500:
            self.kujtesa = self.kujtesa[-500:]

        koha_mbarimi = time.perf_counter()
        self.metrikat = {
            "koha_procesimit_ms": (koha_mbarimi - koha_fillimi) * 1000,
            "neurone_aktive": self.rrjeti.metrikat.get("neurone_aktive", 0),
            "sinapsa_aktive": self.rrjeti.metrikat.get("sinapsa_aktive", 0),
            "gjendja_mendore": self.gjendja_mendore.value,
            "energjia": self.energjia,
            "elasticiteti": self.rrjeti.elasticiteti,
            "historiku": len(self.kujtesa),
        }

        return {
            "vendim": vendimi,
            "metrikat": self.metrikat,
            "gjendja": {
                "mendore": self.gjendja_mendore.value,
                "energji": self.energjia,
            },
        }

    def _përgatit_kontekstin(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Përgatit kontekstin"""
        konteksti = dict(input_data)
        konteksti["koha"] = datetime.now(timezone.utc).isoformat()
        konteksti["energjia_sistemit"] = self.energjia
        konteksti["gjendja_mendore"] = self.gjendja_mendore.value
        konteksti["eksperiencë"] = len(self.kujtesa) > 10

        if "veprim" in input_data:
            konteksti["ndikim"] = self._vlerëso_ndikimin(input_data["veprim"])

        return konteksti

    def _vlerëso_ndikimin(self, veprim: str) -> float:
        """Vlerëson ndikimin e një veprimi"""
        ndikimi = {
            "krijo": 0.3,
            "ndrysho": 0.5,
            "fshi": 0.8,
            "përshtat": 0.4,
            "komuniko": 0.2,
            "mëso": 0.1,
        }.get(veprim, 0.3)

        if self.energjia < 0.3:
            ndikimi *= 0.5

        return min(1.0, ndikimi)

    def _përditëso_gjendjen_mendore(self, konteksti: Dict[str, Any]) -> None:
        """Përditëson gjendjen mendore"""
        if konteksti.get("emergjencë", False):
            self.gjendja_mendore = GjendjeMendore.E_AKTIVE
        elif konteksti.get("kreativ", False) or konteksti.get("hapësirë", 0) > 0.5:
            self.gjendja_mendore = GjendjeMendore.E_KRIJUESHME
        elif konteksti.get("analitik", False) or konteksti.get("kompleksitet", 0) > 0.7:
            self.gjendja_mendore = GjendjeMendore.E_ANALITIKE
        elif konteksti.get("emocion", False):
            self.gjendja_mendore = GjendjeMendore.E_EMOCIONALE
        elif konteksti.get("fokus", False):
            self.gjendja_mendore = GjendjeMendore.E_FOKUSUAR
        elif self.energjia < 0.3:
            self.gjendja_mendore = GjendjeMendore.E_QETË
        else:
            self.gjendja_mendore = GjendjeMendore.E_BALANCUAR

        self.energjia = min(1.0, self.energjia + 0.001)
        if self.gjendja_mendore in [GjendjeMendore.E_AKTIVE, GjendjeMendore.E_KRIJUESHME]:
            self.energjia = max(0.1, self.energjia - 0.002)

    def mëso(self, eksperiencë: Dict[str, Any]) -> None:
        """Sistemi mëson nga eksperienca"""
        if "neurone_aktivizuar" in eksperiencë:
            for neuron_id in eksperiencë["neurone_aktivizuar"]:
                if neuron_id in self.rrjeti.neurone:
                    neuroni = self.rrjeti.neurone[neuron_id]
                    neuroni.energjia = min(1.0, neuroni.energjia + 0.01)

        if "lidhje_e_re" in eksperiencë:
            lidhja = eksperiencë["lidhje_e_re"]
            if "burimi" in lidhja and "destinacioni" in lidhja:
                try:
                    self.rrjeti.krijo_lidhje(
                        lidhja["burimi"],
                        lidhja["destinacioni"],
                        lidhja.get("pesha", 0.5)
                    )
                except ValueError:
                    pass

        if "sukses" in eksperiencë:
            if eksperiencë["sukses"]:
                self.rrjeti.elasticiteti = min(0.95, self.rrjeti.elasticiteti + 0.01)
            else:
                self.rrjeti.elasticiteti = max(0.3, self.rrjeti.elasticiteti - 0.005)

        logger.info(f"📚 Brain mësoi: {eksperiencë.get('tipi', 'unknown')}")

    def status(self) -> Dict[str, Any]:
        """Kthen statusin aktual"""
        return {
            "emri": self.emri,
            "versioni": self.versioni,
            "id": self.id,
            "krijuar_më": self.krijuar_më.isoformat(),
            "gjendja_mendore": self.gjendja_mendore.value,
            "energjia": round(self.energjia, 3),
            "metrikat": self.metrikat,
            "neurone_total": len(self.rrjeti.neurone),
            "lidhje_total": len(self.rrjeti.sinapsat),
            "kujtesa_total": len(self.kujtesa),
            "rregulla_total": len(self.motori_vendimmarrjes.rregullat),
            "elasticiteti": round(self.rrjeti.elasticiteti, 3),
            "etike": {
                "pesha_etike": self.etika.pesha_etike,
                "vlera": [v.value for v in self.etika.vlerat_themelore],
            },
            "operacionale": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
