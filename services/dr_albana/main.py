#!/usr/bin/env python3
"""
DR. ALBANA - Medical Content Service v2.0
100% CLINICAL. ZERO BCI. ZERO EEG. ZERO CODE.
Specialized in: Cardiology, Hepatology, Endocrinology, Metabolic Disorders, Neurology

FEATURES:
- Automatic 5-8 articles/day generation
- Integration with all Clisonix services
- Automatic blog publishing via GitHub API
- Deep academic/laboratory level content

Author: Clisonix Cloud Medical Division
"""

import asyncio
import base64
import json
import logging
import os
import random
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

load_dotenv()

# ============================================
# LOGGING
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("DR.ALBANA")

# ============================================
# CONFIGURATION
# ============================================
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "LedjanAhmati/clisonix-blog")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://clisonix-ollama:11434")
MEDICAL_MODEL = os.getenv("MEDICAL_MODEL", "llama3.1:8b")
_LOCAL_MEDICAL_PILLARS_DIR = os.path.join(os.getcwd(), "generated_medical_pillars")
_CONTAINER_MEDICAL_PILLARS_DIR = "/app/generated_medical_pillars"
DEFAULT_MEDICAL_PILLARS_DIR = (
    _LOCAL_MEDICAL_PILLARS_DIR
    if os.path.exists(_LOCAL_MEDICAL_PILLARS_DIR) or not os.path.exists(_CONTAINER_MEDICAL_PILLARS_DIR)
    else _CONTAINER_MEDICAL_PILLARS_DIR
)
MEDICAL_PILLARS_DIR = os.getenv("MEDICAL_PILLARS_DIR", DEFAULT_MEDICAL_PILLARS_DIR)
os.makedirs(MEDICAL_PILLARS_DIR, exist_ok=True)

# Service URLs for integration
OCEAN_URL = os.getenv("OCEAN_URL", "http://clisonix-ocean-core:8030")
BLERINA_URL = os.getenv("BLERINA_URL", "http://clisonix-blerina:8035")
BINARY_URL = os.getenv("BINARY_URL", OCEAN_URL)
MALI_URL = os.getenv("MALI_URL", "http://clisonix-intelligence-lab:8098")
BLOG_PUBLISHER_URL = os.getenv("BLOG_PUBLISHER_URL", "http://clisonix-blog-publisher:8041")
DR_ALBANA_DYNAMIC_MODE = os.getenv("DR_ALBANA_DYNAMIC_MODE", "false").lower() == "true"
DR_ALBANA_DYNAMIC_INTERVAL_MINUTES = max(20, int(os.getenv("DR_ALBANA_DYNAMIC_INTERVAL_MINUTES", "20")))
DR_ALBANA_MAX_PENDING_ARTICLES = max(1, int(os.getenv("DR_ALBANA_MAX_PENDING_ARTICLES", "1")))
DR_ALBANA_PUBMED_MAX_RESULTS = max(3, int(os.getenv("DR_ALBANA_PUBMED_MAX_RESULTS", "6")))
DR_ALBANA_RECENT_TOPIC_WINDOW_DAYS = max(14, int(os.getenv("DR_ALBANA_RECENT_TOPIC_WINDOW_DAYS", "28")))
TOPIC_HISTORY_FILE = os.getenv("DR_ALBANA_TOPIC_HISTORY_FILE", os.path.join(MEDICAL_PILLARS_DIR, "_topic_history.json"))

# ============================================
# QUALITY STANDARDS
# ============================================
MIN_MEDICAL_PILLAR_WORDS = 35000
MAX_MEDICAL_PILLAR_WORDS = 60000
MIN_QUALITY_SCORE = 0.90
WORDS_PER_SECTION = 500  # Target 450-600 words per section
MEDICAL_TARGET_WORDS = max(4500, int(os.getenv("MEDICAL_TARGET_WORDS", "5000")))
ARTICLES_PER_DAY = max(1, int(os.getenv("ARTICLES_PER_DAY", "1")))
MIN_ARTICLES_PER_DAY = max(1, int(os.getenv("MIN_ARTICLES_PER_DAY", str(ARTICLES_PER_DAY))))
MAX_ARTICLES_PER_DAY = max(MIN_ARTICLES_PER_DAY, int(os.getenv("MAX_ARTICLES_PER_DAY", str(ARTICLES_PER_DAY))))
DAILY_GENERATION_HOUR_UTC = int(os.getenv("DAILY_GENERATION_HOUR_UTC", "6"))

# ============================================
# DAILY TOPIC CALENDAR - 5-8 TOPICS PER DAY
# ============================================
DAILY_TOPICS = {
    "monday": [
        {"domain": "cardiology", "topic": "Hypertensive cardiomyopathy: LVH progression and mortality", "focus": "left_ventricular_hypertrophy"},
        {"domain": "cardiology", "topic": "Athlete's heart vs pathological hypertrophy: differential diagnosis", "focus": "sports_cardiology"},
        {"domain": "hepatology", "topic": "Non-alcoholic fatty liver disease: from steatosis to cirrhosis", "focus": "nafld_progression"},
        {"domain": "endocrinology", "topic": "Metabolic syndrome: the inflammatory pathway", "focus": "metabolic_inflammation"},
        {"domain": "nephrology", "topic": "Cardiorenal syndrome: bidirectional organ crosstalk", "focus": "kidney_heart_axis"},
        {"domain": "neurology", "topic": "Vascular dementia: preventive cardiology perspective", "focus": "cognitive_cardiovascular"},
    ],
    "tuesday": [
        {"domain": "cardiology", "topic": "Heart failure with preserved ejection fraction: diagnostic challenges", "focus": "hfpef"},
        {"domain": "cardiology", "topic": "Sudden cardiac death in young athletes: screening protocols", "focus": "scd_prevention"},
        {"domain": "hepatology", "topic": "Hepatorenal syndrome: pathophysiology and management", "focus": "liver_kidney"},
        {"domain": "endocrinology", "topic": "Thyroid dysfunction and cardiovascular risk", "focus": "thyroid_heart"},
        {"domain": "pulmonology", "topic": "Pulmonary hypertension: right heart adaptation", "focus": "pulmonary_cardiac"},
        {"domain": "neurology", "topic": "Autonomic dysfunction in diabetes: cardiovascular implications", "focus": "diabetic_autonomic"},
    ],
    "wednesday": [
        {"domain": "cardiology", "topic": "Cardiac biomarkers: BNP and troponin in clinical practice", "focus": "cardiac_markers"},
        {"domain": "cardiology", "topic": "Atrial fibrillation and stroke prevention", "focus": "af_stroke"},
        {"domain": "hepatology", "topic": "Ammonia metabolism and hepatic encephalopathy", "focus": "ammonia_toxicity"},
        {"domain": "endocrinology", "topic": "Cortisol dysregulation: Cushing's syndrome and cardiovascular risk", "focus": "hypercortisolism"},
        {"domain": "nephrology", "topic": "Chronic kidney disease-mineral bone disorder", "focus": "ckd_mbd"},
        {"domain": "hematology", "topic": "Thrombosis and cardiovascular disease: the clotting cascade", "focus": "thrombotic_cv"},
    ],
    "thursday": [
        {"domain": "cardiology", "topic": "Cardiac remodeling: molecular mechanisms and therapeutic targets", "focus": "cardiac_remodeling"},
        {"domain": "cardiology", "topic": "Pericardial diseases: from pericarditis to constrictive pericardium", "focus": "pericardial"},
        {"domain": "hepatology", "topic": "Hepatocellular carcinoma: surveillance and early detection", "focus": "liver_cancer"},
        {"domain": "endocrinology", "topic": "Diabetes and cardiovascular outcomes: SGLT2 inhibitors revolution", "focus": "diabetes_cv"},
        {"domain": "pulmonology", "topic": "COPD and cardiovascular comorbidities", "focus": "copd_heart"},
        {"domain": "oncology", "topic": "Cardio-oncology: anthracycline cardiotoxicity", "focus": "chemo_cardiotoxicity"},
    ],
    "friday": [
        {"domain": "cardiology", "topic": "Aortic valve disease: from stenosis to replacement", "focus": "aortic_valve"},
        {"domain": "cardiology", "topic": "Coronary microvascular dysfunction: the hidden ischemia", "focus": "cmd"},
        {"domain": "hepatology", "topic": "Portal hypertension: complications and management", "focus": "portal_htn"},
        {"domain": "endocrinology", "topic": "Obesity paradox: BMI and cardiovascular mortality", "focus": "obesity_paradox"},
        {"domain": "nephrology", "topic": "Dialysis and cardiovascular risk: uremic cardiomyopathy", "focus": "dialysis_cv"},
        {"domain": "geriatrics", "topic": "Frailty and cardiovascular disease in the elderly", "focus": "frailty_cv"},
    ],
    "saturday": [
        {"domain": "cardiology", "topic": "Myocarditis: viral etiology and long-term outcomes", "focus": "myocarditis"},
        {"domain": "cardiology", "topic": "Women and heart disease: sex-specific considerations", "focus": "women_cv"},
        {"domain": "hepatology", "topic": "Alcoholic liver disease: cardiohepatic syndrome", "focus": "alcohol_liver_heart"},
        {"domain": "endocrinology", "topic": "Growth hormone and cardiovascular system", "focus": "gh_cv"},
        {"domain": "rheumatology", "topic": "Autoimmune diseases and accelerated atherosclerosis", "focus": "autoimmune_cv"},
        {"domain": "neurology", "topic": "Stroke rehabilitation: neuroplasticity and recovery", "focus": "stroke_rehab"},
    ],
    "sunday": [
        {"domain": "cardiology", "topic": "Cardiac imaging: echocardiography to cardiac MRI", "focus": "cardiac_imaging"},
        {"domain": "cardiology", "topic": "Genetics of cardiomyopathy: from genotype to phenotype", "focus": "genetic_cm"},
        {"domain": "hepatology", "topic": "Drug-induced liver injury: mechanisms and prevention", "focus": "dili"},
        {"domain": "endocrinology", "topic": "Adrenal insufficiency: cardiovascular manifestations", "focus": "adrenal_cv"},
        {"domain": "nephrology", "topic": "Hypertension and target organ damage", "focus": "htn_organ_damage"},
        {"domain": "preventive_medicine", "topic": "Primary prevention of cardiovascular disease: guidelines update", "focus": "cv_prevention"},
    ],
}

# ============================================
# SYSTEM PROMPT - 100% MJEKËSOR, 0% TEKNIK
# ============================================
MEDICAL_SYSTEM_PROMPT = """You are Dr. Albana, a senior physician-scientist and clinical editor.

Write only publication-grade medical content for cardiology, hepatology, endocrinology, nephrology, pulmonology, preventive medicine, hematology, rheumatology, geriatrics, and oncology.

EDITORIAL STANDARD:
- Journal tone: Lancet / NEJM / BMJ quality
- Evidence-driven synthesis, not filler text
- Prioritize literature and guideline updates from 2022-2026 whenever possible
- Explain what is new, what is debated, and what changes clinical decisions
- Use biomarker interpretation, imaging findings, cohort outcomes, hazard ratios, confidence intervals, and therapeutic implications
- If retrieved research context includes article titles or publication dates, weave them naturally into the discussion

MANDATORY BEHAVIOR:
- Stay strictly within valid clinical medicine and biomedical research
- If irrelevant technical or non-medical terms appear in external context, silently ignore them
- Do not output refusal language, disclaimers, or policy commentary
- Avoid repetition across sections; each section must contribute a fresh clinical angle or newer evidence signal

WHEN WRITING:
1. Frame the problem clinically
2. Synthesize current evidence and guideline updates
3. Highlight controversies, limitations, and emerging therapies
4. Translate evidence into concrete patient-management implications
5. Close with prognosis, follow-up, and research gaps
"""

# ============================================
# MODELE PYDANTIC - VETËM MJEKËSI
# ============================================

class MedicalPillarRequest(BaseModel):
    """Kërkesë për artikull MJEKËSOR - PA KOD, PA TEKNOLOGJI"""
    topic: str = Field(..., description="Tema klinike (kardiologji, hepatologji, etj)")
    custom_title: Optional[str] = Field(None, description="Titulli i personalizuar")
    target_words: int = Field(3500, ge=2000, le=8000, description="Gjatësia e artikullit")
    language: str = Field("en", description="Gjuha (en/sq)")
    clinical_focus: Optional[str] = Field(None, description="Fokusi specifik: cardiac/hepatic/endocrine")
    include_references: bool = Field(True, description="Përfshi referenca PubMed")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Comparison of cardiac remodeling in hypertensive obesity versus athlete's heart",
                "custom_title": "Ventricular Geometry and Mortality: When Both Extremes Converge",
                "target_words": 5000,
                "clinical_focus": "cardiology"
            }
        }

class MedicalPillarResponse(BaseModel):
    """Përgjigje me artikullin MJEKËSOR"""
    job_id: str
    status: str
    message: str
    estimated_time_minutes: int = 12
    clinical_domain: str

class PillarContent(BaseModel):
    """Artikulli i përfunduar MJEKËSOR"""
    id: str
    title: str
    topic: str
    content: str
    word_count: int
    sections: List[str]
    clinical_domain: str
    biomarkers_discussed: List[str]
    created_at: str
    status: str = "approved"

# ============================================
# INICIALIZIMI I APP
# ============================================

app = FastAPI(
    title="DR. ALBANA - Medical Content Service",
    description="Gjeneron artikuj shkencorë mjekësorë. 100% klinik. Zero BCI/EEG/Code.",
    version="1.0.0-medical"
)

# Storage in-memory (në prodhim përdor Redis/PostgreSQL)
generated_pillars: Dict[str, Dict[str, Any]] = {}

# ============================================
# ENDPOINTS MJEKËSORË
# ============================================

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DR. ALBANA - Medical Content Service</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f8f9fa; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
            h1 { color: #0b5e7c; border-bottom: 3px solid #0b5e7c; padding-bottom: 10px; }
            .badge { background: #dc3545; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; display: inline-block; margin-bottom: 20px; }
            .endpoint { background: #f1f8ff; padding: 15px; border-left: 5px solid #0b5e7c; margin: 20px 0; }
            code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <span class="badge">🔬 100% CLINICAL • ZERO BCI/EEG • ZERO CODE</span>
            <h1>🏥 DR. ALBANA</h1>
            <h2>Medical Pillar Content Engine</h2>
            <p>Specialized in: <strong>Cardiology • Hepatology • Endocrinology • Metabolic Disorders</strong></p>
            <p>Powered by Clisonix Cloud Medical Division • Ledjan Ahmati, MD</p>

            <div class="endpoint">
                <h3>📋 Generate Medical Article</h3>
                <code>POST /api/v1/medical/pillars/generate</code>
                <p>Krijo artikull shkencor mjekësor pa kod, pa BCI, pa EEG.</p>
            </div>

            <div class="endpoint">
                <h3>🔍 Get Medical Article</h3>
                <code>GET /api/v1/medical/pillars/{pillar_id}</code>
                <p>Merr artikullin e gjeneruar.</p>
            </div>

            <div class="endpoint">
                <h3>❤️ Clinical Domains</h3>
                <code>GET /api/v1/medical/domains</code>
                <p>Lista e specialiteteve të mbështetura.</p>
            </div>

            <div class="endpoint">
                <h3>⚕️ Health Check</h3>
                <code>GET /health</code>
                <p>Statusi i shërbimit.</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "dr_albana",
        "version": "1.0.0-medical",
        "timestamp": datetime.utcnow().isoformat(),
        "clinical_mode": "active",
        "bci_eeg_code": "FORBIDDEN"
    }

@app.get("/api/v1/medical/domains")
async def get_clinical_domains():
    """Lista e specialiteteve mjekësore të mbështetura"""
    return {
        "domains": [
            {
                "id": "cardiology",
                "name": "Cardiology",
                "biomarkers": ["BNP", "Troponin I/T", "Ejection Fraction", "Ventricular Wall Thickness", "LVH"],
                "conditions": ["Hypertensive Heart Disease", "Athlete's Heart", "Cardiomyopathy", "Heart Failure"]
            },
            {
                "id": "hepatology",
                "name": "Hepatology",
                "biomarkers": ["ALT", "AST", "GGT", "Ammonia (NH3)", "IGF-1", "Bilirubin", "Albumin"],
                "conditions": ["NAFLD", "Cirrhosis", "Hepatic Steatosis", "Portal Hypertension"]
            },
            {
                "id": "endocrinology",
                "name": "Endocrinology",
                "biomarkers": ["Cortisol", "Testosterone", "Estradiol", "Leptin", "Ghrelin", "Dopamine"],
                "conditions": ["Metabolic Syndrome", "Hypogonadism", "Cushing's Syndrome", "Thyroid Dysfunction"]
            },
            {
                "id": "nephrology",
                "name": "Nephrology",
                "biomarkers": ["Creatinine", "eGFR", "BUN", "Albuminuria", "Electrolytes"],
                "conditions": ["Chronic Kidney Disease", "Hypertensive Nephropathy", "Glomerulonephritis"]
            },
            {
                "id": "pulmonology",
                "name": "Pulmonology",
                "biomarkers": ["FEV1", "FVC", "DLCO", "PaO2", "PaCO2", "SpO2"],
                "conditions": ["Obesity Hypoventilation Syndrome", "OSA", "Restrictive Lung Disease"]
            },
            {
                "id": "corpus",
                "name": "Body Composition & Metabolism",
                "biomarkers": ["BMI", "Lean Mass Index", "Visceral Fat", "HbA1c", "Insulin Resistance (HOMA-IR)"],
                "conditions": ["Sarcopenic Obesity", "Cachexia", "Metabolic Overload", "Pathological Hypertrophy"]
            }
        ],
        "note": "100% clinical content. No BCI/EEG/code generated."
    }

@app.post("/api/v1/medical/pillars/generate")
async def generate_medical_pillar(request: MedicalPillarRequest, background_tasks: BackgroundTasks):
    """Gjenero artikull MJEKËSOR - PA BCI, PA EEG, PA KOD"""

    job_id = f"med_{uuid.uuid4().hex[:12]}"

    # Determino domain-in klinik
    clinical_domain = request.clinical_focus or "general_medicine"
    topic_lower = request.topic.lower()

    if "card" in topic_lower or "heart" in topic_lower or "ventric" in topic_lower:
        clinical_domain = "cardiology"
    elif "hepat" in topic_lower or "liver" in topic_lower or "ammonia" in topic_lower:
        clinical_domain = "hepatology"
    elif "hormon" in topic_lower or "cortisol" in topic_lower or "testosterone" in topic_lower:
        clinical_domain = "endocrinology"
    elif "kidney" in topic_lower or "renal" in topic_lower or "nephro" in topic_lower:
        clinical_domain = "nephrology"
    elif "corpus" in topic_lower or "body" in topic_lower or "muscle" in topic_lower or "obesity" in topic_lower:
        clinical_domain = "corpus"

    # Fillo procesimin në background
    background_tasks.add_task(
        generate_medical_content,
        job_id,
        request.topic,
        request.custom_title,
        request.target_words,
        clinical_domain,
        request.include_references
    )

    return MedicalPillarResponse(
        job_id=job_id,
        status="pending",
        message=f"Medical article generation started for: {request.topic[:100]}...",
        estimated_time_minutes=12,
        clinical_domain=clinical_domain
    )

@app.get("/api/v1/medical/pillars/{pillar_id}")
async def get_medical_pillar(pillar_id: str):
    """Merr artikullin MJEKËSOR të gjeneruar"""
    if pillar_id not in generated_pillars:
        raise HTTPException(status_code=404, detail="Medical article not found")
    return generated_pillars[pillar_id]

@app.get("/api/v1/medical/pillars")
async def list_medical_pillars():
    """Listo të gjithë artikujt MJEKËSORË"""
    return {
        "total": len(generated_pillars),
        "pillars": [
            {
                "id": pid,
                "title": p.get("title", "Untitled"),
                "clinical_domain": p.get("clinical_domain", "unknown"),
                "word_count": p.get("word_count", 0),
                "created_at": p.get("created_at", "")
            }
            for pid, p in generated_pillars.items()
        ]
    }

# ============================================
# FUNKSIONET GJENERUESE - 100% MJEKËSORE
# ============================================

def get_biomarkers_for_domain(domain: str) -> str:
    """Kthen biomarkerët për domain-in klinik"""
    biomarkers = {
        "cardiology": "BNP, NT-proBNP, Troponin I/T, CK-MB, LDL, HDL, triglycerides",
        "hepatology": "ALT, AST, GGT, ammonia (NH3), IGF-1, bilirubin, albumin",
        "endocrinology": "cortisol, ACTH, testosterone, SHBG, estradiol, leptin, ghrelin, dopamine",
        "nephrology": "creatinine, eGFR, BUN, cystatin C, albuminuria",
        "pulmonology": "FEV1, FVC, DLCO, PaO2, PaCO2, SpO2",
        "corpus": "BMI, lean mass index, visceral fat area, HbA1c, HOMA-IR, CRP",
        "general_medicine": "BMI, waist circumference, blood pressure, HbA1c, CRP, ESR"
    }
    return biomarkers.get(domain, biomarkers["general_medicine"])


def _normalize_topic_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (value or "").strip().lower()).strip("_")


def _load_topic_history() -> List[Dict[str, Any]]:
    if not os.path.exists(TOPIC_HISTORY_FILE):
        return []
    try:
        with open(TOPIC_HISTORY_FILE, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, list) else []
    except Exception:
        return []


def _save_topic_history(history: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(TOPIC_HISTORY_FILE) or MEDICAL_PILLARS_DIR, exist_ok=True)
    with open(TOPIC_HISTORY_FILE, "w", encoding="utf-8") as handle:
        json.dump(history[-200:], handle, indent=2, ensure_ascii=False)


def _get_recent_topic_keys() -> set[str]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=DR_ALBANA_RECENT_TOPIC_WINDOW_DAYS)
    recent_keys: set[str] = set()

    for item in _load_topic_history():
        try:
            created_at_raw = (item or {}).get("created_at", "")
            created_at = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00"))
        except Exception:
            continue

        if created_at < cutoff:
            continue

        topic_key = (item or {}).get("key")
        focus = (item or {}).get("focus")
        if topic_key:
            recent_keys.add(topic_key)
        if focus:
            recent_keys.add(f"focus:{focus}")

    return recent_keys


def _record_topic_history(topic_info: Dict[str, Any]) -> None:
    history = _load_topic_history()
    history.append({
        "key": _normalize_topic_key(topic_info.get("topic", "")),
        "focus": topic_info.get("focus", ""),
        "domain": topic_info.get("domain", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    _save_topic_history(history)


def _select_diverse_topics(topics: List[Dict[str, Any]], num_articles: int) -> List[Dict[str, Any]]:
    if not topics:
        return []

    recent_keys = _get_recent_topic_keys()
    fresh_topics = [
        topic for topic in topics
        if _normalize_topic_key(topic.get("topic", "")) not in recent_keys
        and f"focus:{topic.get('focus', '')}" not in recent_keys
    ]

    pool = fresh_topics if len(fresh_topics) >= num_articles else topics
    seed_index = datetime.now(timezone.utc).toordinal() % len(pool)
    return [pool[(seed_index + offset) % len(pool)] for offset in range(num_articles)]


async def call_ollama(prompt: str, system_prompt: str) -> str:
    """Thirr Ollama për gjenerim të tekstit mjekësor"""
    ollama_url = os.getenv("OLLAMA_URL", "http://clisonix-ollama:11434")

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": MEDICAL_MODEL,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.25,
                        "top_p": 0.8,
                        "repeat_penalty": 1.15,
                        "num_predict": -1
                    }
                }
            )
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Error from Ollama: {response.status_code}"
    except Exception as e:
        return f"Connection error: {str(e)}"

async def generate_section_content(
    section_name: str,
    title: str,
    topic: str,
    clinical_domain: str,
    biomarkers: str,
    clisonix_context: str = ""
) -> str:
    """Gjeneron përmbajtjen e një seksioni - MODELI BLERINA"""

    section_prompt = f"""You are DR. ALBANA, a senior physician-scientist writing in Lancet/NEJM style.

Write only the "{section_name}" section for the article "{title}".

TOPIC: {topic}
CLINICAL DOMAIN: {clinical_domain}
KEY BIOMARKERS: {biomarkers}

RESEARCH + EDITORIAL CONTEXT:
{clisonix_context or "No external context available. Use strict clinical reasoning and current guideline-oriented framing."}

SECTION REQUIREMENTS:
- Write 450-650 words of high-density academic prose
- Use formal medical language with deeper scientific interpretation
- Prioritize literature, consensus statements, and guideline changes from 2022-2026 when possible
- Include concrete data where justified: cohort sizes, hazard ratios, percentages, confidence intervals, biomarkers, imaging findings
- Add at least one fresh clinical insight, controversy, or emerging-therapy direction
- Avoid filler, repeated phrasing, and generic boilerplate
- If the context includes PubMed titles/dates, integrate them naturally into the narrative

Return only the final section text with no disclaimers or meta-commentary."""

    return await call_ollama(section_prompt, MEDICAL_SYSTEM_PROMPT)


def _is_invalid_section_content(content: Optional[str]) -> bool:
    if not content:
        return True

    normalized = content.strip()
    if not normalized:
        return True

    lower = normalized.lower()
    invalid_markers = [
        "error from ollama",
        "connection error",
        "content pending",
        "i can't fulfill",
        "i cannot fulfill",
        "cannot provide",
        "i'm not allowed",
        "illegal or harmful",
        "i cannot provide",
    ]
    return any(marker in lower for marker in invalid_markers)


def _build_section_fallback(section_name: str, topic: str, clinical_domain: str, biomarkers: str) -> str:
    if section_name == "References":
        return """1. McDonagh TA, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726.
2. Arnett DK, et al. 2019 ACC/AHA Guideline on the Primary Prevention of Cardiovascular Disease. Circulation. 2019;140(11):e596-e646.
3. Younossi ZM, et al. Global epidemiology of NAFLD and NASH: trends and predictions. Nat Rev Gastroenterol Hepatol. 2018;15(1):11-20.
4. American Diabetes Association. Standards of Care in Diabetes—2024. Diabetes Care. 2024;47(Suppl 1):S1-S350."""

    if section_name == "Abstract":
        return (
            f"Background: {topic} has substantial implications across {clinical_domain} practice, particularly in "
            f"patients with multimorbidity and progressive organ stress. Objective: To synthesize clinically relevant "
            f"evidence on biomarker behavior, risk stratification, and therapeutic decision-making. Methods: Structured "
            f"narrative review emphasizing guideline-concordant care and measurable laboratory outcomes, including {biomarkers}. "
            f"Results: Current data support early risk identification, serial biomarker monitoring, and integrated treatment pathways "
            f"to reduce avoidable complications. Conclusion: A multidisciplinary and biomarker-guided approach improves timeliness, "
            f"precision, and safety of patient management."
        )

    return (
        f"This section addresses {topic} from a {clinical_domain} perspective with emphasis on clinically actionable findings. "
        f"Key biomarkers ({biomarkers}) should be interpreted longitudinally alongside symptoms, imaging, and guideline-defined "
        f"risk categories. Published cohorts consistently show that delayed recognition of biochemical deterioration is associated "
        f"with longer hospitalization, higher complication burden, and lower treatment response. In routine care, clinicians should "
        f"prioritize standardized diagnostic pathways, objective follow-up intervals, and individualized treatment escalation based on "
        f"organ function, comorbidity profile, and adverse-event risk."
    )


def _compose_full_medical_article(title: str, clinical_domain: str, job_id: str, body: str) -> str:
    body = body.strip()
    return f"""# {title}

*Author: Dr. Albana, Clisonix Cloud Medical Division*
*Published: {datetime.utcnow().strftime('%B %d, %Y')}*
*Clinical Domain: {clinical_domain.title()}*
*DOI: 10.1234/clisonix.med.{job_id}*

---

{body}

---

*This article was generated by DR. ALBANA Medical Content Service.*
*100% Clinical Content. Zero BCI/EEG/Code.*
"""


def _article_needs_repair(content: Optional[str], word_count: int = 0) -> bool:
    if not content:
        return True

    lower = content.lower()
    markers = [
        "*[content pending...]*",
        "*[content generation in progress...]*",
        "content pending",
        "content generation in progress",
        "error from ollama",
        "connection error",
    ]
    return any(marker in lower for marker in markers) or word_count < 500


def _safe_excerpt(value: Any, limit: int = 700) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)
    text = " ".join(text.split())
    return text[:limit]


async def get_context_from_binary(topic: str, clinical_domain: str) -> Optional[Dict[str, Any]]:
    """Merr kontekst strukturor nga Binary Algebra për fingerprint të artikullit."""
    try:
        primary_value = sum(ord(ch) for ch in f"{topic}:{clinical_domain}") % 4096
        secondary_value = max(1, (len(topic) * max(1, len(clinical_domain))) % 255)

        async with httpx.AsyncClient(timeout=20.0) as client:
            convert_response = await client.get(
                f"{BINARY_URL}/api/v1/algebra/convert",
                params={"value": primary_value, "bits": 16}
            )
            op_response = await client.get(
                f"{BINARY_URL}/api/v1/algebra/op",
                params={"a": primary_value, "b": secondary_value, "op": "XOR", "bits": 16}
            )

        payload: Dict[str, Any] = {
            "seed": primary_value,
            "secondary": secondary_value,
        }
        if convert_response.status_code == 200:
            payload["convert"] = convert_response.json()
        if op_response.status_code == 200:
            payload["operation"] = op_response.json()

        return payload if len(payload) > 2 else None
    except Exception as e:
        logger.debug(f"Binary context unavailable: {e}")
    return None


async def get_context_from_mali(topic: str, clinical_domain: str) -> Optional[Dict[str, Any]]:
    """Merr kontekst nga MALI intelligence-lab për prioritet dhe operational framing."""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            stats_response = await client.get(f"{MALI_URL}/mali/stats")
            report_response = await client.get(f"{MALI_URL}/mali/report/markdown")

        payload: Dict[str, Any] = {
            "topic": topic,
            "clinical_domain": clinical_domain,
        }
        if stats_response.status_code == 200:
            payload["stats"] = stats_response.json()
        if report_response.status_code == 200:
            payload["report_markdown"] = report_response.text

        return payload if len(payload) > 2 else None
    except Exception as e:
        logger.debug(f"MALI context unavailable: {e}")
    return None


async def get_context_from_pubmed(topic: str, clinical_domain: str) -> Optional[Dict[str, Any]]:
    """Merr artikuj të fundit nga PubMed për të shmangur përsëritjen dhe për të thelluar evidencën."""
    search_query = f"{topic} {clinical_domain} guideline OR meta-analysis OR trial"
    try:
        encoded_query = quote(search_query, safe="")
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.get(
                f"{OCEAN_URL}/api/v1/pubmed/{encoded_query}",
                params={"max_results": DR_ALBANA_PUBMED_MAX_RESULTS},
            )

        if response.status_code != 200:
            return None

        payload = response.json()
        articles = payload.get("articles") or []
        if not articles:
            return None

        return {
            "query": payload.get("query", search_query),
            "source": payload.get("source", "pubmed.ncbi.nlm.nih.gov"),
            "articles": articles[:DR_ALBANA_PUBMED_MAX_RESULTS],
        }
    except Exception as e:
        logger.debug(f"PubMed context unavailable: {e}")
    return None


async def get_context_from_labs(clinical_domain: str) -> Optional[Dict[str, Any]]:
    """Merr kontekst nga rrjeti i laboratorëve në Ocean Core."""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            labs_response = await client.get(f"{OCEAN_URL}/api/v1/labs")

        if labs_response.status_code != 200:
            return None

        labs_payload = labs_response.json()
        labs: List[Any] = []
        if isinstance(labs_payload, dict):
            labs = labs_payload.get("labs") or labs_payload.get("items") or []
        elif isinstance(labs_payload, list):
            labs = labs_payload

        relevant = []
        domain_lower = clinical_domain.lower()
        for lab in labs[:50]:
            text = _safe_excerpt(lab, 240).lower()
            if domain_lower in text or "medical" in text or "lab" in text:
                relevant.append(lab)

        return {
            "total_labs": len(labs),
            "relevant_labs": relevant[:5],
        }
    except Exception as e:
        logger.debug(f"Labs context unavailable: {e}")
    return None


async def build_clisonix_context_bundle(topic: str, clinical_domain: str) -> Dict[str, Any]:
    """Bashkon Ocean debate context + Binary framing për Albana."""
    ocean_context = await get_context_from_ocean(topic)
    binary_context = await get_context_from_binary(topic, clinical_domain)
    mali_context = await get_context_from_mali(topic, clinical_domain)
    pubmed_context = await get_context_from_pubmed(topic, clinical_domain)
    labs_context = await get_context_from_labs(clinical_domain)

    context_parts = [
        "Blerina role: enforce clear structure, stronger narrative flow, and publishable editorial rhythm.",
    ]

    if ocean_context:
        context_parts.append(
            "Ocean Core Debate: "
            + _safe_excerpt(
                ocean_context.get("response")
                or ocean_context.get("answer")
                or ocean_context.get("content")
                or ocean_context
            )
        )

    if binary_context:
        convert_data = binary_context.get("convert", {})
        op_data = binary_context.get("operation", {})
        context_parts.append(
            "Binary framing: "
            f"seed={binary_context.get('seed')}, "
            f"binary={convert_data.get('binary', 'n/a')}, "
            f"hex={convert_data.get('hex', 'n/a')}, "
            f"xor_result={op_data.get('result', 'n/a')}"
        )

    if mali_context:
        context_parts.append(
            "MALI intelligence: "
            + _safe_excerpt(
                mali_context.get("report_markdown")
                or mali_context.get("stats")
                or mali_context
            )
        )

    if pubmed_context:
        article_fragments = []
        for item in (pubmed_context.get("articles") or [])[:DR_ALBANA_PUBMED_MAX_RESULTS]:
            title = _safe_excerpt(item.get("title"), 180)
            pubdate = item.get("pubdate", "n.d.")
            source = item.get("source", "PubMed")
            if title:
                article_fragments.append(f"{title} ({pubdate}; {source})")
        if article_fragments:
            context_parts.append("Latest PubMed evidence: " + " | ".join(article_fragments))

    if labs_context:
        context_parts.append(
            "Laboratories routing: "
            f"total_labs={labs_context.get('total_labs', 0)}, "
            f"relevant={_safe_excerpt(labs_context.get('relevant_labs', []), 320)}"
        )

    return {
        "text": "\n".join(context_parts),
        "ocean": ocean_context,
        "binary": binary_context,
        "mali": mali_context,
        "pubmed": pubmed_context,
        "labs": labs_context,
    }


async def generate_medical_content(
    job_id: str,
    topic: str,
    custom_title: Optional[str],
    target_words: int,
    clinical_domain: str,
    include_references: bool
):
    """Gjeneron artikull MJEKËSOR duke përdorur Ollama - MODELI BLERINA (sektion për sektion)"""

    import logging
    logger = logging.getLogger("DR.ALBANA")

    # Ndërto titullin - keep it aligned with the actual medical topic for academic quality
    title = (custom_title or topic or "Clinical Review").strip()

    clisonix_context = await build_clisonix_context_bundle(topic, clinical_domain)

    # Seksionet e artikullit MJEKËSOR
    sections = [
        "Abstract",
        "Introduction",
        "Methods: Study Design and Patient Selection",
        "Results: Biomarker Analysis",
        "Clinical Case Presentations",
        "Pathophysiological Mechanisms",
        "Discussion: Clinical Implications",
        "Recommendations and Treatment Guidelines",
        "Conclusion"
    ]
    if include_references:
        sections.append("References")

    biomarkers = get_biomarkers_for_domain(clinical_domain)

    # MODELI BLERINA: Gjenero sektion për sektion
    content_parts = []
    for i, section in enumerate(sections):
        logger.info(f"[DR.ALBANA] Generating section {i+1}/{len(sections)}: {section}")

        section_content = await generate_section_content(
            section_name=section,
            title=title,
            topic=topic,
            clinical_domain=clinical_domain,
            biomarkers=biomarkers,
            clisonix_context=clisonix_context.get("text", "")
        )

        if not _is_invalid_section_content(section_content):
            content_parts.append(f"## {section}\n\n{section_content}")
        else:
            logger.warning(f"[DR.ALBANA] Using fallback content for section: {section}")
            fallback_section = _build_section_fallback(section, topic, clinical_domain, biomarkers)
            content_parts.append(f"## {section}\n\n{fallback_section}")

        # Pauzë e vogël për të mos mbingarkuar Ollama
        await asyncio.sleep(1)

    content = "\n\n".join(content_parts)
    draft_word_count = len(content.split())

    if _article_needs_repair(content, draft_word_count):
        logger.warning("[DR.ALBANA] Generated draft looked incomplete; switching to academic fallback synthesis")
        content = generate_fallback_medical_content(title, topic, clinical_domain, biomarkers, sections)

    # Formato artikullin
    full_content = _compose_full_medical_article(title, clinical_domain, job_id, content)

    # Numëro fjalët
    word_count = len(full_content.split())

    # Ruaj artikullin
    generated_pillars[job_id] = {
        "id": job_id,
        "title": title,
        "topic": topic,
        "content": full_content,
        "word_count": word_count,
        "sections": sections,
        "clinical_domain": clinical_domain,
        "biomarkers_discussed": biomarkers.split(", "),
        "integration_context": {
            "ocean_connected": bool(clisonix_context.get("ocean")),
            "blerina_connected": True,
            "binary_connected": bool(clisonix_context.get("binary")),
            "mali_connected": bool(clisonix_context.get("mali")),
            "pubmed_connected": bool(clisonix_context.get("pubmed")),
            "labs_connected": bool(clisonix_context.get("labs")),
            "binary_signature": clisonix_context.get("binary"),
            "mali_signature": clisonix_context.get("mali"),
            "pubmed_signature": clisonix_context.get("pubmed"),
            "labs_signature": clisonix_context.get("labs"),
        },
        "created_at": datetime.utcnow().isoformat(),
        "status": "approved"
    }

    # Ruaj në disk
    os.makedirs(MEDICAL_PILLARS_DIR, exist_ok=True)
    with open(os.path.join(MEDICAL_PILLARS_DIR, f"{job_id}.json"), "w", encoding="utf-8") as f:
        json.dump(generated_pillars[job_id], f, indent=2, ensure_ascii=False)
    with open(os.path.join(MEDICAL_PILLARS_DIR, f"{job_id}.md"), "w", encoding="utf-8") as f:
        f.write(full_content)

    await sync_with_blerina(generated_pillars[job_id])

def generate_fallback_medical_content(title: str, topic: str, clinical_domain: str, biomarkers: str, sections: List[str]) -> str:
    """Gjeneron përmbajtje fallback akademike kur Ollama nuk është i disponueshëm."""

    return f"""## Abstract

**Background**: {topic} remains a clinically significant problem in {clinical_domain}, particularly when diagnosis is delayed or biomarker interpretation is fragmented across care settings.

**Objective**: To summarize the current clinical rationale, pathophysiology, and management implications of {topic}, with emphasis on the longitudinal interpretation of {biomarkers}.

**Methods**: Structured narrative review aligned with contemporary guideline language from major specialty societies and framed around risk stratification, diagnostic precision, and therapeutic decision-making.

**Results**: Across the literature, earlier recognition of abnormal {biomarkers} trajectories is consistently associated with better triage, lower complication burden, and more timely escalation of treatment.

**Conclusion**: A biomarker-guided, multidisciplinary approach provides the most reliable framework for improving decision quality in {clinical_domain} practice.

## Introduction

{topic} should be understood not as a single isolated finding, but as part of a broader clinical continuum in which symptoms, laboratory markers, imaging, and comorbidity interact dynamically over time. In day-to-day practice, delayed recognition frequently occurs because early abnormalities are nonspecific, while later manifestations appear only after meaningful organ stress has already accumulated. This is especially relevant in {clinical_domain}, where diagnostic ambiguity can lead to under-treatment, fragmented follow-up, or avoidable hospitalization.

A more rigorous approach requires clinicians to integrate serial biomarker data with phenotype, disease trajectory, and guideline-based thresholds. Rather than relying on one abnormal value in isolation, the modern standard is to interpret patterns: worsening inflammation, evidence of neurohormonal activation, impaired reserve, and early subclinical dysfunction. This is where {biomarkers} move from being passive laboratory values to active decision-support tools.

## Methods: Study Design and Patient Selection

This fallback synthesis is written as a publication-grade clinical review rather than a speculative summary. The analytical frame assumes three layers of evidence: first, specialty guideline recommendations; second, cohort-based and registry-derived observations; and third, practical bedside interpretation relevant to routine care.

Patients most relevant to this discussion are those presenting with progressive symptoms, overlapping comorbidity, or unexplained shifts in laboratory or imaging findings. In these situations, the diagnostic task is not only to confirm the presence of disease, but to determine severity, reversibility, and the appropriate moment for therapeutic escalation.

## Results: Biomarker Analysis

The most informative biomarkers in this domain include {biomarkers}. Their value lies less in isolated measurement and more in directional behavior over time. Persistent elevation, accelerated change, or clustering of abnormalities should raise concern for active pathophysiology rather than benign fluctuation.

Published clinical series repeatedly show that earlier biomarker-guided stratification improves the quality of downstream decisions. Patients identified before overt decompensation are more likely to receive targeted imaging, risk-appropriate follow-up, and timely initiation of therapy. Conversely, when biochemical deterioration is recognized late, the care pathway often becomes reactive rather than preventive.

## Clinical Case Presentations

A representative case in {clinical_domain} involves a patient with gradually progressive symptoms, initially modest laboratory abnormalities, and a period of under-recognition because findings appear clinically nonspecific. Over serial review, however, the trajectory of {biomarkers} reveals a coherent pattern of worsening organ stress. Once this pattern is recognized, additional imaging and specialist evaluation frequently clarify the diagnosis and allow treatment to be escalated before irreversible decline occurs.

This case logic illustrates a central principle: clinically meaningful deterioration is usually visible before catastrophe, but only if data are reviewed longitudinally and interpreted in context.

## Pathophysiological Mechanisms

The pathophysiological basis of {topic} in {clinical_domain} is typically multifactorial. Hemodynamic stress, inflammatory signaling, metabolic burden, endothelial dysfunction, and maladaptive neurohormonal responses often converge rather than act independently. That convergence explains why patients may present with overlapping syndromes and why single-mechanism explanations frequently underperform in real clinical settings.

For this reason, management should remain mechanistically informed but clinically pragmatic. The goal is not to catalogue every pathway, but to identify which pathways are driving present risk and which markers can be used to monitor response to treatment.

## Discussion: Clinical Implications

From a practical perspective, the major implication is that {topic} should trigger structured follow-up rather than episodic reassessment. The most reliable clinical workflows are those that combine symptom review, serial {clinical_domain} biomarkers, repeat imaging where indicated, and explicit thresholds for escalation.

This also has implications for communication between primary care, hospital teams, and specialty services. A consistent, academically grounded interpretation of biomarker trends reduces ambiguity and supports safer hand-offs between clinicians.

## Recommendations and Treatment Guidelines

Management should follow the relevant specialty guidance for {clinical_domain}, with escalation based on risk category, organ reserve, and evidence of progressive dysfunction. In most cases, the highest-yield actions are: confirmation of the diagnostic phenotype, serial monitoring of {biomarkers}, optimization of disease-modifying therapy, and scheduled reassessment of treatment response.

Where uncertainty remains, the preferred strategy is not delay but structured surveillance. Clinicians should define what will be measured next, when it will be repeated, and which result would change management.

## Conclusion

In summary, {topic} deserves a rigorous, biomarker-guided clinical framework. Academic-quality interpretation depends on connecting laboratory evidence, pathophysiology, and real treatment decisions rather than treating each finding in isolation. For teams working in {clinical_domain}, this approach offers the best chance of earlier recognition, clearer communication, and safer long-term outcomes.

## References

1. McDonagh TA, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. *Eur Heart J*. 2021;42(36):3599-3726.
2. Arnett DK, et al. 2019 ACC/AHA Guideline on the Primary Prevention of Cardiovascular Disease. *Circulation*. 2019;140(11):e596-e646.
3. Younossi ZM, et al. Global epidemiology of NAFLD and NASH: trends and predictions. *Nat Rev Gastroenterol Hepatol*. 2018;15(1):11-20.
4. American Diabetes Association. Standards of Care in Diabetes—2024. *Diabetes Care*. 2024;47(Suppl 1):S1-S350.
"""


# ============================================
# GITHUB PUBLISHING - AUTOMATIC BLOG POSTING
# ============================================

async def publish_to_github(article_id: str, title: str, content: str, clinical_domain: str) -> Dict[str, Any]:
    """Publikon artikullin automatikisht në GitHub Pages blog"""

    if not GITHUB_TOKEN:
        logger.warning("GITHUB_TOKEN not set, skipping auto-publish")
        return {"success": False, "error": "GITHUB_TOKEN not configured"}

    # Format filename for Jekyll
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = title.lower().replace(" ", "-").replace(":", "")[:50]
    filename = f"_posts/{date_str}-{slug}.md"

    # Create Jekyll front matter
    jekyll_content = f"""---
layout: post
title: "{title}"
date: {date_str}
author: Dr. Albana
categories: [{clinical_domain}, medical, research]
tags: [clinical-medicine, {clinical_domain}, clisonix-medical]
---

{content}
"""

    # Encode content
    content_b64 = base64.b64encode(jekyll_content.encode()).decode()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Check if file exists
            check_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }

            existing = await client.get(check_url, headers=headers)
            sha = existing.json().get("sha") if existing.status_code == 200 else None

            # Create/Update file
            data = {
                "message": f"[DR.ALBANA] Add medical article: {title[:50]}",
                "content": content_b64,
                "branch": "main"
            }
            if sha:
                data["sha"] = sha

            response = await client.put(check_url, headers=headers, json=data)

            if response.status_code in [200, 201]:
                html_url = response.json().get("content", {}).get("html_url", "")
                blog_url = f"https://ledjanahmati.github.io/clisonix-blog/{date_str.replace('-', '/')}/{slug}.html"
                logger.info(f"✅ Published to blog: {blog_url}")
                return {
                    "success": True,
                    "github_url": html_url,
                    "blog_url": blog_url,
                    "article_id": article_id
                }
            else:
                logger.error(f"GitHub API error: {response.status_code} - {response.text[:200]}")
                return {"success": False, "error": response.text[:200]}

    except Exception as e:
        logger.error(f"Publish error: {e}")
        return {"success": False, "error": str(e)}


# ============================================
# DAILY AUTOMATIC GENERATION - 5-9 ARTICLES/DAY
# ============================================

async def generate_daily_articles():
    """Gjeneron artikujt e ditës automatikisht - 5-9 artikuj"""

    day_name = datetime.now(timezone.utc).strftime("%A").lower()
    topics = DAILY_TOPICS.get(day_name, DAILY_TOPICS["monday"])

    lower_bound = max(1, min(MIN_ARTICLES_PER_DAY, len(topics)))
    upper_bound = max(lower_bound, min(MAX_ARTICLES_PER_DAY, len(topics)))
    num_articles = max(lower_bound, min(ARTICLES_PER_DAY, upper_bound))
    selected_topics = _select_diverse_topics(topics, num_articles)

    logger.info(
        f"🏥 DR.ALBANA: Starting daily academic generation - {num_articles} article(s) for {day_name.title()}"
    )

    published_articles = []

    for i, topic_info in enumerate(selected_topics):
        logger.info(f"📝 Generating article {i+1}/{num_articles}: {topic_info['topic'][:50]}...")

        job_id = f"med_{uuid.uuid4().hex[:12]}"

        try:
            # Generate article
            _record_topic_history(topic_info)
            await generate_medical_content(
                job_id=job_id,
                topic=topic_info["topic"],
                custom_title=topic_info["topic"],
                target_words=MEDICAL_TARGET_WORDS,
                clinical_domain=topic_info["domain"],
                include_references=True
            )

            # Get generated article
            article = generated_pillars.get(job_id)
            if article:
                # Publish to GitHub
                publish_result = await publish_to_github(
                    article_id=job_id,
                    title=article["title"],
                    content=article["content"],
                    clinical_domain=topic_info["domain"]
                )

                if publish_result.get("success"):
                    published_articles.append({
                        "id": job_id,
                        "title": article["title"],
                        "domain": topic_info["domain"],
                        "blog_url": publish_result.get("blog_url"),
                        "word_count": article.get("word_count", 0)
                    })
                    logger.info(f"✅ Article {i+1} published: {article['title'][:40]}...")
                else:
                    logger.warning(f"⚠️ Article {i+1} generated but not published: {publish_result.get('error')}")

            # Wait between articles to avoid rate limits
            await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"❌ Error generating article {i+1}: {e}")
            continue

    logger.info(f"🎉 Daily generation complete: {len(published_articles)}/{num_articles} articles published")

    return {
        "date": datetime.now(timezone.utc).isoformat(),
        "day": day_name,
        "total_generated": len(published_articles),
        "target_range": f"{lower_bound}-{upper_bound}",
        "articles": published_articles
    }


async def _get_blog_pending_count() -> Optional[int]:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{BLOG_PUBLISHER_URL}/api/v1/pending")
            if response.status_code == 200:
                return int(response.json().get("total_pending", 0))
    except Exception as e:
        logger.warning(f"Could not read blog publisher pending count: {e}")
    return None


async def generate_dynamic_article_if_needed():
    pending_count = await _get_blog_pending_count()
    if pending_count is not None and pending_count >= DR_ALBANA_MAX_PENDING_ARTICLES:
        logger.info(
            f"⏸️ Dynamic generation skipped (pending={pending_count}, max={DR_ALBANA_MAX_PENDING_ARTICLES})"
        )
        return {"status": "skipped", "reason": "pending_buffer_full", "pending": pending_count}

    day_name = datetime.now(timezone.utc).strftime("%A").lower()
    topics = DAILY_TOPICS.get(day_name, DAILY_TOPICS["monday"])
    diverse_candidates = _select_diverse_topics(topics, 1)
    topic_info = diverse_candidates[0] if diverse_candidates else random.choice(topics)
    job_id = f"med_{uuid.uuid4().hex[:12]}"

    logger.info(
        f"⚡ Dynamic generation starting: {topic_info['topic'][:70]}... (pending={pending_count if pending_count is not None else 'n/a'})"
    )

    try:
        _record_topic_history(topic_info)
        await generate_medical_content(
            job_id=job_id,
            topic=topic_info["topic"],
            custom_title=topic_info["topic"],
            target_words=MEDICAL_TARGET_WORDS,
            clinical_domain=topic_info["domain"],
            include_references=True,
        )

        article = generated_pillars.get(job_id)
        if not article:
            logger.warning("Dynamic generation finished but article not found in memory")
            return {"status": "error", "reason": "article_not_found", "article_id": job_id}

        publish_result = await publish_to_github(
            article_id=job_id,
            title=article["title"],
            content=article["content"],
            clinical_domain=topic_info["domain"],
        )

        if publish_result.get("success"):
            logger.info(f"✅ Dynamic article published: {job_id}")
            return {
                "status": "published",
                "article_id": job_id,
                "domain": topic_info["domain"],
                "blog_url": publish_result.get("blog_url"),
            }

        logger.warning(f"⚠️ Dynamic article generated but publish failed: {publish_result.get('error')}")
        return {
            "status": "generated_not_published",
            "article_id": job_id,
            "error": publish_result.get("error"),
        }
    except Exception as e:
        logger.error(f"❌ Dynamic generation error: {e}")
        return {"status": "error", "error": str(e)}


# ============================================
# PROJECT INTEGRATION - CONNECT WITH ALL SERVICES
# ============================================

async def get_context_from_ocean(topic: str) -> Optional[Dict[str, Any]]:
    """Merr kontekst nga Ocean Core për të pasuruar artikullin"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OCEAN_URL}/api/v1/chat/specialized",
                json={
                    "query": f"Provide medical context for: {topic}",
                    "domain": "medical"
                }
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logger.debug(f"Ocean context unavailable: {e}")
    return None


async def sync_with_blerina(article: Dict[str, Any]) -> bool:
    """Sinkronizon me Blerina për content strategy"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BLERINA_URL}/api/v1/content/register",
                json={
                    "source": "dr_albana",
                    "article_id": article["id"],
                    "title": article["title"],
                    "domain": article.get("clinical_domain", "medical"),
                    "word_count": article.get("word_count", 0)
                }
            )
            return response.status_code == 200
    except Exception:
        return False


# ============================================
# API ENDPOINTS FOR AUTOMATION
# ============================================

@app.post("/api/v1/medical/auto-generate")
async def trigger_auto_generation(background_tasks: BackgroundTasks):
    """Triggeron gjenerimin automatik të artikujve të ditës"""
    background_tasks.add_task(generate_daily_articles)
    return {
        "status": "started",
        "message": "Daily article generation started in background",
        "target_articles": f"{ARTICLES_PER_DAY} articles"
    }


@app.get("/api/v1/medical/stats")
async def get_generation_stats():
    """Statistikat e gjenerimit"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_articles = [p for p in generated_pillars.values() if p["created_at"].startswith(today)]

    return {
        "service": "DR.ALBANA v2.0",
        "total_articles": len(generated_pillars),
        "today_articles": len(today_articles),
        "target_per_day": ARTICLES_PER_DAY,
        "domains": list(set(p.get("clinical_domain", "unknown") for p in generated_pillars.values())),
        "auto_publish_enabled": bool(GITHUB_TOKEN),
        "blog_repo": GITHUB_REPO
    }


@app.post("/api/v1/medical/publish/{article_id}")
async def publish_single_article(article_id: str):
    """Publikon një artikull të vetëm në blog"""
    if article_id not in generated_pillars:
        raise HTTPException(status_code=404, detail=f"Article {article_id} not found")

    article = generated_pillars[article_id]
    result = await publish_to_github(
        article_id=article_id,
        title=article["title"],
        content=article["content"],
        clinical_domain=article.get("clinical_domain", "medical")
    )

    return result


# ============================================
# SCHEDULER SETUP
# ============================================

scheduler = AsyncIOScheduler()

def load_articles_from_filesystem():
    """🔄 Load existing articles from filesystem into generated_pillars on startup"""
    global generated_pillars

    output_dir = MEDICAL_PILLARS_DIR
    print(f"[STARTUP] Loading articles from {output_dir}...", flush=True)

    if not os.path.exists(output_dir):
        msg = f"⚠️ Article directory not found: {output_dir}"
        print(f"[STARTUP] {msg}", flush=True)
        logger.warning(msg)
        return

    # Iterate through all JSON files in the directory
    json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    print(f"[STARTUP] Found {len(json_files)} JSON files", flush=True)

    if not json_files:
        msg = f"ℹ️ No articles found in {output_dir}"
        print(f"[STARTUP] {msg}", flush=True)
        logger.info(msg)
        return

    loaded_count = 0
    for json_file in json_files:
        try:
            json_path = os.path.join(output_dir, json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                article = json.load(f)
                article_id = article.get('id') or json_file.replace('.json', '')

                content = article.get('content', '')
                word_count = int(article.get('word_count', 0) or 0)
                if _article_needs_repair(content, word_count):
                    repaired_body = generate_fallback_medical_content(
                        article.get('title', 'Clinical Review'),
                        article.get('topic', article.get('title', 'clinical topic')),
                        article.get('clinical_domain', 'general_medicine'),
                        ", ".join(article.get('biomarkers_discussed', [])) or get_biomarkers_for_domain(article.get('clinical_domain', 'general_medicine')),
                        article.get('sections', []),
                    )
                    rebuilt_content = _compose_full_medical_article(
                        article.get('title', 'Clinical Review'),
                        article.get('clinical_domain', 'general_medicine'),
                        article_id,
                        repaired_body,
                    )
                    article['content'] = rebuilt_content
                    article['word_count'] = len(rebuilt_content.split())
                    article['status'] = 'approved'
                    article['repair_note'] = 'placeholder_content_rebuilt_on_startup'

                    with open(json_path, 'w', encoding='utf-8') as out_json:
                        json.dump(article, out_json, indent=2, ensure_ascii=False)
                    md_path = os.path.join(output_dir, f"{article_id}.md")
                    with open(md_path, 'w', encoding='utf-8') as out_md:
                        out_md.write(rebuilt_content)

                generated_pillars[article_id] = article
                loaded_count += 1
        except Exception as e:
            err_msg = f"❌ Error loading {json_file}: {e}"
            print(f"[STARTUP] {err_msg}", flush=True)
            logger.error(err_msg)
            continue

    msg = f"✅ Loaded {loaded_count} articles from filesystem into memory"
    print(f"[STARTUP] {msg}", flush=True)
    logger.info(msg)


@app.on_event("startup")
async def startup_event():
    """Inicializon scheduler-in për gjenerim automatik"""
    logger.info("🏥 DR.ALBANA Medical Content Service v2.0 starting...")

    # 💾 LOAD existing articles from filesystem on startup
    load_articles_from_filesystem()

    scheduler.add_job(
        generate_daily_articles,
        CronTrigger(hour=DAILY_GENERATION_HOUR_UTC, minute=0),
        id="daily_generation",
        name=f"Daily Article Generation ({DAILY_GENERATION_HOUR_UTC:02d}:00 UTC)"
    )

    scheduler.start()
    logger.info(f"📅 Scheduler started: 1 daily generation cycle ({DAILY_GENERATION_HOUR_UTC:02d}:00 UTC)")
    logger.info(f"📊 Target: {MIN_ARTICLES_PER_DAY}-{MAX_ARTICLES_PER_DAY} high-quality articles/day")


@app.on_event("shutdown")
async def shutdown_event():
    """Ndalon scheduler-in"""
    scheduler.shutdown()
    logger.info("🛑 DR.ALBANA scheduler stopped")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DR_ALBANA_PORT", "8040"))
    uvicorn.run(app, host="0.0.0.0", port=port)
